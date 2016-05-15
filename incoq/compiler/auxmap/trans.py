"""Auxiliary map and SetFromMap transformation."""


__all__ = [
    'AuxmapInvariant',
    'SetFromMapInvariant',
    'WrapInvariant',
    
    'InvariantFinder',
    'InvariantTransformer',
    
    'make_auxmap_type',
    'make_setfrommap_type',
    'make_wrap_type',
    
    'define_map',
    'define_set',
    'define_wrap_set',
    'transform_setfrommap',
    'transform_auxmaps',
    'transform_all_wraps',
]


from collections import OrderedDict
from simplestruct import Struct, TypedField

from incoq.util.collections import OrderedSet
from incoq.util.type import typechecked
from incoq.compiler.incast import L
from incoq.compiler.type import T
from incoq.compiler.symbol import N


class AuxmapInvariant(Struct):
    
    """Auxiliary map invariant."""
    
    map = TypedField(str)
    """Name of variable holding the map to be created."""
    rel = TypedField(str)
    """Name of relation being indexed."""
    mask = TypedField(L.mask)
    """Mask for the indexing."""
    unwrap_key = TypedField(bool)
    """Whether the bound part is a single unwrapped component."""
    unwrap_value = TypedField(bool)
    """Whether the unbound part is a single unwrapped component."""
    
    def __init__(self, map, rel, mask, unwrap_key, unwrap_value):
        assert not (unwrap_key and mask.m.count('b') > 1)
        assert not (unwrap_value and mask.m.count('u') > 1)
    
    def get_maint_func_name(self, op):
        op_name = L.set_update_name(op)
        return N.get_maint_func_name(self.map, self.rel, op_name)


class SetFromMapInvariant(Struct):
    
    """SetFromMap invariant."""
    
    # The map key must be a tuple. The mask must be a mapmask with a
    # number of bound components equal to the arity of the map key.
    
    rel = TypedField(str)
    """Name of variable holding the relation to be created."""
    map = TypedField(str)
    """Name of map being indexed."""
    mask = TypedField(L.mask)
    """Mask for relating the map to the set."""
    
    def __init__(self, rel, map, mask):
        assert L.is_mapmask(mask)
    
    def get_maint_func_name(self, op):
        assert op in ['assign', 'delete']
        return N.get_maint_func_name(self.rel, self.map, op)


class WrapInvariant(Struct):
    
    """Wrap invariant."""
    
    rel = TypedField(str)
    """Name of variable holding the relation to be maintained."""
    oper = TypedField(str)
    """Name of variable holding the operand relation."""
    unwrap = TypedField(bool)
    """True for Unwrap, False for Wrap."""
    
    def get_maint_func_name(self, op):
        op_name = L.set_update_name(op)
        return N.get_maint_func_name(self.rel, self.oper, op_name)


@typechecked
def make_imgadd(fresh_vars, target: str, key: str, elem: str):
    """Make code to add elem to the image set for key in target."""
    var = next(fresh_vars)
    return L.Parser.pc('''
        if _KEY not in _TARGET:
            _VAR = Set()
            _TARGET.mapassign(_KEY, _VAR)
        _TARGET[_KEY].add(_ELEM)
        ''', subst={'_TARGET': target,
                    '_KEY': key,
                    '_ELEM': elem,
                    '_VAR': var})


@typechecked
def make_imgremove(fresh_vars, target: str, key: str, elem: str):
    """Make code to remove elem from the image set for key in target."""
    return L.Parser.pc('''
        _TARGET[_KEY].remove(_ELEM)
        if len(_TARGET[_KEY]) == 0:
            _TARGET.mapdelete(_KEY)
        ''', subst={'_TARGET': target,
                    '_KEY': key,
                    '_ELEM': elem})


