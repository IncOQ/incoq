"""Analysis of scopes, query parameters, and query demand."""


__all__ = [
    'ScopeBuilder',
    'ParamAnalyzer',
]


from itertools import chain

from incoq.util.collections import OrderedSet
from incoq.mars.incast import L


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
    scope information.
    """
    
    def __init__(self, symtab, scope_info):
        super().__init__()
        self.symtab = symtab
        self.scope_info = scope_info
    
    def visit_Query(self, node):
        # Lookup scope info before we do any recursive transformation.
        _node, scope = self.scope_info[id(node)]
        
        # Get variables used in this query, including subqueries.
        # Parameters are listed in the order found by IdentFinder.
        vars = L.IdentFinder.find_vars(node.query)
        params = tuple(vars.intersection(scope))
        
        # Update symbol info.
        sym = self.symtab.get_queries()[node.name]
        sym.params = params
        
        # Recurse.
        node = self.generic_visit(node)
