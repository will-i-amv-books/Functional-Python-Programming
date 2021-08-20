###########################################
# Imports
###########################################

import os, sys
import csv
import re
from urllib.request import urlopen
from collections import namedtuple

###########################################
# Parsing CSV files
###########################################

# Creae the read_rows_csv() function, that returns the iterator 
# over the rows in a tab-delimited file

def read_rows_csv(fh):
    return csv.reader(fh, delimiter="\t")

# A convert_to_float() function that handles the conversion 
# of a single string to float values, converting bad data to None value

def convert_to_float(item):
    try:
        return float(item)   
    except ValueError:
        return None

# A HOF convert_to_floats() that converts all items of a row 
# to a float or None value

def convert_to_floats(rows):
    return (
        tuple(map(convert_to_float, row))
        for row in rows
    )

'''
def convert_row_to_float(row):
    return tuple(map(convert_to_float, row))

def convert_to_floats(rows):
    return map(convert_row_to_float, rows)
'''

# A row-level validator based on the use of the all() function 
# to assure that none of the values are None:

def is_row_numeric(row): 
    return all(row) and len(row) == 8

# A higher-order function which rejects all rows 
# that have a None item:

def filter_headings(rows):
    return filter(is_row_numeric, rows)

# The CSV file parser will be as follows:

with open("../Anscombe.txt") as fh:
    coordinates = tuple(\
        filter_headings(\
        convert_to_floats(\
        read_rows_csv(fh)
        )))


###########################################
# Parsing plain text files with headers
###########################################

# In Chapter 3, Functions, Iterators, and Generators, 
# the Crayola.GPL file was presented without showing the parser

'''
GIMP Palette
Name: Crayola
Columns: 16
#

239 222 205 Almond
205 149 117 Antique Brass
'''

# The low-level parser that handles both head and tail:

def read_rows_gpl(fh):
    def read_head(fh):
        pattern = r"GIMP Palette\nName:\s*(.*?)\nColumns:\s*(.*?)\n#\n"
        header = re.compile(pattern, re.M)
        text = "".join(fh.readline() for _ in range(4))
        match = header.match(text)
        return (match.group(1), match.group(2)), fh
    def read_tail(headers, fh):
        tail = (next_line.split() for next_line in fh)
        return headers, tail
    return read_tail(*read_head(fh))

# The higher-level parser:

Color  = namedtuple("Color", ("red", "green", "blue", "name"))

def get_color_palette(headers, iterable):
    name, columns = headers
    colors = tuple(
        Color(int(r), int(g), int(b), " ".join(name))
        for r, g, b, *name in iterable)
    return name, columns, colors

# Using this two-tier parser:

with open("../crayola.gpl") as fh:
    name, columns, colors  = get_color_palette(*read_rows_gpl(fh))
    print(name, columns, colors)

