###########################################
# Imports
###########################################

import random
from operator import add, mul, truediv
from functools import partial, reduce

from pymonad.tools import curry
from pymonad.reader import Compose
from pymonad.maybe import Maybe, Just, Nothing
from pymonad.list import ListMonad

###########################################
# Functional composition and currying
###########################################

# Here's a concrete example of a function that implements a 
# multiple-regression-based model for systolic blood pressure.

@curry(4)
def calc_systolic_bp(bmi, age, gender_male, treatment):
    return 68.15 + 0.58*bmi + 0.65*age + 0.94*gender_male + 6.44*treatment

# We can use the calc_systolic_bp() function with all four arguments, 
# as follows:

calc_systolic_bp(25, 50, 1, 0)
calc_systolic_bp(30, 50, 0, 1)

# We can create intermediate results that are similar to 
# partially applied functions, as follows:

'''Similar to the functools.partial() function.'''

treatment = calc_systolic_bp(25, 50, 0)

treatment(0)
treatment(1)

# Here's an example of creating some additional curried functions:

gender_treatment = calc_systolic_bp(25, 50)
gender_treatment(1, 0)
gender_treatment(0, 1)

#-----------
# Using curried higher-order functions
#-----------
'''
The new version of pymonad doesn't support currying with 
functions as arguments, so the functools.partial()
will be used instead
'''

# The functools.reduce() function is not "curryable" 
# so that we can't do this:

sum = reduce(add)
prod = reduce(mul)

# But the functools.partial() can be used to create 'curried' functions
# with another function as argument, as follows:

mysum = partial(reduce, add)
mysum([1,2,3]) 

mymax = partial(reduce, lambda x,y: x if x > y else y)
mymax([2,5,3])

#-----------
# Currying the hard way
#-----------

# We can create curried functions manually, as follows:

def f(x, *args):
    def f1(y, *args):
        def f2(z):
            return (x+y)*z
        if args:
            return f2(*args)
        return f2
    if args:
        return f1(*args)
    return f1

###########################################
# Functional composition and the PyMonad multiplication operator
###########################################

'''
The new version of pymonad doesn't recommend the use of operators.
Instead, the Compose class will be used instead
'''

# Here's a first function that computes the product 
# of the values of an iterable:

def calc_product(n):
    product = partial(reduce, mul)
    return product(n)

# Here's a second function that will produce an alternate range of values,
# depending if the input number is even or odd:

def calc_alternate_range(n):
    if n == 0: return range(1, 2) # Only 1
    if n % 2 == 0: return range(2, n+1, 2)
    else: return range(1, n+1, 2)

# Here's how we can combine the prod() and calc_alternate_range() functions 
# with Compose():

def calc_semifactorial(x):
    composite = (Compose(calc_alternate_range).then(calc_product))
    return composite(x)

calc_semifactorial(9)

###########################################
# Functors and applicative functors
###########################################
'''
A functor is a functional representation of a piece of simple data.
'''

# A functor version of the PI is a function of zero arguments 
# that returns this value, as follows:

pi = lambda : 3.14

'''
* We can wrap Python simple types with a subclass of the Maybe functor. 
* The Maybe functor gives us a way to deal gracefully with missing data

* There are two subclasses of the Maybe functor:
    • Nothing - A stand-in for the Python value of None
    • Just (some simple value) - All other Python objects
'''

# We can use a curried function with these Maybe objects 
# to tolerate missing data gracefully, as follows:

x1  = Maybe.\
    apply(calc_systolic_bp).\
    to_arguments(Just(25), Just(50), Just(1), Just(0))


x2  = Maybe.\
    apply(calc_systolic_bp).\
    to_arguments(Just(25), Just(50), Just(1), Nothing)

# Printing final values

x1Value = x1.value
print(x1Value)

x2Value = x2.value
print(x2Value is None)

# Printing final values - A better implementation (*)

x1Value = x1.maybe(0, lambda x: x)
print(x1Value)

x2Value = x2.maybe(None, lambda x: x)
print(x2Value is None)

