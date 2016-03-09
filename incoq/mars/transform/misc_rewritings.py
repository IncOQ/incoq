"""Rewritings that are not language-level pre/post processings."""


__all__ = [
    'rewrite_vars_clauses',
    'lift_firstthen',
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


def lift_firstthen(tree, symtab):
    """Lift FirstThen nodes outside of Unwrap nodes."""
    class Trans(L.NodeTransformer):
        def visit_Unwrap(self, node):
            node = self.generic_visit(node)
            
            if isinstance(node.value, L.FirstThen):
                # Shuffle the Unwrap and FirstThen's then child.
                firstthen = node.value
                new_unwrap = node._replace(value=firstthen.then)
                node = firstthen._replace(then=new_unwrap)
            
            return node
    
    return Trans.run(tree)
