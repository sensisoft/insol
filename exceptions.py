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