@typechecked
def make_auxmap_maint_func(fresh_vars,
                           auxmap: AuxmapInvariant, op: L.setupop):
    """Make maintenance function for auxiliary map."""
    # Fresh variables for components of the element.
    vars = N.get_subnames('_elem', len(auxmap.mask.m))
    
    decomp_code = (L.DecompAssign(vars, L.Name('_elem')),)
    
    key, value = L.split_by_mask(auxmap.mask, vars)
    key = L.tuplify(key, unwrap=auxmap.unwrap_key)
    value = L.tuplify(value, unwrap=auxmap.unwrap_value)
    fresh_var_prefix = next(fresh_vars)
    key_var = fresh_var_prefix + '_key'
    value_var = fresh_var_prefix + '_value'
    
    decomp_code += L.Parser.pc('''
        _KEY_VAR = _KEY
        _VALUE_VAR = _VALUE
        ''', subst={'_KEY_VAR': key_var, '_KEY': key,
                    '_VALUE_VAR': value_var, '_VALUE': value})
    
    img_func = {L.SetAdd: make_imgadd,
                L.SetRemove: make_imgremove}[op.__class__]
    img_code = img_func(fresh_vars, auxmap.map, key_var, value_var)
    
    func_name = auxmap.get_maint_func_name(op)
    
    func = L.Parser.ps('''
        def _FUNC(_elem):
            _DECOMP
            _IMGCODE
        ''', subst={'_FUNC': func_name,
                    '<c>_DECOMP': decomp_code,
                    '<c>_IMGCODE': img_code})
    
    return func


@typechecked
def make_setfrommap_maint_func(fresh_vars,
                               setfrommap: SetFromMapInvariant,
                               op: str):
    mask = setfrommap.mask
    nb = L.break_mapmask(mask)
    # Fresh variables for components of the key and value.
    key_vars = N.get_subnames('_key', nb)
    
    decomp_code = (L.DecompAssign(key_vars, L.Name('_key')),)
    
    vars = L.combine_by_mask(mask, key_vars, ['_val'])
    elem = L.tuplify(vars)
    fresh_var_prefix = next(fresh_vars)
    elem_var = fresh_var_prefix + '_elem'
    
    decomp_code += (L.Assign(elem_var, elem),)
    
    setopcls = {'assign': L.SetAdd,
                'delete': L.SetRemove}[op]
    update_code = (L.RelUpdate(setfrommap.rel, setopcls(), elem_var),)
    
    func_name = setfrommap.get_maint_func_name(op)
    
    if op == 'assign':
        func = L.Parser.ps('''
            def _FUNC(_key, _val):
                _DECOMP
                _UPDATE
            ''', subst={'_FUNC': func_name,
                        '<c>_DECOMP': decomp_code,
                        '<c>_UPDATE': update_code})
    elif op == 'delete':
        lookup_expr = L.DictLookup(L.Name(setfrommap.map),
                                   L.Name('_key'), None)
        func = L.Parser.ps('''
            def _FUNC(_key):
                _val = _LOOKUP
                _DECOMP
                _UPDATE
            ''', subst={'_FUNC': func_name,
                        '_LOOKUP': lookup_expr,
                        '<c>_DECOMP': decomp_code,
                        '<c>_UPDATE': update_code})
    else:
        assert()
    
    return func


def make_wrap_maint_func(fresh_vars,
                         wrapinv: WrapInvariant,
                         op: L.setupop):
    fresh_var_prefix = next(fresh_vars)
    v = fresh_var_prefix + '_v'
    
    update_code = (L.RelUpdate(wrapinv.rel, op, v),)
    
    func_name = wrapinv.get_maint_func_name(op)
    
    if wrapinv.unwrap:
        v_code = L.Parser.pc('_V = index(_elem, 0)',
                             subst={'_V': v})
    else:
        v_code = L.Parser.pc('_V = (_elem,)',
                             subst={'_V': v})
    
    func = L.Parser.ps('''
        def _FUNC(_elem):
            _V_CODE
            _UPDATE
        ''', subst={'_FUNC': func_name,
                    '<c>_V_CODE': v_code,
                    '<c>_UPDATE': update_code})
    
    return func


