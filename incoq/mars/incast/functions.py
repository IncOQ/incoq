"""Tools for analyzing and inlining functions."""


__all__ = [
    'get_defined_functions',
    'analyze_functions',
    'Inliner',
    'inline_functions',
]


from incoq.util.collections import OrderedSet
from incoq.util.topsort import topsort, get_cycle

from . import nodes as L
from .error import ProgramError, TransformationError


def get_defined_functions(tree):
    """Find names of top-level functions in a block of code.""" 
    names = OrderedSet()
    class Finder(L.NodeVisitor):
        def visit_Fun(self, node):
            names.add(node.name)
    Finder.run(tree)
    return names


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


def analyze_functions(tree, funcs, *, allow_recursion=False):
    """Produce a FunctionCallGraph. funcs is all the name of functions
    that are to be included in the graph. If allow_recursion is False
    and the call graph is cyclic among all_funcs, ProgramError is
    raised.
    """
    graph = FunctionCallGraph()
    
    for func in funcs:
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
            if name not in funcs:
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
            if source is not None and target in funcs:
                graph.calls_map[source].add(target)
                graph.calledby_map[target].add(source)
    
    Visitor.run(tree)
    
    edges = {(x, y) for x, outedges in graph.calledby_map.items()
                    for y in outedges}
    order = topsort(funcs, edges)
    if order is None and not allow_recursion:
        raise ProgramError('Recursive functions found: ' +
                           str(get_cycle(funcs, edges)))
    graph.order = order
    
    return graph


class Inliner(L.NodeTransformer):
    
    """Replace statement-level calls in a block of code with the
    expansions of the corresponding body in body_map. The actual
    argument expressions are assigned to the formal parameters in
    param_map.
    
    Caution: In general, this transformation is not sound because we
    don't prevent variable capture. But this should only be used for
    maintenance functions anyway.
    """
    
    def __init__(self, param_map, body_map):
        super().__init__()
        self.param_map = param_map
        self.body_map = body_map
    
    def visit_Expr(self, node):
        if not isinstance(node.value, L.Call):
            return node
        call = node.value
        name = call.func
        args = call.args
        if name not in self.body_map:
            return node
        body = self.body_map[name]
        params = self.param_map[name]
        
        assert len(params) == len(args)
        if len(params) > 0:
            param_init_code = (L.DecompAssign(params, L.Tuple(args)),)
        else:
            param_init_code = ()
        code = param_init_code + body
        return code


def inline_functions(tree, funcs):
    # Determine function call graph.
    graph = analyze_functions(tree, funcs)
    
    # Sanity test: Make sure none of the functions we're supposed to
    # inline have a return statement.
    class ReturnComplainer(L.NodeVisitor):
        def visit_Return(self, node):
            raise TransformationError('Unexpected return statement in '
                                      'inlined function {}'.format(f))
    for f, body in graph.body_map.items():
        ReturnComplainer.run(body)
    
    # In topological order, pick a function and expand the code listed
    # in the graph's body_map. The order ensures that the body_map
    # already contains entries for all called functions that are to be
    # inlined.
    for f in graph.order:
        new_body = graph.body_map[f]
        new_body = Inliner.run(new_body, graph.param_map, graph.body_map)
        graph.body_map[f] = new_body
    
    # Delete the function definitions so we don't need to process
    # them in the following expansion step.
    class Eliminator(L.NodeTransformer):
        def visit_Fun(self, node):
            if node.name in funcs:
                return ()
            return node
    tree = Eliminator.run(tree)
    
    tree = Inliner.run(tree, graph.param_map, graph.body_map)
    
    # Make sure there are no lingering non-statement-level calls.
    class CallComplainer(L.NodeVisitor):
        def visit_Call(self, node):
            if node.func in funcs:
                raise TransformationError(
                    'Call to function {} remains after inlining'
                    .format(node.func))
    CallComplainer.run(tree)
    
    return tree
