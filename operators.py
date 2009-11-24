from datastructures import Searchable, Query

def OR(*args):
    return Searchable(args, operator = "OR")

def AND(*args):
    return Searchable(args, operator = 'AND')
        
def NOT(searchable):
    return Searchable(searchable, operator='NOT')