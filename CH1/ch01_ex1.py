"""Functional Python Programming

Chapter 1, Example Set 1
"""

###########################################
# A sum in different programming paradigms
###########################################

# Purely imperative

def sum_imperative():
    """Purely imperative.

    >>> sum_imperative()
    23
    """
    result = 0
    for number in range(1, 10):
        if number % 3 == 0 or number % 5 == 0:
            result += number
    print(result)

# Hybrid imperative-OOP

def sum_hybrid_oop():
    """Some Object Features.

    >>> sum_hybrid_oop()
    23
    """
    results = list()
    for number in range(1, 10):
        if number % 3 == 0 or number % 5 == 0:
            results.append(number)
    print(sum(results))

# Purely OOP

class SummableList(list):
    """Full-on OO.
    """
    def sum(self):
        result = 0
        for value in self:
            result += value
        return result


def sum_oop():
    """Full-on OO.

    >>> sum_oop()
    23
    """
    results = SummableList()
    for number in range(1, 10):
        if number % 3 == 0 or number % 5 == 0:
            results.append(number)
    print(results.sum())

# Purely functional

def filter_list(endValue, filter_function, initValue):
    """Build a filtered list

    >>> filter_list(10, lambda x: x%3==0 or x%5==0, 0)
    [0, 3, 5, 6, 9]
    """
    if initValue == endValue:
        return []
    if filter_function(initValue):
        return [initValue] + filter_list(endValue, filter_function, initValue+1)
    else:
        return filter_list(endValue, filter_function, initValue+1)


def is_multipleof_3or5(x):
    """Filter multiples of 3 or 5"""
    return x % 3 == 0 or x % 5 == 0


def sum_sequence(sequence):
    if len(sequence) == 0: return 0
    return sequence[0] + sum_sequence(sequence[1:])


def sum_functional(number):
    """
    >>> sum_functional()
    23
    """    
    filteredItems = filter_list(number, is_multipleof_3or5, 0)
    return sum_sequence(filteredItems)

# Hybrid functional-imperative

def sum_hybrid_functional(number):
    """Hybrid Function.

    >>> sum_hybrid_functional()
    23
    """
    return sum(
        number 
        for number in range(1, 10) 
        if number % 3 == 0 or number % 5 == 0
        )

###########################################
# Performance differences from folding
###########################################

import timeit


def folding():
    """Performance differences from folding.

    >>> ((([]+[1])+[2])+[3])+[4]
    [1, 2, 3, 4]
    >>> []+([1]+([2]+([3]+[4])))
    [1, 2, 3, 4]
    """
    print("foldl", timeit.timeit("((([]+[1])+[2])+[3])+[4]"))
    print("foldr", timeit.timeit("[]+([1]+([2]+([3]+[4])))"))
