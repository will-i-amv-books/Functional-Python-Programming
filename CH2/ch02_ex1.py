#!/usr/bin/env python3
"""Functional Python Programming

Chapter 2, Example Set 1
"""
# pylint: disable=missing-docstring,wrong-import-position

###########################################
# Functions as first-class objects
###########################################

def example(a, b, **kw):
    return a*b


type(example)
example.__code__.co_varnames
example.__code__.co_argcount

###########################################
# Higher-order functions
###########################################

year_cheese = [
    (2000, 29.87), (2001, 30.12), (2002, 30.6), 
    (2003, 30.66),(2004, 31.33), (2005, 32.62), (2006, 32.73), 
    (2007, 33.5), (2008, 32.84), (2009, 33.02), (2010, 32.92)
    ]

# max() gets the tuple with the biggest value in the position 0 
# of the tuples by default
maxYear = max(year_cheese)

# Now max() gets the tuple with the biggest value in the position 1 
# of the tuples
maxCheeseYear = max(year_cheese, key=lambda tuple: tuple[1])

###########################################
# Immutable data
###########################################

year_cheese = [
    (2000, 29.87), (2001, 30.12), (2002, 30.6), 
    (2003, 30.66),(2004, 31.33), (2005, 32.62), (2006, 32.73), 
    (2007, 33.5), (2008, 32.84), (2009, 33.02), (2010, 32.92)
    ]

# Wrap-Process-Unwrap pattern

maxCheeseYear = max(map(lambda tuple: (tuple[1],tuple), year_cheese))[1]

wrapped = map(lambda yc: (yc[1], yc), year_cheese)
processed = max(wrapped)
unwrapped = processed[1]

###########################################
# Strict and lazy evaluation
###########################################

# Lazy evaluation with generator expressions/functions

def numbers():
    for i in range(1024):
        print( "=", i )
        yield i


def sum_to(number: int) -> int:
    results: int = 0
    for i in numbers():
        if i == number:
            break
        results += i
    return results

sum_to(10)

###########################################
# Recursion instead of looping
###########################################

# -------------------------
# Determining if a number is prime
# using the Rabin–Miller primality test
# -------------------------

import math

# Imperative version

def isprime_imperative(number: int) -> bool:
    """Is number prime?

    >>> isprime_imperative(2)
    True
    >>> tuple( isprime_imperative(x) for x in range(3,11) )
    (True, False, True, False, True, False, False, False)
    """
    if number < 2: return False
    if number == 2: return True
    if number % 2 == 0: return False
    for i in range(3, 1 + int(math.sqrt(number)), 2):
        if number % i == 0: 
            return False
    return True

# Recursive version with tail-call optimization
# (breaks for a recursion limit of 1000)

def isprime_recursive(number: int) -> bool:
    """Is number prime?

    >>> isprime_recursive(2)
    True
    >>> tuple( isprime_recursive(x) for x in range(3,11) )
    (True, False, True, False, True, False, False, False)
    """
    def isprime(k: int, coprime: int) -> bool:
        """Is k relatively prime to the value coprime?"""
        if k < coprime*coprime:
            return True
        if k % coprime == 0:
            return False
        return isprime(k, coprime + 2)
    if number < 2: return False
    if number == 2: return True
    if number % 2 == 0: return False
    return isprime(number, 3)

# Using generators with lazy evaluation

def isprime_generator_lazy(number: int) -> bool:
    """Is number prime?

    >>> isprime_generator(2)
    True
    >>> tuple( isprime_generator(x) for x in range(3,11) )
    (True, False, True, False, True, False, False, False)

    Remarkably slow for large primes, for example, M_61=2**61-1.
    """
    if number < 2: return False
    if number == 2: return True
    if number % 2 == 0: return False
    return not any(
        number % p == 0 
        for p in range(3, int(math.sqrt(number)) + 1, 2)
        )

# Using generators with strict evaluation

def isprime_generator_strict(number: int) -> bool:
    """Is number prime?

    >>> isprime_generator(2)
    True
    >>> tuple( isprime_generator(x) for x in range(3,11) )
    (True, False, True, False, True, False, False, False)

    Remarkably slow for large primes, for example, M_61=2**61-1.
    """
    if number < 2: return False
    if number == 2: return True
    if number % 2 == 0: return False
    return all(
        number % p != 0 
        for p in range(3, int(math.sqrt(number)) + 1, 2)
        )
