###########################################
# Imports
###########################################

import os, sys
import pprint
from collections import Counter
from collections import defaultdict
from urllib.request import urlopen

rootRelativePath = '..'
rootAbsolutePath = os.path.abspath(rootRelativePath)
sys.path.append(rootAbsolutePath)

from CH4.ch04_ex1 import calc_haversines, create_pairs_iterative, \
    convert_to_float,  invert_coordinates, read_rows_kml

###########################################
# Group-by reductions – from many to fewer
###########################################

with urlopen("file:../Winter%202012-2013.kml") as fh:
    dataset = tuple(\
        calc_haversines(\
        create_pairs_iterative(\
        convert_to_float(\
        invert_coordinates(\
        read_rows_kml(fh)
                    )))))

# Compute a quantizedDistances distances with a generator expression:

quantizedDistances = (
    5*(dist//5) 
    for start, stop, dist in dataset
    )

###########################################
# Building a mapping with Counter    
###########################################

# Create a mapping from distance to frequency:

frequencies = Counter(quantizedDistances)
mostCommon = frequencies.most_common()

###########################################
# Building a mapping by sorting
###########################################

# Implement a custom Counter class with generators

def group_sort(dataset):
    def group(data):
        previous, count = None, 0
        for item in sorted(data):
            if item == previous:
                count += 1
            elif previous is not None: # and item != previous
                yield previous, count
                previous, count = item, 1
            elif previous is None:
                previous, count = item, 1
            else:
                raise Exception("Bad bad design problem.")
        yield previous, count
    quantizedDistances = (5*(dist//5) for start,stop, dist in dataset)
    return dict(group(quantizedDistances))

# Remove the last elif clause in the group() function
# (doesn't work)

def group(data):
    sorted_data = iter(sorted(data))
    previous, count = next(sorted_data), 1
    for item in sorted(data):
        if item == previous:
            count += 1
        elif previous is not None: # and item != previous
            yield previous, count
            previous, count = item, 1
        else:
            raise Exception("Bad bad design problem.")
    yield previous, count

###########################################
# Grouping or partitioning data by key values
###########################################

# A recursive definition of the itertools.groupby() function

def group_by(key, data):
    def group_into(key, collection, dictionary):
        if len(collection) == 0: 
            return dictionary
        head, *tail= collection
        dictionary[key(head)].append(head)
        return group_into(key, tail, dictionary)
    return group_into(key, data, defaultdict(list))

def quantize_distance_by_5(coordinate):
    return 5*(coordinate[2]//5)

groupedByDistance = group_by(quantize_distance_by_5, dataset)

for distance in sorted(groupedByDistance):
    pprint.pprint(groupedByDistance[distance])

###########################################
# Writing more general group-by reductions
###########################################

# Helper functions to decompose the tuple as follows:

def get_start(coordinates):
    start, end, dist = coordinates
    return start 

def get_end(coordinates):
    start, end, dist = coordinates
    return end

def get_dist(coordinates):
    start, end, dist = coordinates
    return dist

def get_lat(pair):
    lat, lon = pair
    return lat

def get_lon(pair):
    lat, lon = pair
    return lon

point = ((35.505665, -76.653664), (35.508335, -76.654999), 0.1731)

get_start(point)
get_end(point)
get_dist(point)
get_lat(get_start(point))
get_lon(get_start(point))

# Locate the northern-most starting position for the coordinates,
# for each distance level:

def get_northernmost_distances(collection):
    return tuple(
        max(collection[distance], key=lambda x: get_lat(get_start(x)))
        for distance in sorted(collection)
    )

northermosts = get_northernmost_distances(groupedByDistance)
pprint.pprint(northermosts)

###########################################
# Writing higher-order reductions
###########################################

dataset = [4, 3, 7, 5 ,8]

# Reducer functions for statistical calculations:

def s0(data):
    return sum(1 for x in data) # or len(data)

def s1(data):
    return sum(x for x in data) # or sum(data)

def s2(data):
    return sum(x*x for x in data)

# Rewriting the reducer functions in terms of 
# scalar functions and higher order functions

def sum_generalized(function, data):
    return sum(function(x) for x in data)

len_ = sum_generalized(lambda x: 1, dataset) # x**0
sum_ = sum_generalized(lambda x: x, dataset) # x**1
sum_squared = sum_generalized( lambda x: x*x, dataset ) # x**2

# A sum with filter to reject raw data which is 
# unknown or unsuitable in some way

dataset = [4, 3, 7, None, 5 ,8]

# Reject None values in a simple way:

def filtered_sum_generalized(filter, function, data):
    return sum(function(x) for x in data if filter(x))

def is_valid(x):
    return x is not None

len_filtered = filtered_sum_generalized(is_valid, lambda x: 1, dataset)
sum_filtered = filtered_sum_generalized(is_valid, lambda x: x, dataset)