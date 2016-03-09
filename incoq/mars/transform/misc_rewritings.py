"""Rewritings that are not language-level pre/post processings."""


__all__ = [
    'rewrite_vars_clauses',
]


from incoq.mars.incast import L
from incoq.mars.symbol import S


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
