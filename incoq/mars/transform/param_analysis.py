"""Analysis of scopes, query parameters, and query demand."""


__all__ = [
    'make_demand_func',
    'determine_demand_params',
    
    'ScopeBuilder',
    
    'QueryContextInstantiator',
    'ParamAnalyzer',
    'DemandAnalyzer',
    'NestedDemandAnalyzer',
    'analyze_demand',
]


from itertools import chain

from incoq.util.collections import OrderedSet
import incoq.mars.types as T
from incoq.mars.symtab import N
from incoq.mars.incast import L


def make_demand_func(query):
    func = N.get_query_demand_func_name(query)
    uset = N.get_query_demand_set_name(query)
    return L.Parser.ps('''
        def _FUNC(_elem):
            if _elem not in _U:
                _U.reladd(_elem)
        ''', subst={'_FUNC': func, '_U': uset})


def determine_demand_params(clausetools, query):
    """Given a query symbol, decide the demand parameters based on
    the query's params, demand_params, and demand_param_strat
    attributes. Assign the demand_params field and return its value.
    """
    assert isinstance(query.node, L.Comp)
    comp = query.node
    params = query.params
    
    strat = query.demand_param_strat
    if strat != 'explicit' and query.demand_params is not None:
        raise AssertionError('Do not supply demand_params unless '
                             'demand_param_strat is set to "explicit"')
    
    if strat == 'unconstrained':
        uncon_vars = clausetools.uncon_lhs_vars_from_comp(comp)
        demand_params = tuple(p for p in params if p in uncon_vars)
    elif strat == 'all':
        demand_params = params
    elif query.demand_param_strat == 'explicit':
        assert query.demand_params is not None
        demand_params = query.demand_params
    else:
        assert()
    
    query.demand_params = demand_params
    return demand_params


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
    
    def __init__(self, *, bindenv=None):
        super().__init__()
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
    
    def visit_fun(self, node):
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
        self.enter()
        self.generic_visit(node)
        self.exit()
    
    def visit_RelMember(self, node):
        for v in node.vars:
            self.bind(v)
        self.generic_visit(node)
    
    def visit_SingMember(self, node):
        for v in node.vars:
            self.bind(v)
        self.generic_visit(node)
    
    def visit_VarsMember(self, node):
        for v in node.vars:
            self.bind(v)
        self.generic_visit(node)


# For ease of specification, the complete logic for rewriting query
# occurrences based on their context is split across several subclasses,
# each of which handles more complex cases.
#
# QueryContextInstantiator provides the basic behavior of instantiating
# query occurrences based on some criteria for characterizing contexts.
#
# ParamAnalyzer assigns parameter information to query symbols and
# instantiates occurrences with distinct parameters. It does not deal
# with demand at all.
#
# DemandAnalyzer does the same but also rewrites all queries to have
# demand sets for their demand parameters. This is generally not correct
# in the case where queries can be nested.
#
# NestedDemandAnalyzer tackles the most general case, instantiating
# queries based on their parameters and also the clauses of the query
# in which they appear. Outer queries get demand sets and inner
# queries get demand queries.


