###########################################
# Using zip() to structure and flatten sequences
###########################################

xi = [
    1.47, 1.50, 1.52, 1.55, 1.57, 1.60, 1.63, 1.65, 
    1.68, 1.70, 1.73, 1.75, 1.78, 1.80, 1.83,]
yi = [
    52.21, 53.12, 54.48, 55.84, 57.20, 58.57, 59.93, 
    61.29, 63.11, 64.47, 66.28, 68.10, 69.92, 72.19, 74.46,]

pairs = tuple(zip(xi, yi))

# Other zip() operations 

list(zip()) 
list(zip((1,2,3)))
list(zip((1, 2, 3), ('a', 'b')))

###########################################
# Unzipping a zipped sequence
###########################################

xi = (x[0] for x in pairs)
yi = (x[1] for x in pairs)
sumOfProducts = sum(p0*p1 for p0, p1 in pairs)

###########################################
# Flattening sequences
###########################################

structured = [
    ['2', '3', '5', '7', '11', '13', '17', '19', '23', '29'], 
    ['31', '37', '41', '43', '47', '53', '59', '61', '67', '71'],
    ]


def flatten1(sequence):
    return (
        item 
        for row in sequence for item in row
        )


def flatten2(sequence):
    for row in sequence:
        for x in row:
            yield x


flattened1 = list(flatten1(structured))
flattened2 = list(flatten2(structured))

###########################################
# Structuring flat sequences with a custom groupby()
###########################################

flattened = [
    '2', '3', '5', '7', '11', '13', '17', '19', '23', '29', 
    '31', '37', '41', '43', '47', '53', '59', '61', '67', '71'
    ]

# A custom itertools.groupby() for sequences

def group_by_v1(n, sequence):
    flat_iter = iter(sequence)
    full_sized_items = list(
        tuple(next(flat_iter) for i in range(n)) 
        for row in range(len(sequence)//n)
        )
    trailer = tuple(flat_iter)
    if trailer: 
        return full_sized_items + list(trailer)
    else: 
        return full_sized_items

# A custom itertools.groupby() for generic iterables

def group_by_v2(n, iterable): 
    # The function don't handle the StopIteration exception
    row = tuple(next(iterable) for i in range(n))
    while row:
        yield row
        row = tuple(next(iterable) for i in range(n))    


structured1 = group_by_v1(5, flattened)
structured2 = list(group_by_v2(5, iter(flattened)))

###########################################
# Structuring flat sequences using zip()
###########################################

flattened = [
    '2', '3', '5', '7', '11', '13', '17', '19', '23', '29',
    '31', '37', '41', '43', '47', '53', '59', '61', '67', '71' 
    ]

def group_by_even_odd(sequence):
    return zip(sequence[0::2], sequence[1::2])

def group_by_n(n, sequence):
    return zip(*(sequence[i::n] for i in range(n)))

structuredEvenOdd = list(group_by_even_odd(flattened))
structuredByN = list(group_by_n(5, flattened))

###########################################
# Using reversed() to change the order
###########################################

def calc_digits(number, base):
    if number == 0: return
    yield number % base
    for i in calc_digits(number//base, base):
        yield i


def convert_to_base(number, base):
    return reversed(tuple(calc_digits(number, base)))


tuple(convert_to_base(8, 2))

###########################################
# Using enumerate() to include a sequence number
###########################################

xi = [
    1.47, 1.5, 1.52, 1.55, 1.57, 1.6, 1.63, 1.65, 
    1.68, 1.7, 1.73, 1.75, 1.78, 1.8, 1.83
    ]

# enumerate() example

time_series1 = list(enumerate(xi))

# enumerate() expressed in terms of zip()

time_series2 = list(zip(range(len(xi)), xi))
