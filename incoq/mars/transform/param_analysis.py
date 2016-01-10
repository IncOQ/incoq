"""Analysis of scopes, query parameters, and query demand."""


__all__ = [
    'make_demand_func',
    'determine_demand_params',
    
    'ScopeBuilder',
    
    'QueryContextInstantiator',
    'ParamAnalyzer',
    'DemandAnalyzer',
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
        constr_vars = clausetools.constr_lhs_vars_from_comp(comp)
        demand_params = tuple(p for p in params if p not in constr_vars)
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
    """
    
    # We maintain a scope stack -- a list of sets of bound variables,
    # one per scope, ordered outermost first. When a Query node is seen,
    # we add an entry in the map to a shallow copy of the current scope
    # stack, aliasing the underlying sets. This way, we include
    # identifiers that are only bound after the Query node is already
    # processed. At the end, we flatten the scope stacks into singular
    # sets.
    
    def flatten_scope_stack(self, stack):
        return OrderedSet(chain(*stack))
    
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
    # outermost query will be processed first.
    
    def __init__(self, symtab):
        super().__init__()
        self.symtab = symtab
        self.query_contexts = {}
        """Map from query name to context map."""
    
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
        for inst_name, ctx in context_map.items():
            if context == ctx:
                # Found an existing instantiation. Reuse it.
                query_sym = queries[inst_name]
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
        
        # Rewrite this occurrence.
        node = query_sym.make_node()
        # Recurse.
        node = self.generic_visit(node)
        return node


class ParamAnalyzer(QueryContextInstantiator):
    
    """Add parameter information to query symbols based on the given
    scope information. Instantiate query occurrences as needed.
    """
    
    def __init__(self, symtab, scope_info):
        super().__init__(symtab)
        self.scope_info = scope_info
    
    def get_params(self, node):
        """Get parameters for the given query node. The node must be
        indexed in scope_info.
        """
        _node, scope = self.scope_info[id(node)]
        vars = L.IdentFinder.find_vars(node.query)
        params = tuple(vars.intersection(scope))
        return params
    
    def get_context(self, node):
        return self.get_params(node)
    
    def apply_context(self, query, context):
        query.params = context


class DemandAnalyzer(ParamAnalyzer):
    
    """Add parameter information as above, but also rewrite queries to
    use demand sets.
    """
    
    def __init__(self, symtab, scope_info):
        super().__init__(symtab, scope_info)
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
        if isinstance(query.node, L.Comp):
            query.node = ct.rewrite_with_uset(query.node, demand_params, uset)
    
    def apply_context(self, query, context):
        query.params = context
        
        # We can't handle non-Comp queries here.
        if not isinstance(query.node, L.Comp):
            raise AssertionError('No rule for handling demand for {} node'
                                 .format(query.node.__class__.__name__))
        
        self.rewrite_with_demand_set(query)
    
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
        query = self.symtab.get_queries()[node.name]
        if query in self.queries_with_usets:
            demand_call = L.Call(N.get_query_demand_func_name(query.name),
                                 [L.tuplify(query.demand_params)])
            node = L.FirstThen(demand_call, node)
        
        return node


def analyze_demand(tree, symtab):
    """As above, but also perform rewriting to add demand sets
    and corresponding functions.
    """
    scope_info = ScopeBuilder.run(tree)
    return DemandAnalyzer.run(tree, symtab, scope_info)
