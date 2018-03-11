import json
from collections import namedtuple

class Mode(namedtuple("Mode", ["name", "co2", "nox"])):
    __slots__ = ()

    @classmethod
    def from_json(cls, name, json):
        return cls(name, json["co2"], json["nox"])

json_data = json.load(open("modedata.json"))

mode_data = {mode_name: Mode.from_json(mode_name, mode_json) for mode_name, mode_json in json_data.items()}

def get_mode(mode):
    GOOGLE_TYPE_TO_MODE_MAP = {
        "DRIVING": "medium diesel car",
        "CAR": "medium diesel car",
        "TRAIN": "diesel train",
        "RAIL": "diesel train",
        "METRO_RAIL": "diesel train",
        "TRAM": "tram",
        "HEAVY_RAIL": "diesel train",
        "BUS": "bus",
        "WALKING": "foot",
        "BICYCLE": "bike"
    }
    local_type = GOOGLE_TYPE_TO_MODE_MAP.get(mode.upper(), mode)

    return mode_data[local_type]