class QueryContextInstantiator(L.NodeTransformer):
    
    """Framework for instantiating multiple occurrences of the same
    query into different queries whenever they occur in a new context.
    The exact notion of context (e.g., different bound parameter
    variables) is defined in a subclass. A new query symbol is created
    for each new instantiation.
    """
    
    # We keep a map whose keys are query names and whose values are
    # query context maps. Each query context map goes from the name
    # of an instantiated version of the query to the context for which
    # it was made.
    #
    # At an occurrence of a query, we compare the context of the
    # occurrence with each entry in the context map for that query name
    # and pick the instantiated version having the same context. If none
    # exists, we create a new instantiated query (including a new
    # symbol) and add the entry to the map.
    #
    # The first instantiation is named the same as the original query
    # and reuses its query symbol object, although its AST may be
    # rewritten according to context info.
    #
    # The determination of what constitutes context, and how to rewrite
    # an instantiated query, is made by a subclass.
    #
    # Queries occurrences are visited in a top-down order, so the
    # outermost query will be processed first. It is assumed that
    # whenever there are two occurrences of an outer query in the same
    # context, the contexts for their respective inner queries will be
    # the same.
    
    def __init__(self, symtab):
        super().__init__()
        self.symtab = symtab
        self.query_contexts = {}
        """Map from query name to context map."""
    
    def process(self, tree):
        self.scope_info = ScopeBuilder.run(tree)
        tree = super().process(tree)
        return tree
    
    def get_context(self, node):
        """Return a context object for the given Query node."""
        raise NotImplementedError
    
    def apply_context(self, query, context):
        """Update the attributes (including possibly the AST) of a
        query symbol to include the given context info.
        """
        raise NotImplementedError
    
    def visit_Query(self, node):
        queries = self.symtab.get_queries()
        name = node.name
        context = self.get_context(node)
        
        # Determine the query instantiation name and symbol, creating
        # them if necessary.
        context_map = self.query_contexts.setdefault(name, {})
        already_instantiated = False
        for inst_name, ctx in context_map.items():
            if context == ctx:
                # Found an existing instantiation. Reuse it.
                query_sym = queries[inst_name]
                already_instantiated = True
                break
        else:
            if len(context_map) == 0:
                # No instantiations so far. Create the initial
                # "instantiation" having the original query's name
                # and symbol.
                inst_name = name
                query_sym = queries[inst_name]
            else:
                # Create a new instantiation name.
                num = len(context_map) + 1
                inst_name = N.get_query_inst_name(name, str(num))
                # Create the new symbol.
                attrs = queries[name].clone_attrs()
                query_sym = self.symtab.define_query(inst_name, **attrs)
            
            # Update the context map and query symbol.
            context_map[inst_name] = context
            self.apply_context(query_sym, context)
        
        # Rewrite this occurrence. Then recurse, if we haven't already
        # processed this query in this context.
        #
        # We need to make sure that at the time we recurse, there is
        # up-to-date scope info for this node since it has been
        # rewritten according to the changes to the query symbol made in
        # apply_context(). (We don't need to update this info after
        # recursing because we assume the visitor needs only the scope
        # info for the present node, not previously visited ones.)
        #
        # We also need to ensure that after recursing, we update the
        # symbol's node for any changes to the subqueries. This does
        # not cause inconsistency with other occurrences because it
        # happens only once per instantiated query symbol.
        
        if already_instantiated:
            # Rewrite this occurrence.
            node = query_sym.make_node()
        else:
            # Save old scope info.
            _node, bindenv = self.scope_info[id(node)]
            # Rewrite.
            node = query_sym.make_node()
            # Determine scope info for rewritten part.
            new_info = ScopeBuilder.run(node, bindenv=bindenv)
            self.scope_info.update(new_info)
            
            # Recurse.
            node = self.generic_visit(node)
            # Update symbol.
            query_sym.node = node.query
        
        return node


class ParamAnalyzer(QueryContextInstantiator):
    
    """ContextInstantiator based on parameter information."""
    
    def get_params(self, node):
        """Get parameters for the given query node. The node must be
        indexed in scope_info.
        """
        _node, scope = self.scope_info[id(node)]
        vars = L.IdentFinder.find_vars(node.query)
        params = tuple(vars.intersection(scope))
        return params
    
    # For this visitor and DemandAnalyzer, the context is just a tuple
    # of parameters for the query occurrence. We abstract this via
    # params_from_context() for the sake of NestedDemandAnalyzer.
    
    def params_from_context(self, context):
        return context
    
    def get_context(self, node):
        return self.get_params(node)
    
    def apply_context(self, query, context):
        query.params = self.params_from_context(context)


class DemandAnalyzer(ParamAnalyzer):
    
    """ContextInstantiator based on parameter information and demand
    sets.
    """
    
    def __init__(self, symtab):
        super().__init__(symtab)
        self.queries_with_usets = OrderedSet()
    
    def rewrite_with_demand_set(self, query):
        ct = self.symtab.clausetools
        symtab = self.symtab
        
        # Determine demand parameters.
        demand_params = determine_demand_params(ct, query)
        
        # If there aren't any demand parameters, no demand transformation.
        if len(demand_params) == 0:
            return
        
        # Add demand set for symbol.
        uset = N.get_query_demand_set_name(query.name)
        uset_type = T.Set(symtab.analyze_expr_type(L.tuplify(demand_params)))
        symtab.define_relation(uset, type=uset_type)
        query.demand_set = uset
        
        self.queries_with_usets.add(query)
        
        # Rewrite AST to use it.
        query.node = ct.rewrite_with_uset(query.node, demand_params, uset)
    
    def rewrite_with_demand(self, query, context):
        return self.rewrite_with_demand_set(query)
    
    def apply_context(self, query, context):
        super().apply_context(query, context)
        
        # Don't touch non-incrementalized queries.
        if query.impl == 'normal':
            return
        
        # We can't handle non-Comp queries here.
        if not isinstance(query.node, L.Comp):
            raise AssertionError('No rule for handling demand for {} node'
                                 .format(query.node.__class__.__name__))
        
        self.rewrite_with_demand(query, context)
    
    def add_demand_function_call(self, node):
        query = self.symtab.get_queries()[node.name]
        if query not in self.queries_with_usets:
            return node
        demand_call = L.Call(N.get_query_demand_func_name(query.name),
                             [L.tuplify(query.demand_params)])
        return L.FirstThen(demand_call, node)
    
    def visit_Module(self, node):
        node = self.generic_visit(node)
        
        # Add declarations for demand functions.
        funcs = []
        for query in self.queries_with_usets:
            func = make_demand_func(query.name)
            funcs.append(func)
        
        node = node._replace(decls=tuple(funcs) + node.decls)
        return node
    
    def visit_Query(self, node):
        # Do all the fancy processing, including recursing.
        node = super().visit_Query(node)
        # Then insert a call to the demand function, if needed.
        node = self.add_demand_function_call(node)
        return node


