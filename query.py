#!/usr/bin/env python
# -*- coding: utf-8 -*-



"""
Created by michal.domanski on 2009-02-24.

"""


from datastructures import CleverDict, py_to_solr
import config
import urllib
import copy

class SpecialTypeField(CleverDict):
    """
    
    class for handling faceting in pythonic way, yet with a somehow shameful biterness of java

    """
    def __init__(self, *args, **kwargs):
        #if initial data exists then we parse it out and put it in the right fields
        # expects a list of tuples. Facets shouldn't be built directly, only of queries
        # Standard Fields
        self.field = []
        self.queries = []
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

    Here's how to use it:

    using list of tuples
    
    >>> q = Query([('q', 'lorem'), ('fl', 'model'), ('model', 'example__event')])
    >>> q._url
    'rows=20&q=lorem+AND+model%3Aexample__event&start=0&fl=model'

    using a dict

    >>> q = Query({'q' : 'lorem', 'fl' : 'model', 'model': 'test' })
    >>> q._url
    'rows=20&q=lorem+AND+model%3Atest&start=0&fl=model'    
    
    setting up faceting
    
    >>> q.facet.facet = True
    >>> q.facet.fields.append('regions_names')
    >>> q.url
    'q=lorem+AND+model%3Atest&fl=model&facet=true&facet.field=regions_names'
    >>> import connection
    >>> connection.search(q)
    """
    list_connector = ' AND '
    
    def __init__(self, *args, **kwargs):
        self.q = {}
        self.sort = {}
        self.fq = {}
        self.fl = []
        self.start = 0
        self.rows = 20
        self.clean(*args, **kwargs)
        
    

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
            elif isinstance(value, (list, dict)):
                temp_list.append((key,value))
            else:
                temp_list.append(('%s' % key, py_to_solr(value)))
        return temp_list

        
    def _copy(self):
        return copy.deepcopy(self)
            
    def filter(self, **kwargs):
        copied = self._copy()
        copied.fq.update(kwargs)
        return copied
        
    def as_list(self):
        return [(key, value) for key, value in self.items()]

    def clean(self, *args, **kwargs):
        """
        
        
        Expects a list of tuples like:
        [('q', 'model'), ('sort', 'date desc'), ('facet.field', 'model')]
        
        """
        params = []
        if args:
            first_arg = args[0] # one lookup, not three
            params = (isinstance(first_arg, dict) and list(first_arg.items())) or first_arg
        params.extend(kwargs.items())
        
        self.facet = SpecialTypeField(dict(), instance='facet')
        self.stats = SpecialTypeField(dict(), instance='stats')
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

        q = False
        for key, value in self.items():
            if not value:
                continue
            if isinstance(value, dict):
                params.append((key, self.list_connector.join(['%s:%s' % elem for elem in value.iteritems()])))
            elif isinstance(value, list):
                params.append( (key, self.list_connector.join(['%s' % x for x in value])), )
            elif key == 'sort':
                params.append( ('sort', ','.join(value)), )
            else:
                params.append( (key, value), )

        query = urllib.urlencode(params)

        if hasattr(self, 'facet') and self.facet:
            query = '%s&%s' % (query, 'facet=true')

        if hasattr(self, 'stats') and self.stats:
            query = '%s&%s' % (query, 'stats=true')

            
        return query



    