class InvariantFinder(L.NodeVisitor):
    
    """Find all set invariants needed in the program."""
    
    def process(self, tree):
        self.auxmaps = OrderedSet()
        self.setfrommaps = OrderedSet()
        self.wraps = OrderedSet()
        
        super().process(tree)
        
        return self.auxmaps, self.setfrommaps, self.wraps
    
    def imglookup_helper(self, node):
        """Create an AuxmapInvariant for this node if applicable.
        Return the invariant, or None if not applicable. Do not add
        the invariant yet.
        """
        if not isinstance(node.set, L.Name):
            return None
        rel = node.set.id
        
        map = N.get_auxmap_name(rel, node.mask)
        unwrap_key = len(node.bounds) == 1
        auxmap = AuxmapInvariant(map, rel, node.mask, unwrap_key, False)
        return auxmap
    
    def visit_ImgLookup(self, node):
        self.generic_visit(node)
        
        auxmap = self.imglookup_helper(node)
        if auxmap is not None:
            self.auxmaps.add(auxmap)
    
    def visit_SetFromMap(self, node):
        self.generic_visit(node)
        
        if not isinstance(node.map, L.Name):
            return
        map = node.map.id
        
        rel = N.SA_name(map, node.mask)
        setfrommap = SetFromMapInvariant(rel, map, node.mask)
        self.setfrommaps.add(setfrommap)
    
    def visit_Unwrap(self, node):
        # Catch case where the immediate child is an ImgLookup, in which
        # case we can generate an AuxmapInvariant with the unwrap_value
        # flag set.
        if isinstance(node.value, L.ImgLookup):
            # Recurse over children below the ImgLookup.
            self.generic_visit(node.value)
            
            auxmap = self.imglookup_helper(node.value)
            if auxmap is not None:
                auxmap = auxmap._replace(unwrap_value=True)
                self.auxmaps.add(auxmap)
                return
        
        else:
            # Don't run in the case where we already did generic_visit()
            # above but failed to return.
            self.generic_visit(node)
        
        # Couldn't construct auxmap for ourselves + child;
        # treat this as normal unwrap.
        
        if not isinstance(node.value, L.Name):
            return
        oper = node.value.id
        
        rel = N.get_unwrap_name(oper)
        wrapinv = WrapInvariant(rel, oper, True)
        self.wraps.add(wrapinv)
    
    def visit_Wrap(self, node):
        self.generic_visit(node)
        
        if not isinstance(node.value, L.Name):
            return
        oper = node.value.id
        
        rel = N.get_wrap_name(oper)
        wrapinv = WrapInvariant(rel, oper, False)
        self.wraps.add(wrapinv)


