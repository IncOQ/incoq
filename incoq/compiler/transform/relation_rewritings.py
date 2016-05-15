"""Rewritings for relations and maps."""


__all__ = [
    'rewrite_memberconds',
    'expand_bulkupdates',
    'specialize_rels_and_maps',
    'unspecialize_rels_and_maps',
    'expand_clear',
    'relationalize_comp_queries',
    'relationalize_clauses',
    'eliminate_dead_relations',
]


from incoq.compiler.incast import L
from incoq.compiler.type import T
from incoq.compiler.symbol import S

from incoq.compiler.auxmap import transform_all_wraps


def rewrite_memberconds(tree, symtab):
    """For all comprehension queries, replace membership condition
    clauses (Cond nodes) with membership clauses (Member nodes).
    """
    def process(cl):
        if (isinstance(cl, L.Cond) and
            isinstance(cl.cond, L.Compare) and
            isinstance(cl.cond.op, L.In)):
            cl = L.Member(cl.cond.left, cl.cond.right)
            return cl, [], []
    
    class WrapRewriter(S.QueryRewriter):
        def rewrite_comp(self, symbol, name, comp):
            comp = L.rewrite_comp(comp, process)
            return comp
    
    tree = WrapRewriter.run(tree, symtab)
    return tree


# Templates for expanding bulk update operations.
# Take care to handle the case where target and value are aliased,
# and to make a copy when iterating over sets that will be modified.

# No copy needed because if target and value are aliased, the set
# is not modified.
union_template = '''
for _ELEM in _VALUE:
    if _ELEM not in _TARGET:
        _TARGET.add(_ELEM)
'''

inter_template = '''
for _ELEM in list(_TARGET):
    if _ELEM not in _VALUE:
        _TARGET.remove(_ELEM)
'''

diff_template = '''
for _ELEM in list(_VALUE):
    if _ELEM in _TARGET:
        _TARGET.remove(_ELEM)
'''

symdiff_template = '''
for _ELEM in list(_VALUE):
    if _ELEM in _TARGET:
        _TARGET.remove(_ELEM)
    else:
        _TARGET.add(_ELEM)
'''

copy_template = '''
for _ELEM in list(_TARGET):
    if _ELEM not in _VALUE:
        _TARGET.remove(_ELEM)
for _ELEM in list(_VALUE):
    if _ELEM not in _TARGET:
        _TARGET.add(_ELEM)
'''

# Make sure they aren't aliased so we don't wipe out the value when
# clearing the target.
dictcopy_template = '''
if _TARGET is not _VALUE:
    for _ELEM in list(_TARGET):
        del _TARGET[_ELEM]
    for _ELEM in _VALUE:
        _TARGET[_ELEM] = _VALUE[_ELEM]
'''

class BulkUpdateExpander(L.NodeTransformer):
    
    def __init__(self, fresh_vars):
        super().__init__()
        self.fresh_vars = fresh_vars
    
    def visit_SetBulkUpdate(self, node):
        template = {L.Union: union_template,
                    L.Inter: inter_template,
                    L.Diff: diff_template,
                    L.SymDiff: symdiff_template,
                    L.Copy: copy_template}[node.op.__class__]
        var = next(self.fresh_vars)
        code = L.Parser.pc(template, subst={'_TARGET': node.target,
                                            '_VALUE': node.value,
                                            '_ELEM': var})
        return code
    
    def visit_DictBulkUpdate(self, node):
        template = {L.DictCopy: dictcopy_template}[node.op.__class__]
        var = next(self.fresh_vars)
        code = L.Parser.pc(template, subst={'_TARGET': node.target,
                                            '_VALUE': node.value,
                                            '_ELEM': var})
        return code


def expand_bulkupdates(tree, symtab):
    """Expand BulkUpdate and DictBulkUpdate nodes into elementary update
    operations."""
    tree = BulkUpdateExpander.run(tree, symtab.fresh_names.vars)
    return tree


class Specializer(L.NodeTransformer):
    
    def __init__(self, fresh_vars, rels, maps):
        super().__init__()
        self.fresh_vars = fresh_vars
        self.rels = rels
        self.maps = maps
    
    def visit_SetUpdate(self, node):
        if not (isinstance(node.target, L.Name) and
                node.target.id in self.rels):
            return node
        
        code = ()
        if isinstance(node.value, L.Name):
            elem_var = node.value.id
        else:
            elem_var = next(self.fresh_vars)
            code += L.Parser.pc('_VAR = _VALUE',
                                subst={'_VAR': elem_var,
                                       '_VALUE': node.value})
        update = L.RelUpdate(node.target.id, node.op, elem_var)
        code += (update,)
        return code
    
    def visit_SetClear(self, node):
        if not (isinstance(node.target, L.Name) and
                node.target.id in self.rels):
            return node
        
        return L.RelClear(node.target.id)
    
    def visit_DictAssign(self, node):
        if (isinstance(node.target, L.Name) and
            isinstance(node.key, L.Name) and
            isinstance(node.value, L.Name) and
            node.target.id in self.maps):
            return L.MapAssign(node.target.id, node.key.id, node.value.id)
        return node
    
    def visit_DictDelete(self, node):
        if (isinstance(node.target, L.Name) and
            isinstance(node.key, L.Name) and
            node.target.id in self.maps):
            return L.MapDelete(node.target.id, node.key.id)
        return node
    
    def visit_DictClear(self, node):
        if (isinstance(node.target, L.Name) and
            node.target.id in self.maps):
            return L.MapClear(node.target.id)
        return node
    
    def visit_Member(self, node):
        node = self.generic_visit(node)
        
        if (isinstance(node.iter, L.Name) and
            node.iter.id in self.rels and
            L.is_tuple_of_names(node.target)):
            return L.RelMember(L.detuplify(node.target),
                               node.iter.id)
        return node


