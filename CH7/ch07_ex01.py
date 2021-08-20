###########################################
# Imports
###########################################

import os, sys
import pprint
from collections import namedtuple, defaultdict
from collections.abc import Iterator
from urllib.request import urlopen

rootRelativePath = '..'
rootAbsolutePath = os.path.abspath(rootRelativePath)
sys.path.append(rootAbsolutePath)

from CH3.ch03_ex4 import create_pairs, remove_headings, \
    read_rows
from CH4.ch04_ex2 import calc_correlation
from CH4.ch04_ex1 import calc_haversine, create_pairs_iterative, \
    invert_coordinate, read_rows_kml

Pair = namedtuple("Pair", ("x", "y"))

###########################################
#  Using an immutable namedtuple as a record
###########################################

# Current format of the trip data:

first_leg = (
    (37.54901619777347, -76.33029518659048), 
    (37.840832, -76.273834), 
    17.7246
    )

#-------------
# Three alternatives for selected values out of a tuple
#-------------

# Method 1 - defining selection functions that can pick items 
# from a tuple by index position:

start_point  = lambda leg: leg[0]
end_point = lambda leg: leg[1]
distance_nm = lambda leg: leg[2]
latitude_value = lambda point: point[0]
longitude_value = lambda point: point[1]

latitude_value(start_point(first_leg))

# Method 2 - Using the *parameter notation to conceal 
# some details of the index positions

start = lambda start, end, distance: start
end = lambda start, end, distance: end
distance = lambda start, end, distance: distance
latitude = lambda lat, lon: lat
longitude = lambda lat, lon: lon

latitude(*start(*first_leg))

# Method 3 - Using namedtuples 

Leg = namedtuple("Leg", ("start", "end", "distance"))
Point = namedtuple("Point", ("latitude", "longitude"))

#-------------
# Changing code that uses tuples to namedtuples
#-------------

def convert_rows_to_float_old(rows):
    return (
        tuple(map(float, invert_coordinate(*row)))
        for row in rows
        )

def convert_rows_to_float(rows):
    return (
        Point(*map(float, invert_coordinate(*row)))
        for row in rows
        )

with urlopen("file:../Winter%202012-2013.kml") as fh:
    pathIter  = convert_rows_to_float(read_rows_kml(fh))
    pairIter  = create_pairs_iterative(pathIter)
    tripIter  = (
        Leg(start, end, round(calc_haversine(start, end), 4))
        for start,end in pairIter
        )
    trip = tuple(tripIter)

pprint.pprint(trip)

###########################################
# Avoiding stateful classes by using families of tuples
###########################################

# Extracting four samples from a simple dataset 
# (from Chapter 3):

def convert_rows_to_float(rows):
    return (
        tuple(map(float, row)) 
        for row in rows
        )

with open("../Anscombe.txt") as fh:
    data  = tuple(\
        convert_rows_to_float(\
        remove_headings(\
        read_rows(fh)
        )))
    series_I = tuple(create_pairs(0, data))
    series_II = tuple(create_pairs(1, data))
    series_III = tuple(create_pairs(2, data))
    series_IV = tuple(create_pairs(3, data))

# Applying the enumerate() function to create 2 sequences of values
# ordered by the x and y fields respectively:

y_rank = tuple(\
    enumerate(\
    sorted(series_I, key = lambda pair: pair.y)
    ))

xy_rank = tuple(
    enumerate(\
    sorted(y_rank, key = lambda rank: rank[1].x)
    ))

# Th result dataset look like the following:

'''
((0, (0, Pair(x =4.0, y =4.26))), (1, (2, Pair(x =5.0, y =5.68))), ...,
(10, (9, Pair(x =14.0, y =9.96))))
'''

# To make the extraction less awkward, the following selector functions 
# will be used:

x_rank  = lambda ranked: ranked[0]
y_rank = lambda ranked: ranked[1][0]
raw  = lambda ranked: ranked[1][1]

###########################################
# Assigning statistical ranks
###########################################

'''
To flatten the nested tuple data structure in 'xy_rank':

* First, a higher-order function will assign ranks to either 
the x or y value of a Pair object. 
* Then, the function will be used to create a wrapper around the Pair object 
that includes both x and y rankings.
'''
# The following is a function that will create a rank order 
# for each observation in a dataset:

def rank(data, key =lambda obj:obj):
    def rank_output(duplicates, key_iter, base=0):
        for key in key_iter:
            dups = len(duplicates[key])
            for value in duplicates[key]:
                yield (base + 1 + base + dups)/2, value
            base += dups
    def build_duplicates(duplicates, data_iter, key):
        for item in data_iter:
            duplicates[key(item)].append(item)
        return duplicates
    duplicates = build_duplicates(defaultdict(list), iter(data), key)
    return rank_output(duplicates, iter(sorted(duplicates)), 0)

# Test the rank function as follows

data = ((2, 0.8), (3, 1.2), (5, 1.2), (7, 2.3), (11, 18))

x_rank = list(rank(data, key =lambda x:x[0]))
y_rank = list(rank(data, key =lambda x:x[1]))

###########################################
# Wrapping instead of state changing
###########################################

# The following is how we can create an object that wraps a pair 
# with the rank order based on the y value:

Ranked_Y = namedtuple("Ranked_Y", ("r_y", "raw",))

def rank_y(pairs):
    return (
        Ranked_Y(*row) 
        for row in rank(pairs, lambda pair: pair.y)
        )

