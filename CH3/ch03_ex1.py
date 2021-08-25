#!/usr/bin/env python3
"""Functional Python Programming

Chapter 3, Example Set 1
"""

###########################################
# Callable objects as higher order functions
###########################################


class Mersenne1:
    """Callable object with a **Strategy** plug in required."""
    def __init__(self, algorithm) :
        self.pow2 = algorithm
    def __call__(self, arg):
        return self.pow2(arg) - 1

# Functions that implement 2 ^ b

def shifty(b):
    """2**b via shifting.

    >>> shifty(17)-1
    131071
    """
    return 1 << b


def multy(b):
    """2**b via naive recursion.

    >>> multy(17)-1
    131071
    """
    if b == 0: return 1
    return 2*multy(b-1)


def faster(b):
    """2**b via faster divide-and-conquer recursion.

    >>> faster(17)-1
    131071
    """
    if b == 0: return 1
    if b % 2 == 1: return 2*faster(b-1)
    t = faster(b//2)
    return t*t

# Implementations of Mersenne with strategy objects plugged in properly.

instanceShifty = Mersenne1(shifty)
instanceMulty = Mersenne1(multy)
instanceFaster = Mersenne1(faster)
