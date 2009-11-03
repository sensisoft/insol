#!/usr/bin/env python
# -*- coding: utf-8 -*-
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






