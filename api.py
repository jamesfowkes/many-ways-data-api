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

class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}


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

        origin = string.split(origin,',')
        destination = string.split(destination,',')

        modes_of_travel = ['walking', 'driving', 'transit']

        routes  = []

        for mode in modes_of_travel:
            directions_result = self.google_directions(start=origin,end=destination, mode=mode)

            distance = 0

            leg_keys = []
            modes = []

            for legs in directions_result[0]['legs']:
                tmp_distance = legs['distance']['text']
                tmp_distance = tmp_distance.strip(' km')
                tmp_distance = float(tmp_distance)
                distance = distance + tmp_distance

                for step in legs['steps']:
                    step_distance = step['distance']['value']
                    if 'transit_details' in step:
                        modes.append((step['transit_details']['line']['vehicle']['type'], step_distance))
                    else:
                        modes.append((step['travel_mode'], step_distance))

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
             'routes': routes,
       }

api.add_resource(HelloWorld, '/')
api.add_resource(Journey,
                 '/manyways/<string:start>/<string:end>/',
                 '/manyways/<string:start>/<string:end>',
                 '/manyways/')


if __name__ == '__main__':
    app.run(debug=True)