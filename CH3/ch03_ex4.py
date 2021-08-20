#!/usr/bin/env python3
"""Functional Python Programming

Chapter 3, Example Set 5
"""
###########################################
# Imports
###########################################

import csv
from collections import namedtuple
from typing import TextIO, Iterator, List, Text, NamedTuple

###########################################
# Combining generator expressions
###########################################

def f(x):
    pass

def g(x):
    pass

# -------------------------
# Option 1 (not reusable)
# -------------------------

g_f_x = (
    g(f(x)) 
    for x in range(10)
    )

# -------------------------
# Option 2 (reusable but less clear)
# -------------------------

g_f_x = (
    g(y) 
    for y in (
        f(x) 
        for x in range(10)
        )
    )

# -------------------------
# Option 3 (reusable and clear)
# -------------------------

f_x= (
    f(x) 
    for x in range(10)
    )

g_f_x= (
    g(y) 
    for y in f_x
    )

###########################################
# Cleaning raw data with generator functions
###########################################
# pylint: disable=line-too-long,wrong-import-position

def read_rows(fileHandler: TextIO) -> Iterator[List[Text]]:
    """Read a CSV file and emit a sequence of rows.

    >>> import io
    >>> data = io.StringIO( "1\\t2\\t3\\n4\\t5\\t6\\n" )
    >>> list(read_rows(data))
    [['1', '2', '3'], ['4', '5', '6']]
    """
    return csv.reader(fileHandler, delimiter="\t")


def remove_headings(rows: Iterator[List[Text]]) -> Iterator[List[Text]]:
    """Removing a fixed sequence of headers.

    >>> rows= [
            ["Anscombe's quartet"], 
            ['I', 'II', 'III', 'IV'], 
            ['x','y','x','y','x','y','x','y'], 
            ['1','2','3','4','5','6','7','8']
        ]
    >>> list(remove_headings( iter(rows) ))
    [['1', '2', '3', '4', '5', '6', '7', '8']]
    """
    title = next(rows)
    assert (len(title) == 1
            and title[0] == "Anscombe's quartet")
    heading = next(rows)
    assert (len(heading) == 4
            and heading == ['I', 'II', 'III', 'IV'])
    columns = next(rows)
    assert (len(columns) == 8
            and columns == ['x', 'y', 'x', 'y', 'x', 'y', 'x', 'y'])
    return rows


with open("../Anscombe.txt") as fh:
    data = remove_headings(read_rows(fh))
    print(list(data))

###########################################
# Using namedtuples
###########################################

Pair: NamedTuple = namedtuple("Pair", ("x", "y"))


def create_pairs(n: int, rows: Iterator[List[Text]]) -> Iterator[NamedTuple]:
    """Turn one of the given Anscombe's pairs into two-tuple objects.

    >>> rows = [[1,2, 3,4, 5,6, 7,8],[9,10, 11,12, 13,14, 15,16]]
    >>> list(create_pairs(0, rows))
    [Pair(x=1, y=2), Pair(x=9, y=10)]
    >>> list(create_pairs(1, rows))
    [Pair(x=3, y=4), Pair(x=11, y=12)]
    """
    for row in rows:
        yield Pair(row[n*2], row[n*2 + 1])


with open("../Anscombe.txt") as fh:
    dataset = tuple(remove_headings(read_rows(fh)))
    sample_I = tuple(create_pairs(0, dataset))
    sample_II = tuple(create_pairs(1, dataset))
    sample_III = tuple(create_pairs(2, dataset))
    sample_IV = tuple(create_pairs(3, dataset))
