###########################################
# Imports
###########################################

from math import pow
from collections import namedtuple, defaultdict
from itertools import groupby
from functools import lru_cache, total_ordering, partial, reduce
from numbers import Number
import operator

###########################################
# Memoizing previous results with lru_cache()
###########################################

# A naive fibonacci() implementation

def fibonacci(n):
    if n == 0: return 0
    if n == 1: return 1
    return fibonacci(n-1) + fibonacci(n-2)

# We can apply lru_cache to any function that might benefit 
# from caching previous results

@lru_cache(128)
def fibonacci_lru(n):
    if n == 0: return 0
    if n == 1: return 1
    return fibonacci_lru(n-1) + fibonacci_lru(n-2)

###########################################
# Defining classes with total_ordering()
###########################################

# We can almost emulate a Blackjack playing card 
# with a namedtuple() function as follows:

Card1 = namedtuple("Card1", ("rank", "suit"))

# This suffers from a limitation: all comparisons include 
# both a rank and a suit by default. 
# This leads to the following awkward behavior:

c2s = Card1(2, '\u2660')
c2h = Card1(2, '\u2665')
c2h == c2s
False

#--------------------
# Following is a much more useful class definition. 
#--------------------

@total_ordering
class Card(tuple):
    __slots__ = ()
    
    def __new__( class_, rank, suit ):
        obj = tuple.__new__(Card, (rank, suit))
        return obj
    
    def __repr__(self):
        return "{0.rank}{0.suit}".format(self)
    
    @property
    def rank(self):
        return self[0]
    
    @property
    def suit(self):
        return self[1]

    def __eq__(self, other):
        if isinstance(other, Card):
            return self.rank == other.rank
        elif isinstance(other, Number):
            return self.rank == other
    
    def __lt__(self, other):
        if isinstance(other, Card):
            return self.rank < other.rank
        elif isinstance(other,Number):
            return self.rank < other

# First, we get proper comparison of only the ranks as follows:

c2s= Card(2, '\u2660')
c2h= Card(2, '\u2665')
c2h == c2s
c2h == 2

# Further, we also have a rich set of comparison operators as follows:

c2s= Card(2, '\u2660')
c3h= Card(3, '\u2665')
c4c= Card(4, '\u2663')
c2s <= c3h < c4c
c3h >= c3h
c3h > c2s
c4c != c2s

###########################################
# Applying partial arguments with partial()
###########################################

# We can look at trivial examples as follows:

exp2 = partial(pow, 2)

exp2(12)
exp2(17)-1

# We can also create a partially applied function with
# a lambda form as follows:

exp2 = lambda y: pow(2, y)

###########################################
# Reducing sets of data with reduce()
###########################################

# A sequence object is given as follows:

someList = [2, 4, 4, 4, 5, 5, 7, 9]

# The following function will fold in + operators to the list as follows:

reduce(lambda x, y: x+y, someList) # ((((((2+4)+4)+4)+5)+5)+7)+9

# We can also provide an initial value as follows:

reduce(lambda x,y: x+y**2, someList, 0)

# Following is how the right answer is computed 
# with an explicit 0 initializer:

0+ 2**2+ 4**2+ 4**2+ 4**2+ 5**2+ 5**2+ 7**2+ 9**2

# If we omit the initialization of 0, the reduce() function uses 
# the first item as an initial value:

2+ 4**2+ 4**2+ 4**2+ 5**2+ 5**2+ 7**2+ 9**2

# We can define a number of built-in reductions 
# using the reduce() higher-order function as follows:

count = lambda iterable: reduce(lambda x, y: x+1, iterable, 0)
sum = lambda iterable: reduce(lambda x, y: x+y, iterable)
sum2 = lambda iterable: reduce(lambda x,y: x+y**2, iterable, 0)
min = lambda iterable: reduce(lambda x, y: x if x < y else y, iterable)
max = lambda iterable: reduce(lambda x, y: x if x > y else y, iterable)

