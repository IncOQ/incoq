"""Tools for analyzing and inlining functions."""


__all__ = [
    'analyze_functions',
]


from incoq.util.collections import OrderedSet
from incoq.util.topsort import topsort, get_cycle

from . import nodes as L


class FunctionCallGraph:
    
    """A structure including call graph information for the functions in
    a program.
    """
    
    def __init__(self):
        self.param_map = {}
        """Map from function name to list of formal parameters."""
        self.body_map = {}
        """Map from function name to body AST (sequence of statements)."""
        self.calls_map = {}
        """Map from function name to OrderedSet of called function names."""
        self.calledby_map = {}
        """Map from function name to OrderedSet of names of functions
        calling it.
        """
        self.order = []
        """All function names, in some topological order, or None if
        there is no topological order (i.e., possible recursion).
        """


def analyze_functions(tree, all_funcs, *, allow_recursion=False):
    """Produce a FunctionCallGraph. all_funcs is all the name of
    functions that are to be included in the graph. If allow_recursion
    is False and the call graph is cyclic among all_funcs, ProgramError
    is raised.
    """
    graph = FunctionCallGraph()
    
    for func in all_funcs:
        graph.calls_map[func] = OrderedSet()
        graph.calledby_map[func] = OrderedSet()
    
    class Visitor(L.NodeVisitor):
        def process(self, tree):
            self.current_func = None
            super().process(tree)
        
        def visit_Fun(self, node):
            if self.current_func is not None:
                # Don't analyze nested functions.
                self.generic_visit(node)
                return
            
            name = node.name
            if name not in all_funcs:
                return
            
            graph.param_map[name] = node.args
            graph.body_map[name] = node.body
            
            self.current_func = name
            self.generic_visit(node)
            self.current_func = None
        
        def visit_Call(self, node):
            self.generic_visit(node)
            
            source = self.current_func
            target = node.func
            if source is not None and target in all_funcs:
                graph.calls_map[source].add(target)
                graph.calledby_map[target].add(source)
    
    Visitor.run(tree)
    
    edges = {(x, y) for x, outedges in graph.calledby_map.items()
                    for y in outedges}
    order = topsort(all_funcs, edges)
    if order is None and not allow_recursion:
        raise L.ProgramError('Recursive functions found: ' +
                             str(get_cycle(all_funcs, edges)))
    graph.order = order
    
    return graph
