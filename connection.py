#!/usr/bin/env python
# encoding: utf-8
"""
connection.py

A simple and elegant, yet powerful API for usage with Solr Search Engine


Created by michal.domanski on 2009-02-24.
"""

import config
from results import SelectResponse
import exceptions
from urllib2 import urlopen, URLError  

try:
    from simplejson import loads as decode
except ImportError:
    raise ImportError, 'insol depends on simplejson module but it was not found'


def reload_config():
    import config as new_config
    global config
    config = new_config

def _get_solr_select_url():
    """
    return solr url based on config in app_settings
    """
    return 'http://%s:%s/solr/%s/' % (config.SOLR_ADDRESS, config.SOLR_PORT, config.SOLR_SELECT_PATH)

def _send_query(query, **kwargs):
    """
    default function for sending query to solr
    """
    solr_url = kwargs.get('solr_url', _get_solr_select_url())
    url = '%s?%s' % (solr_url, query)
    return urlopen(url)

def _handle_connection(connection, **kwargs):
    """
    default connection handler, expects and object
    with .read method and performs decoding on it,
    extra parameter decoder for overload of default one
    """
    decoder = kwargs.get('decoder', decode)
    return decoder(connection.read())

def _build_response(data, **kwargs):
    """
    takes a response object and loads it with data from Solr
    then returns it to user , have fun :)
    """
    carrier = kwargs.get('carrier', SelectResponse)()
    carrier._header = data['responseHeader']
    carrier._response = data.get('response')
    carrier._facets = data.get('facet_counts') 
    return carrier


def search(query, **kwargs):
    """
    main interest for most of users of this module, expects a query object, 
    can take extra arguments to override default behaviour
    
    e.g.:
    
    default:
        connection.search(query)
    
    debugging:
        def debug_send_query(query):
            print locals()
            return connection._send_query(query)
        connection.search(query, send_query = debug_send_query)
    this of course is only a simple demo
    
    """
    handlers = {
        'send_query': _send_query, 
        'handle_connection': _handle_connection, 
        'build_response': _build_response, 
    }
    handlers.update(kwargs)
    
    if not 'wt' in query: query.wt = kwargs.get('wt','json')
    if not hasattr(query, '_url'):
        raise exceptions.SolrQueryError, 'no _url attribute on your query object'
        
    connection = handlers['send_query'](query._url)
    data = handlers['handle_connection'](connection)
    response = handlers['build_response'](data)
    return response

                        
def _update(data):
    connection = httplib.HTTPConnection(config.SOLR_ADDRESS, config.SOLR_PORT)
    connection.request('POST', _get_solr_update_url(), data, headers={'Content-type': 'text/xml'})
    return connection.getresponse()        
            
            
def commit(wait_flush = False, wait_searcher = False):
    """
        commit changes
    """
    wait_flush_cmd = 'waitFlush="false"'
    wait_searcher_cmd = 'waitSearcher="false"'
    if  wait_flush:
        wait_flush_cmd = 'waitFlush="true"'
    if wait_searcher:
        wait_searcher_cmd = 'waitSearcher="true"'
    cmd = '<commit %s %s />' % (wait_flush_cmd, wait_searcher_cmd)
    return _update(cmd)

def optimize(wait_flush = False):
    """
        optimize index
    """
    wait_flush_cmd = 'waitFlush="false"'
    if  wait_flush:
        wait_flush_cmd = 'waitFlush="true"'
    cmd = '<optimize %s />' % (wait_flush_cmd,)
    return _update(cmd)          
            
            
def delete(**kwargs):
    if 'id' in kwargs:
        xml = '<delete><id>%s</id></delete>' % kwargs['id']
    return _update(xml)        
            
            
            
        
        
        
    
    
    
    
    
