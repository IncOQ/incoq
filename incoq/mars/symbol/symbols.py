"""Symbols and their attributes."""


__all__ = [
    'Symbol',
    'TypedSymbolMixin',
    'RelationSymbol',
    'MapSymbol',
    'VarSymbol',
    'QuerySymbol',
]


from collections import OrderedDict
from simplestruct import Struct, Field

from incoq.mars.incast import L
from incoq.mars.type import T


class SymbolAttribute(Struct):
    
    name = Field()
    default = Field()
    docstring = Field()
    
    allowed_values = None
    """If not None, must be a sequence of enumerated allowed values."""
    
    def __get__(self, inst, owner):
        if inst is None:
            return self
        else:
            return getattr(inst, '_' + self.name, self.default)
    
    def __set__(self, inst, value):
        if self.allowed_values is not None:
            if value not in self.allowed_values:
                raise ValueError('Value for attribute {} must be one of: {}'
                                 .format(self.name,
                                         ', '.join(self.allowed_values)))
        setattr(inst, '_' + self.name, value)
    
    def defined(self, inst):
        return hasattr(inst, '_' + self.name)


class MetaSymbol(type):
    
    """Metaclass for symbols."""
    
    # Manage a _symbol_attrs field for programmatically dealing with
    # symbol attributes.
    
    @classmethod
    def __prepare__(mcls, name, bases):
        return OrderedDict()
    
    def __new__(mcls, clsname, bases, namespace):
        symbol_attrs = []
        for b in bases:
            if isinstance(b, MetaSymbol):
                symbol_attrs += b._symbol_attrs
        for sym_attr in namespace.values():
            if isinstance(sym_attr, SymbolAttribute):
                symbol_attrs.append(sym_attr)
        
        cls = super().__new__(mcls, clsname, bases, dict(namespace))
        cls._symbol_attrs = tuple(symbol_attrs)
        return cls


class Symbol(metaclass=MetaSymbol):
    
    name = SymbolAttribute('name', None,
            'Name of the symbol')
    
    def __init__(self, name, **kargs):
        self.update(name=name, **kargs)
    
    def update(self, **kargs):
        for name, value in kargs.items():
            if not isinstance(getattr(self.__class__, name, None),
                              SymbolAttribute):
                raise KeyError('Unknown symbol attribute "{}"'.format(name))
            setattr(self, name, value)
    
    def clone_attrs(self):
        """Return a dictionary of attributes for this symbol, not
        including name, suitable for passing to SymbolTable.define_*().
        """
        d = {}
        for attr in self._symbol_attrs:
            if attr.name == 'name':
                continue
            if attr.defined(self):
                d[attr.name] = getattr(self, attr.name)
        return d


class TypedSymbolMixin(Symbol):
    
    # Min/max type can be supplied as INFO inputs, but type
    # should not be.
    
    type = SymbolAttribute('type', T.Bottom,
            'Current annotated or inferred type of the symbol')
    
    min_type = SymbolAttribute('min_type', T.Bottom,
            'Initial minimum type before type inference; the type '
            'of input values for variables')
    
    max_type = SymbolAttribute('max_type', T.Top,
            'Maximum type after type inference; the type of output '
            'values for variables')
    
    def type_helper(self, t):
        return T.eval_typestr(t)
    
    parse_type = type_helper
    parse_min_type = type_helper
    parse_max_type = type_helper
    
    @property
    def decl_comment(self):
        return self.name + ' : ' + str(self.type)

TSM = TypedSymbolMixin


class RelationSymbol(TypedSymbolMixin, Symbol):
    
    counted = SymbolAttribute('counted', False,
            'Allow duplicates, associate a count with each element')
    
    type = TSM.type._replace(default=T.Set(T.Bottom))
    min_type = TSM.min_type._replace(default=T.Set(T.Bottom))
    max_type = TSM.max_type._replace(default=T.Set(T.Top))
    
    def __str__(self):
        s = 'Relation {}'.format(self.name)
        opts = []
        if self.type is not None:
            opts.append('type: {}'.format(self.type))
        if len(opts) > 0:
            s += ' (' + ', '.join(opts) + ')'
        return s
    
    @property
    def decl_constr(self):
        return 'CSet' if self.counted else 'Set'


class MapSymbol(TypedSymbolMixin, Symbol):
    
    type = TSM.type._replace(default=T.Map(T.Bottom, T.Bottom))
    min_type = TSM.min_type._replace(default=T.Map(T.Bottom, T.Bottom))
    max_type = TSM.max_type._replace(default=T.Map(T.Top, T.Top))
    
    def __str__(self):
        s = 'Map {}'.format(self.name)
        if self.type is not None:
            s += ' (type: {})'.format(self.type)
        return s
    
    decl_constr = 'Map'


class VarSymbol(TypedSymbolMixin, Symbol):
    
    def __str__(self):
        s = 'Var {}'.format(self.name)
        if self.type is not None:
            s += ' (type: {})'.format(self.type)
        return s


class QuerySymbol(TypedSymbolMixin, Symbol):
    
    node = SymbolAttribute('node', None,
            'Expression AST node corresponding to (all occurrences of) '
            'the query')
    
    params = SymbolAttribute('params', (),
            'Tuple of parameter identifiers for this query')
    
    impl = SymbolAttribute('impl', 'normal',
            'Implementation strategy, one of: normal, inc')
    impl.allowed_values = ['normal', 'inc']
    
    demand_set = SymbolAttribute('demand_set', None,
            'Name of demand set, or None if not used')
    demand_params = SymbolAttribute('demand_params', None,
            'Tuple of demand parameter identifiers, or None if not used')
    demand_param_strat = SymbolAttribute(
                         'demand_param_strat', 'unconstrained',
            'Strategy to use for determining demand parameters, one of: '
            'unconstrained, all, explicit')
    demand_param_strat.allowed_values = ['unconstrained', 'all',
                                         'explicit']
    
    def __str__(self):
        s = 'Query {}'.format(self.name)
        if self.node is not None:
            s += ' ({})'.format(L.Parser.ts(self.node))
        return s
    
    def make_node(self):
        """Return a Query node for this query symbol."""
        return L.Query(self.name, self.node)
