###########################################
# Imports
###########################################

import os, sys
import pprint
import csv
import random
from contextlib import ExitStack
from collections import namedtuple, defaultdict
from urllib.request import urlopen
from itertools import cycle, repeat, accumulate, chain, groupby, compress, \
    islice, dropwhile, filterfalse, starmap, tee

rootRelativePath = '..'
rootAbsolutePath = os.path.abspath(rootRelativePath)
sys.path.append(rootAbsolutePath)

from CH4.ch04_ex1 import calc_haversine, create_pairs_iterative, \
    invert_coordinates, convert_to_float, read_rows_kml

###########################################
# Using the finite iterators
###########################################

#---------------
# Assigning numbers with enumerate()
#---------------

data = [1.2, .8, 1.2, 2.3, 11, 18]

enumeratedData = tuple(enumerate(sorted(data)))

# From Chapter 7, the Leg namedtuple format looks as follows:

Leg = namedtuple("Leg", ("start", "end", "distance"))

# A more complex version of the Leg class:

OrderedLeg = namedtuple("Leg", ("order", "start", "end", "distance"))

#A function that decomposes pairs and creates OrderedLeg instances

def create_ordereed_pairs(iterable):
    for order, pair in enumerate(iterable):
        start, end = pair
        yield OrderedLeg(
            order, 
            start, 
            end, 
            round(calc_haversine(start, end), 4)
            )

# In the context of the preceding explanation, it is used as follows

with urlopen("file:../Winter%202012-2013.kml") as fh:
    path_iter = convert_to_float(\
        invert_coordinates(\
        read_rows_kml(fh)
        ))
    pair_iter = create_pairs_iterative(path_iter)
    trip_iter = create_ordereed_pairs(pair_iter)
    trip = tuple(trip_iter)

pprint.pprint(trip)

#---------------
# Running totals with accumulate()
#---------------

# The trip variable format looks as follows:

Leg = namedtuple("Leg", ("start", "end", "distance"))

# The calculation of quartiles looks like the following:

distances = (leg.distance for leg in trip)
accumulatedDists = tuple(accumulate(distances))
total = accumulatedDists[-1] + 1.0
quartiles = tuple(int(4*d/total) for d in accumulatedDists)

'''
* We extracted the distance values and computed the accumulated distances 
for each leg. 
* The last of the accumulated distances is the total. 
* We've added 1.0 to the total to assure that 4*d/total is 3.9983, 
which truncates to 3. 
* Without the +1.0 , the final item would have a value of 4, 
which is an impossible fifth quartile. 
'''

#---------------
# Combining iterators with chain()
#---------------

# Combining the chain() function with the contextlib.ExitStack() method 
# to process a collection of files as a single iterable sequence of values. 

def read_rows_csv_tab(*filenames):
    with ExitStack() as stack:
        files = list(
            stack.enter_context(open(name, 'r', newline='')) 
            for name in filenames
            )
        readers = list(
            csv.reader(fh, delimiter='\t') 
            for fh in files
            )
        #readers = map(lambda fh: csv.reader(fh, delimiter='\t'), files)
        yield from chain(*readers)

'''
* We've created an ExitStack object that can contain 
a number of individual contexts open. 
* We created a simple sequence of open file objects; 
these objects were also entered into the ExitStack object.
Given the sequence of files in the 'files' variable, 
we created a sequence of CSV readers in the 'readers' variable. 
* Finally, we chained all of the readers into a single iterator 
with chain(*readers).
* This was used to yield the sequence of rows from all of the files.
'''

#---------------
# Partitioning an iterator with groupby()
#---------------

'''
In the Running totals with accumulate() section, earlier in the chapter, 
we showed how to compute quartile values for an input sequence.
'''
# Given the trip variable with the raw data and the quartile variable 
# with the quartile assignments, we can group the data as follows:

groupedQuartiles = groupby(
    zip(quartiles, trip), 
    key=lambda x: x[0]
    )

for groupKey, groupIterable in groupedQuartiles:
    print(groupKey, tuple(groupIterable))

# We can also create a custom groupby() using the defaultdict(list) method,
# as follows:

def groupby_2(iterable, key):
    groups = defaultdict(list)
    for item in iterable:
        groups[key(item)].append(item)
    for group in groups:
        yield iter(groups[group])

#---------------
# Filtering with compress()
#---------------

# We can think of the filter() function as having the following definition:

def filter(iterable, function):
    iter1, iter2 = tee(iterable, 2)
    return compress(iter1, (function(x) for x in iter2))

# In the Reiterating a cycle with cycle() section of this chapter, 
# we looked at data selection using a simple generator expression.

c = 10000000 / 10000
someIterable = []

chooser = (x == 0 for x in cycle(range(c)))
filteredIterable = (
    row 
    for flag, row in zip(chooser, someIterable) 
    if flag
    )

# The filteredIterable expression can be expressed in terms of 
# compress(someIterable, chooser) method.

select_all = repeat(0) # Pick all rows from the source
select_subset = cycle(range(c)) # Pick 1/c rows from the source
select_random_subset = random.randrange(c) # Pick random 1/c rows from the source

