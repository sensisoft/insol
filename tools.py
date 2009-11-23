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

import config, connection

def iterblocks(iterable, size, **kwds):
    """
    
    http://code.activestate.com/recipes/542194/
    
    Splits given iterable object into a set of objects, each with size given by the size variable, \n
    also takes blocktype keyword argument for description of type of objects to be returned, \n
    can truncate and pad if number of objects in iterable isn't splitable ideally
    
    """
    truncate = kwds.get('truncate',False)
    blocktype = kwds.get('blocktype',tuple)
    if truncate and 'pad' in kwds:
        raise ValueError("'truncate' must be false if 'pad' is given")
    iterator = iter(iterable)
    while True:
        block = blocktype(islice(iterator,size))
        if not block:
            break
        if len(block) < size:
            if 'pad' in kwds:
                block = blocktype(chain(block, repeat(kwds['pad'], size-len(block))))
            elif truncate:
                break
        yield block

def granulate(elems, granulation = 10):
    """
    Performs granulation on a given list, splits it into smaller lists, \n
    granulation param sets defines the amount of returned elems.
    """
    elems_len = float(len(elems))
    package_len = ceil(elems_len / granulation)
    return iterblocks(elems, package_len, blocktype = list)


def filter_even(iterable):
    """
    Filters even indexed objects from given iterable, returns iterator
    """
    return imap(lambda i: iterable[i],filter(lambda i: i%2 == 0,range(len(iterable))))

def filter_odd(iterable):
    """
    Filter odd indexed objects from iterable, returns iterator
    """
    return imap(lambda i: iterable[i],filter(lambda i: i%2 == 1,range(len(iterable))))




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






