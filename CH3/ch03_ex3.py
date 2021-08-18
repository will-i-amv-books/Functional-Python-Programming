#!/usr/bin/env python3
"""Functional Python Programming

Chapter 3, Example Set 4
"""
###########################################
# Generator expressions
###########################################

import math
from typing import Iterator

# Locate the prime factors of a number using generators and for loops

def calc_factors_iterative(x: int) -> Iterator[int]:
    """Loop/Recursion factors. Limited to numbers with 1,000 factors.

    >>> list(calc_factors_iterative(1560))
    [2, 2, 2, 3, 5, 13]
    >>> list(calc_factors_iterative(2))
    [2]
    >>> list(calc_factors_iterative(3))
    [3]
    """
    # Find even factors
    if x % 2 == 0:
        yield 2
        if x // 2 > 1:
            yield from calc_factors_iterative(x//2)
        return
    # Find odd factors
    for i in range(3, int(math.sqrt(x) + 0.5) + 1, 2):
        if x % i == 0:
            yield i
            if x // i > 1:
                yield from calc_factors_iterative(x//i)
            return
    yield x

# Locate the prime factors of a number using pure recursion

def calc_factors_recursive(x: int) -> Iterator[int]:
    """Pure Recursion factors. Limited to numbers below about 4,000,000

    >>> list(calc_factors_recursive(1560))
    [2, 2, 2, 3, 5, 13]
    >>> list(calc_factors_recursive(2))
    [2]
    >>> list(calc_factors_recursive(3))
    [3]
    """
    def factor_n(x: int, n: int) -> Iterator[int]:
        if n*n > x:
            yield x
            return
        if x % n == 0:
            yield n
            if x//n > 1:
                yield from factor_n(x // n, n)
        else:
            yield from factor_n(x, n + 2)
    # Find even factors
    if x % 2 == 0:
        yield 2
        if x//2 > 1:
            yield from calc_factors_recursive(x//2)
        return
    # Find odd factors
    yield from factor_n(x, 3)

###########################################
# Generator limitations
###########################################

import itertools
from typing import Iterable, Any

# Generators don't have a proper value until we consume the generator functions

calc_factors_iterative(1560)
factors = list(calc_factors_iterative(1560))

# Some list methods don't work with generators

len(calc_factors_iterative(1560)) # Will throw error
len(factors) # Will succeed

# Generators can be used only once

result= calc_factors_iterative(1560)
sum(result) # Will show sum
sum(result) # Will show 0

# Using itertools.tee() to clone a generator 2 or more times

def calc_extreme_values(iterable: Iterable[Any]) -> Any:
    """
    >>> calc_extreme_values([1, 2, 3, 4, 5])
    (5, 1)
    """
    max_tee, min_tee = itertools.tee(iterable, 2)
    return max(max_tee), min(min_tee)