selection_rule = select_all # Can also be select_subset or select_random_subset
chooser = (x == 0 for x in selection_rule)
filteredIterable = compress(someIterable, chooser)

#---------------
# Picking subsets with islice()
#---------------

# The following is a simple list:

flat = [
    '2', '3', '5', '7', '11', '13', '17', '19', '23', '29', '31',
    '37', '41', '43', '47', '53', '59', '61', '67', '71'
    ]

# We can create pairs using list slices as follows:

structured = zip(flat[0::2], flat[1::2])

# The islice() function gives us similar capabilities 
# without the overhead of materializing a list object

flatIterable1 = iter(flat)
flatIterable2 = iter(flat)

structured2 = zip(
    islice(flatIterable1, 0, None, 2), 
    islice(flatIterable2, 1, None, 2)
    )

#---------------
# Stateful filtering with dropwhile() and takewhile()
#---------------

# The GPL file format shown in Chapter 3 has 
# a header that looks as follows:

'''
GIMP Palette
Name: Crayola
Columns: 16
#
'''

# This is followed by rows that look like the following example:

'''
255 73 108 Radical Red
'''
# We can locate the final line of the headers
# (the # line—using a parser based on the dropwhile() function):

with open("../crayola.gpl") as fh:
    reader = csv.reader(fh, delimiter='\t')
    rows = dropwhile(lambda row: row[0] != '#', reader)

# We can use the islice() function to discard the first item (#)
# and then parse the color details as follows:

with open("../crayola.gpl") as fh:
    reader = csv.reader(fh, delimiter='\t')
    rows = dropwhile(lambda row: row[0] != '#', reader)
    color_rows = islice(rows, 1, None)
    colors = (
        (color.split(), name) 
        for color, name in color_rows
        )
    print(list(colors))

'''
* The islice(rows, 1, None) expression is similar to asking 
for a rows[1:] slice: the first item is quietly discarded. 
* Once the last of the heading rows have been discarded, 
we can parse the color tuples and return more useful color objects.
'''

#---------------
# Two approaches to filtering with filterfalse() and filter()
#---------------

# The filterfalse() function from the itertools module can be defined 
# from the filter() function, as follows:

def custom_filterfalse(pred, iterable):
    return filter(lambda x: not pred(x), iterable)

'''
* The value of the filter(None, iterable) method 
is all the True values in the iterable.
* The value of the filterfalse(None, iterable) method 
is all of the False values from the iterable:
'''
someList = [0, False, 1, 2]
onlyTrueValues = list(filter(None, someList))
onlyFalseValues = list(filterfalse(None, someList))

# The point of having the filterfalse() function is to promote reuse. 
# The idea is to execute the following commands:

some_source = []
def test_function():
    return None

iter_1, iter_2 = iter(some_source), iter(some_source)
goodValues = filter(test_function, iter_1)
badValues = filterfalse(test_function, iter_2)

#---------------
# Applying a function to data via starmap() and map()
#---------------

# We can think of the simple version of the map() function, as follows:

arg_iter = ()
map(function, arg_iter) == (function(a) for a in arg_iter)

# The starmap() function in the itertools module is 
# the *a version of the map() function, which is as follows:

starmap(function, arg_iter) == (function(*a) for a in arg_iter)


# We can think of the map(function, iter1, iter2, ..., itern) method 
# being defined as follows:

'''
def starmap(function, iter1, iter2, ... ,itern):
    return (
        function(*args) 
        for args in zip(iter1, iter2, ... , itern)
    )

starmap(function, iter1, iter2, ... ,itern)
'''

# From Chapter 7, prior to creating Leg objects, 
# we created pairs of points with the following format:

Point = namedtuple("Point", ("latitude", "longitude"))

# We could use the starmap() function to assemble the Leg objects, 
# as follows:

Leg = namedtuple("Leg", ("start", "end", "distance"))

def make_leg(start, end): 
    return Leg(start, end, calc_haversine(start, end))

with urlopen("file:../Winter%202012-2013.kml") as fh:
    path_iter = convert_to_float(read_rows_kml(fh))
    pair_iter = create_pairs_iterative(path_iter)
    trip = list(starmap(make_leg, pair_iter))

'''
* The create_pairs_iterative() function creates pairs of point objects 
that reflect the start and end of a leg of the voyage. 
* Given these pairs, we can create a simple function, make_leg(),
which accepts a pair of Points object, and returns a Leg object 
with the start point, end point, and distance between the two points.
'''

###########################################
# Cloning iterators with tee()
###########################################

'''
This seems to free us from having to materialize a sequence 
so that we can make multiple passes over the data. 
'''
# A simple average for an immense dataset can be written 
# in the following way:

def mean(iterator):
    iter0, iter1 = tee(iterator, 2)
    s0 = sum(1 for x in iter0)
    s1 = sum(x for x in iter1)
    return s0/s1

'''
* While interesting in principle, the tee() function's implementation 
suffers from a severe limitation. 
* In most Python implementations, the cloning is done 
by materializing a sequence. 
* While this circumvents the "one time only" rule for small collections, 
it doesn't work out well for immense collections.
'''
