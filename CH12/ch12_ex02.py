###########################################
# Imports
###########################################

import os, sys
from re import I
import glob
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Pool
from collections import Counter

'''
import re
import random
import gzip
from datetime import datetime
from urllib.parse import urlparse
from itertools import filterfalse
'''

rootRelativePath = '..'
rootAbsolutePath = os.path.abspath(rootRelativePath)
sys.path.append(rootAbsolutePath)

from CH12.ch12_ex01 import run_analysis

###########################################
# Using a multiprocessing pool for concurrent processing
###########################################

# The recipe for mapping work to a separate process 
# looks as follows:

def run_parallel_analysis(pattern):
    with Pool(4) as workers:
        workers.map(run_analysis, glob.glob(pattern))

'''
The Pool object has 4 map-like methods to allocate work 
to a pool: map() , imap() , imap_unordered() , and starmap()

* The map(function, iterable) method allocates items 
from the iterable to each worker in the pool. 
* The imap(function, iterable) method is described as "lazier" than map.
By default, it sends each individual item from the iterable 
to the next available worker. 
* The imap_unordered(function, iterable) method is similar 
to the imap() method, but the order of the results is not preserved. 
* The starmap(function, iterable) method is similar to 
the itertools.starmap() function. 
'''

# Here is an example of the imap_unordered() method:

def run_parallel_analysis_2():
    pattern = "*.gz"
    combined = Counter()
    with Pool() as workers:
        results = workers.imap_unordered(run_analysis, glob.glob(pattern))
        for result in results:
            combined.update(result)

#---------------
# Using apply() to make a single request
#---------------

# The map() method and its variants are for loops 
# wrapped around the apply() method:

pattern = "*.gz"
with Pool() as workers:
    results = list(
        workers.apply(run_analysis, f) 
        for f in glob.glob(pattern)
        )

#---------------
# Using map_async(), starmap_async(), and apply_async()
#---------------

# The following is a variation using the map_async() method:

def run_parallel_analysis_3():
    pattern = "*.gz"
    combined= Counter()
    with Pool() as workers:
        results = workers.map_async(run_analysis, glob.glob(pattern))
        data = results.get()
        for item in data:
            combined.update(item)

###########################################
# Using the concurrent.futures module
###########################################

# Here is an example of concurrent.futures usage:

def run_multithreaded_analysis():
    pool_size = 4
    pattern = "*.gz"
    combined = Counter()
    with ProcessPoolExecutor(max_workers=pool_size) as workers:
        results = workers.map(run_analysis, glob.glob(pattern))
        for result in results:
            combined.update(result)

