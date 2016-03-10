"""Rewritings that are not language-level pre/post processings."""


__all__ = [
    'mark_query_forms',
    'rewrite_vars_clauses',
    'lift_firstthen',
]


from incoq.mars.incast import L
from incoq.mars.symbol import S


def mark_query_forms(tree, symtab):
    """Create new queries for unmarked comprehensions and aggregates."""
    
    class Marker(L.NodeTransformer):
        
        """Transformer to find and mark comps and aggrs not already
        registered as queries.
        """
        
        def __init__(self, skipfirst=False):
            super().__init__()
            self.skipfirst = skipfirst
            """If True, consider the top-most node we're called on as
            already existing inside a Query node.
            """
        
        def process(self, tree):
            self.firstnode = tree
            tree = super().process(tree)
            return tree
        
        def visit_Query(self, node):
            # Skip immediate child.
            query = self.generic_visit(node.query)
            if query is not node.query:
                node = node._replace(query=query)
            return node
        
        def query_helper(self, node):
            first = node is self.firstnode
            
            node = self.generic_visit(node)
            
            # Don't process first node if requested to skip.
            if first:
                return node
            
            name = next(symtab.fresh_names.queries)
            symtab.define_query(name, node=node)
            node = L.Query(name, node, None)
            return node
        
        visit_Comp = query_helper
        visit_Aggr = query_helper
    
    class Rewriter(S.QueryRewriter):
        def rewrite(self, symbol, name, expr):
            if not isinstance(expr, L.Comp):
                return
            if symbol.impl is S.Normal:
                return
            
            return Marker.run(expr, skipfirst=True)
    
    # Use a rewriter so that we process comps and aggregates appearing
    # inside outer query definitions consistently.
    tree = Rewriter.run(tree, symtab)
    # Then do another pass to get all the ones not in an outer query.
    tree = Marker.run(tree)
    
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
