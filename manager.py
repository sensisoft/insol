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

import config
import pprint

"""

.. module:: manager
   :platform: Unix, Windows, Linux
   :synopsis: Code for managing indexing and searching data converters
.. :moduleauthor: Michal Domanski <michal.domanski@sensisoft.com>

"""

class Manager(object):
    """

    Generic object for managing Searchables/Indexables module loading    \n
    
    .. rubric:: Usage:
    
    >>> from models import Advert
    >>> ad = Advert.objects.filter(title__icontains='test')[:1][0]
    >>> doc = Manager(model_name=ad.__class__.__name__.lower()).init_from(ad)
    
    
    """
    
    def __init__(self, *args, **kwargs):
        self.model_name = kwargs.get('model_name')
        self._searchables = []
        self._indexables = []
    
    
    @property
    def searchables(self):
        """
        List of modules that are initialized from object for searching using solr.
        
        """
        
        if not self._searchables:
            self._load_searchables()
        return self._searchables
        
    @property
    def indexables(self):
        """
        List of modules that are initialized from object for indexing data into solr.
        """
        
        if not self._indexables:
            self._load_indexables()
        return self._indexables
    
    def _load_modules(self):
        """
        Loads all modules defined in config.SEARCH_PLUGINS into local attribute
        """
        
        self._modules = [__import__(module_name, None, None, ['']) for module_name in config.SEARCH_PLUGINS]
        
    def _load_ables(self, attr_name, ables):
        if not self._modules: self._load_modules()        
        for module in self._modules:
            loaded_ables = getattr(module, attr_name, dict())
            if loaded_ables:
                for able, mapping in loaded_ables.iteritems():
                    if self.model_name in mapping and not able in ables:
                        ables.append(able)
        
        
    def _load_searchables(self):
        """
        using modules loaded, performs the searching and loading of searchable for given model
        """
        if not hasattr(self,'_modules'): self._load_modules()        
        self._load_ables("SEARCHABLES", self._searchables)
                        
    def _load_indexables(self):
        """
        using modules loaded, performs the searching and loading of indexables for given model
        """
        
        if not hasattr(self,'_modules'): self._load_modules()
        self._load_ables("INDEXABLES", self._indexables)
        
    def _show_loaded_modules(self):
        self._load_modules()
        pprint.pprint(self._modules)
        
    def init_from(self, object):
        """
        Only method of manager instance that should be actually used.
        
        .. warning::
            You need to write indexables and searchables and configure them for object you want to index. 
            Check :mod:`interface` for reference on this.
        
        :param object: object that represents data you want to index
        :type object: any object that can be used to initialize indexables configured for it
        
        """
        data = dict()

        indexables = [i(object = object) for i in self.indexables]
        for indexable in indexables:
            data.update(indexable.indexed_as())
        return data
        
    