def specialize_rels_and_maps(tree, symtab):
    """Rewrite nodes for sets and dicts as nodes for relations and maps,
    where possible.
    """
    specializer = Specializer(symtab.fresh_names.vars,
                              symtab.get_relations().keys(),
                              symtab.get_maps().keys())
    tree = specializer.process(tree)
    for q in symtab.get_queries().values():
        q.node = specializer.process(q.node)
    return tree


class Unspecializer(L.NodeTransformer):
    
    def visit_RelUpdate(self, node):
        return L.SetUpdate(L.Name(node.rel), node.op, L.Name(node.elem))
    
    def visit_RelClear(self, node):
        return L.SetClear(L.Name(node.rel))
    
    def visit_MapAssign(self, node):
        return L.DictAssign(L.Name(node.map), L.Name(node.key),
                            L.Name(node.value))
    
    def visit_MapDelete(self, node):
        return L.DictDelete(L.Name(node.map), L.Name(node.key))
    
    def visit_MapClear(self, node):
        return L.DictClear(L.Name(node.map))
    
    def visit_RelMember(self, node):
        return L.Member(L.tuplify(node.vars), L.Name(node.rel))


def unspecialize_rels_and_maps(tree, symtab):
    """Rewrite nodes for relations and maps as nodes for sets and dicts."""
    tree = Unspecializer.run(tree)
    for q in symtab.get_queries().values():
        q.node = Unspecializer.run(q.node)
    return tree


setclear_template = '''
for _ELEM in list(_TARGET):
    _TARGET.remove(_ELEM)
'''

dictclear_template = '''
for _ELEM in list(_TARGET):
    del _TARGET[_ELEM]

'''

class ClearExpander(L.NodeTransformer):
    
    def __init__(self, fresh_vars):
        super().__init__()
        self.fresh_vars = fresh_vars
    
    def visit_SetClear(self, node):
        var = next(self.fresh_vars)
        code = L.Parser.pc(setclear_template,
                           subst={'_TARGET': node.target,
                                  '_ELEM': var})
        return code
    
    def visit_DictClear(self, node):
        var = next(self.fresh_vars)
        code = L.Parser.pc(dictclear_template,
                           subst={'_TARGET': node.target,
                                  '_ELEM': var})
        return code


def expand_clear(tree, symtab):
    """Expand SetClear and DictClear nodes (but not RelClear and
    MapClear nodes) into elementary update operations.
    """
    tree = ClearExpander.run(tree, symtab.fresh_names.vars)
    return tree


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
        
        def rewrite_comp(self, symbol, name, comp):
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
    node. Also rewrite aggregate operands as Unwraps of Wrap nodes if
    they are a relation of non-tuple type.
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
        
        def rewrite_comp(self, symbol, name, comp):
            comp = L.rewrite_comp(comp, process)
            return comp
        
        def rewrite_aggr(self, symbol, name, aggr):
            if isinstance(aggr.value, L.Name):
                relsym = symtab.get_relations()[aggr.value.id]
                rel_type = relsym.type
                if not (isinstance(rel_type, T.Set) and
                        isinstance(rel_type.elt, T.Tuple)):
                    new_value = L.Unwrap(L.Wrap(aggr.value))
                    aggr = aggr._replace(value=new_value)
            return aggr
    
    tree = WrapRewriter.run(tree, symtab)
    return tree


def relationalize_comp_queries(tree, symtab):
    """Rewrite each comprehension query so that it is relational. The
    query must already be flattened.
    """
    tree = rewrite_with_unwraps(tree, symtab)
    tree = rewrite_with_wraps(tree, symtab)
    # Transform all wraps introduced. There should only be wraps
    # for relations, not inner comprehensions (or else the user screwed
    # up by mismatching a bare var on the LHS with a comp with a tuple
    # result expression on the RHS), so we don't need to incrementalize
    # anything else first.
    tree = transform_all_wraps(tree, symtab)
    return tree


def relationalize_clauses(tree, symtab):
    """Rewrite clauses whose RHS is a relation and whose LHS is either a
    variable or tuple of variables as a VarsMember or RelMember
    respectively.
    """
    def process(expr):
        if not (isinstance(expr, L.Member) and
                isinstance(expr.iter, L.Name) and
                expr.iter.id in symtab.get_relations()):
            return expr, [], []
        target = expr.target
        rel = expr.iter.id
        
        if L.is_tuple_of_names(target):
            cl = L.RelMember(L.detuplify(target), rel)
        elif isinstance(target, L.Name):
            cl = L.VarsMember([target.id], L.Wrap(L.Name(rel)))
        else:
            raise L.ProgramError('Invalid clause over relation')
        
        return cl, [], []
    
    class Rewriter(S.QueryRewriter):
        def rewrite_comp(self, symbol, name, comp):
            comp = L.rewrite_comp(comp, process)
            return comp
    
    tree = Rewriter.run(tree, symtab)
    return tree


def eliminate_dead_relations(tree, symtab):
    """Eliminate relations that are only updated, never read from."""
    rels = symtab.get_relations().keys()
    vars = L.IdentFinder.find_non_rel_uses(tree)
    elim_rels = set(rels) - set(vars)
    
    class Trans(L.NodeTransformer):
        def visit_RelUpdate(self, node):
            if node.rel in elim_rels:
                return ()
            return node
        def visit_RelClear(self, node):
            if node.rel in elim_rels:
                return ()
            return node
    
    tree = Trans.run(tree)
    for rel in elim_rels:
        del symtab.symbols[rel]
    return tree
