###########################################
# Imports
###########################################

from collections import namedtuple
from functools import reduce
from operator import itemgetter, attrgetter, add, mul, pow, truediv
from itertools import starmap, zip_longest, count, takewhile
from functools import reduce, partial

###########################################
###########################################

# We can use the following to define 
# a product() function:

product = lambda iterable: reduce(lambda x, y: x*y, iterable, 1)
product((1,2,3))

###########################################
# Evaluating conditional expressions
###########################################

# When we have multiple conditions, we have to nest the subexpressions. 
# We might end up with a command which is difficult to comprehend:

def some_expression(n, x, y, z):
    return (x if n==1 else (y if n==2 else z))

# We can use dict keys and lambda functions to create 
# a complex set of conditions. 
# Here's a way to express the factorial function as expressions:

def factorial(n):
    f = { 
        n == 0: lambda n: 1,
        n == 1: lambda n: 1,
        n == 2: lambda n: 2,
        n > 2: lambda n: factorial(n-1)*n }[True]
    return f(n)

###########################################
# Exploiting non-strict dictionary rules
###########################################

# A degenerate case of the max() function, that simply picks 
# the largest of two values:

def max(a, b):
    f = {
        a >= b: lambda: a, 
        b >= a: lambda: b
    }[True]
    return f()

'''
* In the case where a == b , both items in the dictionary 
will have a key of the True condition.
* Since the answer is the same, it doesn't matter which is kept 
and which is treated as a duplicate and overwritten.
'''

###########################################
# Filtering true conditional expressions
###########################################

# Here's another variation of the factorial() function, 
# written using the filter() function:

def semifactorial(n):
    '''n!! = n*(n - 2)(n - 4)*...'''
    alternatives= [
        (n == 0, lambda n: 1),
        (n == 1, lambda n: 1),
        (n == 2, lambda n: 2),
        (n > 2, lambda n: semifactorial(n-2)*n)
        ]
    c, f = next(filter(itemgetter(0), alternatives))
    return f(n)

###########################################
# Using the operator module instead of lambdas
###########################################

yearCheese = [
    (2000, 29.87), (2001, 30.12), (2002, 30.6), (2003, 30.66), 
    (2004, 31.33), (2005, 32.62), (2006, 32.73), (2007, 33.5), 
    (2008, 32.84), (2009, 33.02), (2010, 32.92)
    ]

# For higher order functions, we used lambda forms to pick items 
# from a tuple, as follows:

fst = lambda x: x[0]
snd = lambda x: x[1]
minCheese = min(yearCheese, key=snd)

# Instead of defining the fst() and snd() functions, 
# we can use the itemgetter(0) and the itemgetter(1) parameters, 
# as follows:

minCheese = max(yearCheese, key=itemgetter(1))

###########################################
# Getting named attributes when using higher-order functions
###########################################

# Let's say we're working with namedtuples instead of anonymous tuples,
# as follows

YearCheese = namedtuple("YearCheese", ("year", "cheese"))

yearCheese2 = list(YearCheese(*yc) for yc in yearCheese)

# In that case, there are 2 ways to locate the range of cheese consumption,
# with lambda forms or with the attrgetter() function, as follows:

minCheese1 = min(yearCheese2, key=attrgetter('cheese'))

minCheese2 = min(yearCheese2, key=lambda x: x.cheese)

###########################################
# Starmapping with operators
###########################################

# The itertools.starmap() function can be applied to an operator 
# and a sequence of pairs of values, as follows:

powNumbers = starmap(
    pow, 
    zip_longest([], range(4), fillvalue=60)
    )

# Using the results of the preceding example to calculate 
# the approximate value of π:

dividends = (3, 8, 29, 44)

piValue = sum(starmap(
    truediv, 
    zip(dividends, powNumbers)
    ))

# A simpler version that uses the map(f, x, y) function instead of 
# the starmap(f, zip(x,y)) function:

piValue = sum(map(truediv, dividends, powNumbers))

# A complex version that uses the takewhile() function
# to calculate 4 arctan(1)= π:

num = map(factorial, count())
den = map(semifactorial, (2*n+1 for n in count()))
terms = takewhile(lambda t: t > 1E-10, map(truediv, num, den))
piValue = 2*sum(terms)

###########################################
# Reducing with operators
###########################################

# The operator functions can be combined with functools.reduce(). 
# The sum() function, for example, can be defined as follows:

sum = partial(reduce, add)

# If we have a requirement for a similar function that computes a product, 
# we can define it as follows:

prod = partial(reduce, mul)
