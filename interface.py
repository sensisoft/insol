class Searchable:
    """
    use like
    class Test(Searchable):
        def __init__(self, *args, **kwargs):
            self.some_field = args[0]
            Searchable.__init__(self, field='test_field_in_solr', multiValue = False)
        
        def search_term(self):
            data = self.some_field.strip()
            return self.term % (data, )
    
    """
    
    
    def __init__(self, *args, **kwargs):
        self.field = kwargs.get('field')
        self.multiValue = kwargs.get('multiValue', False)
        self.mandatory = kwargs.get('mandatory', False)
        self.has_boost = 'boost' in kwargs
        self.boost = kwargs.get('boost')
        
            
    @property
    def term(self):
        """
        most default behaviour, override if needed
        """
        temp = []
        if self.mandatory: temp.append('+')
        temp.append('(')
        temp.append(str(self.field))
        temp.append(':')
        temp.append('%s')
        if self.has_boost:
            temp.append('^%s')
        temp.append(')')
        return ''.join(temp)
                
    def search_term(self):
        raise NotImplementedError, 'this has to be specificaly defined'
    
        