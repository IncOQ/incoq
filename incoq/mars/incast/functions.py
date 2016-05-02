"""Tools for analyzing and inlining functions."""


__all__ = [
    'get_defined_functions',
    'prefix_locals',
    'analyze_functions',
    'Inliner',
    'inline_functions',
]


from incoq.util.collections import OrderedSet
from incoq.util.topsort import topsort_helper, get_cycle

from . import nodes as L
from .tools import BindingFinder, Templater
from .error import ProgramError, TransformationError


def get_defined_functions(tree):
    """Find names of top-level functions in a block of code.""" 
    names = OrderedSet()
    class Finder(L.NodeVisitor):
        def visit_Fun(self, node):
            names.add(node.name)
    Finder.run(tree)
    return names


def prefix_locals(tree, prefix, extra_boundvars):
    """Rename the local variables in a block of code with the given
    prefix. The extra_boundvars are treated as additional variables
    known to be bound even if they don't appear in a binding occurrence
    within tree.
    """
    localvars = OrderedSet(extra_boundvars)
    localvars.update(BindingFinder.run(tree))
    tree = Templater.run(tree, {v: prefix + v for v in localvars})
    return tree


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
    
    edges = [(x, y) for x, outedges in graph.calledby_map.items()
                    for y in outedges]
    order, rem_funcs, _rem_edges = topsort_helper(funcs, edges)
    if len(rem_funcs) > 0 and not allow_recursion:
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
    
    def __init__(self, param_map, body_map, prefixes, *,
                 comment_markers=False):
        super().__init__()
        self.param_map = param_map
        self.body_map = body_map
        self.prefixes = prefixes
        self.comment_markers = comment_markers
    
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
        
        # Generate a new prefix, use it on the body and the params.
        prefix = next(self.prefixes)
        body = prefix_locals(body, prefix, params)
        params = tuple(prefix + p for p in params)
        
        assert len(params) == len(args)
        if len(params) > 0:
            param_init_code = (L.DecompAssign(params, L.Tuple(args)),)
        else:
            param_init_code = ()
        
        code = param_init_code + body
        
        if self.comment_markers:
            code = ((L.Comment('Begin inlined {}.'.format(name)),) +
                    code +
                    (L.Comment('End inlined {}.'.format(name)),))
        
        return code


def inline_functions(tree, funcs, prefixes, *,
                     comment_markers=False):
    """Inline all of the functions named in funcs, instantiating local
    variables using the given prefixes. The functions must be acyclic,
    not contain return statements, and only be called at statement
    level.
    """
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
        new_body = Inliner.run(new_body, graph.param_map, graph.body_map,
                               prefixes, comment_markers=comment_markers)
        graph.body_map[f] = new_body
    
    # Delete the function definitions so we don't need to process
    # them in the following expansion step.
    class Eliminator(L.NodeTransformer):
        def visit_Fun(self, node):
            if node.name in funcs:
                return ()
            return node
    tree = Eliminator.run(tree)
    
    tree = Inliner.run(tree, graph.param_map, graph.body_map, prefixes,
                       comment_markers=comment_markers)
    
    # Make sure there are no lingering non-statement-level calls.
    class CallComplainer(L.NodeVisitor):
        def visit_Call(self, node):
            if node.func in funcs:
                raise TransformationError(
                    'Call to function {} remains after inlining'
                    .format(node.func))
    CallComplainer.run(tree)
    
    return tree
