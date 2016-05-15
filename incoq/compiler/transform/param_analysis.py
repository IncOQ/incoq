"""Analysis of scopes, query parameters, and query demand."""


__all__ = [
    'find_nested_queries',
    'make_demand_func',
    'determine_comp_demand_params',
    'make_demand_set',
    'make_demand_query',
    
    'ScopeBuilder',
    'ContextTracker',
    
    'ParamAnalyzer',
    'DemandParamAnalyzer',
    'DemandTransformer',
    'DemandResetter',
    
    'analyze_params',
    'analyze_demand_params',
    'transform_demand',
]


from itertools import chain

from incoq.util.collections import OrderedSet
from incoq.compiler.type import T
from incoq.compiler.symbol import S, N
from incoq.compiler.incast import L


def find_nested_queries(node):
    """Return a list of all Query nodes that are properly contained
    inside the given node.
    """
    class Finder(L.NodeVisitor):
        def process(self, tree):
            self.start = tree
            self.queries = []
            super().process(tree)
            return self.queries
        def visit_Query(self, node):
            self.generic_visit(node)
            if node != self.start:
                self.queries.append(node)
    
    return Finder.run(node)


def make_demand_func(query):
    func = N.get_query_demand_func_name(query.name)
    uset = N.get_query_demand_set_name(query.name)
    
    maxsize = query.demand_set_maxsize
    
    if maxsize is None:
        code = L.Parser.ps('''
            def _FUNC(_elem):
                if _elem not in _U:
                    _U.reladd(_elem)
            ''', subst={'_FUNC': func, '_U': uset})
    elif maxsize == 1:
        code = L.Parser.ps('''
            def _FUNC(_elem):
                if _elem not in _U:
                    _U.relclear()
                    _U.reladd(_elem)
            ''', subst={'_FUNC': func, '_U': uset})
    elif not isinstance(maxsize, int) or maxsize <= 0:
        raise L.ProgramError('Invalid value for demand_set_maxsize')
    else:
        code = L.Parser.ps('''
            def _FUNC(_elem):
                if _elem not in _U:
                    while len(_U) >= _MAXSIZE:
                        _stale = _U.peek()
                        _U.relremove(_stale)
                    _U.reladd(_elem)
            ''', subst={'_FUNC': func, '_U': uset,
                        '_MAXSIZE': L.Num(maxsize)})
    
    return code


def determine_comp_demand_params(clausetools, comp, params, demand_params,
                                 demand_param_strat):
    """Given a Comp node, and values for the associated attributes
    params, demand_params, and demand_param_strat, return the proper
    demand_params.
    """
    assert isinstance(comp, L.Comp)
    strat = demand_param_strat
    
    if strat != S.Explicit and demand_params is not None:
        raise AssertionError('Do not supply demand_params unless '
                             'demand_param_strat is set to "explicit"')
    
    if strat == S.Unconstrained:
        con_vars = clausetools.con_lhs_vars_from_comp(comp)
        result  = tuple(p for p in params if p not in con_vars)
    elif strat == S.All:
        result = params
    elif strat == S.Explicit:
        assert demand_params is not None
        result = demand_params
    else:
        assert()
    
    return result


def make_demand_set(symtab, query):
    """Create a demand set, update the query's demand_set attribute, and
    return the new demand set symbol.
    """
    uset_name = N.get_query_demand_set_name(query.name)
    uset_tuple = L.tuplify(query.demand_params)
    uset_tuple_type = symtab.analyze_expr_type(uset_tuple)
    uset_type = T.Set(uset_tuple_type)
    maxsize = query.demand_set_maxsize
    uset_lru = maxsize is not None and maxsize > 1
    uset_sym = symtab.define_relation(uset_name, type=uset_type,
                                      lru=uset_lru)
    
    query.demand_set = uset_name
    
    return uset_sym


