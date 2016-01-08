"""Transformation to implement comprehensions."""


__all__ = [
    'JoinExpander',
    'make_comp_maint_func',
    'CompMaintainer',
    'incrementalize_comp',
    'expand_maintjoins',
]


from incoq.mars.incast import L
import incoq.mars.types as T
from incoq.mars.symtab import N, QueryRewriter
from .order import order_clauses


class JoinExpander(L.NodeTransformer):
    
    """Rewrites DecompFor loops over joins by expanding the join into
    its nested clauses.
    
    A DecompFor loop is rewritable if the right-hand side is a Query
    node wrapping a Comp node that is a join, and if the target of
    the loop consists of the same variables (in the same order) as
    those returned by the join.
    
    A rewritable DecompFor loop is rewritten if the query name matches
    one of the given names. Other occurrences of the query are ignored.
    """
    
    def __init__(self, clausetools, queries):
        super().__init__()
        self.clausetools = clausetools
        """ClauseTools instance."""
        self.queries = queries
        """Names of queries that wrap joins that are to be expanded.
        If None, expand all rewritable joins.
        """
    
    def visit_DecompFor(self, node):
        ct = self.clausetools
        
        node = super().generic_visit(node)
        
        # Skip if the RHS isn't a comprehension query for which
        # expansion was requested.
        if not (isinstance(node.iter, L.Query) and
                node.iter.name in self.queries and
                isinstance(node.iter.query, L.Comp)):
            return node
        comp = node.iter.query
        
        # Check that it's a join and the variables match the loop target.
        if not (ct.is_join(comp) and
                ct.lhs_vars_from_comp(comp) == node.vars):
            return node
        
        # Reorder the clauses according to the greedy heuristic.
        clauses = order_clauses(self.clausetools, comp.clauses)
        comp = comp._replace(clauses=clauses)
        
        return ct.get_code_for_clauses(comp.clauses, (), node.body)


def make_comp_maint_func(clausetools, fresh_vars, fresh_join_names,
                         comp, result_var, rel, op, *,
                         counted):
    """Make maintenance function for a comprehension."""
    assert isinstance(op, (L.SetAdd, L.SetRemove))
    
    op_name = L.set_update_name(op)
    func_name = N.get_maint_func_name(result_var, rel, op_name)
    
    update = L.RelUpdate(rel, op, '_elem')
    code = clausetools.get_maint_code(fresh_vars, fresh_join_names,
                                      comp, result_var, update,
                                      counted=counted)
    func = L.Parser.ps('''
        def _FUNC(_elem):
            _CODE
        ''', subst={'_FUNC': func_name,
                    '<c>_CODE': code})
    
    return func


class CompMaintainer(L.NodeTransformer):
    
    """Insert comprehension maintenance functions and calls to these
    functions at relevant updates.
    """
    
    def __init__(self, clausetools, fresh_vars, fresh_join_names,
                 comp, result_var, *,
                 counted):
        super().__init__()
        self.clausetools = clausetools
        self.fresh_vars = fresh_vars
        self.fresh_join_names = fresh_join_names
        self.comp = comp
        self.result_var = result_var
        self.counted = counted
        
        self.rels = self.clausetools.rhs_rels_from_comp(self.comp)
    
    def visit_Module(self, node):
        ct = self.clausetools
        
        node = self.generic_visit(node)
        
        funcs = []
        for rel in self.rels:
            for op in [L.SetAdd(), L.SetRemove()]:
                    func = make_comp_maint_func(
                            ct, self.fresh_vars, self.fresh_join_names,
                            self.comp, self.result_var, rel, op,
                            counted=self.counted)
                    funcs.append(func)
        
        node = node._replace(decls=tuple(funcs) + node.decls)
        return node
    
    def visit_RelUpdate(self, node):
        if not isinstance(node.op, (L.SetAdd, L.SetRemove)):
            return node
        if node.rel not in self.rels:
            return node
        
        op_name = L.set_update_name(node.op)
        func_name = N.get_maint_func_name(self.result_var, node.rel, op_name)
        
        code = (node,)
        call_code = (L.Expr(L.Call(func_name, [L.Name(node.elem)])),)
        code = L.insert_rel_maint(code, call_code, node.op)
        return code


def incrementalize_comp(tree, symtab, query, result_var):
    """Incrementalize the given comprehension query symbol. Insert
    maintenance functions and calls at updates, and replace all
    occurrences of the query (including within other queries in the
    symbol table) with uses of the stored result variable.
    """
    clausetools = symtab.clausetools
    fresh_vars = symtab.fresh_names.vars
    comp = query.node
    
    comp = clausetools.rewrite_with_patterns(comp, query.params)
    comp = clausetools.elim_sameclause_eqs(comp)
    
    if query.params != ():
        assert isinstance(comp.resexp, L.Tuple)
        orig_arity = len(comp.resexp.elts)
        comp = clausetools.rewrite_resexp_with_params(comp, query.params)
        
        # Update the query symbol type.
        assert (isinstance(query.type, T.Set) and
                isinstance(query.type.elt, T.Tuple))
        query.type = symtab.analyze_expr_type(comp)
    
    query.maint_joins = []
    
    used_join_names = []
    
    def fresh_join_names():
        for join_name in N.fresh_name_generator(query.name + '_J{}'):
            used_join_names.append(join_name)
            yield join_name
    
    tree = CompMaintainer.run(tree, clausetools, fresh_vars,
                              fresh_join_names(),
                              comp, result_var,
                              counted=True)
    
    # Define symbols for each maintenance join introduced.
    class MaintJoinDefiner(L.NodeVisitor):
        def visit_Query(self, node):
            self.generic_visit(node)
            
            if (node.name in used_join_names and
                node.name not in symtab.get_symbols()):
                sym = symtab.define_query(node.name, node=node.query)
                query.maint_joins.append(sym)
    
    MaintJoinDefiner.run(tree)
    
    class CompExpander(QueryRewriter):
        
        def rewrite(self, symbol, name, expr):
            if name == query.name:
                if query.params == ():
                    return L.Name(result_var)
                else:
                    mask = L.mask('b' * len(query.params) + 'u' * orig_arity)
                    return L.ImgLookup(result_var, mask, query.params)
    
    tree = CompExpander.run(tree, symtab, expand=True)
    
    return tree


def expand_maintjoins(tree, symtab, query):
    """Expand the maintenance joins for the given query symbol."""
    join_names = [join.name for join in query.maint_joins]
    tree = JoinExpander.run(tree, symtab.clausetools, join_names)
    return tree
