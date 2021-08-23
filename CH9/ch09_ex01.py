###########################################
# Imports
###########################################

import os, sys
import math
from collections import namedtuple, defaultdict
from itertools import product, groupby, permutations, combinations

rootRelativePath = '..'
rootAbsolutePath = os.path.abspath(rootRelativePath)
sys.path.append(rootAbsolutePath)

from CH4.ch04_ex2 import calc_correlation

###########################################
# Enumerating the Cartesian product
###########################################

# Mathematically, the product of two 3-item sets has 9 pairs as follows:

set1 = {1, 2, 3}
set2 = {'D', 'H', 'S'}
cartesianProd = {
    (1, 'D'), (1, 'S'), (1, 'H'), 
    (2, 'D'), (2, 'S'), (2, 'H'), 
    (3, 'D'), (3, 'S'), (3, 'H')
}

# We can produce the preceding results by executing the following commands:

cartesianProd = list(product(range(1, 4), 'DHS'))

###########################################
# Reducing a product
###########################################

# We can use the join() custom function to join two tables, 
# as shown in the following command:

def join(table1, table2, where):
    return filter(where, product(table1, table2))

# Assume that we have a table of Color objects as follows:

Color  = namedtuple("Color", ("red", "green", "blue", "name"))

rgbColorNames = [
    Color(rgb=(239, 222, 205), name='Almond'),
    Color(rgb=(255, 255, 153), name='Canary'),
    Color(rgb=(28, 172, 120), name='Green'),
    Color(rgb=(255, 174, 66), name='Yellow Orange')
    ]


# Given a PIL.Image object, we can iterate over the collection of pixels 
# with something like the following:

def calc_pixels_from_coords(image):
    w, h = image.size
    return (
        (color, image.getpixel(color)) 
        for color in product(range(w), range(h))
        )

'''
* We've determined the range of each coordinate based on the image size. 
* The calculation of the product(range(w), range(h)) method creates 
all the possible combinations of coordinates.
'''

#----------------
# Computing distances
#----------------

'''
* When doing color matching, we won't have a simple equality test.
* We're often forced to define a minimal distance function 
to determine whether two colors are close enough, 
without being the same three values of R, G, and B.
'''
# Here are the Euclidean and Manhattan distance functions:

def euclidean(pixel, color):
    return math.sqrt(sum(map(\
        lambda x, y: (x -y)**2, 
        pixel, 
        color.rgb
        )))

def manhattan(pixel, color):
    return sum(map(\
        lambda x, y: abs(x - y), 
        pixel, 
        color.rgb
        ))

'''
For each individual pixel, we can compute the distance from that pixel's color 
to the available colors in a limited color set. 
'''
# The results of this calculation for a single pixel might look like this:

pixelDistances = (
    ((0, 0), (92, 139, 195), Color(rgb=(239, 222, 205), name='Almond'), 
    169.10943202553784), 
    ((0, 0), (92, 139, 195), Color(rgb=(255, 255, 153), name='Canary'), 
    204.42357985320578),
    ((0, 0), (92, 139, 195), Color(rgb=(28, 172, 120), name='Green'), 
    103.97114984456024), 
    ((0, 0), (92, 139, 195), Color(rgb=(48, 186, 143), name='Mountain Meadow'), 
    82.75868534480233), 
)

'''
Each of the four tuples contains the following contents:
• The pixel's coordinates, for example, (0,0)
• The pixel's original color, for example, (92, 139, 195)
• A Color object from our set of seven colors, for example, 
Color(rgb=(239,222, 205),name='Almond')
• The Euclidean distance between the original color 
and the given Color object
'''

# The smallest Euclidean distance is the closest match color. 
# This kind of reduction is done with the min() function:

pixelMinDistance = min(pixelDistances, key=lambda x: x[3])

#----------------
# Getting all pixels and all colors
#----------------

# One way to map pixels to colors is to enumerate all pixels 
# and all colors using the product() function:

xy_coords = lambda xyp_c: xyp_c[0][0]
pixel = lambda xyp_c: xyp_c[0][1]
color = lambda xyp_c: xyp_c[1]

def get_pixelcolor_pairs(image, colors):
    return (
        (
            xy_coords(item), 
            pixel(item), 
            color(item), 
            euclidean(pixel(item), color(item))
        )
        for item in product(calc_pixels_from_coords(image), colors)
    )

distances = get_pixelcolor_pairs('someImage', rgbColorNames)
for _, choices in groupby(distances, key=lambda x: x[0]):
    print(min(choices, key=lambda x: x[3]))

#----------------
# Performance analysis
#----------------

# Here is a basic algorithm to collect some data from a .JPG image:

def group_pixel_by_color(image):
    palette = defaultdict(list)
    for xy_pixel in calc_pixels_from_coords(image):
        xy_coords, pixel = xy_pixel
        palette[pixel].append(xy_coords)
    w, h = image.size
    print("Total pixels ", w*h)
    print("Total colors ", len(palette))


# We can apply mask values to the RGB bytes with the following:

maskedColors = tuple(map(lambda x: x&0b11100000, rgbColorNames))

#----------------
# Combining two transformations
#----------------

# Here is a way to build a color map that combines both distances 
# to a given set of colors and truncation of the source colors:

img = 'someImage'
bit3 = range(0, 256, 0b100000)
best = (
    (min(euclidean(rgb, color), rgb, color) for color in rgbColorNames)
    for rgb in product(bit3, bit3, bit3)
    )
color_map = dict((b[1], b[2].rgb) for b in best)

# The following are the commands for the image replacement:

clone = img.copy()
for xy, p in calc_pixels_from_coords(img):
    r, g, b = p
repl = color_map[(0b11100000&r, 0b11100000&g, 0b11100000&b)]
clone.putpixel(xy, repl)
clone.show()

###########################################
# Permuting a collection of values
###########################################

'''
* One popular example of combinatorial optimization problems is the
assignment problem. 
* We have n agents and n tasks, but the cost of each agent
performing a given task is not equal. 
* Some agents have trouble with some details, 
while other agents excel at these details. 
* If we can properly assign tasks to agents, we can minimize the costs.
'''
# Assuming that we have a cost matrix with 36 values that show 
# the costs of six agents and six tasks, 
# we can formulate the problem as follows:

cost = [] # 6X6 Matrix
perms = permutations(range(6))
alt = (
    (sum(cost[x][y] for y, x in enumerate(perm)), perm) 
    for perm in perms
    )
minMatrix = min(alt)[0]
print(ans for s, ans in alt if s == minMatrix)

###########################################
# Generating all combinations
###########################################

# There are 2,598,960 5-card poker hands. 
# We can actually enumerate all 2 million hands as follows:

hands = list(combinations(tuple(product(range(13), '♠♥♦♣')), 5))

# Let's get some sample data from http://www.tylervigen.com 
# We'll pick three datasets with the same time range: 
# numbers 7, 43, and 3890. 
# We'll laminate the data into a grid, repeating the year column.
# This is how the first and the remaining rows of the yearly data will look:

dataset = [
    ('year', 
    'Per capita consumption of cheese (US) - Pounds (USDA)',
    'Number of people who died by becoming tangled in their \
        bedsheets - Deaths (US) (CDC)'),
    ('year', 
    'Per capita consumption of mozzarella cheese (US) - Pounds (USDA)', 
    'Civil engineering doctorates awarded (US) - \
        Degrees awarded (National Science Foundation)'),
    ('year', 
    'US crude oil imports from Venezuela - Millions of barrels \
        (Dept. of Energy)', 
    'Per capita consumption of high fructose corn syrup (US) - Pounds (USDA)')
    (2000,	29.8,	327,	2000,	9.3, 480, 2000, 446, 62.6),
    (2001,	30.1,	456,	2001,	9.7, 501, 2001, 471, 62.5),
    (2002,	30.5,	509,	2002,	9.7, 540, 2002, 438, 62.8),
    (2003,	30.6,	497,	2003,	9.7, 552, 2003, 436, 60.9),
    (2004,	31.3,	596,	2004,	9.9, 547, 2004, 473, 59.8),
    (2005,	31.7,	573,	2005,	10.2, 622, 2005, 449, 59.1),
    (2006,	32.6,	661,	2006,	10.5, 655, 2006, 416, 58.2),
    (2007,	33.1,	741,	2007,	11, 701, 2007, 420, 56.1),
    (2008,	32.7,	809,	2008,	10.6, 712, 2008, 381, 53),
    (2009,	32.8,	717,	2009,	10.6, 708, 2009, 352, 50.1)
]

# Wwe can use the combinations() function to emit all the combinations 
# of the nine variables in this dataset, taken two at a time:

combinations(range(9), 2)

# Here is a function that picks a column of data out of our dataset:

def column(source, x):
    for row in source:
        yield row[x]

# This is how we can compute all combinations of correlations:

    for p, q in combinations(range(9), 2):
        header_p, *data_p = list(column(source, p))
        header_q, *data_q = list(column(source, q))
        if header_p == header_q: continue
        r_pq = calc_correlation(data_p, data_q)
        print("{2: 4.2f}: {0} vs {1}".format(
            header_p, 
            header_q, 
            r_pq)
            )

