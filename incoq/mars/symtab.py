"""Symbol tables."""


__all__ = [
    'N',
    'SymbolTable',
]


from incoq.util.collections import OrderedSet


class N:
    
    """Namespace for naming scheme helpers."""
    
    @classmethod
    def get_subnames(cls, prefix, num):
        """Return a list of num many fresh variable names that share
        a common prefix.
        """
        return [prefix + '_v' + str(i) for i in range(1, num + 1)]
    
    @classmethod
    def get_auxmap_name(cls, map, mask):
        return '{}_{}'.format(map, mask.m)
    
    @classmethod
    def get_maint_func_name(cls, inv, param, op):
        return '_maint_{}_for_{}_{}'.format(inv, param, op)


class SymbolTable:
    
    def __init__(self):
        self.rels = OrderedSet()
        """Names of relations in declaration order."""
        self.maps = OrderedSet()
        """Names of maps in declaration order."""
    
    def add_syminfo(self, syminfo):
        for sym, info in syminfo.items():
            if sym not in self.rels:
                raise L.ProgramError('No relation symbol "{}"'.format(sym))
