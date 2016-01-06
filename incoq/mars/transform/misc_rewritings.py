"""Rewritings that are not language-level pre/post processings."""


__all__ = [
    'relationalize_comp_queries',
]


from incoq.mars.incast import L
from incoq.mars.symtab import QueryRewriter


def relationalize_comp_queries(tree, symtab):
    """Rewrite each comprehension query so that the comprehension result
    expression is a tuple.
    """
    changed_queries = set()
    
    class CompRewriter(QueryRewriter):
        def rewrite(self, symbol, name, expr):
            if not isinstance(expr, L.Comp):
                return None
            if isinstance(expr.resexp, L.Tuple):
                return None
            
            changed_queries.add(name)
            new_resexp = L.Tuple([expr.resexp])
            return expr._replace(resexp=new_resexp)
    
    class UnwrapAdder(QueryRewriter):
        def rewrite(self, symbol, name, expr):
            if name in changed_queries:
                return L.Unwrap(L.Query(name, expr))
            return None
    
    tree = CompRewriter.run(tree, symtab)
    tree = UnwrapAdder.run(tree, symtab, expand=True)
    
    return tree
