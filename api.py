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

app = Flask(__name__)
api = Api(app)

app.config.update(
    MAPS_API_KEY = os.environ.get("MAPS_API_KEY"),
    DEBUG = True,
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
    for step in steps:
        step_distance = step['distance']['value']
        if 'transit_details' in step:
            return (step['transit_details']['line']['vehicle']['type'], step_distance)
        else:
            return (step['travel_mode'], step_distance)

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

    def get(self, start=(52.935405,-2.2419356), end=(52.935405,-1.2419356)):
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

        routes  = []

        for mode in modes_of_travel:
            directions_result = self.google_directions(start=origin,end=destination, mode=mode)

            distance = 0

            leg_keys = []
            modes = []

            for legs in directions_result[0]['legs']:
                distance = distance + distance_from_distance_str(legs['distance']['text'])
                modes.append(process_steps(legs['steps']))

            modes.sort(key=lambda tup: tup[1])

            mode = modes[len(modes) - 1][0]

            def gen_lat_long_string(lat_long):
                lat_long_string = lat_long[0] + ',' + lat_long[1]

                return lat_long_string

            request_url = 'http://localhost:8000/score?start={}&end={}&distance={}&mode={}'.format(gen_lat_long_string(origin),
                                                                                                   gen_lat_long_string(destination),
                                                                                                   distance,
                                                                                                   mode)

            r = requests.get(request_url)
            score = r.json()
            total_score = r.json()['total_score']

            polylines = []
            for step in directions_result[0]['legs'][0]['steps']:
                polylines.append(step['polyline']['points'])


            route = {
                'type': mode,
                "bounds": directions_result[0]['bounds'],
                'distance': distance,
                'score': score,
                'total_score': total_score,
                'polylines': polylines,
                'end_location': directions_result[0]['legs'][0]['steps'][0]['end_location'],
                'start_location': directions_result[0]['legs'][0]['steps'][0]['start_location'],
            }

            routes.append(route)

        return {
            'time': str(datetime.now()),
            'routes': routes,
       }

api.add_resource(HelloWorld, '/')
api.add_resource(Journey,
                 '/manyways/<string:start>/<string:end>/',
                 '/manyways/<string:start>/<string:end>',
                 '/manyways/')


if __name__ == '__main__':
    app.run(debug=True)