class InvariantTransformer(L.AdvNodeTransformer):
    
    """Insert maintenance functions, insert calls to these functions
    at updates, and replace expressions with uses of stored results.
    """
    
    # There can be at most one SetFromMap mask for a given map.
    # Multiple distinct masks would have to differ on their arity,
    # which would be a type error.
    
    def __init__(self, fresh_vars, auxmaps, setfrommaps, wraps):
        super().__init__()
        self.fresh_vars = fresh_vars
        self.maint_funcs = OrderedSet()
        
        # Index over auxmaps for fast retrieval.
        self.auxmaps_by_rel = OrderedDict()
        self.auxmaps_by_relmask = OrderedDict()
        for auxmap in auxmaps:
            self.auxmaps_by_rel.setdefault(auxmap.rel, []).append(auxmap)
            # Index by relation, mask, and whether value is a singleton.
            # Not indexed by whether key is a singleton; if there are
            # two separate invariants that differ only on that, we may
            # end up only using one but maintaining both.
            stats = (auxmap.rel, auxmap.mask, auxmap.unwrap_value)
            self.auxmaps_by_relmask[stats] = auxmap
        
        # Index over setfrommaps.
        self.setfrommaps_by_map = sfm_by_map = OrderedDict()
        for sfm in setfrommaps:
            if sfm.map in sfm_by_map:
                raise L.ProgramError('Multiple SetFromMap invariants on '
                                     'same map {}'.format(sfm.map))
            sfm_by_map[sfm.map] = sfm
        
        self.wraps_by_rel = OrderedDict()
        for wrap in wraps:
            self.wraps_by_rel.setdefault(wrap.oper, []).append(wrap)
    
    def in_loop_rhs(self):
        """Return True if the current node is the iter of a For node.
        Note that this checks the _visit_stack, and is sensitive to
        where in the recursive visiting we are.
        """
        stack = self._visit_stack
        if len(stack) < 2:
            return False
        _current, field, _index = stack[-1]
        parent, _field, _index = stack[-2]
        return isinstance(parent, L.For) and field == 'iter'
    
    def visit_Module(self, node):
        node = self.generic_visit(node)
        
        funcs = []
        for auxmaps in self.auxmaps_by_rel.values():
            for auxmap in auxmaps:
                for op in [L.SetAdd(), L.SetRemove()]:
                    func = make_auxmap_maint_func(self.fresh_vars, auxmap, op)
                    funcs.append(func)
        for sfm in self.setfrommaps_by_map.values():
            for op in ['assign', 'delete']:
                func = make_setfrommap_maint_func(self.fresh_vars, sfm, op)
                funcs.append(func)
        for wraps in self.wraps_by_rel.values():
            for wrap in wraps:
                for op in [L.SetAdd(), L.SetRemove()]:
                    func = make_wrap_maint_func(self.fresh_vars, wrap, op)
                    funcs.append(func)
        
        func_names = L.get_defined_functions(tuple(funcs))
        self.maint_funcs.update(func_names)
        
        node = node._replace(body=tuple(funcs) + node.body)
        return node
    
    def visit_RelUpdate(self, node):
        if not isinstance(node.op, (L.SetAdd, L.SetRemove)):
            return node
        
        code = (node,)
        
        auxmaps = self.auxmaps_by_rel.get(node.rel, set())
        for auxmap in auxmaps:
            func_name = auxmap.get_maint_func_name(node.op)
            call_code = (L.Expr(L.Call(func_name, [L.Name(node.elem)])),)
            code = L.insert_rel_maint(code, call_code, node.op)
        
        wraps = self.wraps_by_rel.get(node.rel, set())
        for wrap in wraps:
            func_name = wrap.get_maint_func_name(node.op)
            call_code = (L.Expr(L.Call(func_name, [L.Name(node.elem)])),)
            code = L.insert_rel_maint(code, call_code, node.op)
        
        return code
    
    def visit_RelClear(self, node):
        code = (node,)
        
        auxmaps = self.auxmaps_by_rel.get(node.rel, set())
        for auxmap in auxmaps:
            clear_code = (L.MapClear(auxmap.map),)
            code = L.insert_rel_maint(code, clear_code, L.SetRemove())
        
        wraps = self.wraps_by_rel.get(node.rel, set())
        for wrap in wraps:
            clear_code = (L.RelClear(wrap.rel),)
            code = L.insert_rel_maint(code, clear_code, L.SetRemove())
        
        return code
    
    def visit_MapAssign(self, node):
        sfm = self.setfrommaps_by_map.get(node.map, None)
        if sfm is None:
            return node
        
        code = (node,)
        func_name = sfm.get_maint_func_name('assign')
        call_code = (L.Expr(L.Call(func_name, [L.Name(node.key),
                                               L.Name(node.value)])),)
        code = L.insert_rel_maint(code, call_code, L.SetAdd())
        return code
    
    def visit_MapDelete(self, node):
        sfm = self.setfrommaps_by_map.get(node.map, None)
        if sfm is None:
            return node
        
        code = (node,)
        func_name = sfm.get_maint_func_name('delete')
        call_code = (L.Expr(L.Call(func_name, [L.Name(node.key)])),)
        code = L.insert_rel_maint(code, call_code, L.SetRemove())
        return code
    
    def visit_MapClear(self, node):
        sfm = self.setfrommaps_by_map.get(node.map, None)
        if sfm is None:
            return node
        
        code = (node,)
        clear_code = (L.RelClear(sfm.rel),)
        code = L.insert_rel_maint(code, clear_code, L.SetRemove())
        return code
    
    def imglookup_helper(self, node, *, in_unwrap, on_loop_rhs):
        """Return the replacement for an ImgLookup node, or None if
        no replacement is applicable.
        """
        if not isinstance(node.set, L.Name):
            return None
        rel = node.set.id
        
        stats = (rel, node.mask, in_unwrap)
        auxmap = self.auxmaps_by_relmask.get(stats, None)
        if auxmap is None:
            return None
        
        key = L.tuplify(node.bounds, unwrap=auxmap.unwrap_key)
        empty = L.Parser.pe('()') if on_loop_rhs else L.Parser.pe('Set()')
        return L.Parser.pe('_MAP[_KEY] if _KEY in _MAP else _EMPTY',
                           subst={'_MAP': auxmap.map,
                                  '_KEY': key,
                                  '_EMPTY': empty})
    
    def visit_ImgLookup(self, node):
        node = self.generic_visit(node)
        
        repl = self.imglookup_helper(node, in_unwrap=False,
                                     on_loop_rhs=self.in_loop_rhs())
        if repl is not None:
            node = repl
        
        return node
    
    def visit_SetFromMap(self, node):
        node = self.generic_visit(node)
        
        if not isinstance(node.map, L.Name):
            return node
        map = node.map.id
        
        sfm = self.setfrommaps_by_map.get(map, None)
        if sfm is None:
            return node
        
        if not sfm.mask == node.mask:
            raise L.ProgramError('Multiple SetFromMap expressions on '
                                 'same map {}'.format(map))
        return L.Name(sfm.rel)
    
    def wrap_helper(self, node):
        """Process a wrap invariant at a Wrap or Unwrap node.
        Don't recurse.
        """
        if not isinstance(node.value, L.Name):
            return node
        rel = node.value.id
        
        wraps = self.wraps_by_rel.get(rel, [])
        for wrap in wraps:
            if ((isinstance(node, L.Wrap) and not wrap.unwrap) or
                (isinstance(node, L.Unwrap) and wrap.unwrap)):
                return L.Name(wrap.rel)
        
        return node
    
    def visit_Unwrap(self, node):
        # Handle special case of an auxmap with the unwrap_value flag.
        if isinstance(node.value, L.ImgLookup):
            # Recurse over children below the ImgLookup.
            value = self.generic_visit(node.value)
            node = node._replace(value=value)
            # See if an auxmap invariant applies.
            repl = self.imglookup_helper(value, in_unwrap=True,
                                         on_loop_rhs=self.in_loop_rhs())
            if repl is not None:
                return repl
        
        else:
            # Don't run in case we already did generic_visit() above
            # and didn't return.
            node = self.generic_visit(node)
        
        return self.wrap_helper(node)
    
    def visit_Wrap(self, node):
        node = self.generic_visit(node)
        node = self.wrap_helper(node)
        return node


