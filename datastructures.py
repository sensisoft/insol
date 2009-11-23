#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

"""
Datastructures for new solr api

Created by michal.domanski on 2009-02-24.

"""




from datetime import date, datetime
from converters import py_to_solr


class ResultDict(dict):
    
    def __init__(self, data = {}):
        self.update(data)

    def __getattr__(self, name):
        return self[name]
    def __setattr__(self, name, value):
        self[name] = value    
    def __nonzero__(self):
        if self.items():
            return True
        return False
        
        
class CleverDict(ResultDict):
    """
    Used for Facet, Query and Highlight
    
    based on :
    
    http://haystacksearch.org/
    
    
    """

    def __init__(self, *args, **kwargs):
        dict.__setattr__(self, '_name', kwargs.pop('instance', self.__class__.__name__.lower()))
        self._clean(*args)
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

    def _clean(self, *args):
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
    
class Partial(object):
    """
    partial1=Partial(field_name='a', field_value=1)
    partial2=Partial(field_name='b', field_value=2)
    OR(AND(partial1, partial2), NOT(partial2)).parsed
    
    """
    def __init__(self, *args, **kwargs):
        self._field_name = kwargs.get('field_name', None)
        self._field_value = kwargs.get('field_value', None)
        self._parsed_val = kwargs.get('parsed_val', None)

    @property
    def parsed(self):
        if not self._parsed_val:
            self._parsed_val = '%s:%s' % (self._field_name, self._field_value)
        return self._parsed_val
        
def OR(*args):
    return Partial(parsed_val='(%s)' % ' OR '.join(map(lambda elem:elem.parsed, args)))

def AND(*args):
    return Partial(parsed_val='(%s)' % ' AND '.join(map(lambda elem:elem.parsed, args)))
        
def NOT(partial):
    return Partial(parsed_val='NOT %s' % partial.parsed)
    
