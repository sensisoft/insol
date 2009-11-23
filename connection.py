#!/usr/bin/env python
# encoding: utf-8

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

.. module:: connection
   :platform: Unix, Windows, Linux
   :synopsis: Code for handling of python to solr communication
.. :moduleauthor: Maciej Dziardziel <maciej.dziardziel@sensisoft.com>
.. :moduleauthor: Michal Domanski <michal.domanski@sensisoft.com>

"""

import httplib
import os.path
import socket
import urlparse

from urllib2 import urlopen, URLError

import exceptions
import config
from results import SelectResponse
from converters import msg_from_iterable

try:
    import simplejson
except ImportError:
    raise ImportError, 'insol depends on simplejson module but it was not found'
    


def reload_config():
    import config as new_config
    global config
    config = new_config

def _get_solr_url():
    current_config = config.get_current_config()
    return urlparse.urlunparse(['http', '%s:%s' % (current_config['host'], current_config['port']),
        os.path.join('solr', current_config['core'], ''), '', '', ''])

def _get_solr_select_url():
    """
    return solr url based on config in app_settings
    """
    return '%s%s/' % (_get_solr_url(), config.SOLR_SELECT_PATH)

def _get_solr_ping_url():
    
    return '%s%s/' % (_get_solr_url(), config.SOLR_PING_PATH)

def _get_solr_update_url():

    return '%s%s/' % (_get_solr_url(), config.SOLR_UPDATE_PATH)
    

def _send_query(query, **kwargs):
    """
    default function for sending query to solr
    """
    solr_url = kwargs.get('solr_url', _get_solr_select_url())
    url = '%s?%s' % (solr_url, query)
    try:
        return urlopen(url)
    except URLError, exc:
        raise exceptions.SolrConnectionError(exc)


def _handle_connection(connection, **kwargs):
    """
    default connection handler, expects and object
    with .read method and performs decoding on it,
    extra parameter decoder for overload of default one
    """
    decoder = kwargs.get('decoder', simplejson.loads)
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
    carrier._stats = data.get('stats') 
    return carrier

def _update(data):
    connection = httplib.HTTPConnection(config.SOLR_ADDRESS, config.SOLR_PORT)
    connection.request('POST', _get_solr_update_url(), data, headers={'Content-type': 'text/xml'})
    try:
        response = connection.getresponse()
    except httplib.HTTPException, e:
        raise exceptions.SolrConnectionError(e.message)
    except socket.timeout, e:
        raise exceptions.SolrConnectionTimeout(e.message)
    return response



def add(elems):
    """
    Add data to solr index.

    :param elems: data for solr to add to index
    :type elems: iterable
    :return: response to sent data
    :rtype: HTTPResponse
    
    """
    if not isinstance(elems, (tuple, list)):
        elems = [elems]
    return _update(msg_from_iterable(elems))  
                        

def commit(wait_flush = False, wait_searcher = False):
    """
    Send 'commit' message to solr. If not used, your changes will not be visible.
    
    :param wait_flush: not clear, i suppose this makes connection wait for searcher flush
    :param wait_searcher: wait for creation of new searcher, guarantees you get updated data when searching
    :type wait_flush: bool
    :type wait_searcher: bool

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
    Send 'optimize' command to solr. Rebuilds and optimizes solr index.
    
    :param wait_flush: not clear, need to be updated
    :type wait_flush: bool
    
    
    .. warning::
        This operation is generates extra load on solr server and may render server unresponsive in extreme situations.
    
    
    """
    wait_flush_cmd = 'waitFlush="false"'
    if  wait_flush:
        wait_flush_cmd = 'waitFlush="true"'
    cmd = '<optimize %s />' % (wait_flush_cmd,)
    return _update(cmd)

def is_alive():
    """
    Check if solr responds.
    
    """
    
    connection = httplib.HTTPConnection(config.SOLR_ADDRESS, config.SOLR_PORT)
    connection.request('GET', _get_solr_ping_url())
    try:
        response = connection.getresponse()
    except httplib.HTTPException, e:
        return False
    except socket.timeout, e:
        return False
    return (response.status==200)

def delete(**kwargs):
    """
    Remove data from solr. Need to be reworked to accept query param.
    
    :param id: id of document to remove
    :type id: int
    
    
    """
    if 'id' in kwargs:
        xml = '<delete><id>%s</id></delete>' % kwargs['id']
    return _update(xml)

def delete_multi(doc_ids, field_name='id'):
    """
    Deletes multiple documents at once.
    
    :param doc_ids: list of document ids to removed from solr index
    :type doc_ids: iterable
    :param field_name: field to be used as the parameter for removal
    :type field_name: str
    
    """
    xml = '\n'.join('<delete><%(field_name)s>%(doc_id)s</%(field_name)s></delete>' % {'field_name':field_name, 'doc_id':doc_id } for doc_id in doc_ids)
    return _update(xml)

def search(query, **kwargs):
    """
    Main interest for most of users of this module, expects a query object, 
    can take extra arguments to override default behaviour
  
  
    :param query: main and only required object, carries data for searching in solr
    :type query: :mod:`query`
    :param send_query: optional handler for sending data
    :type send_query: callable
    :param handle_connection: optional handler for handling connection with solr
    :type handle_connection: callable
    :param build_response: handler for building response object from received data
    :type build_response: callable
    

    
    .. rubric:: Usage:
    
    1.default::
    
    >>> connection.search(query)
    
    2.debugging::
    
    >>> def debug_send_query(query):
    >>>     print locals()
    >>>     return connection._send_query(query)
    >>> connection.search(query, send_query = debug_send_query)
    
    This of course is only a simple demo.
    
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

            
def search_multicore(core_config_name, query):
    config.load_config(core_config_name)
    return search(query)
            
            
            
            
            
            
            
            
            
            
        
        
        
    
    
    
    
    