# Test rank_y() with the first sample 'series_I' as follows

rankedByY = list(rank_y(series_I))

###########################################
# Rewrapping instead of state changing
###########################################
'''
We're going to create a flat namedtuple with multiple peer attributes. 
'''
# The following function builds the is how the x-y ranking builds on the y-ranking:

Ranked_XY = namedtuple("Ranked_XY", ("r_x", "r_y", "raw",))

def rank_xy(pairs):
    return (
        Ranked_XY(
            r_x = r_x, 
            r_y = rank_y_raw[0], 
            raw = rank_y_raw[1]
            ) 
        for r_x, rank_y_raw in rank(rank_y(pairs), lambda r: r.raw.x)
        )

# Test rank_xy() with the first sample 'series_I' as follows

rankedByXandY = list(rank_xy(series_I))

###########################################
# # Computing the Spearman rank-order correlation
###########################################

# The Python version of the formula depends 
# on the sum() and len() functions, as follows:

def calc_spearman_corr(pairs):
    ranked = rank_xy(pairs)
    sum_d_2  = sum(
        (r.r_x - r.r_y)**2 
        for r in ranked
        )
    n  = len(pairs)
    return 1 - 6*sum_d_2/(n*(n**2 - 1))


# Test calc_spearman_corr() with the first sample 'series_I' as follows

spearmanCorr = round(calc_spearman_corr(series_I), 3)

# For comparison, the Pearson correlation can be calculated as follows

def calc_pearson_corr(pairs):
    X  = tuple(p.x for p in pairs)
    Y  = tuple(p.y for p in pairs)
    return calc_correlation(X, Y)

pearsonCorr = round(calc_pearson_corr(series_I), 3)











###########################################
# Polymorphism and Pythonic pattern matching
###########################################
'''
Generalizing our idea of rank-order information. 
'''
# A namedtuple that handles a tuple of ranks and a tuple of raw data:

Rank_Data  = namedtuple("Rank_Data", ("rank_seq", "raw"))

# Using a isinstance() check, to distinguish an iterable from a collection:

def some_function(seq_or_iter, key):
    if not isinstance(seq_or_iter, Iterator):
        yield from some_function(iter(seq_or_iter), key)
        return
    # Do the real work of the function using the iterable

# In the context of our rank-ordering function, 
# we will use this variation on the design pattern:

def rank_data(seq_or_iter, key =lambda obj:obj):
    
    # Not a sequence? Materialize a sequence object
    if isinstance(seq_or_iter, Iterator):
        yield from rank_data(tuple(seq_or_iter), key)
    data  = seq_or_iter
    head = seq_or_iter[0]
    
    # Convert to Rank_Data and process.
    if not isinstance(head, Rank_Data):
        ranked = tuple(
            Rank_Data((), d) 
            for d in data
            )
        for r, rd in rerank(ranked, key):
            yield Rank_Data(rd.rank_seq + (r,), rd.raw)
        return
    
    # Collection of Rank_Data is what we prefer.
    for r, rd in rerank(data, key):
        yield Rank_Data(rd.rank_seq + (r,), rd.raw)

# The rerank() function follows a slightly different design 
# than the example of the rank() function shown previously.
# This version of the algorithm uses sorting instead of 
# creating a groups in a objects like Counter object:

def rerank(rank_data_collection, key):
    sorted_iter = iter(
        sorted(
            rank_data_collection, 
            key = lambda obj: key(obj.raw)
            )
        )
    head  = next(sorted_iter)
    yield from ranker(sorted_iter, 0, [head], key)

# The ranker() function accepts an iterable, a base rank number, 
# a collection of values with the same rank, and a key:

def ranker(sorted_iter, base, same_rank_seq, key):
    """Rank values from a sorted_iter using a base rank value.
    If the next value's key matches same_rank_seq, accumulate those.
    If the next value's key is different, accumulate same rank values
    and start accumulating a new sequence.
    """
    try:
        value = next(sorted_iter)
    except StopIteration:
        dups = len(same_rank_seq)
        yield from yield_sequence(
            (base + 1 + base + dups)/2, 
            iter(same_rank_seq)
            )
        return
    if key(value.raw) == key(same_rank_seq[0].raw):
        yield from ranker(
            sorted_iter, 
            base, 
            same_rank_seq + [value], 
            key
            )
    else:
        dups = len(same_rank_seq)
        yield from yield_sequence(
            (base + 1 + base + dups)/2, 
            iter(same_rank_seq)
            )
        yield from ranker(
            sorted_iter, 
            base + dups, 
            [value], 
            key
            )

# The yield_sequence() function looks as follows:

def yield_sequence(rank, same_rank_iter):
    head = next(same_rank_iter)
    yield rank, head
    yield from yield_sequence(rank, same_rank_iter)

###########################
# NONE OF THE FOLLOWING EXAMPLES WORK!!!
###########################

'''
The following are some examples of using this function 
to rank (and rerank) data.
We'll start with a simple collection of scalar values:
'''

scalars = [0.8, 1.2, 1.2, 2.3, 18]
list(ranker(scalars))

'''
When we work with a slightly more complex object, we can also have multiple
rankings. The following is a sequence of two tuples:
'''

pairs = ((2, 0.8), (3, 1.2), (5, 1.2), (7, 2.3), (11, 18))

ranked_x = tuple(ranker(pairs, key =lambda x:x[0] ))
ranked_xy = (ranker(ranked_x, key =lambda x:x[1] ))
tuple(rank_xy)
