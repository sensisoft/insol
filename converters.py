#!/usr/bin/env python
# encoding: utf-8
"""
converters.py

same set of python_to_solr data format converting function as in pysolr or solango,
this is as common as it can be

"""

from datetime import datetime, date

def py_to_solr(value):
    """
    Converts python values to a form suitable for insertion into the xml
    we send to solr.
    """
    if isinstance(value, datetime):
        value = value.strftime('%Y-%m-%dT%H:%M:%S.000Z')
    elif isinstance(value, date):
        value = value.strftime('%Y-%m-%dT00:00:00.000Z')
    elif isinstance(value, bool):
        if value:
            value = 'true'
        else:
            value = 'false'
    elif isinstance(value, unicode):
        pass
    elif isinstance(value, str):
        value = unicode(value, 'utf8')
    else:
        value = unicode(value)
    return value

def bool_to_python(self, value):
    """
    Convert a 'bool' field from solr's xml format to python and return it.
    """
    if value == 'true':
        return True
    elif value == 'false':
        return False

def str_to_python(self, value):
    """
    Convert an 'str' field from solr's xml format to python and return it.
    """
    return unicode(value)

def int_to_python(self, value):
    """
    Convert an 'int' field from solr's xml format to python and return it.
    """
    return int(value)

def date_to_python(self, value):
    """
    Convert a 'date' field from solr's xml format to python and return it.
    """
    # this throws away fractions of a second
    return datetime(*strptime(value[:-5], "%Y-%m-%dT%H:%M:%S")[0:6])

def double_to_python(self, value):
    """
    Convert a 'double' field from solr's xml format to python and
    return it.
    As Python does not have separate type for double, this is the same
    as float.
    """
    return self.float_to_python(value)

def float_to_python(self, value):
    """
    Convert a 'float' field from solr's xml format to python and return it.
    """
    return float(value)

# API Methods ############################################################
