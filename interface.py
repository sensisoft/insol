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

"""


from django.utils.html import escape
from urllib import urlencode
from django.utils.datastructures import MultiValueDict

EMPTYLIST = ['']

class Searchable(object):
    """ 
    An interface that all fields handled by SOLR share. All DisplayFields implement
    these methods in addition to staticly indexed fields.

    Field parameters are class variables, define per class
    """
    OPERATORS = {
        'PLUS':'+',
        'MINUS':'-',
        'AND': ' AND ',
        'OR': ' OR ',
        'NOT': ' NOT ',
        }    
    
    multivalued = False
    required = False    # field required by the search app (show "what should i search for")
    boost = False
    field_name = None   # the application field_name, used as query parameters, may be different from the...
    solr_field = None   # SOLR schema name
    solr_query_param = 'q'  #default target for solr query, either q or fq.
                        #using fq allows better query result caching in solr, so params with commonly used values shoud go there
                        #good candidates are: advert_type, region, category, is_active
    path_order = 100    # used to determine position when constructing a seo friendly path
    sort_order = 100    # sort sort orders when more then one sort_term is returned by searchables
    
    orderable = False   # is it possible to order search results by it?
    operator = OPERATORS['OR'] # default multivalued join operator should be OR

    def __init__(self, *args, **kwargs):
        """ 
        Searchables are initialized with an all_values keyword parameter or an advert
        kw parameter (when indexing).
        Displayfields can use this __init__ func to fetch their src from the datadict.
        
        """
        op = kwargs.get('operator') # override multivalued join default (OR)
        if op: self.operator = op
        self.object = kwargs.get('object') # MVD returns None on keyerrors
        self.all_values = kwargs.get('all_values', MultiValueDict())
        self.other_searchables = kwargs.get('searchables')
        self.src = None
        self.value = None
        self.src_sort = None
        self.info_messages = []  #list of messages that should be displayed. See verticals.webapps.pennysaver.customfields for example
                                 #when displayed, this list will be cleared

        if self.field_name is not None:
            # some indexing searchables don't define it at all
            sorting = self.all_values.get('sort_method', '')
            if sorting.startswith(self.field_name):
                if sorting.endswith('asc'): self.src_sort = 1
                elif sorting.endswith('desc'): self.src_sort = -1

        if self.all_values is not None and self.field_name in self.all_values:
            self.src = self.pre_process_src(self.src)
            if self.multivalued:
                try:
                    src = self.all_values.getlist(self.field_name)
                    if src!=EMPTYLIST: self.src = src # not interested in ['']
                except AttributeError: # if it's only a dict, still supply a list to fields that expect to see a list
                    src = self.all_values.get(self.field_name)
                    src = self.pre_process_src(src)
                    if src: 
                        if not isinstance(src,list):                            
                            self.src = [src] # we eliminate [''] values!
                        else:
                            self.src = src
            else: 
                self.src = self.all_values.get(self.field_name)

    def search_term(self, query=None):
        """ 
        The solr term which will be appended to the query.
        eg: return self.term % self.src (for a standard displayfield)
        
        The optional value parameter enables fulltext search in admin, where we query
        all searchables for the given query
        """
        if query is None: query = self.src
        if query:
            if type(query) is list and len(query)>0:                    
                return '(%s)' % self.operator.join([self.single_term(self.solr_field, s) for s in query])
            else:
                return self.single_term(self.solr_field, query)
        return None


    def prepare_faceting(self, sensisearch_obj):
        """
        Take sensisearch_obj and set facet params using new solr api (see query.py for details and example)
        """
        self._facets = []
        if not (sensisearch_obj.params['use_faceting'] and self.clusterable):
            return
        sensisearch_obj._query.facet.field.append(self.solr_field)


    def parse_faceting(self, sensisearch_obj):
        """
        Get facets from search
        """
        self._facets = []
        if self.solr_field in sensisearch_obj.results.facets['facet_fields']:
            facets = sensisearch_obj.results.get_facet_as_dict(self.solr_field)
            for f in facets:
                self._facets.append( {'src':f, 'label': f, 'count':facets[f], 'url': '%s=%s' % (self.field_name,f) } )
        if sensisearch_obj.results.facets['facet_queries']:
            for key in sensisearch_obj.results.facets['facet_queries']:
                if key.startswith(self.solr_field+':'):
                    self._facets.append( {'src': key, 'label':key, 'count': sensisearch_obj.results.facets['facet_queries'][key]} )
        self._full_facets = self._facets

    def sort_term(self):
        """
        Sorting term for solr generated by this searchable
        return list of tuples (sort_order, sort_term), ie. [ (50, 'score desc'), (100, 'price asc') ]
        """
        if self.src_sort is None: return []
        elif self.src_sort>0: return [(self.sort_order, "%s asc" % self.solr_field)]
        else: return [ (self.sort_order, "%s desc" % self.solr_field) ]

    def indexed_as(self):
        """ 
        Returns a dict to be added to indexed doc
        eg: return {self.field: self.src}
        
        Return an empty dictionary when nothing to index
        """
        return self.src is not None and {self.solr_field: self.src} or {}

    # A helper method for returning a single solr term according to the fields mandatory and boost settings
    # Can be used to join multivalue queries (right?)
    @classmethod
    def single_term(cls, key, value):
        """ 
        Default search term for signle value lookup
        """
        temp = []
        temp.append('(')
        temp.append(str(key))
        temp.append(':')
        temp.append(str(value))
        if cls.boost:
            temp.append('^%s'%str(cls.boost))
        temp.append(')')
        return ''.join(temp)

    def __repr__(self):
        return '%s=%s' % (self.field_name, repr(self.value))
