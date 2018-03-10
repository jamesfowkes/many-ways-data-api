import os
from flask import Flask
from flask_restful import Resource, Api

class Journey(Resource):
    def get(self, start="nottingham", end="amerillo"):
        return {
            'start': start,
            'end': end,
            'api_key': api.config['MAPS_API_KEY']
        }