def make_demand_query(symtab, query, left_clauses):
    """Create a demand query, update the query's demand_query attribute,
    and return the new demand query symbol.
    """
    ct = symtab.clausetools
    
    demquery_name = N.get_query_demand_query_name(query.name)
    
    demquery_tuple = L.tuplify(query.demand_params)
    demquery_tuple_type = symtab.analyze_expr_type(demquery_tuple)
    demquery_type = T.Set(demquery_tuple_type)
    
    demquery_comp = L.Comp(demquery_tuple, left_clauses)
    prefix = next(symtab.fresh_names.vars)
    demquery_comp = ct.comp_rename_lhs_vars(demquery_comp,
                                            lambda x: prefix + x)
    
    demquery_sym = symtab.define_query(demquery_name, type=demquery_type,
                                       node=demquery_comp, impl=query.impl)
    
    query.demand_query = demquery_name
    
    return demquery_sym


class ScopeBuilder(L.NodeVisitor):
    
    """Determine scope information for each Query node in the tree.
    Return a map from Query node identity (i.e. id(node)) to a pair
    of the node itself and a set of variables that are bound in scopes
    outside the node.
    
    Lexical scopes are introduced for the top level, function
    definitions, and comprehensions. Binding is flow-insensitive,
    so a name may be considered bound at a query even if it is only
    introduced below the query's occurrence.
    
    The map is keyed by Query node identity (its memory address), rather
    than by Query node value or query name, because multiple occurrences
    of the same query may have distinct scope information. This means
    that this information becomes stale and unusable when a Query node
    is transformed (even if it is replaced by a structurally identical
    copy). The node itself is included in the map value in case the user
    of the map does not already have a reference to the node, and to
    prevent the node from being garbage collected (which could lead to
    inconsistency if a new node is later allocated to the same address).
    
    If bindenv is given, these variables are assumed to be declared
    outside the given tree and are included in every scope.
    """
    
    # We maintain a scope stack -- a list of sets of bound variables,
    # one per scope, ordered outermost first. When a Query node is seen,
    # we add an entry in the map to a shallow copy of the current scope
    # stack, aliasing the underlying sets. This way, we include
    # identifiers that are only bound after the Query node is already
    # processed. At the end, we flatten the scope stacks into singular
    # sets.
    
    def __init__(self, clausetools, *, bindenv=None):
        super().__init__()
        self.clausetools = clausetools
        if bindenv is None:
            bindenv = []
        self.bindenv = OrderedSet(bindenv)
    
    def flatten_scope_stack(self, stack):
        return OrderedSet(chain(self.bindenv, *stack))
    
    def enter(self):
        self.current_stack.append(OrderedSet())
    
    def exit(self):
        self.current_stack.pop()
    
    def bind(self, name):
        self.current_stack[-1].add(name)
    
    def process(self, tree):
        self.current_stack = []
        self.query_scope_info = info = {}
        
        super().process(tree)
        assert len(self.current_stack) == 0
        
        for k, (node, stack) in info.items():
            info[k] = (node, self.flatten_scope_stack(stack))
        return info
    
    def visit_Module(self, node):
        self.enter()
        self.generic_visit(node)
        self.exit()
    
    def visit_Fun(self, node):
        # Bind the name of the function in the outer scope,
        # its parameters in the inner scope.
        self.bind(node.name)
        self.enter()
        for a in node.args:
            self.bind(a)
        self.visit(node.body)
        self.exit()
    
    def visit_For(self, node):
        self.bind(node.target)
        self.generic_visit(node)
    
    def visit_DecompFor(self, node):
        for v in node.vars:
            self.bind(v)
        self.generic_visit(node)
    
    def visit_Assign(self, node):
        self.bind(node.target)
        self.generic_visit(node)
    
    def visit_DecompAssign(self, node):
        for v in node.vars:
            self.bind(v)
        self.generic_visit(node)
    
    def visit_Query(self, node):
        # Shallow copy: The copy will be affected by adding new bindings
        # to stacks, but not by pushing and popping to the list itself.
        stack_copy = list(self.current_stack)
        self.query_scope_info[id(node)] = (node, stack_copy)
        self.generic_visit(node)
    
    def visit_Comp(self, node):
        ct = self.clausetools
        
        self.enter()
        
        for cl in node.clauses:
            if isinstance(cl, L.Member):
                # Hack so that we can scope comprehensions that aren't
                # being incrementalized, for the sake of determining
                # parameters of inner comprehensions. Will fail for
                # bizarre cases like "o.f in R".
                vars = L.IdentFinder.find_vars(cl.target)
            else:
                vars = ct.lhs_vars(cl)
            for v in vars:
                self.bind(v)
        
        self.generic_visit(node)
        self.exit()


