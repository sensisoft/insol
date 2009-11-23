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
Search tools

refactor in progress, don't commit to common until done

svns pre commit hook should stop me from commiting this file!
"""

from common.lib.search import config, connection
from common.lib.iterators import granulate


def index(add_iterable, remove_iterable, config_name = None ):
    """
    Takes config_name and data in a form of iterable object, selects apropiate config \n
    and indexes data. If error occurs, recuretly finds error source.     \n
    """

    if config_name : config.load_config(config_name)
    errors = []
    def recurently_do(operation, iterable, granulation=1):
        iterables = granulate(iterable, granulation)
        for iterable in iterables:
            response = operation(iterable)
            if not response.status==200:
                if len(iterable)==1:
                    if isinstance(iterable[0], dict) and iterable[0].has_key('id'):
                        errors.append(iterable[0]['id'])
                    else:
                        errors.append(iterable[0])
                else:
                    recurently_do(operation, iterable, granulation*10)
    # go go go
    recurently_do(connection.add, add_iterable)
    recurently_do(connection.delete_multi, remove_iterable)
    return errors