def make_auxmap_type(auxmapinv, reltype):
    """Given a mask and a relation type, determine the corresponding
    auxiliary map type.
    
    We obtain by lattice join the smallest relation type that is at
    least as big as the given relation type and that has the correct
    arity. This should have the form {(T1, ..., Tn)}. The map type is
    then from a tuple of some Ts to a set of tuples of the remaining Ts.
    
    If no such type exists, e.g. if the given relation type is {Top}
    or a set of tuples of incorrect arity, we instead give the map type
    {Top: Top}.
    """
    mask = auxmapinv.mask
    arity = len(mask.m)
    bottom_reltype = T.Set(T.Tuple([T.Bottom] * arity))
    top_reltype = T.Set(T.Tuple([T.Top] * arity))
    
    norm_type = reltype.join(bottom_reltype)
    well_typed = norm_type.issmaller(top_reltype)
    
    if well_typed:
        assert (isinstance(norm_type, T.Set) and
                isinstance(norm_type.elt, T.Tuple) and
                len(norm_type.elt.elts) == arity)
        t_bs, t_us = L.split_by_mask(mask, norm_type.elt.elts)
        t_key = t_bs[0] if auxmapinv.unwrap_key else T.Tuple(t_bs)
        t_value = t_us[0] if auxmapinv.unwrap_value else T.Tuple(t_us)
        map_type = T.Map(t_key, T.Set(t_value))
    else:
        map_type = T.Map(T.Top, T.Top)
    
    return map_type


