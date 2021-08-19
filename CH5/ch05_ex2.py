###########################################
# Imports
###########################################

import os, sys
import math
from urllib.request import urlopen
from typing import Collection
from collections.abc import Callable

rootRelativePath = '..'
rootAbsolutePath = os.path.abspath(rootRelativePath)
sys.path.append(rootAbsolutePath)

from CH4.ch04_ex1 import calc_haversine, calc_haversines, \
    create_pairs_iterative, convert_to_float,  invert_coordinates, read_rows_kml

###########################################
# Writing higher-order mappings and filters
###########################################

# -------------
# Three equivalent ways to express a mapping, 
# given a function and a collection

C = tuple()

def f():
    pass

# The map() function:

map(f, C)

# The generator expression:

(f(x) for x in C)

# The generator function:

def mymap(f, C):
    for x in C:
        yield f(x)

mymap(f, C)

# -------------
# Three equivalent ways to express a filter

# The filter() function:

filter(f, C)

# The generator expression:

(x for x in C if f(x))

# The generator function:

def myfilter(f, C):
    for x in C:
        if f(x):
            yield x

myfilter(f, C)

###########################################
# Unwrapping data while mapping
###########################################

with urlopen("file:../Winter%202012-2013.kml") as fh:
    dataset = tuple(\
        calc_haversines(\
        create_pairs_iterative(\
        convert_to_float(\
        invert_coordinates(\
        read_rows_kml(fh)
                    )))))

# The following is a concrete example of unwrapping while mapping

def to_miles(distance): 
    return distance*5280/6076.12

def to_kilometers(distance):
    return distance*1.852

def convert_units(conversion, coordinate):
    return (conversion(distance) for start, end, distance in coordinate)

datasetInMiles = list(convert_units(to_miles, dataset))

# A more general solution for this kind of unwrapping

def lat(coordinate):
    return coordinate[0]

def lon(coordinate):
    return coordinate[1]

def dist(coordinate):
    return coordinate[2]

datasetInMiles2 = list(map(lambda x: to_miles(dist(x)), dataset))

###########################################
# Wrapping additional data while mapping
###########################################

# Create the trip data from the path of points

with urlopen("file:../Winter%202012-2013.kml") as fh:
    coordinates = tuple(\
        convert_to_float(\
        invert_coordinates(\
        read_rows_kml(fh)
                    )))

dataset = tuple(
    (start, end, round(calc_haversine(start, end), 4)) 
    for start, end in create_pairs_iterative(iter(coordinates))
    )

# Modify the last example to create a higher-order function that 
# separates the wrapping from the other functions.

def calc_distances(distance, iterable):
    return (
        (start, end, round(distance(start, end), 4)) 
        for start, end in iterable
        )

# Apply the calc_haversine() function to compute distances

dataset2 = tuple(calc_distances(
    calc_haversine, 
    create_pairs_iterative(iter(coordinates))
    )
)

###########################################
# Flattening data while mapping
###########################################

# Convert the strig to a flat sequence of numbers

text = """
2 3 5 7 11 13 17 19 23 29
31 37 41 43 47 53 59 61 67 71
73 79 83 89 97 101 103 107 109
113 127 131 137 139 149 151 157 163 167 173
179 181 191 193 197 199 211 223 227 229
"""

# -------------
# Apply a conversion function while flattening the structure 
# from its original format

def numbers_from_rows(conversion, text):
    return (
        conversion(char) 
        for line in text.splitlines() for char in line.split()
        )

floatNumbers = list(numbers_from_rows(float, text))

# -------------
# Alternative implementation using higher-order functions 
# and generator expressions

floatNumbers2 = list(map(
    float, 
    (v for line in text.splitlines() for v in line.split())
    )
)
###########################################
# Structuring data while filtering
###########################################

# -------------
# A function to group the output from an iterable:

def groupby_iterative(n, iterable):
    row = tuple(next(iterable) for i in range(n))
    while row:
        yield row
        row = tuple(next(iterable) for i in range(n))

def is_multipleof_3or5(x):
    return x%3 == 0 or x%5 == 0

filteredNumbers = filter(is_multipleof_3or5 , range(100))
groupedNumbers =list(groupby_iterative(7, filteredNumbers))

# -------------
# Merge grouping and filtering into a single function 
# that does both operations in a single function body

def groupby_and_filter(n, predicate, iterable):
    data  = filter(predicate, iterable)
    row = tuple(next(data) for i in range(n))
    while row:
        yield row
        row = tuple(next(data) for i in range(n))

groupedNumbers = list(groupby_and_filter(7, is_multipleof_3or5, range(1,100)))

###########################################
# Writing generator functions
###########################################

# A function where the first value that is True is sufficient
# to stop the iteration

def first(predicate, collection):
    for x in collection:
        if predicate(x): return x

# A function that tests a number for being prime

def isprime(x):
    if x == 2: return True
    if x % 2 == 0: return False    
    numbers = range(3, int(math.sqrt(x) + 0.5) + 1, 2)
    predicate = lambda n: x % n == 0
    return first(predicate , numbers) is None

isprime(89)

# A version of the map() function that also filters bad data

data = [2, 5, 'e', 7, None, 3, 6, 8]

def map_not_none(function, iterable):
    for x in iterable:
        try:
            yield function(x)
        except Exception as e:
            pass

filteredData = list(map_not_none(int, data))

###########################################
# Building higher-order functions with Callables
###########################################

# A 'Null-aware' logarithm function  
# built from a Callable class definition

scale = [10, 100, None, 50, 60]

class NullAware(Callable):
    def __init__(self, some_func):
        self.some_func = some_func
    
    def __call__(self, arg):
        return \
            None \
            if arg is None else \
            self.some_func(arg)

null_aware_logarithm = NullAware(math.log)

logScale  = list(map(null_aware_logarithm, scale))

# A sum with filter function 
# built from a Callable class definition:

class Sum_Filter(Callable):
    __slots__ = ["filter", "function"]
    def __init__(self, filter, function):
        self.filter = filter
        self.function = function
    def __call__(self, iterable):
        return sum(
            self.function(x) 
            for x in iterable
            if self.filter(x)
            )

count_not_none = Sum_Filter(lambda x: x is not None, lambda x: 1)

lengthOfScale = count_not_none(logScale)