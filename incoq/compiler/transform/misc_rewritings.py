"""Rewritings that are not language-level pre/post processings."""


__all__ = [
    'mark_query_forms',
    'unmark_normal_impl',
    'rewrite_vars_clauses',
    'lift_firstthen',
    'count_updates',
    'reorder_clauses',
    'distalgo_preprocess',
    'rewrite_aggregates',
    'elim_dead_funcs',
]


from incoq.compiler.incast import L
from incoq.compiler.symbol import S


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
    kindcount = 0
    
    class RelFinder(S.QueryRewriter):
        
        def rewrite_comp(self, symbol, name, comp):
            # Count number of unique relations in this query,
            # add that to the kind count, then union that with
            # all the relations seen in any query so far.
            thiscomp_rels = set()
            
            for cl in comp.clauses:
                if isinstance(cl, (L.VarsMember, L.Member)):
                    if isinstance(cl.iter, (L.Wrap, L.Unwrap)):
                        if isinstance(cl.iter.value, L.Name):
                            thiscomp_rels.add(cl.iter.value.id)
                else:
                    rel = ct.rhs_rel(cl)
                    if rel is not None:
                        thiscomp_rels.add(rel)
            
            nonlocal kindcount
            kindcount += len(thiscomp_rels)
            rels.update(thiscomp_rels)
        
        def rewrite_aggr(self, symbol, name, aggr):
            oper = aggr.value
            if isinstance(oper, L.Unwrap):
                oper = oper.value
            if isinstance(oper, L.ImgLookup):
                oper = oper.set
            
            if isinstance(oper, L.Name):
                if oper.id not in rels:
                    rels.add(oper.id)
                    nonlocal kindcount
                    kindcount += 1
    
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
    # Double kindcount for counting additions and removals.
    symtab.stats['updatekinds_input'] = kindcount * 2


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


def distalgo_preprocess(tree, symtab):
    """Special rewriting for DistAlgo inc interface.
    
    Effects:
        - replace len() with count()
    """
    class LenReplacer(L.NodeTransformer):
        def visit_Call(self, node):
            node = self.generic_visit(node)
            if node.func == 'len':
                if not len(node.args) == 1:
                    raise L.ProgramError('Expected one argument for len()')
                return L.Aggr(L.Count(), node.args[0])
            return node
    
    tree = LenReplacer.run(tree)
    return tree


def rewrite_aggregates(tree, symtab):
    """Rewrite a min/max of a set union of set terms, by distributing
    the query down to the non-set-literal terms, and combining the terms
    with min2/max2
    """
    class Rewriter(S.QueryRewriter):
        expand = True
        
        def rewrite_aggr(self, symbol, name, aggr):
            # Only operate on min and max nodes.
            if isinstance(aggr.op, L.Min):
                func = 'min2'
            elif isinstance(aggr.op, L.Max):
                func = 'max2'
            else:
                return
            
            parts = L.get_setunion(aggr.value)
            if len(parts) <= 1:
                return
            multiple_queries = \
                len([p for p in parts if not isinstance(p, L.Set)]) > 1
            
            i = 2
            done_first_query = False
            new_parts = []
            for p in parts:
                if isinstance(p, L.Set):
                    # Flatten the literal elements as arguments to
                    # min2/max2.
                    new_parts.extend(p.elts)
                else:
                    new_query_node = aggr._replace(value=p)
                    if done_first_query:
                        # Create a new query symbol and node for this
                        # non-literal argument.
                        new_name = name + '_aggrop' + str(i)
                        i += 1
                        new_parts.append(L.Query(new_name, new_query_node,
                                                 None))
                        symtab.define_query(new_name, node=new_query_node,
                                            impl=symbol.impl)
                    else:
                        # Push the Query node down to the first non-literal
                        # argument.
                        new_parts.append(L.Query(name, new_query_node, None))
                        symbol.node = new_query_node
                        done_first_query = True
            
            return L.Call(func, new_parts)
    
    tree = Rewriter.run(tree, symtab)
    return tree


def elim_dead_funcs(tree, symtab):
    """Remove uncalled maintenance functions."""
    called = set()
    
    class CallFinder(L.NodeVisitor):
        def visit_Call(self, node):
            self.generic_visit(node)
            if node.func in symtab.maint_funcs:
                called.add(node.func)
    CallFinder.run(tree)
    
    class CallDeleter(L.NodeTransformer):
        def visit_Fun(self, node):
            if (node.name in symtab.maint_funcs and
                node.name not in called):
                return ()
    tree = CallDeleter.run(tree)
    
    return tree
