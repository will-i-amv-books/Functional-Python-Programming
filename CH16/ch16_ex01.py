###########################################
# Imports
###########################################

import csv

from functools import reduce, lru_cache

from collections.abc import Callable
from collections import Counter

from operator import mul
from fractions import Fraction
from types import SimpleNamespace
import warnings

###########################################
# Specializing memoization
###########################################

'''
* The binomial coefficient (mCn) shows the number of ways 
m different things can be arranged in groups of size n. 

* The value is as follows:

(mCn) = m!/n!*(m - n)!
'''
# Here's a helper function that we'll need:

product = lambda x: reduce(mul, x)

# Here's a Callable object with two caches 
# that uses the product() function:

class Binomial(Callable):
    def __init__(self):
        self.factorial_cache = {}
        self.binomial_cache = {}
    def factorial(self, n):
        if n not in self.factorial_cache:
            self.factorial_cache[n] = product(range(1, n+1))
        return self.factorial_cache[n]
    def __call__(self, n, m):
        if (n,m) not in self.binomial_cache:
            self.binomial_cache[n,m]  = \
                self.factorial(n) // (self.factorial(m)*self.factorial(n-m))
        return self.binomial_cache[n, m]

# We can use the preceding Callable class as follows:

binomial = Binomial()
binomial(52,5)

###########################################
# Tail recursion optimizations
###########################################

#---------------
# The general approach is this:
#---------------

# Design the base case and the recursive cases of a recursion.
# For example, this is a definition of computing a factorial:

'''n! = n*(n − 1)!'''

def factorial(n):
    if n == 0: 
        return 1
    else: 
        return n*factorial(n-1)

# If the recursion has a simple call at the end, 
# replace the recursive case with a for loop:

def factorial_tco(n):
    if n == 0: return 1
    result = 1
    for i in range(2, n): 
        result = result*i
    return result

###########################################
# Case study – making a chi-squared decision
###########################################

#---------------
# Filtering and reducing the raw data with a Counter object
#---------------

'''
* We'll represent the essential defect counts as a Counter parameter.
* We'll build counts of dataset by shift and defect type 
from the detailed raw data.
'''

# Here's a function to read some raw data from a CSV file:

def read_defects_dataset(fh):
    reader = csv.DictReader(fh)
    fieldNames = sorted(reader.fieldnames)
    expectedFieldNames = ["defect_type", "serial_number", "shift"]
    assert fieldNames == expectedFieldNames
    rows_ns = (
        SimpleNamespace(**row) 
        for row in reader
        )
    dataset = (
        (row.shift, row.defect_type) 
        for row in rows_ns 
        if row.defect_type
        )  
    return Counter(dataset)

# We'll use the read_defects_dataset() function to gather 
# and summarize the data as follows:

with open("../qa_data.csv", newline="" ) as fh:
    dataset = read_defects_dataset(fh)
    print(dataset)

#---------------
# Reading summarized data
#---------------
'''
* As an alternative to reading all of the raw data, 
we can look at processing only the summary counts. 
* Given summaries, we simply create a Counter object 
from the input dictionary.
'''

# Here's a function that will read our summary data:

def read_defects_summary(fh):
    reader = csv.DictReader(fh)
    assert reader.fieldnames == ["shift", "defect_code", "count"]
    convert = map(
        lambda x: ((x['shift'], x['defect_code']), int(x['count'])), 
        reader)
    return Counter(dict(convert))

#---------------
# Computing probabilities from a Counter object
#---------------

'''
* We need to compute the probabilities 
of dataset by shift and dataset by type.
* In order to compute the expected probabilities, 
we need to start with some simple sums
'''
# The first sum is the overall sum of all dataset, 
# which can be calculated as follows:

totalDefects = sum(dataset.values())

# Here's the sum of the dataset by shift:

totalDefectsByShift = sum(
    (
        Counter({shift : dataset[shift, defectCode]}) 
        for shift, defectCode in dataset
    ),
    Counter()
    )

# Here's the sum of the dataset by type (defect code):

totalDefectsByType = sum(
    (
        Counter({defectCode : dataset[shift, defectCode]}) 
        for shift, defectCode in dataset
    ),
    Counter()
    )

#---------------
# Alternative summary approaches
#---------------

# Here's how we can compute the probabilities of defect 
# by shift and by defect type:

pShift = dict(
    (shift, Fraction(totalDefectsByShift[shift], totalDefects))
    for shift in sorted(totalDefectsByShift)
    )

pType = dict(
    (type, Fraction(totalDefectsByType[type], totalDefects)) 
    for type in sorted(totalDefectsByType)
    )

#---------------
# Computing expected values and displaying a contingency table
#---------------

# Here's the calculation of expected probability*defect values:

expectedDataset = dict(
    (
        (shift, type_), 
        pShift[shift]*pType[type_]*totalDefects
    ) 
    for  type_ in pType for shift in pShift
    )

'''
* We'll print the observed and expected times in pairs. 
* There will be 4 groups of 12 cells. 
* Each cell has values with the observed number of dataset 
and an expected number of dataset. 
* Each row will end with the shift totals, and each column will end 
with the defect totals.
'''
# Here's a sequence of statements to create 
# the contingency table:

print("obs exp "*len(totalDefectsByType))

