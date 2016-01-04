"""Symbol tables."""


__all__ = [
    'N',
    
    'Symbol',
    'RelationSymbol',
    'MapSymbol',
    'VarSymbol',
    'QuerySymbol',
    
    'SymbolTable',
    
    'QueryRewriter',
]


from collections import OrderedDict
from itertools import count
from types import SimpleNamespace
from simplestruct import Struct, Field

from incoq.util.collections import OrderedSet
from incoq.mars.incast import L
import incoq.mars.types as T


class N:
    
    """Namespace for naming scheme helpers."""
    
    @classmethod
    def fresh_name_generator(cls, template='_v{}'):
        return (template.format(i) for i in count(1))
    
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


class Symbol:
    
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
    
    decl_constr = 'Set'


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
    
    impl = SymbolAttribute('impl', 'normal',
            'Implementation strategy, one of: normal, inc')
    impl.allowed_values = ['normal', 'inc']
    
    def __str__(self):
        s = 'Query {}'.format(self.name)
        if self.node is not None:
            s += ' ({})'.format(L.Parser.ts(self.node))
        return s


class SymbolTable:
    
    def __init__(self):
        self.symbols = OrderedDict()
        """Global symbols, in declaration order."""
        
        self.fresh_names = SimpleNamespace()
        self.fresh_names.vars = N.fresh_name_generator()
        self.fresh_names.queries = N.fresh_name_generator('Query{}')
        
        self.ignored_queries = OrderedSet()
        """Names of queries that cannot or should not be processed."""
    
    def define_symbol(self, name, kind, **kargs):
        """Define a new symbol of the given kind. Return the symbol."""
        if name in self.symbols:
            raise L.ProgramError('Symbol "{}" already defined'.format(name))
        sym = kind(name, **kargs)
        self.symbols[name] = sym
        return sym
    
    def define_relation(self, name, **kargs):
        return self.define_symbol(name, RelationSymbol, **kargs)
    
    def define_map(self, name, **kargs):
        return self.define_symbol(name, MapSymbol, **kargs)
    
    def define_var(self, name, **kargs):
        return self.define_symbol(name, VarSymbol, **kargs)
    
    def define_query(self, name, **kargs):
        return self.define_symbol(name, QuerySymbol, **kargs)
    
    def get_symbols(self, kind=None):
        """Return an OrderedDict of symbols of the requested kind.
        If kind is None, all symbols are returned.
        """
        result = OrderedDict(self.symbols)
        if kind is not None:
            for name, sym in self.symbols.items():
                if not isinstance(sym, kind):
                    result.pop(name)
        return result
    
    def get_relations(self):
        return self.get_symbols(RelationSymbol)
    
    def get_maps(self):
        return self.get_symbols(MapSymbol)
    
    def get_vars(self):
        return self.get_symbols(VarSymbol)
    
    def get_queries(self):
        return self.get_symbols(QuerySymbol)
    
    def apply_symconfig(self, name, info):
        """Given a symbol name and a key-value dictionary of symbol
        config attribute, apply the attributes.
        """
        if name not in self.symbols:
            raise L.ProgramError('No symbol "{}"'.format(name))
        sym = self.symbols[name]
        # Hook into a parse_*()  method, if one exists for that
        # attr key on the symbol.
        new_info = {}
        for k, v in info.items():
            parse_method = getattr(sym, 'parse_' + k, None)
            if parse_method is not None:
                v = parse_method(v)
            new_info[k] = v
        sym.update(**new_info)
    
    def dump_symbols(self):
        """Return a string describing the defined global symbols."""
        entries = []
        for sym in self.symbols.values():
            entries.append(str(sym))
        return '\n'.join(entries)


class QueryRewriter(L.NodeTransformer):
    
    """Base class for a transformer that rewrites queries in a
    consistent way.
    
    The consistency condition is defined over a program AST and a set of
    query symbols. It states that for each query symbol, the definition
    for that symbol agrees with all of its Query node occurrences, in
    both the program and in other query symbol definitions.
    
    For each unique Query node, the method rewrite() is called on that
    query, and the resulting expression AST is used to replace all of
    its occurrences and to update the corresponding symbol. The AST
    returned by rewrite() is not recursively processed. Provided that
    the AST returned by rewrite() does not contain occurrences of other
    queries, this transformer preserves the consistency condition, and
    furthermore raises TransformationError if a violation is detected.
    rewrite() is called only once per unique query appearing in the
    program.
    
    When queries are nested, the innermost ones are processed first,
    and the outer query definitions are rewritten to reflect the new
    inner query.
    
    If expand is True, the symbol for the query is not changed, and all
    occurrences of the query in the tree and in other query definitions
    are replaced with the result of rewrite(), not wrapped in a Query
    node.
    """
    
    def __init__(self, symtab, *, expand=False):
        super().__init__()
        self.symtab = symtab
        self.expand = expand
    
    def process(self, tree):
        # Keep maps from each seen query name to its original expression
        # and its rewritten expression.
        self.queries_before = {}
        self.queries_after = {}
        
        # A query's symbol definition has to be updated before we
        # discover any of its occurrences, or it will be incorrectly
        # interpreted as a consistency error. For this reason, process
        # all query definitions before the tree, and process these
        # definitions in order of increasing size so that inner queries
        # come first.
        queries = list(self.symtab.get_queries().values())
        queries.sort(key=lambda q: L.tree_size(q.node))
        for query in queries:
            query.node = super().process(query.node)
        
        # Process tree.
        tree = super().process(tree)
        
        return tree
    
    def visit_Query(self, node):
        node = super().generic_visit(node)
        
        name = node.name
        this_occ = node.query
        
        # The first time we see a query, obtain the symbol, check
        # for consistency with the symbol, call the rewriter, and
        # update the symbol.
        if name not in self.queries_before:
            sym = self.symtab.get_queries().get(name, None)
            if sym is None:
                raise L.TransformationError('No symbol for query name "{}"'
                                            .format(name))
            if this_occ != sym.node:
                raise L.TransformationError(
                    'Inconsistent symbol and occurrence for query '
                    '"{}": {}, {}'.format(name, sym.node, this_occ))
            
            replacement = self.rewrite(sym, name, this_occ)
            self.queries_before[name] = this_occ
            self.queries_after[name] = replacement
            if replacement is not None and not self.expand:
                sym.node = replacement
        
        # Each subsequent time, check for consistency with the previous
        # occurrences, and reuse the replacement that was determined the
        # first time.
        else:
            prev_occ = self.queries_before[name]
            # Check for consistency with previous occurrences.
            if this_occ != prev_occ:
                raise L.TransformationError(
                    'Inconsistent occurrences for query "{}": {}, {}'
                    .format(name, prev_occ, this_occ))
            replacement = self.queries_after[name]
        
        if replacement is not None:
            if self.expand:
                node = replacement
            else:
                node = node._replace(query=replacement)
        return node
    
    def rewrite(self, symbol, name, expr):
        """Called once for each unique query name that occurs in the
        tree. Arguments are the query symbol, the query's name, and
        the expression of the query (which all occurrences of the query,
        as well as the symbol itself, should agree on). The return value
        is a new expression AST for the query, or None to indicate no
        change.
        """
        pass
