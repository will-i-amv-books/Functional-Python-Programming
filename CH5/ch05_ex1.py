###########################################
# Imports
###########################################
import os, sys

rootRelativePath = '..'
rootAbsolutePath = os.path.abspath(rootRelativePath)
sys.path.append(rootAbsolutePath)

from CH4.ch04_ex2 import calc_mean, calc_stdev, calc_normalized_score
from CH4.ch04_ex1 import calc_haversine, calc_haversines, \
    create_pairs_iterative, convert_to_float,  invert_coordinates, read_rows_kml

from urllib.request import urlopen

###########################################
# Using max() and min() to find extrema
###########################################

with urlopen("file:../Winter%202012-2013.kml") as fh:
    dataset = tuple(\
        calc_haversines(\
        create_pairs_iterative(\
        convert_to_float(\
        invert_coordinates(\
        read_rows_kml(fh)
                    )))))

# Method 1 - Extract the maximum and minimum distances 
# with generator functions

distances = tuple(dist for start, end, dist in dataset)
long, short = max(distances), min(distances)
print(long, short)

# Method 2 - Extract the maximum and minimum distances 
# with the unwrap(process(wrap())) pattern.

def wrap(sequence):
    return ((coordinate[2],coordinate) for coordinate in sequence)

def unwrap(wrappedCoordinate):
    distance, coordinate = wrappedCoordinate
    return coordinate

long, short = unwrap(max(wrap(dataset))), unwrap(min(wrap(dataset)))
print(long, short)

# Method 3 - Extract the maximum and minimum distances 
# using max() and min() as higher-order functions

def sort_by_distance(coordinate):
    lat, lon, distance = coordinate
    return distance

long, short = max(dataset, key=sort_by_distance), min(dataset, key=sort_by_distance)
print(long, short)

###########################################
# Using Python lambda forms
###########################################

long = max(dataset, key=lambda coord: coord[2])
short = min(dataset, key=lambda coord: coord[2])
print(long, short)

###########################################
# Using the map() function to apply a function to a collection
###########################################

str_data = [
    '2', '3', '5', '7', '11', '13', '17', '19', '23', '29',
    '31', '37', '41', '43', '47', '53', '59', '61', '67', '71',
    '73', '79', '83', '89', '97', '101', '103', '107', '109', '113',
    '127', '131', '137', '139', '149', '151', '157', '163', '167',
    '173', '179', '181', '191', '193', '197', '199', '211', '223',
    '227', '229'
    ]

int_data = list(map(int, str_data))

###########################################
# Working with lambda forms and map()
###########################################

# Convert coordinates from nautical miles to statute miles

def start(iterable): 
    return iterable[0]

def end(iterable): 
    return iterable[1]

def dist(iterable): 
    return iterable[2]


def convert_to_sm1(iterable, factor):
    return map(
        lambda x: (start(x), end(x), dist(x)*factor), 
        iterable
        )

def convert_to_sm2(iterable, factor):
    return map(
        lambda x: (x[0], x[1], x[2]*factor), 
        iterable
        )


dataset_sm1 = list(convert_to_sm1(dataset, 6076.12/5280))
dataset_sm2 = list(convert_to_sm2(dataset, 6076.12/5280))

###########################################
# Using map() with multiple sequences
###########################################

# Implement create_pairs() and calc_haversines() with map() and zip()

with urlopen("file:../Winter%202012-2013.kml") as fh:
    coordinates = tuple(\
        convert_to_float(\
        invert_coordinates(\
        read_rows_kml(fh)
                    )))

# Method 1

def create_pairs_1(iterable):
    return zip(iterable, iterable[1:])

def calc_haversines_1(iterable):
    return map(
        lambda x: (x[0], x[1], calc_haversine(*x)),
        iterable
    )

distances1 = list(\
    calc_haversines_1(\
    create_pairs_1(coordinates)
    ))

# Method 2

def calc_haversines_2(iterable):
    return map(
        lambda start, end: (start, end, calc_haversine(start, end)), 
        iterable, iterable[1:]
    )

distances2 = list(calc_haversines_2(coordinates))

###########################################
# Using the filter() function to pass or reject data
###########################################

def dist(iterable): 
    return iterable[2]

longDistances = list(filter(lambda x: dist(x) >= 50, dataset))

###########################################
# Using filter() to identify outliers
###########################################

distances = list(map(dist, dataset))
meanDist = calc_mean(distances)
stdevDist = calc_stdev(distances)

def is_outlier(x):
    #return calc_normalized_score(dist(x), meanDist, stdevDist) > 3
    return calc_normalized_score(dist(x), meanDist, stdevDist) > 2

'''
is_outlier = lambda x: \
    calc_normalized_score(dist(x), meanDist, stdevDist) > 2
'''

outliers = list(filter(is_outlier, dataset))
print("Outliers: \n", outliers)

###########################################
# Using sorted() to put data in order
###########################################

def dist(iterable): 
    return iterable[2]

# Keeping only the distance data from 'dataset'

sortedDistances1 = sorted(dist(x) for x in dataset)

# Keeping the items of 'dataset' intact

sortedDistances2 = sorted(dataset, key=dist)