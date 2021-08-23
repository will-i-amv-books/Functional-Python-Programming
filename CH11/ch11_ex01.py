###########################################
# Imports
###########################################

import math
from functools import wraps
from decimal import Decimal, InvalidOperation
'''
from collections import namedtuple, defaultdict
from itertools import groupby
from functools import lru_cache, total_ordering, partial, reduce
from numbers import Number
import operator
'''

###########################################
# Decorators as higher-order functions 
###########################################

#--------------
# Decorator usage
#--------------

# As a prefix that creates a new function with the same name 
# as the base function as follows:

def decorator():
    pass

@decorator
def decorated_function():
    pass

# As an explicit operation that returns a new function, 
# possibly with a new name:

def decorated_function():
    pass

new_function = decorator(decorated_function)

# Here's an example of a simple decorator:

def nullable(function):
    @wraps(function)
    def null_wrapper(arg):
        return None if arg is None else function(arg)
    return null_wrapper

# We can apply our @nullable decorator to create a composite function 
# as follows:

null_aware_log = nullable(math.log)

# We can use our composite, null_aware_log() function, as follows:

someData = [10, 100, None, 50, 60]
logData = list(map(null_aware_log, someData))

# Here's how we can create a null-aware rounding function 
# using decorator notation:

@nullable
def null_aware_round4(x):
    return round(x, 4)

# We could also create the null-aware rounding function 
# using the following:

null_aware_round4 = nullable(lambda x: round(x,4))

# We can use this null_aware_round4() function to create 
# a better test case for null_aware_log() function as follows:

someData = [10, 100, None, 50, 60]
logData = map(null_aware_log, someData)
roundedLogData = list(
    null_aware_round4(value) 
    for value in logData
    )

###########################################
# Composite design 
###########################################

# Python's multiple-line definition of function composition
# is as follows:

def f():
    pass

@f
def g(x):
    # Do something
    return

###########################################
# Preprocessing bad data
###########################################

'''
* We'll focus on three bad-data conversion functions: clean_int(), 
bd_float(), and bd_decimal(). 
* The composite feature we're adding will be defined before the
built-in conversion function.
'''
# Here's a simple bad-data decorator:

def remove_commas(function):
    @wraps(function)
    def wrap_bad_data(text, *args, **kwargs):
        try:
            return function(text, *args, **kwargs)
        except (ValueError, InvalidOperation):
            cleanedText = text.replace(",", "")
            return function(cleanedText, *args, **kwargs)
    return wrap_bad_data

# We can use this wrapper as follows:

clean_int = remove_commas(int)
clean_float = remove_commas(float)
clean_decimal = remove_commas(Decimal)

# Following are some examples of using the clean_int() function:

clean_int("13")
clean_int("1,371")
clean_int("1,371", base=16)

###########################################
# Adding a parameter to a decorator
###########################################

# In Python syntax, we can write it as follows:

def decorator(arg):
    pass

@decorator(arg='someParameter')
def decorated_function():
    # Do something
    return

# We can expand the remove_commas() decorator to create a more flexible 
# decorator that can accept parameters of characters to remove

def clean_list(text, charList):
    """Remove all of the given charList from a string."""
    if charList:
        return clean_list(text.replace(charList[0], ""), charList[1:])
    return text

def remove_chars(*charList):
    def outer_decorator(function):
        @wraps(function)
        def inner_decorator(text, *args, **kw):
            try:
                return function(text, *args, **kw)
            except (ValueError, InvalidOperation):
                cleanedText = clean_list(text, charList)
                return function(cleanedText, *args, **kw)
        return inner_decorator
    return outer_decorator

# We can use this decorator to create conversion functions as follows:

@remove_chars("$", ",")
def convert_to_currency (text, **kw):
    return Decimal(text, **kw)

# This convert_to_currency() function will now handle 
# some variant data formats:

convert_to_currency("13")
convert_to_currency("$3.14")
convert_to_currency("$1,701.00")

###########################################
# Implementing more complex descriptors
###########################################

# We can write nested decorators as follows, if our intent is 
# to handle some cross-cutting concerns

def f_wrap():
    pass

def g_wrap():
    pass

@f_wrap
@g_wrap
def h(x):
    #Do something
    return

# If we're using a decoration to create a composite function, 
# it might be better to use the following command:

f_g_h= f_wrap(g_wrap(h))

###########################################
# Recognizing design limitations
###########################################

'''
* In the case of data cleanup, the simplistic removal of stray characters 
may not be sufficient. 
* When working with the geolocation data, we may have a wide variety 
of input formats: 
- simple degrees ( 37.549016197 ), 
- degrees and minutes ( 37° 32.94097′ ), 
- degrees-minutes-seconds ( 37° 32′ 56.46″ ).
* For this reason, it is necessary to provide a separate cleansing function 
that's bundled in with the conversion function
'''

# Method 1 - Include the cleansing function as an argument to the decorator 
# on the conversion as follows:

def cleanse_before():
    pass

@cleanse_before(cleanser='cleanser_function')
def convert(text):
    # Do something
    return

# Method 2 - Include the conversion function as an argument 
# to the decorator for a cleansing function as follows:

def then_convert():
    pass

@then_convert(converter='converter_function')
def clean(text):
    # Do something
    return

# For the cleanse and then convert route, the decorator looks as follows:

def then_convert(convert_function):
    def clean_convert_decorator(clean_function):
        @wraps(clean_function)
        def cc_wrapper(text, *args, **kw):
            try:
                return convert_function(text, *args, **kw)
            except (ValueError, InvalidOperation):
                cleanedText = clean_function(text)
                return convert_function(cleanedText, *args, **kw)
        return cc_wrapper
    return clean_convert_decorator

# We can now build a more flexible cleanse and convert function 
# as follows:

@then_convert(int)
def remove_punctuation(text):
    return text.replace(",", "").replace("$", "")

# We can use the integer conversion as follows:

remove_punctuation("1,701")
remove_punctuation("97")

'''
While this encapsulates some sophisticated cleansing and converting 
into a very tidy package, the results are potentially confusing. 
'''

# As an alternative, we can use the prefix notation as follows:

def remove_punctuation(text):
    return text.replace(",", "").replace("$", "")

remove_punctuation_int = then_convert(int)(remove_punctuation)

