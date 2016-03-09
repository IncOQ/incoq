"""Transformation to implement comprehensions."""


__all__ = [
    'JoinExpander',
    'process_maintjoins',
    'convert_subquery_clause',
    'convert_subquery_clauses',
    'make_comp_maint_func',
    'CompMaintainer',
    'preprocess_comp',
    'incrementalize_comp',
    'transform_comp_query',
    'rewrite_all_comps_with_patterns',
]


from incoq.mars.incast import L
from incoq.mars.type import T
from incoq.mars.symbol import S, N
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
                L.detuplify(comp.resexp) == node.vars):
            return node
        
        return ct.get_code_for_clauses(comp.clauses, (), node.body)


def process_maintjoins(tree, symtab, query):
    """Order and filter maintenance joins for a query."""
    ct = symtab.clausetools
    maint_joins = [join.name for join in query.maint_joins]
    filters = query.filters
    
    class Rewriter(S.QueryRewriter):
        def rewrite(self, symbol, name, expr):
            if name not in maint_joins:
                return
            assert isinstance(expr, L.Comp)
            clauses = expr.clauses
            
            clause_indices = {cl: i for i, cl in enumerate(clauses)}
            clauses = order_clauses(ct, clauses)
            
            if filters is not None:
                # Rename filters so that query variable prefixes match.
                renamer = lambda x: symbol.join_prefix + '_' + x
                renamed_filters = ct.clauses_rename_lhs_vars(filters, renamer)
                # Reorder filters so that they correspond to reordered
                # clauses.
                reordered_filters = [renamed_filters[clause_indices[cl]]
                                     for cl in clauses]
                # Apply filtering.
                clauses = ct.filter_clauses(clauses, reordered_filters, [])
            
            return expr._replace(clauses=clauses)
    
    tree = Rewriter.run(tree, symtab)
    return tree


def convert_subquery_clause(clause):
    """Given a clause, if it is a VarsMember clause for an
    incrementalized subquery, return an equivalent RelMember clause.
    For any other clause return the clause unchanged.
    
    The two forms recognized are:
    
        - right-hand side is a Name node
        
        - right-hand side is an ImgLookup node on a Name, with a keymask
    """
    if not isinstance(clause, L.VarsMember):
        return clause
    
    if isinstance(clause.iter, L.Name):
        return L.RelMember(clause.vars, clause.iter.id)
    elif (isinstance(clause.iter, L.ImgLookup) and
          isinstance(clause.iter.set, L.Name) and
          L.is_keymask(clause.iter.mask)):
        nb, nu = L.break_keymask(clause.iter.mask)
        assert nb == len(clause.iter.bounds)
        assert nu == len(clause.vars)
        return L.RelMember(clause.iter.bounds + clause.vars,
                           clause.iter.set.id)
    
    return clause

def convert_subquery_clauses(comp):
    """Given a Comp node, return a modified node where clauses over
    incrementalized subqueries are replaced with RelMember.
    """
    # We need a visitor in order to handle cases where clauses are
    # nested inside other clauses. The visitor should not reach into any
    # non-incrementalized subqueries (although there shouldn't be any
    # at this stage). We can't just use L.rewrite_comp() without a
    # visitor because we need to recurse over nested clause structures
    # (in the case of WithoutMember).
    class Trans(L.NodeTransformer):
        def visit_VarsMember(self, node):
            return convert_subquery_clause(node)
        def visit_Comp(self, node):
            return node
    
    new_clauses = Trans.run(comp.clauses)
    return comp._replace(clauses=new_clauses)