class ContextTracker(L.NodeTransformer):
    
    """Mixin for tracking what clauses form the context for inner
    queries. A subclass can access this list by calling
    get_left_clauses().
    
    For comprehensions, an inner query's context consists of the
    clauses appearing to the left of its occurrence in the outer query.
    For aggregates (AggrRestr nodes only), the context is a single
    clause over the restriction set.
    
    Queries whose impl attribute is Normal are not tracked in this
    manner.
    """
    
    def __init__(self, symtab):
        super().__init__()
        self.symtab = symtab
    
    def process(self, tree):
        self.context_stack = []
        """Each stack entry corresponds to a level of nesting of a
        Query node for a comprehension whose impl is not Normal.
        The value of each entry is a list of the clauses at that level
        that have already been fully processed (for a Comp node) or a
        clause over a restriction set (for an AggrRestr node).
        """
        self.enter_query_flag = False
        """Flag indicating whether the next call to visit_Comp or
        visit_AggrRestr should affect the context stack. This is set
        when we are in the Query node just before we recurse. It helps
        us distinguish transformable queries from non-transformable
        ones and stray non-Query Comp nodes.
        """
        
        tree = super().process(tree)
        
        assert len(self.context_stack) == 0
        return tree
    
    def push_context(self):
        self.context_stack.append([])
    
    def pop_context(self):
        self.context_stack.pop()
    
    def add_clause(self, cl):
        if len(self.context_stack) > 0:
            self.context_stack[-1].append(cl)
    
    def get_left_clauses(self):
        """Get the sequence of clauses to the left of the current
        containing comprehension query, or None if there is no such
        query.
        """
        if len(self.context_stack) > 0:
            return tuple(self.context_stack[-1])
        else:
            return None
    
    def comp_visit_helper(self, node):
        """Visit while marking clauses in the context stack."""
        clauses = []
        for cl in node.clauses:
            cl = self.visit(cl)
            self.add_clause(cl)
            clauses.append(cl)
        resexp = self.visit(node.resexp)
        return node._replace(resexp=resexp, clauses=clauses)
    
    def visit_Comp(self, node):
        if self.enter_query_flag:
            self.enter_query_flag = False
            self.push_context()
            node = self.comp_visit_helper(node)
            self.pop_context()
        else:
            node = self.generic_visit(node)
        return node
    
    def aggr_visit_helper(self, node):
        """Visit after setting a context for the restriction set."""
        cl = L.VarsMember(node.params, node.restr)
        self.add_clause(cl)
        node = self.generic_visit(node)
        return node
    
    def visit_AggrRestr(self, node):
        if self.enter_query_flag:
            self.enter_query_flag = False
            self.push_context()
            node = self.aggr_visit_helper(node)
            self.pop_context()
        else:
            node = self.generic_visit(node)
        return node
    
    def visit_Query(self, node):
        query_sym = self.symtab.get_queries()[node.name]
        if (isinstance(node.query, (L.Comp, L.AggrRestr)) and
            query_sym.impl != S.Normal):
            self.enter_query_flag = True
        
        return self.generic_visit(node)


class ParamAnalyzer(L.NodeVisitor):
    
    """Annotate all query symbols with params attribute info. Raise
    ProgramError if any query has multiple occurrences with inconsistent
    context information.
    """
    
    def __init__(self, symtab, scope_info):
        super().__init__()
        self.symtab = symtab
        self.scope_info = scope_info
        self.query_param_map = {}
        """Map from query name to param info."""
    
    def get_params(self, node):
        """Get parameters for the given query node. The node must be
        indexed in scope_info.
        """
        _node, scope = self.scope_info[id(node)]
        vars = L.IdentFinder.find_non_rel_uses(node.query)
        params = tuple(vars.intersection(scope))
        return params
    
    def visit_Query(self, node):
        ct = self.symtab.clausetools
        querysym = self.symtab.get_queries()[node.name]
        cache = self.query_param_map
        
        # Analyze parameters from node.
        params = self.get_params(node)
        
        # If we've already analyzed this query, just confirm that this
        # occurrence's parameters match what we're expecting.
        if node.name in cache:
            if params != cache[node.name]:
                raise L.ProgramError('Inconsistent parameter info for query '
                                     '{}: {}, {}'.format(
                                     querysym.name, cache[node.name], params))
        
        # Otherwise, add to the cache and update the symbol.
        else:
            cache[node.name] = params
            querysym.params = params
        
        self.generic_visit(node)


