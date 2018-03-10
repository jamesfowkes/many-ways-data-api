import os
from config.config import Hack24LaptopConfig
from config.config import Hack24ServerConfig
from flask import Flask
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

if os.environ.get('MANY_ENV') == 'LAPTOP':
    MANY_ENV = 'LAPTOP'
else:
    MANY_ENV = 'SERVER'

if MANY_ENV == 'LAPTOP':
    app.config.from_object('Hack24LaptopConfig')
# else:
#     app.config.from_object('Hack24ServerConfig')