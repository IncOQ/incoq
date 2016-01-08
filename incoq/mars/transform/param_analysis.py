"""Analysis of scopes, query parameters, and query demand."""


__all__ = [
    'QueryContextInstantiator',
    
    'ScopeBuilder',
    'ParamAnalyzer',
    'analyze_parameters',
]


from itertools import chain

from incoq.util.collections import OrderedSet
from incoq.mars.symtab import N
from incoq.mars.incast import L


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


class ParamAnalyzer(L.NodeTransformer):
    
    """Add parameter information to query symbols based on the given
    scope information. Instantiate multiple occurrences of the same query
    if the occurrences have distinct parameter information.
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
    # Context information is determined by what tuple of parameters the
    # query occurrence has.
    
    def __init__(self, symtab, scope_info):
        super().__init__()
        self.symtab = symtab
        self.scope_info = scope_info
        self.query_contexts = {}
    
    def visit_Query(self, node):
        query_sym = self.symtab.get_queries()[node.name]
        
        # Lookup scope info before we do any transformation.
        _node, scope = self.scope_info[id(node)]
        
        # Get variables used in this query, including subqueries.
        # Parameters are listed in the order found by IdentFinder.
        vars = L.IdentFinder.find_vars(node.query)
        params = tuple(vars.intersection(scope))
        context = params
        
        # Rewrite as per context map.
        context_map = self.query_contexts.setdefault(node.name, {})
        for inst_name, ctx in context_map.items():
            if context == ctx:
                # Found an existing instantiation.
                # Rewrite to use its name.
                node = node._replace(name=inst_name)
                break
        else:
            if len(context_map) == 0:
                # No instantiations so far, use the original query name
                # but update its parameter info.
                context_map[node.name] = context
                query_sym.params = params
            else:
                # Create a new query instantiation entry.
                num = len(context_map) + 1
                inst_name = N.get_query_inst_name(node.name, str(num))
                context_map[inst_name] = context
                
                # Create its symbol.
                attrs = query_sym.clone_attrs()
                attrs['params'] = params
                self.symtab.define_query(inst_name, **attrs)
        
        # Recurse.
        node = self.generic_visit(node)


def analyze_parameters(tree, symtab):
    """Assign parameter information to queries and instantiate
    query occurrences as needed.
    """
    scope_info = ScopeBuilder.run(tree)
    return ParamAnalyzer.run(tree, symtab, scope_info)