class NestedDemandAnalyzer(DemandAnalyzer):
    
    """ContextInstantiator based on parameters, demand sets for outer
    queries, and demand queries for inner queries.
    """
    
    # A context for this visitor is a tuple whose first component
    # are the query parameters, and whose second component is
    #
    #   1) for an outermost query, None, or
    #
    #   2) for an inner query, a sequence of clauses appearing to
    #      the left of this query in the immediate containing query.
    #
    # Outermost queries (not counting queries whose impl attribute is
    # "normal") get demand sets, while inner queries get demand queries.
    #
    # We keep track of the clauses of the containing query by
    # maintaining a stack corresponding to nested queries, where each
    # stack entry lists the clauses seen so far at that level.
    
    def process(self, tree):
        self.comp_stack = []
        """Each stack entry corresponds to a level of nesting of a
        Query node for a comprehension whose impl is not "normal".
        The value of each entry is a list of the clauses at that
        level that have already been fully processed.
        """
        self.push_next_comp = False
        """Flag indicating whether the next call to visit_Comp should
        affect the comp stack. This is set when we see a Query node
        whose immediate descendant is a Comp. It helps us distinguish
        proper comprehension queries from stray non-Query Comp nodes.
        """
        tree = super().process(tree)
        return tree
    
    def push_comp(self):
        self.comp_stack.append([])
    
    def pop_comp(self):
        self.comp_stack.pop()
    
    def add_clause(self, cl):
        if len(self.comp_stack) > 0:
            self.comp_stack[-1].append(cl)
    
    def current_left_clauses(self):
        """Get the list of clauses to the left of the current containing
        comprehension query, or None if there is no such query.
        """
        return self.comp_stack[-1] if len(self.comp_stack) > 0 else None
    
    def params_from_context(self, context):
        params, _clauses = context
        return params
        
    def get_context(self, node):
        return self.get_params(node), self.current_left_clauses()
    
    def rewrite_with_demand_query(self, query, context):
        ct = self.symtab.clausetools
        symtab = self.symtab
        
        # Determine demand parameters. No demand parameters means no
        # transformation.
        demand_params = determine_demand_params(ct, query)
        if len(demand_params) == 0:
            return
        
        # Add demand set for symbol.
        demquery_name = N.get_query_demand_query_name(query.name)
        t_demand_params = symtab.analyze_expr_type(L.tuplify(demand_params))
        demquery_type = T.Set(t_demand_params)
        demquery_comp = L.Comp(L.tuplify(demand_params),
                               self.current_left_clauses())
        prefix = next(symtab.fresh_names.vars)
        demquery_comp = ct.comp_rename_lhs_vars(
                            demquery_comp, lambda x: prefix + x)
        demquery_sym = symtab.define_query(demquery_name, type=demquery_type,
                                           node=demquery_comp, impl=query.impl)
        query.demand_query = demquery_name
        
        # Rewrite AST to use it.
        demquery_node = L.Query(demquery_name, demquery_comp)
        query.node = ct.rewrite_with_demand_query(
                            query.node, demand_params, demquery_node)
    
    def rewrite_with_demand(self, query, context):
        _params, clauses = context
        
        if clauses is None:
            # Outermost, just add a U-set.
            return self.rewrite_with_demand_set(query)
        else:
            return self.rewrite_with_demand_query(query, context)
    
    def visit_Query(self, node):
        # Check for impl == "normal" using the pre-instantiated query
        # symbol, since that shouldn't change during instantiation
        # anyway.
        sym = self.symtab.get_queries()[node.name]
        if isinstance(node.query, L.Comp) and sym.impl != 'normal':
            self.push_next_comp = True
        
        return super().visit_Query(node)
    
    def comp_visit_helper(self, node):
        """Visit while marking clauses in the comp stack."""
        clauses = []
        for cl in node.clauses:
            cl = self.visit(cl)
            self.add_clause(cl)
            clauses.append(cl)
        resexp = self.visit(node.resexp)
        return node._replace(resexp=resexp, clauses=clauses)
    
    def visit_Comp(self, node):
        if self.push_next_comp:
            self.push_next_comp = False
            self.push_comp()
            node = self.comp_visit_helper(node)
            self.pop_comp()
        else:
            node = self.generic_visit(node)
        return node


def analyze_demand(tree, symtab):
    """Analyze parameter and demand information for all queries. Assign
    this information to symbol attributes and rewrite queries to use
    demand sets and demand queries.
    """
    return NestedDemandAnalyzer.run(tree, symtab)