class DemandParamAnalyzer(ContextTracker):
    
    """Annotate all query symbols with demand_params attribute info."""
    
    # This is written as a NodeTransformer so that we can use
    # ContextTracker without having to make a NodeVisitor version
    # of it, but we don't actually modify the tree at all.
    
    # We work on queries innermost-first so that at the time we process
    # an aggregate of a comprehension, we know the demand_params of the
    # comprehension. We make sure to only process each query once.
    
    def process(self, tree):
        self.processed = set()
        """Names of queries already handled."""
        super().process(tree)
    
    def determine_demand_params(self, node):
        # Skip if already processed.
        if node.name in self.processed:
            return
        
        symtab = self.symtab
        ct = symtab.clausetools
        query_sym = symtab.get_queries()[node.name]
        
        if query_sym.impl is S.Aux:
            # No demand for aux impl.
            demand_params = ()
            uses_demand = False
        
        elif isinstance(node.query, L.Comp):
            demand_params = determine_comp_demand_params(
                ct, node.query, query_sym.params,
                query_sym.demand_params, query_sym.demand_param_strat)
            uses_demand = len(demand_params) > 0
        
        elif isinstance(node.query, L.Aggr):
            # If the operand contains a demand-driven query, or if the
            # aggregate appears in a transformed comprehension, then the
            # aggregate must be demand-driven for all parameters.
            operand_uses_demand = False
            aggr_in_comp = self.get_left_clauses() is not None
            
            for q in find_nested_queries(node):
                inner_sym = symtab.get_queries()[q.name]
                if inner_sym.uses_demand:
                    operand_uses_demand = True
            
            if operand_uses_demand or aggr_in_comp:
                uses_demand = True
                demand_params = query_sym.params
            else:
                uses_demand = False
                demand_params = ()
        
        else:
            kind = query_sym.node.__class__.__name__
            raise L.ProgramError('No rule for analyzing parameters of '
                                 '{} query'.format(kind))
        
        query_sym.uses_demand = uses_demand
        query_sym.demand_params = demand_params
        self.processed.add(query_sym.name)
    
    def visit_Query(self, node):
        super().visit_Query(node)
        
        query_sym = self.symtab.get_queries()[node.name]
        if query_sym.impl is not S.Normal:
            self.determine_demand_params(node)


