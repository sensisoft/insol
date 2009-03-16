#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
Datastructures for new solr api

Created by michal.domanski on 2009-02-24.

"""
try:
    from django.conf import settings
except ImportError:
    pass

SEARCH_FACET_PARAMS = ''
SEARCH_HL_PARAMS = ''

SOLR_ADDRESS = 'localhost'
SOLR_PORT = 8983
SOLR_SELECT_PATH = 'select'