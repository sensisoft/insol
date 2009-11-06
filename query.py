#!/usr/bin/env python
# -*- coding: utf-8 -*-



"""

.. module:: query
   :platform: Unix, Windows, Linux
   :synopsis: Code for construction and handling of data send to solr
.. :moduleauthor: Maciej Dziardziel <maciej.dziardziel@sensisoft.com>
.. :moduleauthor: Michal Domanski <michal.domanski@sensisoft.com>

"""


from datastructures import CleverDict, py_to_solr
import config
import urllib


class Facet(CleverDict):
    """
    
    Class for handling faceting in pythonic way, yet with a somehow shameful biterness of java.
    Used only as an attribute of Query class instance.
    
    .. warning:: 
        Beware, this should only be used in conjuntion with Query class instance.
    

    """
    def __init__(self, *args, **kwargs):
        #if initial data exists then we parse it out and put it in the right fields
        # expects a list of tuples. Facets shouldn't be built directly, only of queries
        # Standard Fields
        self.field = []
        self.query = []
        CleverDict.__init__(self, *args, **kwargs)

    @property
    def _url(self):
        """
        descendant of clever dict, so it implements _url, yet I don't plan on using it
        """
        params = self.as_list()
        return urllib.urlencode(params)

class Stats(CleverDict):
    """
    
    Class for handling stats, just as Facet class instances
    
    .. warning:: 
        Beware, this should only be used in conjuntion with Query class instance.
    """
    def __init__(self, *args, **kwargs):
        #if initial data exists then we parse it out and put it in the right fields
        # expects a list of tuples. Facets shouldn't be built directly, only of queries
        # Standard Fields
        self.field = []
        self.query = []
        CleverDict.__init__(self, *args, **kwargs)

    @property
    def _url(self):
        """
        descendant of clever dict, so it implements _url, yet I don't plan on using it
        """
        params = self.as_list()
        return urllib.urlencode(params)

class Query(dict):
    """
    
    Every request to solr should be handled with Query type object whenever possible
    
    .. rubric:: Usage:

    Initialize using list of tuples:
    
    >>> q = Query([('q', 'lorem'), ('fl', 'model'), ('model', 'example__event')])

    or using a dict::

    >>> q = Query({'q' : 'lorem', 'fl' : 'model', 'model': 'test' })
  
    and you are good to go. Simply do::
    
    >>> import connection
    >>> response = connection.search(q) 
    
    Additionaly you can set up faceting::
    
    >>> q.facet.facet = True
    >>> q.facet.fields.append('regions_names')
    >>> response = connection.search(q)
    
    
    """

    def __init__(self, *args, **kwargs):
        self.clear()
        self._clean(*args, **kwargs)
        self._query_connector = ' AND '

    def clear(self):
        """
           Clear any changes to query
        """
        self.q = {}
        self.sort = []
        self.fq = {}
        self.fl = []
        self.start = 0
        self.rows = 20


    #So we can do url.url
    def __getattr__(self, name):
        return self[name]
    #So we can do url.url = '/'
    def __setattr__(self, name, value):
        self[name] = value

    def items(self):
        temp_list = []
        for key, value in  super(Query, self).items():
            if isinstance(value, CleverDict):
                temp_list.extend(value.items())
            elif isinstance(value, list):
                temp_list.append((key,value))
            else:
                temp_list.append(('%s' % key, py_to_solr(value)))
        return temp_list


    def as_list(self):
        return [(key, value) for key, value in self.items()]

    def _clean(self, *args, **kwargs):
        """        
        """
        params = []
        if args:
            first_arg = args[0] # one lookup, not three
            params = (isinstance(first_arg, dict) and list(first_arg.items())) or first_arg
        params.extend(kwargs.items())
        
        self.facet = Facet(dict(), instance='facet')
        self.stats = Stats(dict(), instance='stats')
        if not params:
            return 
            
        # for default faceting parameters, not used, but API can do that
        facet_params = hasattr(config, 'SEARCH_FACET_PARAMS') and config.SEARCH_FACET_PARAMS
        

        for key, value in params:
            if key.startswith('facet'):
                facet_params.append((key, value),)
            else:
                try:
                    v = self[key]
                    if isinstance(v, list):
                        self[key].append(value)
                    else:
                        self[key] = value
                except KeyError:
                    self.q.append('%s:%s' % (key, value))

        self.facet.update(facet_params)
        
    @property
    def _url(self):
        """
        returns url to which user should query, made with _ because it was designed for use with this 
        API, and is rather less than readable
        
        """
        params = []
        list_connector = ' AND '
        q = False
        for key, value in self.items():
            if not value or key.startswith('_'):
                continue
            if key == 'q':
                qparams =  ('q', self._query_connector.join([ qpart for qpart in self.q.values() if qpart]))
                if qparams[1]:
                    params.append(qparams)
                    q = True
            # tagging of separate query filters requires separate fq parameters
            # (not joining them with AND)
            # http://wiki.apache.org/solr/SimpleFacetParameters#head-f277d409b221b407d9c5430f552bf40ee6185c4c
            elif key == 'fq':
                for v in self.fq.values():
                    if isinstance(v, list):
                        for fq_part in v:
                            params.append(('fq',fq_part))
                    else:
                        params.append(('fq',v))
            elif key == 'sort':
                params.append( ('sort', ','.join(value)), )
            elif isinstance(value, list):
                params.append( (key, list_connector.join([x for x in value])), )
            else:
                params.append( (key, value), )

        if not q:
            params.append(('q','*:*'))


        query = urllib.urlencode(params)

        if hasattr(self, 'facet') and self.facet:
            query = '%s&%s' % (query, 'facet=true')

        if hasattr(self, 'stats') and self.stats:
            query = '%s&%s&%s' % (query, 'stats=on', self.stats._url)
            
        return query




