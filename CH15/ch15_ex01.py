###########################################
# Imports
###########################################

import re
import os, sys
import traceback
import random
import base64

import json
import csv, io
import xml.etree.ElementTree as XML
import string

import wsgiref
from urllib.request import urlopen
from urllib.parse import parse_qs
from http.server import HTTPServer, SimpleHTTPRequestHandler

from functools import wraps

rootRelativePath = '..'
rootAbsolutePath = os.path.abspath(rootRelativePath)
sys.path.append(rootAbsolutePath)

from CH3.ch03_ex4 import create_pairs, remove_headings, read_rows, Pair

###########################################
# The HTTP request-response model
###########################################

# An HTTP client executes something similar to the following:

url = 'http://slott-softwarearchitect.blogspot.com'

with urlopen(url) as response:
    print(response.read())

# At the other end of the protocol, a static content server 
# should also be stateless.
# For that end, we can use the http.server library as follows:


running = True
httpd = HTTPServer(
    ('localhost',8080), 
    SimpleHTTPRequestHandler
    )

while running:
    httpd.handle_request()
    httpd.shutdown()

#-----------------
# Considering a server with a functional design
#-----------------

# Conceptually, a web service should have a top-level implementation 
# that can be summarized as follows:

request = 'some_request'
response = httpd(request)

#-----------------
# Looking more deeply into the functional view
#-----------------

# We can think of a web server like this:

headers = 'some_headers'
uploads = 'some_uploads'

headers, content = httpd(headers, request, [uploads])

#-----------------
# Nesting the services
#-----------------

# A conceptual view of the functions that compose a web service
# is something like this:

def check_authentication():
    pass

def check_csrf():
    #Cross-site request forgery
    pass

def check_session():
    pass

def send_content():
    pass

forms = {}

response = send_content(\
    check_authentication(\
    check_csrf(\
    check_session(headers, request, [forms])
    )))

'''
* The problem with the nested function view is that each nested context 
may also need to tweak the response instead of 
or in addition to tweaking the request.
'''
# Instead, we want something more like this:

def check_session(headers, request, forms):
    # pre-process: determine session
    # content = csrf(headers, request, forms)
    # post-processes the content
    # return the content
    pass

def check_csrf(headers, request, forms):
    # pre-process: validate csrf tokens
    # content= check_authentication(headers, request, forms)
    # post-processes the content
    # return the content
    pass

###########################################
# The WSGI standard
###########################################

# Each WSGI "application" has the same interface:

def some_app(environ, start_response):
    return content

'''
* The environ is a dictionary that contains all of the arguments 
of the request in a single, uniform structure
* The start_response is a function that must be used 
to send the status and headers of a response.
'''

# Here's a very simple routing application:

def demo_app():
    pass

def static_app():
    pass

def welcome_app():
    pass

SCRIPT_MAP = {
    'demo': demo_app,
    'static': static_app,
    '': welcome_app,
}

def routing(environ, start_response):
    top_level = wsgiref.util.shift_path_info(environ)
    app = SCRIPT_MAP.get(top_level, SCRIPT_MAP[''])
    content = app(environ, start_response)
    return content

#-----------------
# Throwing exceptions during WSGI processing
#-----------------

# We can define a WSGI application that provides static content 
# as follows:

def index_app():
    pass

CONTENT_HOME = '/home/dir'

def static_app(environ, start_response):
    try:
        with open(CONTENT_HOME + environ['PATH_INFO']) as static:
            content = static.read().encode('utf-8')
            headers = [
                ('Content-Type', 'text/plain; charset ="utf-8"'),
                ('Content-Length', str(len(content))),
                ]
        start_response('200 OK', headers)
        return [content]
    except IsADirectoryError as e:
        return index_app(environ, start_response)
    except FileNotFoundError as e:
        start_response('404 NOT FOUND', [])
        return([repr(e).encode('utf-8')])

'''
* In this case, we tried to open the requested path as a text file. 
* There are two common reasons why we can't open a given file, 
both of which are handled as exceptions:
    • If the file is a directory, we'll use a different application 
    to present directory contents
    • If the file is simply not found, we'll return 
    an HTTP 404 NOT FOUND response
'''

