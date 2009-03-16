#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Datastructures for new solr api

Created by michal.domanski on 2009-02-24.

"""


__revision__ = '$Id: datastructures.py 30476 2009-03-02 10:35:23Z michal.domanski $'


from datetime import date, datetime
from converters import py_to_solr


class ResultDict(dict):
    
    def __init__(self, data = {}):
        self.update(data)

    def __getattr__(self, name):
        return self[name]
    #So we can do url.url = '/'
    def __setattr__(self, name, value):
        self[name] = value
    
    def __nonzero__(self):
        if self.items():
            return True
        return False
        
        
class CleverDict(ResultDict):
    """
    Used for Facet, Query and Highlight
    """

    def __init__(self, *args, **kwargs):
        dict.__setattr__(self, '_name', kwargs.pop('instance', self.__class__.__name__.lower()))
        self.clean(*args)
        dict.__init__(self, **kwargs)

    def items(self):
        temp_list = []
        for key, value in  super(CleverDict, self).items():
            if isinstance(value, CleverDict):
                temp_list.extend([('%s.%s' % (self._name, k), py_to_solr(v)) for k, v in value.items() if v])
            elif isinstance(value, list):
                temp_list.extend([('%s.%s' % (self._name, key), py_to_solr(v)) for v in value])
            else:
                temp_list.append(('%s.%s' % (self._name, key), py_to_solr(value)))
        return temp_list


    def as_list(self):
        return [(key, value) for key, value in self.items()]

    def clean(self, *args):
        """
        Expects a list of tuples like:
        [('facet.field', 'model'), (facet.limit, 10)]
        """
        if not args or not isinstance(args[0], list):
            return None
        for key, value in  args[0]:
            if key.startswith(self._name):
                bits = key.split('.')
                if len(bits) is 1:
                    # something like ('facet', True)
                    continue
                try:
                    v = self[bits[1]]
                    if isinstance(v, list):
                        self[bits[1]].append(value)
                    elif isinstance(v, CleverDict):
                        self[bits[1]][bits[2]] = value
                    else:
                        self[bits[1]] = value
                except KeyError:
                    #Doesn't exist yet.
                    self[bits[1]] = value
                    

    
