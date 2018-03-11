import os
import string
from flask import Flask
from flask_restful import Resource, Api
import googlemaps
from datetime import datetime
from flask_restful import reqparse
import json
import requests
from collections import Counter
import logging

import requests_cache
requests_cache.install_cache('maps_cache')

import enviro
from latlng import LatLng

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
api = Api(app)

app.config.update(
    MAPS_API_KEY = os.environ.get("MAPS_API_KEY"),
    DEBUG = False,
    LOCAL = True,
)

park_and_rides = {
   "Wilkinson Street Park & Ride": (52.972727652720891,-1.178095145038694),
   "Racecourse Park & Ride": (52.949202938055173,-1.114290514897690),
   "Phoenix Park & Ride": (52.989046559946239,-1.208008404285609),
   "Moor Bridge Park & Ride": (53.014345727625326,-1.187462109287195),
   "Forest Park & Ride": (52.965181584766448,-1.164717506856619),
   "Queens Drive Park & Ride": (52.928718217981476,-1.164183075524257),
   "Clifton Park & Ride": (52.896244, -1.194184),
   "Toton Lane Park & Ride": (52.918419, -1.262344),
   "Hucknall Park & Ride": (53.038133, -1.195858)
}

class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}

def distance_from_distance_str(s):
    d = s.strip(' km')
    return float(d)

def process_steps(steps):
    step_data = []
    for step in steps:
        step_distance = step['distance']['value']
        if 'transit_details' in step:
            #step_data.append((step['transit_details']['line']['vehicle']['type'], step_distance))
            return [(step['transit_details']['line']['vehicle']['type'], step_distance)]
        else:
            #step_data.append((step['travel_mode'], step_distance))            
            return [(step['travel_mode'], step_distance)]

    return step_data

def get_score(origin, destination, distance, mode):

    population_modifier = enviro.get_route_population_density_modifier(LatLng(*origin), LatLng(*destination))
    (co2_score, nox_score) = enviro.get_scores(enviro.get_mode(mode), distance, pop=population_modifier)

    return {
        "co2_score": co2_score,
        "nox_score": nox_score,
        "total_score": co2_score+nox_score
    }

def get_closest_pandr(origin, park_and_rides):
    closest_name = ""
    closest_distance = 10000000
    for pandr_name, pandr_latlng in park_and_rides.items():
        distance = LatLng(*pandr_latlng).distance_from(LatLng(*origin))
        if distance < closest_distance:
            closest_name = pandr_name
            closest_distance = distance

    logging.info("closest: %s, %s", closest_name, closest_distance)

    return park_and_rides[closest_name]

class Journey(Resource):
    def google_directions(self, start=None, end=None, mode="walking"):
        gmaps = googlemaps.Client(key=app.config['MAPS_API_KEY'])

        # Request directions via public transit
        now = datetime.now()
        directions_result = gmaps.directions(start,
                                             end,
                                             mode=mode,
                                             departure_time=now)

        return directions_result

    def get_route_for_mode(self, origin, destination, mode):
        directions_result = self.google_directions(start=origin,end=destination, mode=mode)

        distance = 0

        leg_keys = []
        modes = []

        for legs in directions_result[0]['legs']:
            distance = distance + distance_from_distance_str(legs['distance']['text'])
            step_data = process_steps(legs['steps'])
            for mode, distance in step_data:
                score_data = get_score(origin, destination, distance, mode)
                modes.append((mode, distance, score_data, score_data["total_score"]))

        cumulative_total_score = sum([mode[3] for mode in modes])

        modes.sort(key=lambda tup: tup[1])

        mode = modes.reverse()

        polylines = []
        for step in directions_result[0]['legs'][0]['steps']:
            polylines.append(step['polyline']['points'])

        route = {
            'type': [mode[0] for mode in modes],
            "bounds": directions_result[0]['bounds'],
            'distance': distance,
            'scores': [mode[2] for mode in modes],
            'total_score': cumulative_total_score,
            'polylines': polylines,
            'end_location': directions_result[0]['legs'][0]['steps'][0]['end_location'],
            'start_location': directions_result[0]['legs'][0]['steps'][0]['start_location'],
        }

        return route

    def get_pandr_route(self, origin, pandr_latlng, destination):
        to_pandr_route = self.get_route_for_mode(origin, pandr_latlng, "driving")
        from_pandr_route = self.get_route_for_mode(pandr_latlng, destination, "transit")
        
        return {
            "to_pandr" : to_pandr_route,
            "from_pandr" : from_pandr_route,
            "total_score" : to_pandr_route["total_score"] + from_pandr_route["total_score"]
        }

    def get(self, start=(52.935405,-2.2419356), end=(52.935405,-1.2419356)):

        logging.info("get: %s, %s", start, end)

        parser = reqparse.RequestParser()
        parser.add_argument('start', type=str, help='origin cannot be converted')
        parser.add_argument('end', type=str, help='destination cannot be converted')
        parser.add_argument('mode', type=str, default='walking')

        args = parser.parse_args()

        origin = args.get('start') or 'start not set'
        destination = args.get('end') or 'end not set'
        mode = args.get('mode')

        try:
            origin = string.split(origin,',')
            destination = string.split(destination,',')
        except AttributeError:
            origin = str.split(origin,',')
            destination = str.split(destination,',')

        modes_of_travel = ['walking', 'driving', 'transit']

        direct_routes = []
        for mode in modes_of_travel:
            direct_routes.append(self.get_route_for_mode(origin, destination, mode))

        pandr_routes = {}
        closest_pandr = get_closest_pandr(origin, park_and_rides)

        pandr_route = self.get_pandr_route(origin, closest_pandr, destination)

        return {
            'time': str(datetime.now()),
            'direct_routes': direct_routes,
            'pandr_route': pandr_route
       }

api.add_resource(HelloWorld, '/')
api.add_resource(Journey,
                 '/manyways/<string:start>/<string:end>/',
                 '/manyways/<string:start>/<string:end>',
                 '/manyways/')

if __name__ == '__main__':    
    app.run(debug=True)