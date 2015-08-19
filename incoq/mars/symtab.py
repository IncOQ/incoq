"""Symbol tables."""


__all__ = [
    'N',
    
    'Symbol',
    'RelationSymbol',
    'MapSymbol',
    
    'SymbolTable',
]


from collections import OrderedDict

from incoq.util.collections import OrderedSet
from incoq.mars.incast import L


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


class Symbol:
    pass


class RelationSymbol(Symbol):
    
    def __init__(self, name):
        self.name = name
        self.arity = None
    
    def __str__(self):
        s = 'Relation {}'.format(self.name)
        if self.arity is not None:
            s += ' (arity: {})'.format(self.arity)
        return s
    
    def unify(self, **kargs):
        for k, v in kargs.items():
            method = getattr(self, 'unify_' + k)
            method(v)
    
    def unify_arity(self, new_arity):
        if self.arity is not None and self.arity != new_arity:
            raise L.ProgramError('Inconsistent arities for relation "{}": '
                                 '{}, {}'.format(self.name, self.arity,
                                                 new_arity))
        self.arity = new_arity


class MapSymbol(Symbol):
    
    def __init__(self, name):
        self.name = name
    
    def __str__(self):
        return 'Map {}'.format(self.name)


class SymbolTable:
    
    def __init__(self):
        self.rels = OrderedDict()
        """Names of relations in declaration order."""
        self.maps = OrderedSet()
        """Names of maps in declaration order."""
    
    def define_relation(self, name):
        """Create a relation with the given name."""
        if name in self.rels:
            raise L.ProgramError('Relation "{}" already defined'.format(name))
        sym = RelationSymbol(name)
        self.rels[name] = sym
    
    def define_map(self, name):
        """Create a map with the given name."""
        if name in self.maps:
            raise L.ProgramError('Map "{}" already defined'.format(name))
        sym = MapSymbol(name)
        self.maps.add(sym)
    
    def apply_syminfo(self, name, info):
        """Given a symbol name and a key-value dictionary of symbol
        properties, apply the properties.
        """
        if name not in self.rels:
            raise L.ProgramError('No symbol "{}"'.format(name))
        sym = self.rels[name]
        sym.unify(**info)
    
    def dump_symbols(self):
        """Return a string describing the defined global symbols."""
        entries = []
        for sym in self.rels.values():
            entries.append(str(sym))
        for sym in self.maps:
            entries.append(str(sym))
        return '\n'.join(entries)
