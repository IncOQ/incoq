"""Symbol tables, naming, rewriting."""


__all__ = [
    'N',
    'SymbolTable',
    'QueryRewriter',
]


import builtins
from collections import OrderedDict
from itertools import count
from types import SimpleNamespace

from incoq.util.collections import OrderedSet
from incoq.compiler.incast import L
from incoq.compiler.type import T

from .symbols import *


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
    def get_resultset_name(cls, query):
        return 'R_{}'.format(query)
    
    @classmethod
    def get_auxmap_name(cls, map, mask):
        return '{}_{}'.format(map, mask.m)
    
    @classmethod
    def get_wrap_name(cls, rel):
        return '{}_wrapped'.format(rel)
    
    @classmethod
    def get_unwrap_name(cls, rel):
        return '{}_unwrapped'.format(rel)
    
    Aprefix = 'A_'
    @classmethod
    def A_name(cls, oper):
        assert isinstance(oper, str)
        return cls.Aprefix + oper
    @classmethod
    def is_A(cls, name):
        return name.startswith(cls.Aprefix)
    @classmethod
    def get_A(cls, name):
        assert cls.is_A(name)
        return name[len(cls.Aprefix):]
    
    # SetFromMap prefix.
    SAprefix = 'SA_'
    @classmethod
    def SA_name(cls, map, mask):
        return 'S{}'.format(map)
    @classmethod
    def is_SA(cls, name):
        return name.startswith(cls.SAprefix)
    @classmethod
    def get_SA(cls, name):
        assert cls.is_SA(name)
        return name[len(cls.SAprefix):]
    
    @classmethod
    def get_compute_func_name(cls, query):
        return '_compute_{}'.format(query)
    
    @classmethod
    def get_maint_func_name(cls, inv, param, op):
        return '_maint_{}_for_{}_{}'.format(inv, param, op)
    
    @classmethod
    def get_query_demand_func_name(cls, query):
        return '_demand_{}'.format(query)
    
    @classmethod
    def get_query_demand_set_name(cls, query):
        return '_U_{}'.format(query)
    
    @classmethod
    def get_query_demand_query_name(cls, query):
        return '_QU_{}'.format(query)
    
    @classmethod
    def get_query_inst_name(cls, query, inststr):
        return query + '_ctx' + inststr
    
    # Object domain relations.
    
    M = '_M'
    @classmethod
    def is_M(cls, name):
        return name == cls.M
    
    Fprefix = '_F_'
    @classmethod
    def F(cls, attr):
        assert isinstance(attr, str)
        return cls.Fprefix + attr
    @classmethod
    def is_F(cls, name):
        return name.startswith(cls.Fprefix)
    @classmethod
    def get_F(cls, name):
        assert cls.is_F(name)
        return name[len(cls.Fprefix):]
    
    MAP = '_MAP'
    @classmethod
    def is_MAP(cls, name):
        return name == cls.MAP
    
    TUPprefix = '_TUP_'
    @classmethod
    def TUP(cls, k):
        assert isinstance(k, int)
        return cls.TUPprefix + str(k)
    @classmethod
    def is_TUP(cls, name):
        if not name.startswith(cls.TUPprefix):
            return False
        try:
            int(name[len(cls.TUPprefix)])
        except ValueError:
            return False
        return True
    @classmethod
    def get_TUP(cls, name):
        assert cls.is_TUP(name)
        return int(name[len(cls.TUPprefix):])
    
    @classmethod
    def get_tag_name(cls, query, var, n=None):
        s = query + '_T_' + var
        if n is not None:
            assert isinstance(n, int)
            s += '_' + str(n)
        return s
    
    @classmethod
    def get_filter_name(cls, query, rel, n=None):
        s = query + '_d' + rel
        if n is not None:
            assert isinstance(n, int)
            s += '_' + str(n)
        return s


