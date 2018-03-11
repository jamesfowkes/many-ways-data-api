""" enviro.py

Usage:
    enviro.py <mode> <start_latlng> <end_latlng>

"""

import docopt
import json
import sys

from collections import namedtuple

from latlng import LatLng
from mode import get_mode

from population_density import find_nearest

def population_density_to_modifier(density):
    return density/200

def get_route_population_density_modifier(start, end):
    midpoint = LatLng.from_midpoint(start, end)
    population_density = find_nearest(midpoint).density
    return population_density_to_modifier(population_density)

class Modifiers(namedtuple("Modifiers", ["CO2", "NOX", "POP", "AQI"])):
    __slots__ = ()

    DEFAULT_CO2 = 0.0000115
    DEFAULT_NOX = 0.00067
    DEFAULT_POP = 1
    DEFAULT_AQI = 1

    @classmethod
    def from_kwargs(cls, **kwargs):
        co2 = max(kwargs.get("co2", cls.DEFAULT_CO2), cls.DEFAULT_CO2)
        nox = max(kwargs.get("nox", cls.DEFAULT_NOX), cls.DEFAULT_NOX)
        pop = max(kwargs.get("pop", cls.DEFAULT_POP), 1)
        aqi = max(kwargs.get("aqi", cls.DEFAULT_AQI), 1)
        return cls(co2, nox, pop, aqi)

def get_scores(data, distance_in_km, **kwargs):
    mods = Modifiers.from_kwargs(**kwargs)
    co2_per_km = data.co2
    nox_per_km = data.nox

    distance_in_km = max(distance_in_km, 0.1)
    
    co2_score = 1/(co2_per_km * distance_in_km * mods.CO2)
    nox_score = 1/(nox_per_km * distance_in_km * mods.NOX * mods.POP * mods.AQI)

    return (co2_score, nox_score)

def get_combined_score(data, distance_in_km, **kwargs):
    (co2_score, nox_score) = get_scores(data, distance_in_km, **kwargs)
    return co2_score + nox_score

if __name__ == "__main__":
    
    args = docopt.docopt(__doc__)

    mode = args["<mode>"].upper()
    mode = get_mode(mode)

    start = LatLng.from_string(args["<start_latlng>"])
    end = LatLng.from_string(args["<end_latlng>"])
    
    distance_in_km = start.distance_from(end)
    population_density_mod = get_route_population_density_modifier(start, end)
    
    print("Baseline scores:")
    print(get_scores(mode, distance_in_km))
    print(get_combined_score(mode, distance_in_km))
    print("With population data:")
    print(get_scores(mode, distance_in_km, pop=population_density_mod))
    print(get_combined_score(mode, distance_in_km, pop=population_density_mod))