#-----------------
# Defining web services as functions
#-----------------

'''
* We'll split our application into two tiers: 
    - A web tier, which will be a simple WSGI application.
    - The rest of the processing, which will be 
    more typical functional programming. 
    
* We need to provide two pieces of information to the web service:
    - The quartet that we want.     
    - The output format we want.

* A URL we can use will look like this:
http://localhost:8080/anscombe/III/?form=csv
'''

#-----------------
# Defining web services as functions
#-----------------

# First, we'll use a URL pattern-matching expression to define 
# the one and only routing in our application:

urlPathPattern = re.compile(r'^/anscombe/(?P<dataset>.*?)/?$')

# Here's the unit test that demonstrates how this pattern works:

testPattern = """
    >>> m1 = urlPathPattern.match(""/anscombe/I"")
    >>> m1.groupdict()
    {'dataset': 'I'}
    >>> m2 = urlPathPattern.match(""/anscombe/II/"")
    >>> m2.groupdict()
    {'dataset': 'II'}
    >>> m3 = urlPathPattern.match(""/anscombe/"")
    >>> m3.groupdict()
    {'dataset': ''}
"""

# We can include the three previously mentioned examples a
# s part of the overall doctest:

__test__ = {
    "test_pattern": testPattern,
}

#-----------------
# Getting raw data
#-----------------

# The read_raw_data() function is copied from Chapter 3, 
# with some important changes, as follows:

def read_raw_data():
    """
    >>> read_raw_data()['I'] #doctest: +ELLIPSIS
    (Pair(x=10.0, y=8.04), Pair(x=8.0, y=6.95), ...
    """
    with open("../Anscombe.txt") as fh:
        dataset = tuple(remove_headings(read_rows(fh)))
        mapping = dict(
            (id_str, tuple(create_pairs(_id, dataset)))
            for _id, id_str in enumerate(['I', 'II', 'III', 'IV'])
        )
    return mapping

#-----------------
# Applying a filter
#-----------------

# The entire filter process is embodied in the following function:

def anscombe_filter(set_id, raw_data):
    """
    >>> anscombe_filter(""II"", raw_data()) #doctest: +ELLIPSIS
    (Pair(x=10.0, y=9.14), Pair(x=8.0, y=8.14), Pair(x=13.0, y=8.74),
    ...
    """
    return raw_data[set_id]

#-----------------
# Serializing the results
#-----------------

'''
The serializers fall into two groups, those that produce strings 
and those that produce bytes. 
* A serializer that produces a string will need 
to have the string encoded as bytes. 
* A serializer that produces bytes doesn't need any further work.
'''

# Here's how we can standardize the conversion to bytes
# using a decorator, as follows:

def to_bytes(function):
    @wraps(function)
    def decorated(*args, **kw):
        text = function(*args, **kw)
        return text.encode('utf-8')
    return decorated

#-----------------
# Serializing data into the JSON or CSV format
#-----------------

# The JSON serializer is implemented as follows:

@to_bytes
def serialize_json(series, data):
    """
    >>> data = [Pair(2,3), Pair(5,7)]
    >>> serialize_json(""test"", data)
    b'[{"x": 2, "y": 3}, {"x": 5, "y": 7}]'
    """
    obj = list(
        dict(x=row.x, y=row.y) 
        for row in data
        )
    text = json.dumps(obj, sort_keys=True)
    return text

# The CSV serializer is implemented as follows:

@to_bytes
def serialize_csv(series, data):
    """
    >>> data  = [Pair(2,3), Pair(5,7)]
    >>> serialize_csv(""test"", data)
    b'x,y\\r\\n2,3\\r\\n5,7\\r\\n'
    """
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, Pair._fields)
    writer.writeheader()
    writer.writerows(row._asdict() for row in data)
    return buffer.getvalue()

#-----------------
# Serializing data into XML
#-----------------

# The XML serializer is implemented as follows:

def serialize_xml(series, data):
    """
    >>> data = [Pair(2,3), Pair(5,7)]
    >>> serialize_xml("test", data)
    b'<series name="test">
        <row>
            <x>2</x>
            <y>3</y>
        </row>
        <row>
            <x>5</x>
            <y>7</y>
        </row>
    </series>'
    """
    doc = XML.Element("series", name=series)
    for row in data:
        row_xml = XML.SubElement(doc, "row")
        x = XML.SubElement(row_xml, "x")
        x.text = str(row.x)
        y = XML.SubElement(row_xml, "y")
        y.text = str(row.y)
    return XML.tostring(doc, encoding='utf-8')

#-----------------
# Serializing data into HTML
#-----------------

# The HTML serializer is implemented as follows:

data_page = string.Template(
    """
    <html>
        <head>
            <title>Series ${title}</title>
        </head>
        <body>
            <h1>Series ${title}</h1>
            <table>
                <thead>
                    <tr>
                        <td>x</td>
                        <td>y</td>
                    </tr>
                </thead>
                <tbody>${rows}</tbody>
            </table>
        </body>
    </html>""")

error_page = string.Template('Some_HTML_template')

@to_bytes
def serialize_html(series, data):
    """
    >>> data = [Pair(2,3), Pair(5,7)]
    >>> serialize_html(""test"", data) #doctest: +ELLIPSIS
    b'<html>...<tr><td>2</td><td>3</td></tr>\\n<tr><td>5</td>
    <td>7</td></tr>...
    """
    htmlRows = (
        '<tr>\
            <td>{0.x}</td>\
            <td>{0.y}</td>\
        </tr>'.format(row) 
        for row in data
        )
    text = data_page.substitute(
        title=series,
        rows='\n'.join(htmlRows)
    )
    return text

# Now the generic serializer function can pick 
# from the list of specific serializers. 

# The collection of serializers are as follows:

serializers = {
    'xml': ('application/xml', serialize_xml),
    'html': ('text/html', serialize_html),
    'json': ('application/json', serialize_json),
    'csv': ('text/csv', serialize_csv),
}

# The generic serializer function is implemented as follows:

def write_serialized_data(format, title, data):
    """json/xml/csv/html serialization.
    >>> data = [Pair(2,3), Pair(5,7)]
    >>> write_serialized_data(""json"", ""test"", data)
    (b'[{""x"": 2, ""y"": 3}, {""x"": 5, ""y"": 7}]', 'application/json')
    """
    mime, function = serializers.get(
        format.lower(), 
        ('text/html', serialize_html))
    return function(title, data), mime

# And the overall WSGI application is implemented as follows:

def wsgi_anscombe_app(environ, start_response):
    log = environ['wsgi.errors']
    try:
        match = urlPathPattern\
            .match(environ['PATH_INFO']) # Which set to extract
        setID = match\
            .group('dataset')\
            .upper()
        query = parse_qs(environ['QUERY_STRING']) # Which output format to use
        print(
            environ['PATH_INFO'], 
            environ['QUERY_STRING'],
            match.groupdict(), 
            file=log
            )
        log.flush()
        dataset = anscombe_filter(setID, read_raw_data())
        content, mime = write_serialized_data(
            query['form'][0], 
            setID, 
            dataset
            )
        headers = [
            ('Content-Type', mime),
            ('Content-Length', str(len(content))),
        ]
        start_response("200 OK", headers)
        return [content]
    except Exception as e:
        traceback.print_exc(file =log)
        tb = traceback.format_exc()
        page = error_page.substitute(
            title="Error",
            message=repr(e), 
            traceback=tb
            )
        content = page.encode("utf-8")
        headers  = [
            ('Content-Type', "text/html"),
            ('Content-Length', str(len(content))),
        ]
        start_response("404 NOT FOUND", headers)
        return [content]

###########################################
# Tracking usage
###########################################

'''
Many publicly available APIs require the use of an API Key. 
* The API Key is used to authenticate access. 
* It's also be used to authorize specific features. 
* It's also used to track usage. 
'''

# To create API Keys, a cryptographic random number can be used
# to generate a difficult-to-predict key string, as follows:

rng = random.SystemRandom()
def make_key_1(rng=rng, size=1):
    key_bytes = bytes(
        rng.randrange(0,256) 
        for i in range(18*size)
        )
    return base64.urlsafe_b64encode(key_bytes)
