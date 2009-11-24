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

.. module:: datastructures
   :platform: Unix, Windows, Linux
   :synopsis: Code for easy data managment
.. :moduleauthor: Michal Domanski <michal.domanski@sensisoft.com>


"""




from datetime import date, datetime
from converters import py_to_solr
from config import DEFAULT_OPERATOR


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

class Searchable(object):
    """ 
    Field parameters are class variables, define per class
    """

    multivalued = False
    required = False    # field required by the search app (show "what should i search for")
    boost = False
    field_name = None   # the application field_name, used as query parameters, may be different from the...
    solr_query_field = None   # SOLR schema name
    solr_index_field = None
    solr_query_param = 'q'  #default target for solr query, either q or fq.
                        #using fq allows better query result caching in solr, so params with commonly used values shoud go there
                        #good candidates are: advert_type, region, category, is_active

    orderable = False   # is it possible to order search results by it?
    _parsed_search_term = None


    def __init__(self, *searchables, **kwargs):
        self.operator = kwargs.get('operator', DEFAULT_OPERATOR )
        if isinstance(searchables[0], Searchable):# we are inside more complicated query
            self._parsed_search_term = operator.join([term for term in searchable.parsed_search_term])
        else:# we are simple creating one object
            self.value = searchables[0]
            assert solr_query_field is not None

    # A helper method for returning a single solr term according to the fields mandatory and boost settings
    # Can be used to join multivalue queries (right?)
    @property
    def parsed_search_term(self):
        if not self._parsed_search_term:
            self._parsed_search_term = self.__class__.search_term(self.solr_query_field, self.value)
        return self._parsed_search_term
        
    @classmethod
    def search_term(cls, key, value):
        """ 
        Default search term for signle value lookup
        """
        temp = []
        temp.append('(')
        temp.append(str(key))
        temp.append(':')
        temp.append(py_to_solr(value))
        if cls.boost:
            temp.append('^%s'%str(cls.boost))
        temp.append(')')
        return ''.join(temp)
    
