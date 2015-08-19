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


symbol_kindmap = {
    'Set': RelationSymbol,
    'Map': MapSymbol,
}


class SymbolTable:
    
    def __init__(self):
        self.symbols = OrderedDict()
        """Global symbols, in declaration order."""
    
    def define_symbol(self, name, kind):
        """Define a new symbol of the given kind."""
        symcls = symbol_kindmap[kind]
        if name in self.symbols:
            raise L.ProgramError('Symbol "{}" already defined'.format(name))
        sym = symcls(name)
        self.symbols[name] = sym
    
    def define_relation(self, name):
        self.define_symbol(name, 'Set')
    
    def define_map(self, name):
        self.define_symbol(name, 'Map')
    
    def get_symbols(self, kind=None):
        """Return an OrderedSet of symbols of the requested kind.
        If kind is None, all symbols are returned.
        """
        result = OrderedDict(self.symbols)
        if kind is not None:
            symcls = symbol_kindmap[kind]
            for name, sym in self.symbols.items():
                if not isinstance(sym, symcls):
                    result.pop(name)
        return result
    
    def get_relations(self):
        return self.get_symbols('Set')
    
    def get_maps(self):
        return self.get_symbols('Map')
    
    def apply_syminfo(self, name, info):
        """Given a symbol name and a key-value dictionary of symbol
        properties, apply the properties.
        """
        if name not in self.symbols:
            raise L.ProgramError('No symbol "{}"'.format(name))
        sym = self.symbols[name]
        sym.unify(**info)
    
    def dump_symbols(self):
        """Return a string describing the defined global symbols."""
        entries = []
        for sym in self.symbols.values():
            entries.append(str(sym))
        return '\n'.join(entries)
