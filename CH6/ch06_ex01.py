###########################################
# Imports
###########################################

import pprint
from collections import Counter
from collections import defaultdict

###########################################
# Simple numerical recursions
###########################################

# A Recursive definition of sum

def add(a, b):
    if a == 0: return b
    else: return add(a - 1, b + 1)

###########################################
# Implementing tail-call optimization
###########################################

# Recursive definition of factorial

def factorial(number):
    if number == 0: return 1
    else: return number*factorial(number-1)

# A Fibonacci definition with TCO

def factorial_tco(number):
    if number == 0: return 1
    fact = 1
    for i in range(2, number):
        fact = fact*i
    return fact

###########################################
# Leaving recursion in place
###########################################

# The exponentiation by the squaring algorithm as a recursion

def fast_exponentiation(base, exponent):
    if exponent == 0: return 1
    elif exponent % 2 == 1: 
        # Odd exponents
        return base * fast_exponentiation(base, exponent - 1)
    else:
        # Even exponents
        t = fast_exponentiation(base, exponent//2)
        return t * t

###########################################
# Handling difficult tail-call optimization
###########################################

# A naive Fibonacci implementation

def fibonacci(number):
    if number == 0: return 0
    if number == 1: return 1
    return fibonacci(number-1) + fibonacci(number-2)

# A Fibonacci implementation with TCO

def fibonacci_tco(number):
    if number == 0: return 0
    if number == 1: return 1
    factor1, factor2 = 1, 1
    for i in range(3, number + 1):
        factor1, factor2 = factor2, factor1 + factor2
    return factor2

###########################################
# Processing collections via recursion
###########################################

# A purely recursive version of the older map() function
# (It materializes an iterable)

def map_recursive(function, collection):
    if len(collection) == 0: 
        return []
    head = map_recursive(function, collection[:-1])
    tail = list(function(collection[-1]))
    return  head + tail

###########################################
# Tail-call optimization for collections
###########################################

# A higher-order function that behaves like the built-in map() function:

def map_hof(f, C):
    return (f(x) for x in C)

# A generator function that behaves like the built-in map() function:

def map_generator(f, C):
    for x in C:
        yield f(x)

mapped1 = list(map_hof(lambda x:2**x, [0, 1, 2, 3, 4]))
mapped2  = list(map_generator(lambda x:2**x, [0, 1, 2, 3, 4]))

###########################################
# Reductions and folding – from many to one
###########################################

# Recursive definitions of sum and product

def sum_recursive(collection):
    if len(collection) == 0: return 0
    return collection[0] + sum_recursive(collection[1:])


def product_recursive(collection):
    if len(collection) == 0: return 1
    return collection[0] * product_recursive(collection[1:])

# A recursive product function which works 
# with an iterable source of data

def prodri(iterable):
    try:
        head = next(iterable)
    except StopIteration:
        return 1
    return head*prodri(iterable)

# A general imperative structure for reduction functions:

def product_tco(iterable):
    product = 1
    for n in iterable: 
        product *= n
    return product
