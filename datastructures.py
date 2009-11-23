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
   
  
  
def _list(value):
    if isinstance(value, (list, tuple)):
        return value
    if isinstance(value, dict):
        return value.values()
    return [value]
    

class MVDict(dict):
    """

    .. warning:: 
        REIMPLEMENTED 
        
        Ported from django and customized for use in this API, if you want classic MVD,
        use django's
    
    
    """
    def __init__(self, key_to_list_mapping=()):
        super(MVDict, self).__init__(key_to_list_mapping)

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__,
                             super(MVDict, self).__repr__())

    def __getitem__(self, key):
        """
        MODIFIED
        
        if you contain list, return list
        
        Returns the last data value for this key, or [] if it's an empty list;
        raises KeyError if not found.
        """
        try:
            value = super(MVDict, self).__getitem__(key)
        except KeyError:
            raise KeyError, "Key %r not found in %r" % (key, self)
        try:
            return value
        except IndexError:
            return []

    def __setitem__(self, key, value):
        """
        MODIFIED
        
        nested list would create bugs
        
        """
        super(MVDict, self).__setitem__(key, _list(value))

    def __copy__(self):
        return self.__class__(super(MVDict, self).items())

    def __deepcopy__(self, memo=None):
        import copy
        if memo is None:
            memo = {}
        result = self.__class__()
        memo[id(self)] = result
        for key, value in dict.items(self):
            dict.__setitem__(result, copy.deepcopy(key, memo),
                             copy.deepcopy(value, memo))
        return result

    def get(self, key, default=None):
        """
        Returns the last data value for the passed key. If key doesn't exist
        or value is an empty list, then default is returned.
        """
        try:
            val = self[key]
        except KeyError:
            return default
        if val == []:
            return default
        return val


    def append_to(self, key, value):
        """Appends an item to the internal list associated with key."""
        self[key] = self.get(key,[]) + _list(value)

    def prepend_to(self, key, value):
        """Prepends an item to the internal list associated with key."""
        self[key] = _list(value) + self.get(key,[])
        
    def copy(self):
        """Returns a copy of this object."""
        return self.__deepcopy__()

    def update(self, *args, **kwargs):
        """
        update() extends rather than replaces existing key lists.
        Also accepts keyword args.
        """
        if len(args) > 1:
            raise TypeError, "update expected at most 1 arguments, got %d" % len(args)
        if args: # we have a dict passed :)
            other_dict = args[0]
            for key, value in other_dict.items():
                self[key] = self.get(key,[]).update(_list(value))
        for key, value in kwargs.iteritems():
            self.setlistdefault(key, []).append(value)

    
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
    
