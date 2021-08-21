###########################################
# Imports
###########################################

import csv
from itertools import count, cycle, repeat

###########################################
# Working with the infinite iterators
###########################################

#---------------
# Counting with count()
#---------------

# The enumerate() function can be defined in terms 
# of zip() and count() functions:

def enumerate(x, start=0): 
    return zip(count(start), x)

# The following two commands are equivalent to each other:

some_iterator = ()
zip(count(), some_iterator)
enumerate(some_iterator)

# A function that evaluate items from an iterator 
# until some condition is met

def iterate_until_condition(function, iterator):
    i = next(iterator)
    if function(*i): return i
    return iterate_until_condition(function, iterator)

# A source iterable and a comparison function

someIterator = zip(count(0, 0.1), (0.1*c for c in count()))
someFunction = lambda x, y: abs(x - y) > 1.0E-12

iterate_until_condition(someFunction, someIterator)

# The smallest detectible difference can be computed as follows:

iterate_until_condition(lambda x, y: x != y, someIterator)

#---------------
# Reiterating a cycle with cycle()
#---------------

# Using the cycle() function to emit sequences 
# of True and False values as follows:

is_multipleof_3 = (i == 0 for i in cycle(range(3)))
is_multipleof_5 = (i == 0 for i in cycle(range(5)))

# Here's a sequence of values and their multiplier flags:
multipliers = zip(range(10), is_multipleof_3, is_multipleof_5)

# Decompose the triples and use a filter to pass numbers 
# which are multiples and reject all others

validMultipliers = sum(
    i 
    for i, *multipliers in multipliers 
    if any(multipliers)
    )

'''
We often need to work with samples of large sets of data. 
We can use the cycle() function to fairly select rows from within a larger set. 
The population size, NP , and the desired sample size, NS , 
denotes how long we can use a cycle:
c = NP / NS
'''
NP = 10000000
NS = 10000
c = NP / NS

# Assuming that the data can be parsed with the csv module, 
# we can create subsets using the following commands

with open('source_file.csv') as source_file:
    with open('target_file.csv') as target_file:
        chooser = (x == 0 for x in cycle(range(c)))
        readerObj = csv.reader(source_file)
        writerObj = csv.writer(target_file)
        writerObj.writerows(
            row 
            for pick, row in zip(chooser, readerObj) 
            if pick
            )

#---------------
# Repeating a single value with repeat()
#---------------

# Pick all data

all_data = repeat(0)
chooser1 = (x == 0 for x in all_data)

# Pick a subset of the data

subset_data = cycle(range(100))
chooser2 = (x == 0 for x in subset_data)

# We can embed repeat() in nested loops to create more complex structures. 

squares1 = list(
    tuple(repeat(i, times=i)) 
    for i in range(10)
    )

squares2 = list(
    sum(repeat(i, times=i)) 
    for i in range(10)
    )