# Initial transformation statistics.
init_stats = {
    'lines': 0,
    'ast_nodes': 0,
    'time': 0,
    'queries_input': 0,
    'updates_input': 0,
    'updatekinds_input': 0,
    'tags_created': 0,
    'filters_created': 0,
    'comps_transformed': 0,
    'aggrs_transformed': 0,
    'auxmaps_transformed': 0,
}


class SymbolTable:
    
    class Stats(dict):
        def __init__(self):
            super().__init__(init_stats)
        
        def __setkey__(self, key, value):
            if key not in init_stats:
                raise KeyError('Invalid stat key')
            super().__setkey__(key, value)
    
    def __init__(self):
        self.symbols = OrderedDict()
        """Global symbols, in declaration order."""
        
        self.stats = SymbolTable.Stats()
        
        self.fresh_names = SimpleNamespace()
        self.fresh_names.vars = N.fresh_name_generator()
        self.fresh_names.queries = N.fresh_name_generator('Query{}')
        self.fresh_names.inline = N.fresh_name_generator('_i{}')
        
        self.ignored_queries = OrderedSet()
        """Names of queries that cannot or should not be processed."""
        
        self.maint_funcs = OrderedSet()
        """Names of inserted maintenance functions that can be inlined."""
    
    def print(self, *args, flush=True, **kargs):
        if self.config.verbose:
            builtins.print(*args, flush=flush, **kargs)
    
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
        sym.parse_and_update(self, **info)
    
    def dump_symbols(self):
        """Return a string describing the defined global symbols."""
        entries = []
        for sym in self.symbols.values():
            entries.append(str(sym))
        return '\n'.join(entries)
    
    def get_type_store(self):
        """Return a type store (mapping from symbol name to type) based
        on all current symbol type information. Also return a set of
        fixed vars (vars whose types cannot be changed by inference).
        """
        store = {name: sym.min_type.join(sym.type) 
                 for name, sym in self.symbols.items()
                 if hasattr(sym, 'type')}
        
        fixed_vars = set()
        for name, sym in self.symbols.items():
            ann_type = getattr(sym, 'ann_type', None)
            if ann_type is not None:
                fixed_vars.add(name)
                store[name] = ann_type
        
        return store, fixed_vars
    
    def run_type_inference(self, tree):
        """Run type inference over the program, using each symbol's
        type attribute as a starting point. Return a list of nodes where
        well-typedness is violated, and a list of variables whose max
        type is exceeded.
        """
        store, fixed_vars = self.get_type_store()
        
        store, illtyped = T.analyze_types(tree, store, fixed_vars)
        
        # Write back non-query symbol types.
        badsyms = set()
        for name, type in store.items():
            sym = self.symbols[name]
            sym.type = type
            if not type.issmaller(sym.max_type):
                badsyms.add(sym)
        
        # Write back query symbol types.
        for sym in self.get_queries().values():
            type = T.analyze_expr_type(sym.node, store)
            sym.type = type
        
        return illtyped, badsyms
    
    def analyze_expr_type(self, expr):
        store, _fixed_vars = self.get_type_store()
        return T.analyze_expr_type(expr, store)


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
    
    Annotations in each Query node are unaffected by rewrite(), and may
    be different across the occurrences.
    
    When queries are nested, the innermost ones are processed first,
    and the outer query definitions are rewritten to reflect the new
    inner query.
    
    If class attribute expand is True, the symbol for the query is not
    changed, and all occurrences of the query in the tree and in other
    query definitions are replaced with the result of rewrite(), not
    wrapped in a Query node.
    """
    
    expand = False
    
    def __init__(self, symtab):
        super().__init__()
        self.symtab = symtab
    
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
        # By default, dispatch to rewrite_comp() or rewrite_aggr().
        if isinstance(expr, L.Comp):
            return self.rewrite_comp(symbol, name, expr)
        elif isinstance(expr, (L.Aggr, L.AggrRestr)):
            return self.rewrite_aggr(symbol, name, expr)
        else:
            return None
    
    def rewrite_comp(self, symbol, name, comp):
        return None
    
    def rewrite_aggr(self, symbol, name, aggr):
        return None
