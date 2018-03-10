import os

class Hack24Config():
    MAPS_API_KEY = os.environ.get("MAPS_API_KEY")

class Hack24LaptopConfig(Hack24Config):
    DEBUG = True
    LOCAL = True

class Hack24ServerConfig(Hack24Config):
    DEBUG = False
    LOCAL = False