def make_comp_maint_func(clausetools, fresh_var_prefix, fresh_join_names,
                         comp, result_var, rel, op, *,
                         counted):
    """Make maintenance function for a comprehension."""
    assert isinstance(op, (L.SetAdd, L.SetRemove))
    
    op_name = L.set_update_name(op)
    func_name = N.get_maint_func_name(result_var, rel, op_name)
    
    update = L.RelUpdate(rel, op, '_elem')
    code = clausetools.get_maint_code(fresh_var_prefix, fresh_join_names,
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
                fresh_var_prefix = next(self.fresh_vars)
                func = make_comp_maint_func(
                        ct, fresh_var_prefix, self.fresh_join_names,
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
    
    def visit_RelClear(self, node):
        if node.rel not in self.rels:
            return node
        
        code = (node,)
        clear_code = (L.RelClear(self.result_var),)
        code = L.insert_rel_maint(code, clear_code, L.SetRemove())
        return code


def rewrite_comp_resexp(symtab, query, comp):
    """Rewrite a comprehension query to add the parameters to the result
    expression. Update the symbol's type and return the new Comp AST,
    but don't change the symbol's node attribute.
    """
    ct = symtab.clausetools
    if query.params != ():
        assert isinstance(comp.resexp, L.Tuple)
        comp = ct.rewrite_resexp_with_params(comp, query.params)
        
        # Update the query symbol type.
        assert (isinstance(query.type, T.Set) and
                isinstance(query.type.elt, T.Tuple))
        query.type = symtab.analyze_expr_type(comp)
    
    return comp


def preprocess_comp(tree, symtab, query):
    """Preprocess a comprehension query for incrementalization."""
    ct = symtab.clausetools
    comp = query.node
    
    # Rewrite uses of subquery results.
    comp = convert_subquery_clauses(comp)
    # Even though we already ran this in a preprocessing step,
    # do it again to get any equality patterns introduced by other
    # rewritings (such as convert_subquery_clauses() above).
    comp = ct.elim_sameclause_eqs(comp)
    # Broaden to express result for all parameter values.
    comp = rewrite_comp_resexp(symtab, query, comp)
    
    class Rewriter(S.QueryRewriter):
        def rewrite(self, symbol, name, expr):
            if name == query.name:
                return comp
    
    return Rewriter.run(tree, symtab)


def incrementalize_comp(tree, symtab, query, result_var):
    """Incrementalize the given comprehension query symbol. Insert
    maintenance functions and calls at updates, and replace all
    occurrences of the query (including within other queries in the
    symbol table) with uses of the stored result variable.
    """
    clausetools = symtab.clausetools
    fresh_vars = symtab.fresh_names.vars
    comp = query.node
    
    query.maint_joins = []
    
    # Some hackery for tracking the names of maintenance joins and
    # their corresponding variable prefixes.
    current_prefix = None
    used_join_names = []
    join_prefixes = {}
    
    def fresh_vars():
        nonlocal current_prefix
        for v in symtab.fresh_names.vars:
            current_prefix = v
            yield v
    
    def fresh_join_names():
        for join_name in N.fresh_name_generator(query.name + '_J{}'):
            used_join_names.append(join_name)
            join_prefixes[join_name] = current_prefix
            yield join_name
    
    tree = CompMaintainer.run(tree, clausetools, fresh_vars(),
                              fresh_join_names(),
                              comp, result_var,
                              counted=True)
    
    # Define symbols for each maintenance join introduced.
    class MaintJoinDefiner(L.NodeVisitor):
        def visit_Query(self, node):
            self.generic_visit(node)
            
            if (node.name in used_join_names and
                node.name not in symtab.get_symbols()):
                sym = symtab.define_query(
                    node.name, node=node.query,
                    display=False, join_prefix=join_prefixes[node.name])
                query.maint_joins.append(sym)
    
    MaintJoinDefiner.run(tree)
    
    orig_arity = len(comp.resexp.elts) - len(query.params)
    
    class CompExpander(S.QueryRewriter):
        
        def rewrite(self, symbol, name, expr):
            if name == query.name:
                if query.params == ():
                    return L.Name(result_var)
                else:
                    mask = L.keymask_from_len(len(query.params), orig_arity)
                    return L.ImgLookup(L.Name(result_var), mask, query.params)
    
    tree = CompExpander.run(tree, symtab, expand=True)
    
    return tree


def transform_firsthalf(tree, symtab, query):
    result_var = N.get_resultset_name(query.name)
    tree = preprocess_comp(tree, symtab, query)
    tree = incrementalize_comp(tree, symtab, query, result_var)
    symtab.define_relation(result_var, counted=True,
                           type=query.type)
    return tree

def transform_secondhalf(tree, symtab, query):
    tree = process_maintjoins(tree, symtab, query)
    join_names = [join.name for join in query.maint_joins]
    tree = JoinExpander.run(tree, symtab.clausetools, join_names)
    return tree

def transform_comp_query(tree, symtab, query):
    """Do all the transformation associated with incrementalizing a
    comprehension query.
    """
    # Incrementalize the query.
    tree = transform_firsthalf(tree, symtab, query)
    # Process and expand the maintenance joins.
    tree = transform_secondhalf(tree, symtab, query)
    return tree


def rewrite_all_comps_with_patterns(tree, symtab):
    """Perform pattern rewriting for all comprehension queries that
    are to be incrementalized. Parameter information must be available.
    """
    class Rewriter(S.QueryRewriter):
        def rewrite(self, symbol, name, expr):
            if not isinstance(expr, L.Comp):
                return
            if symbol.impl == S.Normal:
                return
            
            ct = self.symtab.clausetools
            comp = ct.rewrite_with_patterns(expr, symbol.params)
            return comp
    
    return Rewriter.run(tree, symtab)
