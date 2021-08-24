###########################################
# Imports
###########################################

import re
import random
import glob
import gzip
from collections import namedtuple, Counter
from datetime import datetime
from urllib.parse import urlparse
from itertools import filterfalse

###########################################
###########################################

# When working with a collection, we have situations where the
# processing order among items in the collection doesn't matter, 
# such as the following two examples:

y = range(10)

def func():
    pass

x1 = list(func(item) for item in y)
x2 = list(reversed([func(item) for item in y[::-1]]))

# The following command snippet also has the same result:

indices = list(range(len(y)))
random.shuffle(indices)

x = [None]*len(y)

for k in indices:
    x[k] = func(y[k])

###########################################
# Using multiprocessing pools and tasks
###########################################

#---------------
# Processing many large files
#---------------

# The functional design for parsing Apache CLF files 
# look as follows:

'''
data = remove_fields(\
    convert_to_accessdetail_tuples(\
    convert_to_access_tuples(\
    read_gzip_files(filename)
    )))
'''

'''
* The read_gzip_files() function reads rows from locally-cached GZIP files. 
* The convert_to_access_tuples() function creates a namedtuple object 
for each row in the access log. 
* The convert_to_accessdetail_tuples() function will expand on some 
of the more difficult to parse fields. 
* The remove_fields() function will discard some paths 
and file extensions that aren't of analytical value.
'''

#---------------
# Parsing log files – gathering the rows 
#---------------

# The read_gzip_files() function reads lines from locally cached files, 
# as follows

def read_gzip_files(pattern):
    zip_logs = glob.glob(pattern)
    for zip_file in zip_logs:
        with gzip.open(zip_file, "rb") as fh:
            yield (
                line.decode('us-ascii').rstrip() 
                for line in fh
                )

# An alternative implementation of read_gzip_files() 

def read_gzip_file(zip_file):
    log = gzip.open(zip_file, "rb")
    return (
        line.decode('us-ascii').rstrip() 
        for line in log
        )

def read_gzip_files_2(pattern):
    map(read_gzip_file, glob.glob(pattern))


#---------------
# Parsing log lines into namedtuples
#---------------

# Here is a regular expression to parse lines in a CLF file:

formatPattern = re.compile(
    r"(?P<host>[\d\.]+)\s+"
    r"(?P<identity>\S+)\s+"
    r"(?P<user>\S+)\s+"
    r"\[(?P<time>.+?)\]\s+"
    r'"(?P<request>.+?)"\s+'
    r"(?P<status>\d+)\s+"
    r"(?P<bytes>\S+)\s+"
    r'"(?P<user_agent>.+?)"\s*'
)

# Each individual access can be summarized as a namedtuple() function 
# as follows:

Access = namedtuple(
    'Access', 
    ['host', 'identity', 'user', 'time', 'request', 
    'status', 'bytes', 'user_agent']
    )

# Here is the convert_to_access_tuples() function that requires each file 
# to be represented as an iterator over the lines of the file:

def convert_to_access_tuples(iterable):
    for logfile in iterable:
        for line in logfile:
            match = formatPattern.match(line)
            if match:
                yield Access(**match.groupdict())

# An alternative implementation of convert_to_access_tuples() 

def convert_to_access_tuple(line):
    match = formatPattern.match(line)
    if match:
        return Access(**match.groupdict())

def convert_to_access_tuples(iterable):
    return map(
        convert_to_access_tuple, 
        (line for logfile in iterable for line in logfile)
        )

#---------------
# Parsing additional fields of an Access object
#---------------

# The resulting object will be a namedtuple object that 
# will wrap the original Access tuple.
# It will have additional fields for the details parsed separately:

AccessDetails = namedtuple(
    'AccessDetails', 
    ['access', 'time', 'method', 'url', 'protocol', 'agent']
    )

# The agent attribute can be broken down into fine-grained fields. 
# Here are the fields that comprise agent details:

AgentDetails= namedtuple(
    'AgentDetails', 
    ['product', 'system', 'platform_details_extensions']
    )

# Combining 3 detailed parser functions into a single parsing function.
# Here is the first part with the various detail parsers:

agentPattern = re.compile(
    r"(?P<product>\S*?)\s+"
    r"\((?P<system>.*?)\)\s*"
    r"(?P<platform_details_extensions>.*)")

def parse_request(request):
    words = request.split()
    return words[0], ' '.join(words[1:-1]), words[-1]

def parse_time(ts):
    return datetime.strptime(ts, "%d/%b/%Y:%H:%M:%S %z")

def parse_agent(user_agent):
    agent_match = agentPattern.match(user_agent)
    if agent_match:
        return AgentDetails(**agent_match.groupdict())

def convert_to_accessdetail_tuples(iterable):
    for access in iterable:
        try:
            meth, uri, protocol = parse_request(access.request)
            yield AccessDetails(
                access = access,
                time = parse_time(access.time),
                method = meth,
                url = urlparse(uri),
                protocol = protocol,
                agent = parse_agent(access.user_agent)
            )
        except ValueError as e:
            print(e, repr(access))

# An alternative implementation of convert_to_accessdetail_tuples() 

def convert_to_accessdetail_tuple(access):
    try:
        meth, uri, protocol = parse_request(access.request)
        return AccessDetails(
            access = access,
            time = parse_time(access.time),
            method = meth,
            url = urlparse(uri),
            protocol = protocol,
            agent = parse_agent(access.user_agent)
        )
    except ValueError as e:
        print(e, repr(access))

def convert_to_accessdetail_tuples(iterable):
    return filter(
        None, 
        map(convert_to_accessdetail_tuple, iterable)
        )

#---------------
# Filtering the access details
#---------------

# An optimized version of the remove_fields() function looks as follows:

excludedNames = {
    'favicon.ico', 'robots.txt', 'humans.txt', 'crossdomain.xml' , 
    '_images', 'search.html', 'genindex.html', 
    'searchindex.js', 'modindex.html', 'py-modindex.html',
}
excludedExtensions = {'.png', '.js', '.css',}

def remove_fields(iterable):    
    for detail in iterable:
        path = detail.url.path.split('/')
        if not any(path):
            continue
        if any(p in excludedNames for p in path):
            continue
        final = path[-1]
        if any(final.endswith(ext) for ext in excludedExtensions):
            continue
        yield detail

# An alternative implementation of remove_fields() 

def is_nonempty_path(path):
    return any(path)

def arethere_excluded_names(path):
    return any(
        p in excludedNames 
        for p in path
        )

def arethere_excluded_extensions(string):
    return any(
        string.endswith(ext) 
        for ext in excludedExtensions
        )

def remove_fields_2(iterable):    
    for detail in iterable:
        path = detail.url.path.split('/')
        if not is_nonempty_path(path): continue
        if arethere_excluded_names(path): continue
        if arethere_excluded_extensions(path[-1]): continue
        yield detail

# Another alternative implementation of remove_fields() 

def remove_fields_3(iterable):    
    return \
        filterfalse(arethere_excluded_extensions, \
        filterfalse(arethere_excluded_names,\
        filter(is_nonempty_path, iterable)
        ))

#---------------
# Analyzing the access details
#---------------

'''
* We'll define 2 functions to filter and analyze the individual 
AccessDetails objects. 
'''
# The filter_books() function will pass only specific paths, 
# Here is the filter_books() function:

def isthere_book_in_path(detail):
    paths = tuple(
        item 
        for item in detail.url.path.split('/') 
        if item
        )
    return paths[0] == 'book' and len(paths) > 1

def filter_books(iterable):
    return filter(isthere_book_in_path, iterable)

# The second function will summarize the occurrences 
# of each distinct path, as follows

def reduce_book_total(iterable):
    counts = Counter()
    for detail in iterable:
        counts[detail.url.path] += 1
    return counts

#---------------
# The complete analysis process
#---------------

# The composite run_analysis() function that digests 
# a collection of logfiles looks as follows

def run_analysis(filename):
    details = remove_fields(\
        convert_to_accessdetail_tuples(\
        convert_to_access_tuples(\
        read_gzip_files(filename)
        )))
    books = filter_books(details)
    totals = reduce_book_total(books)
    return totals


results = dict(run_analysis('example.log.gz'))