'''
(*)

* If you need to get a value out of a Maybe or an Either, 
you can access the .value property directly. 

a = Just(2)
b = Nothing

print(a.value) # 2
print(b.value) # None

* But .value may not contain valid data  and checking whether the data 
is valid or not is the problem these monads are supposed to solve

* Given a Maybe value m, the maybe() method takes a default value, 
which will be returned if m is Nothing, and a function which 
will be applied to the value inside of a Just.

print(a.maybe(0, lambda x: x)) # 2
print(b.maybe(None, lambda x: x)) # None
'''

#-----------
# Using the lazy ListMonad() functor
#-----------

'''
If you want to evaluate range(10):
* The built-in list()function will evaluate the range() object 
to create a list with 10 items.
* The PyMonad List() functor, however, is too lazy to even 
do this evaluation
'''

# A comparison of list() and ListMonad():

someList = list(range(10))
someLazyList = ListMonad(range(10))

# The ListMonad() functor is useful to collect functions 
# without evaluating them. We can evaluate them later as required:

x = ListMonad(range(10))
x2 = list(x[0])

# Here's a version of the range() function 
# that has a lower bound of 1 instead of 0. 

def calc_range_nonzero(x):
    if x == 0: 
        return range(1, 2) # Only 1
    return range(1, x+1)

# Since a ListMonad object is a functor, we can map functions 
# to the ListMonad object, as follows:

def calc_product(n):
    product = partial(reduce, mul)
    return product(n)

def calc_factorial(x):
    composite_func = (Compose(calc_range_nonzero).then(calc_product))
    return composite_func(x)

sequence20 = ListMonad(*range(20))

results1 = map(calc_factorial, sequence20)

# Here's another function that we'll use to extend this example:

def calc_n21(n):
    return 2*n + 1

# This calcn21() function does a simple computation. 
# Here's the next part of the preceding example:

def calc_semifactorial(x):
    composite_func = (Compose(calc_alternate_range).then(calc_product))
    return composite_func(x)

def calc_n21_semifactorial(x):
    composite_func = (Compose(calc_n21).then(calc_semifactorial))
    return composite_func(x)

results2 = map(calc_n21_semifactorial, sequence20)

# We can now map the truedivision (/) operator to the 
# results1 and results2 iterables:

def calc_pi(iterable1, iterable2):
    return 2*sum(map(truediv, iterable1, iterable2))

PI = calc_pi(results1, results2)

###########################################
# Monad concepts, the bind() function and the Binary Right Shift operator
###########################################
'''
* A monad is a function that has a strict order. 
* The underlying assumption behind much functional programming 
is that functional evaluation is lazy.
* A monad provides an exception that imposes a strict left-to-right ordering.
* To impose strict evaluation, we use a binding between a monad 
and a function that will return a monad. 
* A flat expression is converted to nested bindings 
that can't be reordered by an optimizing compiler. 

* The bind() function is mapped to the >> operator, 
allowing us to write expressions like this:

Just(some_file) >> read_header >> read next >> read next

* The preceding expression would be converted to the following:

bind(bind(bind(Just(some file), read header), read next), read next)
'''

#-----------
# Implementing simulation with monads
#-----------

# We'll need a source of random numbers:

def rng():
    return (random.randint(1,6), random.randint(1,6))

# The come_out_roll() function looks like this:

@curry
def come_out_roll(dice, status):
    d= dice()
    if sum(d) in (7, 11):
        return Just(("win", sum(d), [d]))
    elif sum(d) in (2, 3, 12):
        return Just(("lose", sum(d), [d]))
    else:
        return Just(("point", sum(d), [d]))

# The point_roll() function looks like this:

@curry
def point_roll(dice, status):
    prev, point, so_far = status
    if prev != "point":
        return Just(status)
    d = dice()
    if sum(d) == 7:
        return Just(("craps", point, so_far+[d]))
    elif sum(d) == point:
        return Just(("win", point, so_far+[d]))
    else:
        return Just(("point", point, so_far+[d])) >> point_roll(dice)

# Here's our expectation from the overall game:

def craps():
    outcome = Just(("", 0, []) ) >> come_out_roll(rng) >> point_roll(rng)
    print(outcome.value)

craps()

