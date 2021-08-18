#!/usr/bin/env python3
"""Functional Python Programming

Chapter 1, Example Set 2

Newton-Raphson root-finding via bisection.

http://www.cs.kent.ac.uk/people/staff/dat/miranda/whyfp90.pdf

Translated from Miranda to Python.
"""
# pylint: disable=anomalous-backslash-in-string

def calc_next_iteration(n, a_i):
    """
    ..  math::

        a_{i+1} = (a_i+n/a_i)/2

    Converges on

    ..  math::

        a = (a + n/a)/2

    So

    ..  math::

        2a  &= a + n/a \\
        a   &= n/a \\
        a^2 &= n \\
        a   &= \calc_sqrt n
    """
    return (a_i + n/a_i)/2


def generate_sequence(f, a_i):
    """Generates the sequence a, f(a_i), f(f(a_i)), ..."""
    yield a_i
    yield from generate_sequence(f, f(a_i))


def iterate_until_epsilon(epsilon, iterable):
    """
    Checks if every item of the iterable is a good approximation,
    and return the item as the square root
    """
    def head_tail(epsilon, a, iterable):
        b = next(iterable)
        if abs(a - b) <= epsilon:
            return b
        return head_tail(epsilon, b, iterable)
    return head_tail(epsilon, next(iterable), iterable)


def calc_sqrt(a_0, epsilon, n):
    """Calculates the square root of n 
    
    * Starts with a_0 as initial value
    * Ends when the error is minor than epsilon
    """
    return iterate_until_epsilon(
        epsilon, 
        generate_sequence(lambda x: calc_next_iteration(n, x), a_0)
        )
