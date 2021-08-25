#!/usr/bin/env python3
"""Functional Python Programming

Chapter 3, Example Set 6
"""
# pylint: disable=line-too-long,wrong-import-position,reimported

###########################################
# Imports
###########################################

from bisect import bisect_left
from collections import namedtuple
from collections.abc import Mapping

###########################################
# Using stateful mappings(dicts)
###########################################

example = '''
GIMP Palette
Name: Small
Columns: 3
#
  0   0   0	Black
255 255 255	White
238  32  77	Red
28 172 120	Green
31 117 254	Blue
'''

# Resulting object from parsing the 'example' string

Color = namedtuple("Color", ("red", "green", "blue", "name"))
colorsTuple = (
    Color(red=239, green=222, blue=205, name='Almond'),
    Color(red=205, green=149, blue=117, name='Antique Brass'),
    Color(red=253, green=217, blue=181, name='Apricot'),
    Color(red=197, green=227, blue=132, name='Yellow Green'),
    Color(red=255, green=174, blue=66, name='Yellow Orange')
    )

# Transforming the namedtple to a dict

def convert_to_dict(sequence):
    return dict(
        (color.name, color)
        for color in sequence
        )

colorsDict = convert_to_dict(colorsTuple)

###########################################
# Using the bisect module to create a dict
###########################################

# -------------------------
# Create an immutable class derived from Mapping metaclass
# that implements an ordered dict with bisect.bisect_left()
# -------------------------

class StaticMapping(Mapping):
    def __init__(self, iterable):
        self._data = tuple(iterable)
        self._keys = tuple(sorted(key for key, _ in self._data))
    
    def __getitem__(self, key):
        index = bisect_left(self._keys, key)
        if index != len(self._keys) and self._keys[index] == key:
            return self._data[index][1]
        raise ValueError("{0!r} not found".format(key))
    
    def __iter__(self):
        return iter(self._keys)
    
    def __len__(self):
        return len(self._keys)
