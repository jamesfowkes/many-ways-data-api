import os
import config
from flask import Flask
from flask_restful import Resource, Api
from journey import Journey

app = Flask(__name__)
api = Api(app)

app.config.update(
    MAPS_API_KEY = os.environ.get("MAPS_API_KEY"),
    DEBUG = True,
    LOCAL = True
)

class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}


class Journey(Resource):
    def get(self, start="nottingham", end="amerillo"):
        return {
            'start': start,
            'end': end,
            'api_key': app.config['MAPS_API_KEY']
        }

api.add_resource(HelloWorld, '/')
api.add_resource(Journey,
                 '/manyways/<string:start>/<string:end>/',
                 '/manyways/<string:start>/<string:end>',
                 '/manyways/')


if __name__ == '__main__':
    app.run(debug=True)