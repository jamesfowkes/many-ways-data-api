import sys

from collections import namedtuple

from latlng import LatLng

def int_from_str_with_thousep(s):
    return int(s.replace(",",""))
class DensityData(namedtuple("DensityData", ["lsoa", "pop", "area", "density", "latlng"])):
    __slots__ = ()

    @classmethod
    def from_line(cls, line, sep="\t"):
        parts = line.strip().split(sep)
        latlng = LatLng(float(parts[5]),float(parts[4]))
        pop = int_from_str_with_thousep(parts[1])
        density = int_from_str_with_thousep(parts[3])
        return cls(parts[0], pop, parts[2], density, latlng)

    @classmethod
    def from_existing(cls, existing, **kwargs):
        data = {
            "lsoa": kwargs.get("lsoa", existing.lsoa),
            "pop": kwargs.get("pop", existing.pop),
            "area": kwargs.get("area", existing.area),
            "density": kwargs.get("density", existing.density),
            "latlng": kwargs.get("latlng", existing.latlng)
        }

        return DensityData(**data)

    def __str__(self, sep="\t"):
        return sep.join([self.lsoa, self.pop, self.area, self.density, str(self.latlng.lat), str(self.latlng.lng)])

    def distance_from(self, other):
        return self.latlng.distance_from(other)

with open("population.tsv") as f:
    local_data = [DensityData.from_line(l) for l in f.readlines()]

def find_nearest(to_find, data=None):

    data = data or local_data
    sorter = lambda d: d.distance_from(to_find)
    return sorted(data, key=sorter)[0]
        
if __name__ == "__main__":

    to_find = LatLng(float(sys.argv[1]), float(sys.argv[2]))

    print(find_nearest(to_find, local_data).density)