#--------------------
# Combining map() and reduce()
#--------------------

# We'll show a simplistic map-reduce function that 
# combines the map() and reduce() functions as follows:

def map_reduce(map_function, reduce_function, iterable):
    return reduce(reduce_function, map(map_function, iterable))

# We can build a sum-squared reduction using 
# the map() and reduce() functions separately as follows:

def sum2_mr(iterable):
    return map_reduce(lambda y: y**2, lambda x, y: x+y, iterable)

# We can slightly simplify our map-reduce operation:

def sum2_mr2(iterable):
    return map_reduce(lambda y: y**2, operator.add, iterable)

# Following is how we can count values in an iterable:

def len_mr(iterable):
    return map_reduce(lambda y: 1, operator.add, iterable)

# We should avoid executing commands such as the following
# for efficiency reasons:

reduce(operator.add, ["1", ",", "2", ",", "3"], "")

#--------------------
# Using map() and reduce() to sanitize raw data
#--------------------

# Using the following functions to cleanse input data:

def comma_fix(data):
    try:
        return float(data)
    except ValueError:
        return float(data.replace(",", ""))

def clean_sum(cleaner, data):
    return reduce(operator.add, map(cleaner, data))

# We can apply the previously described function as follows:

someTuple = (
    '1,196', '1,176', '1,269', '1,240', '1,307',
    '1,435', '1,601', '1,654', '1,803', '1,734'
    )

cleanedTuple = clean_sum(comma_fix, someTuple)


# If we're also going to compute a sum of squares, 
# we should not execute the following command:

comma_fix_squared = lambda x: comma_fix(x)**2

cleanedTuple2 = clean_sum(comma_fix_squared, cleanedTuple)

'''
* This will do the comma-fixing operation twice on the data:
once to compute the sum and once to compute the sum of squares.
* This is a poor design; cache the results with lru_cache() instead
'''

#--------------------
# Using groupby() and reduce()
#--------------------

# Following is some sample data that we need to analyze:

data = [
    ('4', 6.1), ('1', 4.0), ('2', 8.3), ('2', 6.5),
    ('1', 4.6), ('2', 6.8), ('3', 9.3), ('2', 7.8), ('2', 9.2),
    ('4', 5.6), ('3', 10.5), ('1', 5.8), ('4', 3.8), ('3', 8.1),
    ('3', 8.0), ('1', 6.9), ('3', 6.9), ('4', 6.2), ('1', 5.4),
    ('4', 5.8)
    ]

# One way to produce usable groups from this data is to build a dictionary 
# that maps a key to a list of members in this group as follows:

def custom_groupby(iterable, key=lambda x:x[0]):
    """Sort not required."""
    pd = defaultdict(list)
    for row in iterable:
        pd[key(row)].append(row)
    for k in sorted(pd):
        yield k, iter(pd[k])

# Following is the same feature done with the itertools.groupby() function:

def wrapped_groupby(iterable, key=lambda x:x[0]):
    """Sort required"""
    return groupby(iterable, key)

# We can extract summary statistics from the grouped data as follows:

def calc_mean(sequence): 
    return sum(sequence)/len(sequence)

def calc_variance(mean, sequence): 
    return sum(
        (x - mean)**2 / mean 
        for x in sequence
        )

def calc_summaries(grouped_iterable):
    key, list_iterable = grouped_iterable
    values = tuple((v for k, v in list_iterable))
    mean = calc_mean(values)
    variance = calc_variance(mean, values)
    return key, mean, variance

# We can use the following command to apply the calc_summaries() function 
# to each partition:

groupedData1 = custom_groupby(data, key=lambda x:x[0])
summaryData1 = list(map(calc_summaries, groupedData1))

# The alternative commands are as follows:

groupedData2 = wrapped_groupby(sorted(data), key=lambda x:x[0])
summaryData2 = list(map(calc_summaries, groupedData2))
