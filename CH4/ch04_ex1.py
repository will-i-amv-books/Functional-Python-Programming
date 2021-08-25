#!/usr/bin/env python3
"""Functional Python Programming

Chapter 4, Example Set 1
"""
# pylint: disable=line-too-long,wrong-import-position,reimported

###########################################
# Imports
###########################################

import xml.etree.ElementTree as XML
from urllib.request import urlopen
from math import radians, sin, cos, sqrt, asin

###########################################
# Parsing an XML file
###########################################

def split_by_comma(text):
    return text.split(",")


def read_rows_kml(fileHandler):
    namespaceDict = {
        "ns0": "http://www.opengis.net/kml/2.2",
        "ns1": "http://www.google.com/kml/ext/2.2"
        }
    pointsPath = "./ns0:Document/ns0:Folder/ns0:Placemark/ns0:Point/ns0:coordinates"
    document = XML.parse(fileHandler)
    return (
        split_by_comma(coordinates.text)
        for coordinates in document.findall(pointsPath, namespaceDict)
        )

with open('../Winter 2012-2013.kml') as fh:
    coordinates = tuple(read_rows_kml(fh))

###########################################
# Parsing a file at a higher level
###########################################

def invert_coordinate(lon, lat, alt):
    return lat, lon


def invert_coordinates(rows):
    """
    >>> data= [['-76.33029518659048', '37.54901619777347', '0']]
    >>> list(lat_lon_kml( data ))
    [('37.54901619777347', '-76.33029518659048')]
    """
    return (
        invert_coordinate(*row) 
        for row in rows
        )


with urlopen("file:../Winter%202012-2013.kml") as fh:
    coordinates = tuple(\
        invert_coordinates(\
        read_rows_kml(fh)
        ))

###########################################
# Pairing up items from a sequence
###########################################

# Create pairs using generators and recursion

#pairs()
def create_pairs_recursive(lat_lon_iterable):
    """Yields list[0:1], list[1:2], list[2:3], ..., list[n-2,n-1]

    >>> trip = iter([(0,0), (1,0), (1,1), (0,1), (0,0)])
    >>> list(create_pairs_recursive(trip))
    [((0, 0), (1, 0)), ((1, 0), (1, 1)), ((1, 1), (0, 1)), ((0, 1), (0, 0))]
    """
    def create_pair(head, iterable_tail):
        next_ = next(iterable_tail)
        yield head, next_
        yield from create_pair(next_, iterable_tail)
    try:
        return create_pair(next(lat_lon_iterable), lat_lon_iterable)
    except StopIteration:
        return iter([])

# Create pairs using only generators

#legs()
def create_pairs_iterative(lat_lon_iterable):
    """Yields list[0:1], list[1:2], list[2:3], ..., list[n-2,n-1]
    Another option is zip( list[0::2], list[1::2] )

    >>> trip = iter([ (0,0), (1,0), (1,1), (0,1), (0,0) ])
    >>> tuple( create_pairs_iterative( trip ) )
    (((0, 0), (1, 0)), ((1, 0), (1, 1)), ((1, 1), (0, 1)), ((0, 1), (0, 0)))
    """
    start = next(lat_lon_iterable)
    for end in lat_lon_iterable:
        yield start, end
        start = end


with urlopen("file:../Winter%202012-2013.kml") as fh:
    coordinatePairs = tuple(\
        create_pairs_iterative(\
        invert_coordinates(\
        read_rows_kml(fh)
                    )))

###########################################
# Extending a simple loop
###########################################

# Using a filter function within a generator function

def filter_pairs(lat_lon_iterable, rejection_rule):
    """
    >>> trip = iter([(0,0), (1,0), (2,0), (2,1), (2,2), (0,1), (0,0)])
    >>> some_rule = lambda b, e: b[0] == 0
    >>> list(filter_pairs(trip, some_rule))
    [((1, 0), (2, 0)), ((2, 0), (2, 1)), ((2, 1), (2, 2)), ((2, 2), (0, 1))]
    """
    begin = next(lat_lon_iterable)
    for end in lat_lon_iterable:
        if rejection_rule(begin, end): 
            pass
        else: 
            yield begin, end
        begin = end

# Using a map function within a generator function

def convert_to_float(lat_lon_iterable):
    """Create float lat-lon pairs from string lat-lon pairs.

    >>> trip = [("1", "2"), ("2.718", "3.142")]
    >>> tuple(convert_to_float(trip))
    ((1.0, 2.0), (2.718, 3.142))
    """
    return (
        (float(lat), float(lon)) 
        for lat, lon in lat_lon_iterable)


with urlopen("file:../Winter%202012-2013.kml") as fh:
    coordinatePairs = tuple(\
        create_pairs_iterative(\
        convert_to_float(\
        invert_coordinates(\
        read_rows_kml(fh)
                    ))))

###########################################
# Applying generator expressions to scalar functions
###########################################

MI = 3959
NM = 3440
KM = 6371

def calc_haversine(point1, point2, R=NM):
    """The great-circle distance between 2 points on a sphere 
    given their longitudes and latitudes.
    * point1 and point2 are two-tuples of latitude and longitude.
    * R is radius, R=MI computes in miles.

    >>> round(calc_haversine((36.12, -86.67), (33.94, -118.40), R=6372.8), 5)
    2887.25995
    """
    lat_1, lon_1 = point1
    lat_2, lon_2 = point2
    lat_1 = radians(lat_1)
    lat_2 = radians(lat_2)
    delta_lat = radians(lat_2 - lat_1)
    delta_lon = radians(lon_2 - lon_1)
    a = sin(delta_lat/2)**2 + cos(lat_1)*cos(lat_2)*sin(delta_lon/2)**2
    c = 2*asin(sqrt(a))
    return R * c


def calc_haversines(pairs_iterable):
    return (
        (start, end, round(calc_haversine(start, end), 4))
        for start, end in pairs_iterable
        )


with urlopen("file:../Winter%202012-2013.kml") as fh:
    coordinates3 = tuple(\
        calc_haversines(\
        create_pairs_iterative(\
        convert_to_float(\
        invert_coordinates(\
        read_rows_kml(fh)
                    )))))
