"""Inlining transformation."""


__all__ = [
    'PlainFunctionFinder',
    'FunctionInfoGetter',
    'CallInliner',
    'inline_functions',
]


from incoq.util.collections import SetDict, OrderedSet
from incoq.util.topsort import topsort, get_cycle

from .nodes import *
from .structconv import NodeVisitor, NodeTransformer, Templater
from .helpers import (is_plainfuncdef, get_plainfuncdef,
                      is_plaincall, get_plaincall)
from .util import FuncEliminator, N


class PlainFunctionFinder(NodeVisitor):
    
    """Return all names of top-level functions that only use plain
    arguments and calls. Non-top-level function definitions are not
    analyzed. Calls of non-Name nodes are not analyzed. It is an
    error for the functions to have multiple definitions.
    
    If stmt_only is True, functions that are called in expression
    context are excluded.
    """
    
    def __init__(self, *, stmt_only):
        super().__init__()
        self.stmt_only = stmt_only
    
    def process(self, tree):
        self.toplevel_funcs = OrderedSet()
        self.excluded_funcs = set()
        
        self.infunc = False
        super().process(tree)
        assert not self.infunc
        
        return self.toplevel_funcs - self.excluded_funcs
    
    def visit_FunctionDef(self, node):
        if self.infunc:
            return
        
        name = node.name
        assert name not in self.toplevel_funcs, \
            'Multiple definitions of function ' + name
        self.toplevel_funcs.add(name)
        
        if not is_plainfuncdef(node):
            self.excluded_funcs.add(name)
        
        self.infunc = True
        self.generic_visit(node)
        self.infunc = False
    
    def visit_Expr(self, node):
        if self.stmt_only and isinstance(node.value, Call):
            # Treat Call nodes specially by directly calling
            # generic_visit() on them, bypassing the visit_Call()
            # behavior that would mark it as a bad call.
            self.generic_visit(node.value)
        else:
            # Otherwise just recurse as normal.
            self.visit(node.value)
    
    def visit_Call(self, node):
        if not isinstance(node.func, Name):
            self.generic_visit(node)
            return
        name = node.func.id
        
        if self.stmt_only:
            # We only get here if this call occurred in expression
            # context.
            self.excluded_funcs.add(name)
        else:
            if not is_plaincall(node):
                self.excluded_funcs.add(name)
        
        self.generic_visit(node)
    
    def visit_DemQuery(self, node):
        # For our purposes here, these are interpreted as calls in
        # expression context.
        name = N.queryfunc(node.demname)
        if self.stmt_only:
            self.excluded_funcs.add(name)
        
        self.generic_visit(node)


class FunctionInfoGetter(NodeVisitor):
    
    """Builds structural information about the given set of functions,
    where each function satisfies the requirements given above for
    PlainFunctionFinder. Returns the following:
    
        1) a mapping from function name to tuple of parameters
        
        2) a mapping from function name to body code
        
        3) an edge relation for a call graph, holding (x, y) if
           function x calls function y and both x and y are in
           the given set of function names
        
        4) a topological sorting of the functions (fewest dependencies
           first) if one exists, or else None
    
    If require_nonrecursive is True, raise an error if a topological
    sorting can't be generated due to recursion.
    """ 
    
    def __init__(self, funcs, *, require_nonrecursive):
        super().__init__()
        self.funcs = funcs
        self.require_nonrecursive = require_nonrecursive
    
    def process(self, tree):
        self.param_map = {}
        self.body_map = {}
        self.adj_map = SetDict()
        
        self.current_func = None
        super().process(tree)
        assert self.current_func is None
        
        edges = {(x, y) for x in self.adj_map for y in self.adj_map[x]}
        order = topsort(self.funcs, edges)
        if order is None and self.require_nonrecursive:
            raise AssertionError('Recursive functions found: ' +
                                 str(get_cycle(self.funcs, edges)))
        if order is not None:
            order.reverse()
        
        return self.param_map, self.body_map, edges, order
    
    def visit_FunctionDef(self, node):
        if self.current_func is not None:
            return
        
        name = node.name
        if name not in self.funcs:
            return
        
        self.param_map[name] = tuple(a.arg for a in node.args.args)
        self.body_map[name] = node.body
        
        self.current_func = name
        self.generic_visit(node)
        self.current_func = None
    
    def visit_Call(self, node):
        if self.current_func is not None and is_plaincall(node):
            name, _args = get_plaincall(node)
            if self.current_func in self.funcs and name in self.funcs:
                self.adj_map[self.current_func].add(name)
        
        self.generic_visit(node)
    
    def visit_DemQuery(self, node):
        name = N.queryfunc(node.demname)
        if self.current_func is not None:
            if self.current_func in self.funcs and name in self.funcs:
                self.adj_map[self.current_func].add(name)
        
        self.generic_visit(node)


class CallInliner(NodeTransformer):
    
    """Replace statement-level calls in a block of code according to
    the given body_map. Occurrences of formal parameters in the body_map
    get replaced with the actual parameter expressions of the call.
    """
    
    def __init__(self, param_map, body_map):
        super().__init__()
        self.param_map = param_map
        self.body_map = body_map
    
    def visit_Expr(self, node):
        if not is_plaincall(node.value):
            return None
        name, args = get_plaincall(node.value)
        
        if name in self.body_map:
            body = self.body_map[name]
            params = self.param_map[name]
            subst = dict(zip(params, args))
            body = Templater.run(body, subst)
            return body
        else:
            return None


def inline_functions(tree, funcs):
    """Inline the given set of functions, removing their definitions.
    Each function must satisfy the requirements of PlainFunctionFinder
    above.
    """
    found_funcs = PlainFunctionFinder.run(tree, stmt_only=True)
    if not set(funcs).issubset(found_funcs):
        bad_funcs = set(found_funcs).difference(funcs)
        raise AssertionError('Cannot inline functions: ' +
                             ', '.join(bad_funcs))
    
    param_map, body_map, edges, order = FunctionInfoGetter.run(
                            tree, funcs, require_nonrecursive=True)
    
    # In topological order, pick a function and expand the code
    # listed in its body_map. The order ensures that the substitution
    # map already contains entries for all called functions that are
    # to be inlined.
    for f in order:
        new_body = body_map[f]
        new_body = CallInliner.run(new_body, param_map, body_map)
        body_map[f] = new_body
    
    # Delete the function definitions so we don't need to process
    # them in the following expansion step.
    tree = FuncEliminator.run(tree, lambda n: n in funcs)
    
    tree = CallInliner.run(tree, param_map, body_map)
    return tree
