"""Rewritings that are not language-level pre/post processings."""


__all__ = [
    'mark_query_forms',
    'unmark_normal_impl',
    'rewrite_vars_clauses',
    'lift_firstthen',
    'count_updates',
    'reorder_clauses',
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
            return Marker.run(expr, skipfirst=True)
    
    # Use a rewriter so that we process comps and aggregates appearing
    # inside outer query definitions consistently.
    tree = Rewriter.run(tree, symtab)
    # Then do another pass to get all the ones not in an outer query.
    tree = Marker.run(tree)
    
    return tree


def unmark_normal_impl(tree, symtab):
    """Eliminate the Query node and symbol for queries with Normal impl."""
    removed = set()
    
    class Rewriter(S.QueryRewriter):
        expand = True
        def rewrite(self, symbol, name, expr):
            if symbol.impl is S.Normal:
                removed.add(symbol)
                return expr
    
    tree = Rewriter.run(tree, symtab)
    for symbol in removed:
        del symtab.symbols[symbol.name]
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
        def rewrite_comp(self, symbol, name, comp):
            return VarsClausesRewriter.run(comp)
    
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


def count_updates(tree, symtab):
    """Gather statistics about the number of updates appearing in the
    program.
    
    An update is a change to a relation that appears in at least
    one of the relations used by a comprehension or aggregate.
    """
    ct = symtab.clausetools
    
    # Determine relations in use.
    rels = set()
    
    class RelFinder(S.QueryRewriter):
        
        def rewrite_comp(self, symbol, name, comp):
            for cl in comp.clauses:
                if isinstance(cl, (L.VarsMember, L.Member)):
                    if isinstance(cl.iter, (L.Wrap, L.Unwrap)):
                        if isinstance(cl.iter.value, L.Name):
                            rels.add(cl.iter.value.id)
                else:
                    rel = ct.rhs_rel(cl)
                    if rel is not None:
                        rels.add(rel)
        
        def rewrite_aggr(self, symbol, name, aggr):
            oper = aggr.value
            if isinstance(oper, L.Unwrap):
                oper = oper.value
            if isinstance(oper, L.ImgLookup):
                oper = oper.set
            
            if isinstance(oper, L.Name):
                rels.add(oper.id)
    
    RelFinder.run(tree, symtab)
    
    # Find updates to used relations.
    
    count = 0
    
    class UpdateFinder(L.NodeVisitor):
        def visit_RelUpdate(self, node):
            nonlocal count
            if node.rel in rels:
                count += 1
        
        def visit_RelClear(self, node):
            nonlocal count
            if node.rel in rels:
                count += 1
    
    UpdateFinder.run(tree)
    
    symtab.stats['updates_input'] = count


def reorder_clauses(tree, symtab):
    """Rearrange clause orders on a per-query basis. This is useful for
    changing the demand strategy.
    """
    class Rewriter(S.QueryRewriter):
        def rewrite_comp(self, symbol, name, comp):
            if symbol.clause_reorder is not None:
                indices = [i - 1 for i in symbol.clause_reorder]
                if not sorted(indices) == list(range(len(comp.clauses))):
                    raise L.ProgramError(
                        'Bad clause_reorder list for query: {}, {}'.format(
                        name, symbol.clause_reorder))
                clauses = [comp.clauses[i] for i in indices]
                comp = comp._replace(clauses=clauses)
            return comp
    
    tree = Rewriter.run(tree, symtab)
    
    return tree
