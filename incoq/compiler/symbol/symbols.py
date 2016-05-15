"""Symbols and their attributes."""


__all__ = [
    'Constants',
    # Programmatically add Constants members.
    
    'SymbolAttribute',
    'EnumSymbolAttribute',
    'Symbol',
    'TypedSymbolMixin',
    
    'RelationSymbol',
    'MapSymbol',
    'VarSymbol',
    'QuerySymbol',
    
    'annotations',
]


from enum import Enum
from collections import OrderedDict

from incoq.compiler.incast import L
from incoq.compiler.type import T

from .common import (parse_bool, parse_list, parse_int_list,
                     ParseableEnumMixin)


def eval_typestr(s, symtab):
    return T.eval_typestr(s, symtab.config.typedefs)


class Constants(ParseableEnumMixin, Enum):
    
    """Enumeration for symbol attribute constants."""
    
    Unspecified = 0
    
    # impl
    Normal = 1
    Aux = 2
    Inc = 3
    Filtered = 4
    
    # demand_param_strat
    Unconstrained = 10
    All = 11
    Explicit = 12

# Flood the namespace with constants.
globals().update(Constants.__members__)
__all__.extend(Constants.__members__.keys())


class SymbolAttribute:
    
    """Descriptor for a symbol attribute."""
    
    _Missing = object()
    def __init__(self, *, doc=None, default=None, parser=_Missing):
        self.name = None
        """Name of attribute. Populated by MetaSymbol."""
        self.doc = doc
        """User documentation."""
        self.default = default
        """Default value. The owner class or instance may override this with
        a new default by defining an attribute named default_<name>.
        """
        if parser is not self._Missing:
            self.parser = parser
        """Callable that takes a string value to a value for this
        attribute. If None, this attribute is internal and should not be
        populated by the user.
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
        setattr(inst, '_' + self.name, value)
    
    def defined(self, inst):
        return hasattr(inst, '_' + self.name)
    
    def parser(self, value, symtab=None):
        # Default parser, identity function.
        return value


class EnumSymbolAttribute(SymbolAttribute):
    
    """SymbolAttribute where value must be one of the members of
    Constant.
    """
    
    def __init__(self, *, allowed_values, **kargs):
        super().__init__(**kargs)
        self.allowed_values = allowed_values
        """Sequence of Constant members."""
    
    def __set__(self, inst, value):
        if self.allowed_values is not None:
            if value not in self.allowed_values:
                vals = ', '.join(str(v) for v in self.allowed_values)
                raise ValueError('Value for attribute {} must be one of: {}'
                                 .format(self.name, vals))
        super().__set__(inst, value)
    
    def parser(self, value, symtab=None):
        """Default parser, construct constant from string representation."""
        assert isinstance(value, str)
        lv = value.lower()
        for member in self.allowed_values:
            if lv == member.name.lower():
                return member
        # Let __set__() raise an error.
        return value


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
                sym_attr.name = key
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
    
    def parse_and_update(self, symtab, **kargs):
        """Like update(), but run the values through the symbol
        attributes' parser functions if present.
        """
        for attr, value in kargs.items():
            desc = getattr(self.__class__, attr, None)
            if not isinstance(desc, SymbolAttribute):
                raise KeyError('Unknown symbol attribute "{}"'.format(attr))
            if desc.parser is None:
                raise ValueError('Attribute "{}" cannot be parsed'
                                 .format(attr))
            value = desc.parser(value, symtab)
            setattr(self, attr, value)
    
    def clone_attrs(self):
        """Return a dictionary of symbol attributes having non-default
        values on this instance.
        """
        return {desc.name: getattr(self, desc.name)
                for desc in self._symbol_attrs
                if desc.defined(self)}
    
    @property
    def decl_comment(self):
        """Comment string to annotate the declaration of this symbol."""
        return None
    
    decl_constructor = None
    """Name of constructor to call when initializing this symbol's
    variable.
    """


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
    
    type = SymbolAttribute(
        doc='Current annotated or inferred type of the symbol',
        default=None,
        parser=eval_typestr)
    
    ann_type = SymbolAttribute(
        doc='Type of symbol as dictated by user',
        default=None,
        parser=eval_typestr)
    
    @property
    def default_type(self):
        return self.min_type
    
    @property
    def decl_comment(self):
        return self.name + ' : ' + str(self.type)


class RelationSymbol(TypedSymbolMixin, Symbol):
    
    counted = SymbolAttribute(
        doc='Allow duplicates, associate a count with each element',
        default=False,
        parser=parse_bool)
    
    lru = SymbolAttribute(
        doc='Support LRU operations',
        default=False,
        parser=parse_bool)
    
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
    def decl_constructor(self):
        if self.lru:
            return 'LRUSet'
        elif self.counted:
            return 'CSet'
        else:
            return 'Set'


class MapSymbol(TypedSymbolMixin, Symbol):
    
    min_type = T.Map(T.Bottom, T.Bottom)
    max_type = T.Map(T.Top, T.Top)
    
    def __str__(self):
        s = 'Map {}'.format(self.name)
        if self.type is not None:
            s += ' (type: {})'.format(self.type)
        return s
    
    decl_constructor = 'Map'


class VarSymbol(TypedSymbolMixin, Symbol):
    
    def __str__(self):
        s = 'Var {}'.format(self.name)
        if self.type is not None:
            s += ' (type: {})'.format(self.type)
        return s


class QuerySymbol(TypedSymbolMixin, Symbol):
    
    node = SymbolAttribute(
        doc='Expression AST node corresponding to (all occurrences of) '
            'the query',
        default=None)
    
    params = SymbolAttribute(
        doc='Tuple of parameter identifiers for this query',
        default=(),
        parser=parse_list)
    
    impl = EnumSymbolAttribute(
        doc='Implementation strategy',
        default=Unspecified,
        allowed_values=[Unspecified, Normal, Aux, Inc, Filtered])
    
    uses_demand = SymbolAttribute(
        doc='Whether or not the query uses demand',
        default=False,
        parser=parse_bool)
    
    demand_set = SymbolAttribute(
        doc='Name of demand set, or None if not used',
        default=None)
    
    demand_params = SymbolAttribute(
        doc='Tuple of demand parameter identifiers, or None if not used',
        default=None,
        parser=parse_list)
    
    demand_param_strat = EnumSymbolAttribute(
        doc='Strategy to use for determining demand parameters',
        default=Unconstrained,
        allowed_values=[Unconstrained, All, Explicit])
    
    demand_set_maxsize = SymbolAttribute(
        doc='If not None, number of elements to hold in demand set '
            'before removing them, LRU style',
        default=None)
        # Should also have parser but needs to accept int or None.
        # Wait to refactor parsing.
    
    clause_reorder = SymbolAttribute(
        doc='Permute clauses by this order for demand strategy '
            'selection; e.g., 3, 1, 2 means do the third clause, '
            'then first, then second',
        default=None,
        parser=parse_int_list)
    
    count_elim_safe_override = SymbolAttribute(
        doc='If True, consider it safe to eliminate counting for this '
        'query even if we can\'t determine that from analysis',
        default=False,
        parser=parse_bool)
    
    well_typed_data = SymbolAttribute(
        doc='If True, all relevant input data to the query is well-typed '
        'at all points in the program',
        default=False,
        parser=parse_bool)
    
    # Internal attributes.
    
    maint_joins = SymbolAttribute(
        doc='List of query symbols of maintenance joins used to help '
            'incrementally compute this comprehension query')
    
    join_prefix = SymbolAttribute(
        doc='Prefix used for maintenance join to rename query variables')
    
    filters = SymbolAttribute(
        doc='List of filtered clauses to use in place of corresponding '
            'normal membership clauses')
    
    display = SymbolAttribute(
        doc='Whether or not to include this query\'s description in '
            'the comment header of the output program',
        default=True)
    
    struct_for_query = SymbolAttribute(
        doc='If this is a tag or filter, name of the query for which '
            'this was created',
        default=None)
    
    def __str__(self):
        s = 'Query {}'.format(self.name)
        if self.node is not None:
            s += ' ({})'.format(L.Parser.ts(self.node))
        return s
    
    def make_node(self):
        """Return a Query node for this query symbol, with no
        annotation.
        """
        return L.Query(self.name, self.node, None)
    
    @property
    def decl_comment(self):
        return '{name} : {params}{node}{type}'.format(
            name=self.name,
            params=', '.join(self.params) + ' -> '
                   if len(self.params) > 0 else '',
            node=L.Parser.ts(self.node),
            type=' : ' + str(self.type) if self.type is not None else '')


annotations = [
    'nodemand',         # Do not call the demand function for this occurrence
]