def make_setfrommap_type(mask, maptype):
    """Given a mask and a map type, determine the corresponding relation
    type.
    
    We obtain by lattice join the smallest map type that is at least as
    big as the given map type and that has the correct key tuple arity.
    This should have the form {(K1, ..., Kn): V}. The relation type is
    then a set of tuples of these types interleaved according to the
    mask.
    
    If no such type exists, e.g. if the given relation type is {Top: Top}
    or the key is not a tuple of correct arity, we instead give the
    relation type {Top}.
    """
    nb = mask.m.count('b')
    assert mask.m.count('u') == 1
    bottom_maptype = T.Map(T.Tuple([T.Bottom] * nb), T.Bottom)
    top_maptype = T.Map(T.Tuple([T.Top] * nb), T.Top)
    
    norm_type = maptype.join(bottom_maptype)
    well_typed = norm_type.issmaller(top_maptype)
    
    if well_typed:
        assert (isinstance(norm_type, T.Map) and
                isinstance(norm_type.key, T.Tuple) and
                len(norm_type.key.elts) == nb)
        t_elts = L.combine_by_mask(mask, norm_type.key.elts,
                                   [norm_type.value])
        rel_type = T.Set(T.Tuple(t_elts))
    else:
        rel_type = T.Set(T.Top)
    
    return rel_type


def make_wrap_type(wrapinv, opertype):
    """Given an operand type, determine the corresponding wrap or unwrap
    type.
    """
    if wrapinv.unwrap:
        top_opertype = T.Set(T.Tuple([T.Top]))
        bottom_opertype = T.Set(T.Tuple([T.Bottom]))
        
        norm_type = opertype.join(bottom_opertype)
        well_typed = norm_type.issmaller(top_opertype)
        
        if well_typed:
            assert (isinstance(norm_type, T.Set) and
                    isinstance(norm_type.elt, T.Tuple) and
                    len(norm_type.elt.elts) == 1)
            return T.Set(norm_type.elt.elts[0])
        else:
            return T.Set(T.Top)
    
    else:
        top_opertype = T.Set(T.Top)
        bottom_opertype = T.Set(T.Bottom)
        
        norm_type = opertype.join(bottom_opertype)
        well_typed = norm_type.issmaller(top_opertype)
        
        if well_typed:
            assert isinstance(norm_type, T.Set)
            return T.Set(T.Tuple([norm_type.elt]))
        else:
            return T.Set(T.Top)


def define_map(auxmap, symtab):
    """Add a map definition to the symbol table."""
    # Obtain relation symbol.
    relsym = symtab.get_relations().get(auxmap.rel, None)
    if relsym is None:
        raise L.TransformationError('No relation "{}" matching map "{}"'
                                    .format(auxmap.rel, auxmap.map))
    map_type = make_auxmap_type(auxmap, relsym.type)
    symtab.define_map(auxmap.map, type=map_type)


