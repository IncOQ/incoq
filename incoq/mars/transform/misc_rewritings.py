"""Rewritings that are not language-level pre/post processings."""


__all__ = [
    'relationalize_comp_queries',
    'rewrite_vars_clauses',
]


from incoq.mars.incast import L
from incoq.mars.type import T
from incoq.mars.symbol import S


def rewrite_with_unwraps(tree, symtab):
    """For every comprehension query with a non-tuple result expression,
    rewrite the result expression to be a singleton tuple and wrap its
    occurrence in an Unwrap node.
    """
    affected_queries = set()
    
    class UnwrapRewriter(S.QueryRewriter):
        def visit_Query(self, node):
            node = super().visit_Query(node)
            # Add an Unwrap node.
            if node.name in affected_queries:
                node = L.Unwrap(node)
            return node
        
        def rewrite(self, symbol, name, expr):
            if not isinstance(expr, L.Comp):
                return
            if symbol.impl is S.Normal:
                return
            comp = expr
            
            # No effect if it's already a tuple.
            if isinstance(comp.resexp, L.Tuple):
                return
            affected_queries.add(name)
            
            comp = comp._replace(resexp=L.Tuple([comp.resexp]))
            t = symbol.type
            t = t.join(T.Set(T.Bottom))
            assert t.issmaller(T.Set(T.Top))
            symbol.type = T.Set(T.Tuple([t.elt]))
            return comp
    
    tree = UnwrapRewriter.run(tree, symtab)
    return tree


def rewrite_with_wraps(tree, symtab):
    """For every Member node in a comprehension query, if the LHS is a
    single variable, rewrite it as a VarsMember with the RHS in a Wrap
    node.
    """
    def process(expr):
        if not (isinstance(expr, L.Member) and
                isinstance(expr.target, L.Name)):
            return expr, [], []
        
        if isinstance(expr.iter, L.Unwrap):
            rhs = expr.iter.value
        else:
            rhs = L.Wrap(expr.iter)
        cl = L.VarsMember([expr.target.id], rhs)
        return cl, [], []
    
    class WrapRewriter(S.QueryRewriter):
        def rewrite(self, symbol, name, expr):
            if not isinstance(expr, L.Comp):
                return
            if symbol.impl is S.Normal:
                return
            comp = expr
            
            comp = L.rewrite_comp(comp, process)
            return comp
    
    tree = WrapRewriter.run(tree, symtab)
    return tree


def relationalize_comp_queries(tree, symtab):
    """Rewrite each comprehension query so that it is relational. The
    query must already be flattened.
    """
    tree = rewrite_with_unwraps(tree, symtab)
    tree = rewrite_with_wraps(tree, symtab)
    return tree


class VarsClausesRewriter(L.NodeTransformer):
    
    """Rewrite general Member clauses of the form
    
        <tuple> in <query>
    
    as VarsMember clauses.
    """
    
    def visit_Member(self, node):
        node = self.generic_visit(node)
        
        if (L.is_tuple_of_names(node.target) and
            isinstance(node.iter, L.Query)):
            node = L.VarsMember(L.detuplify(node.target), node.iter)
        
        return node

def rewrite_vars_clauses(tree, symtab):
    class Rewriter(S.QueryRewriter):
        def rewrite(self, symbol, name, expr):
            if not isinstance(expr, L.Comp):
                return
            if symbol.impl is S.Normal:
                return
            
            return VarsClausesRewriter.run(expr)
    
    return Rewriter.run(tree, symtab)
