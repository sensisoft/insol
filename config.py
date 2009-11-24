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

import exceptions
# from verticals import settings

SEARCH_FACET_PARAMS = ''
SEARCH_HL_PARAMS = ''
SOLR_ADDRESS = ''
SOLR_PORT = 0
SOLR_CORE = ''
SOLR_SELECT_PATH = 'select'
SOLR_UPDATE_PATH = 'update'
SOLR_PING_PATH = 'admin/ping'
DEFAULT_OPERATOR = 'OR'


CONFIGS = {}
SEARCH_PLUGINS = []


def get_configs():
    "return list of configs"
    return CONFIGS
    
def load_config(config_name):
    """
    loads config specified by name given and reload connnection
    """
    import connection
    global SOLR_PORT, SOLR_ADDRESS, SOLR_CORE
    config = CONFIGS[config_name]
    SOLR_CORE = config['core']
    SOLR_PORT = config['port']
    SOLR_ADDRESS = config['host']
    connection.reload_config()

def add_to_plugins(plugin):
    global SEARCH_PLUGINS
    SEARCH_PLUGINS.append(plugin)
        
def set_plugins(plugins):
    global SEARCH_PLUGINS
    SEARCH_PLUGINS = plugins

def set_config(config_name, host, port, core=''):
    """
    adds your config to global set of configs
    """
    global CONFIGS
    CONFIGS[config_name] = {'host': host, 'port': port, 'core': core}
        
def get_current_config():
    """
    return current config loaded data
    """
    global SOLR_ADDRES, SOLR_PORT, SOLR_CORE
    return {'host': SOLR_ADDRESS, 'port': SOLR_PORT, 'core': SOLR_CORE}


