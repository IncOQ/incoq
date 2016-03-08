"""Rewritings for updates."""


__all__ = [
    'expand_bulkupdates',
    'specialize_rels_and_maps',
    'unspecialize_rels_and_maps',
    'expand_clear',
]


from incoq.mars.incast import L


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


def expand_bulkupdates(tree, symtab):
    """Expand BulkUpdate nodes into elementary update operations."""
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
