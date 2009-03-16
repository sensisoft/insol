#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
Simple set of extensible objects for easy handling of data returned from solr

Created by michal.domanski on 2009-02-24.

"""


class Response:
    
    @property
    def time(self):
        return self._header['QTime']
    @property
    def status(self):
        return self._header['status']
    @property
    def params(self):
        return self._header['params']
        
class SelectResponse(Response):
    
    @property
    def docs(self):
        return self._response['docs']
    @property
    def hits(self):
        return self._response['numFound']
    @property
    def facets(self):
        return self._facets