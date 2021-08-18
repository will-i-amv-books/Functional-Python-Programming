#!/usr/bin/env python3
"""Functional Python Programming

Chapter 4, Example Set 4

Definitions of mean, stddev, Pearson correlation
and linear estimation.

http://en.wikipedia.org/wiki/Mean

http://en.wikipedia.org/wiki/Standard_deviation

http://en.wikipedia.org/wiki/Standard_score

http://en.wikipedia.org/wiki/Normalization_(statistics)

http://en.wikipedia.org/wiki/Simple_linear_regression
"""
###########################################
# Imports
###########################################

from math import sqrt
from collections import Sequence

###########################################
# Using any() and all() as reductions
###########################################

def isprime(number: int) -> bool:
    if number < 2: return False
    if number == 2: return True
    if number % 2 == 0: return False
    return not any(
        number % p == 0 
        for p in range(3, int(sqrt(number)) + 1, 2)
        )

primes = [
    '2', '3', '5', '7', '11', '13', '17', '19', '23', '29',
    '31', '37', '41', '43', '47', '53', '59', '61', '67', '71' 
    ]

# Check if there are a number that is not prime

areThereNonprimes = not all(isprime(int(x)) for x in primes)
areThereNonprimes = any(not isprime(int(x)) for x in primes)

###########################################
# Using sums and counts for statistics
###########################################

# Basic sum functions

def s0(samples: Sequence) -> float:
    return len(samples)  # sum(x**0 for x in samples)

def s1(samples: Sequence) -> float:
    return sum(samples)  # sum(x**1 for x in samples)

def s2(samples: Sequence) -> float:
    return sum(x**2 for x in samples)

# Basic statistical functions

def calc_mean(samples: Sequence) -> float:
    """Arithmetic mean.

    >>> d = [4, 36, 45, 50, 75]
    >>> calc_mean(d)
    42.0
    """
    return s1(samples)/s0(samples)


def calc_stdev(samples: Sequence) -> float:
    """Standard deviation.

    >>> d = [ 2, 4, 4, 4, 5, 5, 7, 9 ]
    >>> calc_mean(d)
    5.0
    >>> calc_stdev(d)
    2.0
    """
    N = s0(samples)
    return sqrt((s2(samples)/N) - (s1(samples)/N)**2)


def calc_normalized_score(x: float, mean_x: float, stdev_x: float) -> float:
    """
    Compute a normalized score (Z).

    >>> d = [ 2, 4, 4, 4, 5, 5, 7, 9 ]
    >>> list( 
            calc_normalized_score(x, calc_mean(d), calc_stdev(d)) 
            for x in d 
            )
    [-1.5, -0.5, -0.5, -0.5, 0.0, 0.0, 1.0, 2.0]

    The above example recomputed mean and standard deviation.
    Not a best practice.
    """
    return (x - mean_x) / stdev_x


def calc_correlation(samples1: Sequence, samples2: Sequence) -> float:
    """Pearson product-moment correlation.

    >>> xi= [1.47, 1.50, 1.52, 1.55, 1.57, 1.60, 1.63, 1.65,
    ...     1.68, 1.70, 1.73, 1.75, 1.78, 1.80, 1.83,] #  Height (m)
    >>> yi= [52.21, 53.12, 54.48, 55.84, 57.20, 58.57, 59.93, 61.29,
    ...     63.11, 64.47, 66.28, 68.10, 69.92, 72.19, 74.46,] #  Mass (kg)
    >>> round( calc_correlation( xi, yi ), 5 )
    0.99458
    """
    m_1, s_1 = calc_mean(samples1), calc_stdev(samples1)
    m_2, s_2 = calc_mean(samples2), calc_stdev(samples2)
    z_1 = (calc_normalized_score(x, m_1, s_1) for x in samples1)
    z_2 = (calc_normalized_score(x, m_2, s_2) for x in samples2)
    r = sum(zx1*zx2 for zx1, zx2 in zip(z_1, z_2)) / len(samples1)
    return r

xi = [
    1.47, 1.50, 1.52, 1.55, 1.57, 1.60, 1.63, 1.65,
    1.68, 1.70, 1.73, 1.75, 1.78, 1.80, 1.83,] # Height (m)
yi = [
    52.21, 53.12, 54.48, 55.84, 57.20, 58.57, 59.93, 61.29,
    63.11, 64.47, 66.28, 68.10, 69.92, 72.19, 74.46,] # Mass (kg)

round(calc_correlation( xi, yi ), 5)