class DemandTransformer(ContextTracker):
    
    """Modify each query appearing in the tree to add demand. For
    comprehensions, this means adding a new clause, while for
    aggregates, it means turning an Aggr node into an AggrRestr node.
    
    Outer queries get a demand set, while inner queries get a demand
    query. The demand_set and demand_query symbol attributes are set
    accordingly.
    
    Only the first occurrence of a query triggers new processing.
    Subsequent occurrences are rewritten to be the same as the first.
    """
    
    # Demand rewriting happens in a top-down fashion, so that inner
    # queries are rewritten after their outer comprehensions already
    # have a clause over a demand set or demand query.
    
    def process(self, tree):
        self.queries_with_usets = OrderedSet()
        """Outer queries, for which a demand set and a call to a demand
        function are added.
        """
        self.rewrite_cache = {}
        """Map from query name to rewritten AST."""
        self.demand_queries = set()
        """Set of names of demand queries that we introduced, which
        shouldn't be recursed into.
        """
        
        return super().process(tree)
    
    def add_demand_function_call(self, query_sym, query_node, ann):
        """Return a Query node wrapped with a call to a demand function,
        if needed.
        """
        # Skip if there's no demand set associated with this query.
        if query_sym.name not in self.queries_with_usets:
            return query_node
        # Skip if we have a nodemand annotation.
        if ann is not None and ann.get('nodemand', False):
            return query_node
        
        demand_call = L.Call(N.get_query_demand_func_name(query_sym.name),
                             [L.tuplify(query_sym.demand_params)])
        return L.FirstThen(demand_call, query_node)
    
    def visit_Module(self, node):
        node = self.generic_visit(node)
        
        # Add declarations for demand functions.
        funcs = []
        for query in self.queries_with_usets:
            query_sym = self.symtab.get_queries()[query]
            func = make_demand_func(query_sym)
            funcs.append(func)
        
        node = node._replace(body=tuple(funcs) + node.body)
        return node
    
    def rewrite_with_demand(self, query_sym, node):
        """Given a query symbol and its associated Comp or Aggr node,
        return the demand-transformed version of that node (not
        transforming any subqueries).
        """
        symtab = self.symtab
        demand_params = query_sym.demand_params
        
        if not query_sym.uses_demand:
            return node
        
        # Make a demand set or demand query.
        left_clauses = self.get_left_clauses()
        if left_clauses is None:
            dem_sym = make_demand_set(symtab, query_sym)
            dem_node = L.Name(dem_sym.name)
            dem_clause = L.RelMember(demand_params, dem_sym.name)
            self.queries_with_usets.add(query_sym.name)
        else:
            dem_sym = make_demand_query(symtab, query_sym, left_clauses)
            dem_node = dem_sym.make_node()
            dem_clause = L.VarsMember(demand_params, dem_node)
            self.demand_queries.add(dem_sym.name)
        
        # Determine the rewritten node.
        if isinstance(node, L.Comp):
            node = node._replace(clauses=(dem_clause,) + node.clauses)
        elif isinstance(node, L.Aggr):
            node = L.AggrRestr(node.op, node.value, demand_params, dem_node)
        else:
            raise AssertionError('No rule for handling demand for {} node'
                                 .format(node.__class__.__name__))
        
        return node
    
    def visit_Query(self, node):
        # If this is a demand query that we added, it does not need
        # transformation.
        if node.name in self.demand_queries:
            return node
        
        query_sym = self.symtab.get_queries()[node.name]
        
        # If we've seen it before, reuse previous result.
        if node.name in self.rewrite_cache:
            # Possibly wrap with a call to the demand function.
            ann = node.ann
            node = self.rewrite_cache[node.name]
            node = self.add_demand_function_call(query_sym, node, ann)
            return node
        
        # Rewrite to use demand.
        inner_node = self.rewrite_with_demand(query_sym, query_sym.node)
        node = node._replace(query=inner_node)
        
        # Recurse to handle subqueries.
        node = super().visit_Query(node)
        
        # Update symbol.
        query_sym.node = node.query
        
        # Update cache.
        self.rewrite_cache[query_sym.name] = node
        
        # Possibly wrap with a call to the demand function.
        node = self.add_demand_function_call(query_sym, node, node.ann)
        
        return node


class DemandResetter(L.NodeTransformer):
    
    """Replace ResetDemand nodes with clear updates to the corresponding
    demand sets.
    """
    
    def __init__(self, symtab):
        super().__init__()
        self.queries = symtab.get_queries().values()
    
    def visit_ResetDemand(self, node):
        if len(node.names) == 0:
            demand_sets = [query.demand_set
                           for query in self.queries
                           if query.demand_set is not None]
        else:
            demand_sets = [query.demand_set
                           for query in self.queries
                           if query.name in node.names
                           if query.demand_set is not None]
        
        code = tuple(L.RelClear(ds) for ds in demand_sets)
        return code


def analyze_params(tree, symtab):
    """Determine params symbol attributes for all queries."""
    scope_info = ScopeBuilder.run(tree, symtab.clausetools)
    ParamAnalyzer.run(tree, symtab, scope_info)


def analyze_demand_params(tree, symtab):
    """Determine demand_params symbol attributes for all queries."""
    DemandParamAnalyzer.run(tree, symtab)


def transform_demand(tree, symtab):
    """Transform queries to incorporate demand."""
    tree = DemandTransformer.run(tree, symtab)
    tree = DemandResetter.run(tree, symtab)
    return tree
