#!/usr/bin/env python
# encoding: utf-8


"""

good one, this actually i like

exceptions.py

Created by michal.domanski on 2009-02-24.

"""

class SolrError(Exception):
    """
    generic solr error class
    """
class NoResultsFound(Exception):
    """
    raised when we have no results for query
    """

class SolrConnectionError(SolrError):
    """
    problem with connection
    """
class SolrTimeoutException(SolrError):
    """
    connection to server timeoud out
    """
class SolrQueryError(SolrError):
    """
    query is missing something, check your syntax 
    """
class SolrConfigError(SolrError):
    """
    raised when configuration is somehow wrong
    """