for shift in sorted(totalDefectsByShift):
    pairs = list(
        "{0:3d} {1:5.2f}".format(
            dataset[shift, type_], 
            float(expectedDataset[shift, type_])
            ) 
        for type_ in sorted(totalDefectsByType)
        )
    print("{0} {1:3d}".format("".join(pairs), totalDefectsByShift[shift]))    
    footers = list(
        "{0:3d}".format(totalDefectsByType[type_]) 
        for type_ in sorted(totalDefectsByType)
        )
    print("{0} {1:3d}".format("".join(footers), totalDefects))

#---------------
# Computing the chi-squared value
#---------------

# We can compute the Chi-squared value from its formula 
# as follows:

def calc_diff(expected, observed):
    return ((expected - observed)**2) / expected

chi2 = sum(
    calc_diff(expectedDataset[shift, type_], dataset[shift,type_]) 
    for shift in totalDefectsByShift for type_ in totalDefectsByType
    )

#---------------
# Computing the chi-squared threshold
#---------------

'''
* The cumulative distribution function for a χ2 value, x,  
and degrees of freedom, f, is defined as follows:

F(x, k) = partial_gamma(k/2, x/2) / complete_gamma(k/2)

* The probability of being random is usually defined as:
 
p = 1 − F (χ2, k)

* Where:
    - incomplete_gamma(s, x) is the partial gamma function
    - / complete_gamma(x) is the complete gamma function
'''

# Both the complete and incomplete gamma functions 
# require a factorial calculation, n!.
# We'll use the following one:

@lru_cache(128)
def factorial(k):
    if k < 2: return 1
    return reduce(mul, range(2, int(k)+1))

#---------------
# Computing the partial gamma value
#---------------

# Here's an implementation of the partial gamma function:

def calc_gamma_partial(s, z):
    def terms(s, z):
        for k in range(100):
            t1 = Fraction((-1)**k, factorial(k))
            t2 = Fraction(z**(s + k)) / (s + k)
            term = t1 * t2
            yield term
        warnings.warn("More than 100 terms")
    def take_until(function, iterable):
        for value in iterable:
            if function(value): 
                return
            yield value
    epsilon = 1E-8
    return sum(take_until(\
        lambda t: abs(t) < epsilon,  
        terms(s, z)
        ))

#---------------
# Computing the complete gamma value
#---------------

'''
* We're not interested in the  general implementation 
of the complete gamma function. 
* We're interested only in integer values and halves.

* For integer values, the definition is as follows 

complete_gamma(n) = (n − 1)!
    
* For halves, there's a special form:

complete_gamma(1/2 + n) = ((2*n)! / (4**n) * n!) * sqrt(PI)

'''
# Here's an implementation of the complete gamma function
# for integers and halves:

SQRT_PI = Fraction(677622787, 382307718)

def calc_gamma_complete(k):
    if isinstance(k, int):
        return factorial(k-1)
    elif isinstance(k, Fraction):
        if k.denominator == 1:
            return factorial(k-1)
        elif k.denominator == 2:
            n = k - Fraction(1,2)
        numerator = factorial(2*n)
        denominator = (Fraction(4**n)*factorial(n))
        return  (numerator / denominator) * SQRT_PI
    raise ValueError("Can't compute Γ({0})".format(k))

###########################################
# Computing the odds of a distribution being random
###########################################

'''
* Now that we have both the partial and complete gamma functions,
we can compute the X2 CDF values.
* The CDF value shows us the odds of a given X 2 value 
being random or having some possible correlation.
'''

# The function that calculates the CDF values 
# is implemented as follows:

def calc_cdf(x, k):
    """X² cumulative distribution function.
    :param x: X² value -- generally sum (obs[i]-exp[i])**2/exp[i]
    for parallel sequences of observed and expected values.:
    param k: degrees of freedom >= 1; generally len(data)-1
    """
    numerator = calc_gamma_partial(Fraction(k,2), Fraction(x/2))
    denominator = calc_gamma_complete(Fraction(k,2))
    return 1 - (numerator / denominator)

# To compute the correct CDF values execute the following commands

round(float(calc_cdf(0.004, 1)), 2)
calc_cdf(0.004, 1).limit_denominator(100)

round(float(calc_cdf(10.83, 1)), 3)
calc_cdf(10.83, 1).limit_denominator(1000)

round(float(calc_cdf(3.94, 10)), 2)
calc_cdf(3.94, 10).limit_denominator(100)

round(float(calc_cdf(29.59, 10)), 3)
calc_cdf(29.59, 10).limit_denominator(10000)

# Here's an entire row from a X2 table, 
# computed with a simple generator expression:

chi2 = [
    0.004, 0.02, 0.06, 0.15, 0.46, 1.07, 
    1.64, 2.71, 3.84, 6.64, 10.83
    ]

act = list(
    round(float(x), 3) 
    for x in map(calc_cdf, chi2, [1]*len(chi2))
    )
act
[0.95, 0.888, 0.806, 0.699, 0.498, 0.301, 0.2, 0.1, 0.05, 0.01,
0.001]

# The expected values are as follows:

[0.95, 0.90, 0.80, 0.70, 0.50, 0.30, 0.20, 0.10, 0.05, 0.01, 0.001]

# What we can do with this is get a probability from a X2 value. 
# From the example shown in the last section, 
# the 0.05 probability for six degrees of freedom has a X2 value
# of 12.5916

p = round(float(calc_cdf(12.5916, 6)), 2)
0.05

# The actual value we got for X2 in the example was 19.18. 
# Here's the probability that this value is random:

pIsRandom = round(float(calc_cdf(19.18, 6)), 5)
0.00387

# This probability is 3/775, with the denominator limited to 1000. 
# Those are not good odds of the data being random.
