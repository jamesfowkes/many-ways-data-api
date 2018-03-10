from flask import Flask
from flask_restful import Resource, Api


class Journey(Resource):
    def get(self, start="nottingham", end="amerillo"):
        return {
            'start': start,
            'end': end
        }