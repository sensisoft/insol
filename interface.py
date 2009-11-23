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
 objects for query creeation
"""

class Searchable(object):
    """ 
    An interface that all fields handled by SOLR share. All DisplayFields implement
    these methods in addition to staticly indexed fields.

    Field parameters are class variables, define per class
    """
    
    multivalued = False
    required = False    # field required by the search app (show "what should i search for")
    boost = False
    field_name = None   # the application field_name, used as query parameters, may be different from the...
    solr_field = None   # SOLR schema name
    solr_query_param = 'q'  #default target for solr query, either q or fq.
                        #using fq allows better query result caching in solr, so params with commonly used values shoud go there
                        #good candidates are: advert_type, region, category, is_active

    orderable = False   # is it possible to order search results by it?

    def indexed_as(self):
        """ 
        Returns a dict to be added to indexed doc
        eg: return {self.field: self.src}
        
        Return an empty dictionary when nothing to index
        """
        return {}


    # A helper method for returning a single solr term according to the fields mandatory and boost settings
    # Can be used to join multivalue queries (right?)
    @classmethod
    def search_term(cls, key, value):
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
