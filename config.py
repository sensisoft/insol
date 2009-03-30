#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
Datastructures for new solr api

Created by michal.domanski on 2009-02-24.

"""

import exceptions


SEARCH_FACET_PARAMS = ''
SEARCH_HL_PARAMS = ''
SOLR_ADDRESS = ''
SOLR_PORT = 0
SOLR_SELECT_PATH = 'select'

CONFIGS = {
    'dev': {
        'host':'localhost',
        'port':8983,
    }
}

def get_configs():
    return CONFIGS
    
def load_config(config_name):
    import connection
    global SOLR_PORT, SOLR_ADDRESS
    try:
        config = CONFIGS[config_name]
        SOLR_PORT = config['port']
        SOLR_ADDRESS = config['host']
        connection.reload_config()
    except KeyError:
        raise exceptions.SolrConfigError, 'no such config'

def set_config(config_name, host, port):
    global CONFIGS
    CONFIGS[config_name] = { 'host': host, 'port': port }
    
def get_current_config():
    global SOLR_ADDRES, SOLR_PORT
    return {'host': SOLR_ADDRESS, 'port': SOLR_PORT}