def define_set(setfrommap, symtab):
    """Add a relation definition to the symbol table."""
    # Obtain map symbol.
    mapsym = symtab.get_maps().get(setfrommap.map, None)
    if mapsym is None:
        raise L.TransformationError('No map "{}" matching relation "{}"'
                                    .format(setfrommap.map, setfrommap.rel))
    rel_type = make_setfrommap_type(setfrommap.mask, mapsym.type)
    symtab.define_relation(setfrommap.rel, type=rel_type)


def define_wrap_set(wrapinv, symtab):
    """Add a relation definition for a WrapInvariant."""
    opersym = symtab.get_relations().get(wrapinv.oper, None)
    if opersym is None:
        raise L.TransformationError('No relation "{}" matching wrapped/'
                                    'unwrapped relation "{}"'.format(
                                    wrapinv.oper, wrapinv.rel))
    
    rel_type = make_wrap_type(wrapinv, opersym.type)
    symtab.define_relation(wrapinv.rel, type=rel_type)


def transform_setfrommap(tree, symtab, setfrommap):
    """Transform a single SetFromMapInvariant."""
    define_set(setfrommap, symtab)
    trans = InvariantTransformer(symtab.fresh_names.vars,
                                 [], [setfrommap], [])
    tree = trans.process(tree)
    symtab.maint_funcs.update(trans.maint_funcs)
    return tree


def transform_wrap(tree, symtab, wrapinv):
    """Transform a single WrapInvariant."""
    define_wrap_set(wrapinv, symtab)
    trans = InvariantTransformer(symtab.fresh_names.vars,
                                 [], [], [wrapinv])
    tree = trans.process(tree)
    symtab.maint_funcs.update(trans.maint_funcs)
    return tree


def transform_auxmaps_stepper(tree, symtab):
    """Transform all set expressions we can find that are over Name
    nodes. Return the tree and whether any transformation was done.
    """
    auxmaps, setfrommaps, wraps = InvariantFinder.run(tree)
    if len(auxmaps) == len(setfrommaps) == len(wraps) == 0:
        return tree, False
    
    for auxmap in auxmaps:
        if auxmap.rel not in symtab.get_relations():
            raise L.ProgramError('Cannot make auxiliary map for image-set '
                                 'lookup over non-relation variable {}'
                                 .format(auxmap.rel))
    for auxmap in auxmaps:
        define_map(auxmap, symtab)
    for sfm in setfrommaps:
        define_set(sfm, symtab)
    for wrap in wraps:
        define_wrap_set(wrap, symtab)
    trans = InvariantTransformer(symtab.fresh_names.vars,
                                 auxmaps, setfrommaps, wraps)
    tree = trans.process(tree)
    symtab.maint_funcs.update(trans.maint_funcs)
    
    symtab.stats['auxmaps_transformed'] += len(auxmaps)
    
    return tree, True


def transform_auxmaps(tree, symtab):
    """Transform all ImgLookup and SetFromMap nodes. If any remain that
    do not fit our form, raise an error.
    """
    class Complainer(L.NodeVisitor):
        def visit_ImgLookup(self, node):
            raise L.ProgramError('Invalid ImgLookup expression: {}'
                                 .format(node))
        def visit_SetFromMap(self, node):
            raise L.ProgramError('Invalid SetFromMap expression: {}'
                                 .format(node))
    
    changed = True
    while changed:
        tree, changed = transform_auxmaps_stepper(tree, symtab)
    Complainer.run(tree)
    return tree


def transform_all_wraps(tree, symtab):
    """Transform for Wrap nodes only."""
    _auxmaps, _setfrommaps, wraps = InvariantFinder.run(tree)
    wraps = [w for w in wraps if not w.unwrap]
    for wrap in wraps:
        define_wrap_set(wrap, symtab)
    trans = InvariantTransformer(symtab.fresh_names.vars,
                                 [], [], wraps)
    tree = trans.process(tree)
    for q in symtab.get_queries().values():
        q.node = trans.process(q.node)
    symtab.maint_funcs.update(trans.maint_funcs)
    return tree
