"""Symbols and their attributes."""


__all__ = [
    'SymbolAttribute',
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
    
    """Descriptor for a symbol attribute."""
    
    name = Field()
    """Name of attribute."""
    default = Field()
    """Default value. The owner class or instance may override this with
    a new default by defining an attribute named default_<name>.
    """
    docstring = Field()
    """User documentation."""
    allowed_values = Field(default=None)
    """If not None, sequence of enumerated allowed values."""
    parser = Field(default=None)
    """If not None, a callable that takes a literal value (e.g. a
    string supplied by the user) to a value for this attribute.
    """
    
    def __get__(self, inst, owner):
        if inst is None:
            return self
        
        # Determine default.
        default = getattr(inst, 'default_' + self.name, None)
        if default is None:
            default = self.default
        # Return value or default.
        return getattr(inst, '_' + self.name, default)
    
    def __set__(self, inst, value):
        # Check if the value is allowable.
        if self.allowed_values is not None:
            if value not in self.allowed_values:
                vals = ', '.join(str(v) for v in self.allowed_values)
                raise ValueError('Value for attribute {} must be one of: {}'
                                 .format(self.name, vals))
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
        # Determine base classes' symbol attributes.
        symbol_attrs = []
        for b in bases:
            if isinstance(b, MetaSymbol):
                symbol_attrs += b._symbol_attrs
        # Add new ones for this class.
        for key, sym_attr in namespace.items():
            if isinstance(sym_attr, SymbolAttribute):
                assert key == sym_attr.name
                symbol_attrs.append(sym_attr)
        
        cls = super().__new__(mcls, clsname, bases, dict(namespace))
        cls._symbol_attrs = tuple(symbol_attrs)
        return cls


class Symbol(metaclass=MetaSymbol):
    
    """Base class for symbols."""
    
    def __init__(self, name, **kargs):
        self.name = name
        self.update(**kargs)
    
    def update(self, **kargs):
        """Assign to each symbol attribute as specified in keyword
        arguments.
        """
        for attr, value in kargs.items():
            if not isinstance(getattr(self.__class__, attr, None),
                              SymbolAttribute):
                raise KeyError('Unknown symbol attribute "{}"'.format(attr))
            setattr(self, attr, value)
    
    def parse_and_update(self, **kargs):
        """Like update(), but run the values through the symbol
        attributes' parser functions if present.
        """
        for attr, value in kargs.items():
            desc = getattr(self.__class__, attr, None)
            if not isinstance(desc, SymbolAttribute):
                raise KeyError('Unknown symbol attribute "{}"'.format(attr))
            if desc.parser is not None:
                value = desc.parser(value)
            setattr(self, attr, value)
    
    def clone_attrs(self):
        """Return a dictionary of symbol attributes having non-default
        values on this instance.
        """
        return {desc.name: getattr(self, desc.name)
                for desc in self._symbol_attrs
                if desc.defined(self)}


class TypedSymbolMixin(Symbol):
    
    """Mixin for typed symbols."""
    
    min_type = T.Bottom
    """Minimum allowable type for this symbol; the initial type for
    non-input variables prior to type inference.
    """
    max_type = T.Top
    """Maximum allowable type for this symbol; the initial type for
    input variables in the absence of other constraining information.
    """
    
    type = SymbolAttribute('type', None,
            'Current annotated or inferred type of the symbol',
            parser=lambda t: T.eval_typestr(t))
    
    @property
    def default_type(self):
        return self.min_type
    
    @property
    def decl_comment(self):
        return self.name + ' : ' + str(self.type)


class RelationSymbol(TypedSymbolMixin, Symbol):
    
    counted = SymbolAttribute('counted', False,
            'Allow duplicates, associate a count with each element')
    
    min_type = T.Set(T.Bottom)
    max_type = T.Set(T.Top)
    
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
    
    min_type = T.Map(T.Bottom, T.Bottom)
    max_type = T.Map(T.Top, T.Top)
    
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
            'Implementation strategy, one of: normal, inc',
            allowed_values=['normal', 'inc'])
    
    demand_set = SymbolAttribute('demand_set', None,
            'Name of demand set, or None if not used')
    demand_params = SymbolAttribute('demand_params', None,
            'Tuple of demand parameter identifiers, or None if not used')
    demand_param_strat = SymbolAttribute(
                         'demand_param_strat', 'unconstrained',
            'Strategy to use for determining demand parameters, one of: '
            'unconstrained, all, explicit',
            allowed_values=['unconstrained', 'all', 'explicit'])
    
    def __str__(self):
        s = 'Query {}'.format(self.name)
        if self.node is not None:
            s += ' ({})'.format(L.Parser.ts(self.node))
        return s
    
    def make_node(self):
        """Return a Query node for this query symbol."""
        return L.Query(self.name, self.node)
