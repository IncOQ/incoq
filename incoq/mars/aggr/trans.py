"""Aggregate invariant transformation."""


__all__ = [
    'AggrInvariant',
    'AggrMaintainer',
    'incrementalize_aggr',
]


from simplestruct import Struct, TypedField

from incoq.mars.incast import L
from incoq.mars.type import T
from incoq.mars.symbol import S, N

from .aggrop import handler_for_op


class AggrInvariant(Struct):
    
    """Invariant for an aggregate over a relation or an ImgLookup of
    a relation.
    """
    
    map = TypedField(str)
    """Name of result map."""
    
    op = TypedField(L.aggrop)
    """Aggregate operator."""
    
    rel = TypedField(str)
    """Name of operand relation."""
    
    mask = TypedField(L.mask)
    """Mask for ImgLookup of operand. If there is no ImgLookup, the mask
    is all unbound."""
    
    params = TypedField(str, seq=True)
    """Parameter variables for ImgLookup."""
    
    def get_maint_func_name(self, op):
        op_name = L.set_update_name(op)
        return N.get_maint_func_name(self.map, self.rel, op_name)
    
    def get_handler(self):
        return handler_for_op[self.op.__class__]()


def make_aggr_maint_func(fresh_vars, aggrinv, op):
    """Make the maintenance function for an aggregate invariant and a
    given set update operation (add or remove).
    """
    assert isinstance(op, (L.SetAdd, L.SetRemove))
    
    # Decompose the argument tuple into key and value components,
    # just like in auxmap.py.
    
    vars = N.get_subnames('_elem', len(aggrinv.mask.m))
    kvars, vvars = L.split_by_mask(aggrinv.mask, vars)
    ktuple = L.tuplify(kvars)
    vtuple = L.tuplify(vvars)
    fresh_var_prefix = next(fresh_vars)
    key = fresh_var_prefix + '_key'
    value = fresh_var_prefix + '_value'
    state = fresh_var_prefix + '_state'
    
    # Logic specific to aggregate operator.
    handler = aggrinv.get_handler()
    zero = handler.make_zero_expr()
    empty = handler.make_empty_cond(state)
    updatestate_code = handler.make_update_state_code(fresh_var_prefix,
                                                      state, op, value)
    
    subst = {'_KEY': key, '_KEY_EXPR': ktuple,
             '_VALUE': value, '_VALUE_EXPR': vtuple,
             '_MAP': aggrinv.map, '_STATE': state,
             '_ZERO': zero, '_EMPTY': empty}
    
    decomp_code = (L.DecompAssign(vars, L.Name('_elem')),)
    decomp_code += L.Parser.pc('''
        _KEY = _KEY_EXPR
        _VALUE = _VALUE_EXPR
        ''', subst=subst)
    
    if isinstance(op, L.SetAdd):
        getstate_code = L.Parser.pc('''
            _STATE = _MAP.get(_KEY, _ZERO)
            ''', subst=subst)
        setstate_code = L.Parser.pc('''
            if _KEY in _MAP:
                _MAP.mapdelete(_KEY)
            _MAP.mapassign(_KEY, _STATE)
            ''', subst=subst)
    elif isinstance(op, L.SetRemove):
        getstate_code = L.Parser.pc('''
            _STATE = _MAP[_KEY]
            ''', subst=subst)
        setstate_code = L.Parser.pc('''
            _MAP.mapdelete(_KEY)
            if not _EMPTY:
                _MAP.mapassign(_KEY, _STATE)
            ''', subst=subst)
    else:
        assert()
    
    func_name = aggrinv.get_maint_func_name(op)
    
    func = L.Parser.ps('''
        def _FUNC(_elem):
            _DECOMP
            _GETSTATE
            _UPDATESTATE
            _SETSTATE
        ''', subst={'_FUNC': func_name,
                    '<c>_DECOMP': decomp_code,
                    '<c>_GETSTATE': getstate_code,
                    '<c>_UPDATESTATE': updatestate_code,
                    '<c>_SETSTATE': setstate_code})
    
    return func


class AggrMaintainer(L.NodeTransformer):
    
    def __init__(self, fresh_vars, aggrinv):
        super().__init__()
        self.fresh_vars = fresh_vars
        self.aggrinv = aggrinv
    
    def visit_Module(self, node):
        node = self.generic_visit(node)
        
        funcs = []
        for op in [L.SetAdd(), L.SetRemove()]:
            func = make_aggr_maint_func(self.fresh_vars, self.aggrinv, op)
            funcs.append(func)
        
        node = node._replace(decls=tuple(funcs) + node.decls)
        return node
    
    def visit_RelUpdate(self, node):
        if not isinstance(node.op, (L.SetAdd, L.SetRemove)):
            return node
        if node.rel != self.aggrinv.rel:
            return node
        
        op_name = L.set_update_name(node.op)
        func_name = N.get_maint_func_name(self.aggrinv.map,
                                          node.rel, op_name)
        
        code = (node,)
        call_code = (L.Expr(L.Call(func_name, [L.Name(node.elem)])),)
        code = L.insert_rel_maint(code, call_code, node.op)
        return code
    
    def visit_RelClear(self, node):
        # TODO
        assert()


def get_rel_type(symtab, rel):
    """Helper for returning a relation's element type."""
    # This helper is used below, but it should probably be refactored
    # into a general helper in the type subpackage.
    relsym = symtab.get_symbols().get(rel, None)
    if relsym is None:
        raise L.TransformationError('No symbol info for operand relation {}'
                                    .format(rel))
    t_rel = relsym.type
    # Bad form: What if we have a Set<Bottom>?
    if not (isinstance(t_rel, T.Set) and
            isinstance(t_rel.elt, T.Tuple)):
        raise L.ProgramError('Bad type for relation {}: {}'.format(
                             rel, t_rel))
    return t_rel


def aggrinv_from_query(symtab, query, result_var):
    """Determine the aggregate invariant info for a given query."""
    node = query.node
    assert isinstance(node, L.Aggr)
    
    # Get rel, mask, and param info.
    if isinstance(node.value, L.Name):
        rel = node.value.id
        # Mask will be all-unbound, filled in below.
        mask = None
        params = ()
    elif (isinstance(node.value, L.ImgLookup) and
          isinstance(node.value.set, L.Name)):
        rel = node.value.set.id
        mask = node.value.mask
        params = node.value.bounds
    else:
        raise L.ProgramError('Unknown aggregate form: {}'.format(node))
    
    # Lookup symbol, use type info to determine the relation's arity.
    t_rel = get_rel_type(symtab, rel)
    arity = len(t_rel.elt.elts)
    
    if mask is None:
        mask = L.mask('u' * arity)
    else:
        # Confirm that this arity is consistent with the above mask.
        assert len(mask.m) == arity
    
    return AggrInvariant(result_var, node.op, rel, mask, params)


def incrementalize_aggr(tree, symtab, query, result_var):
    # Form the invariant.
    aggrinv = aggrinv_from_query(symtab, query, result_var)
    handler = aggrinv.get_handler()
    
    # Transform to maintain it.
    tree = AggrMaintainer.run(tree, symtab.fresh_names.vars, aggrinv)
    
    # Transform occurrences of the aggregate.
    
    class CompExpander(S.QueryRewriter):
        def rewrite(self, symbol, name, expr):
            if name == query.name:
                return L.DictLookup(L.Name(aggrinv.map),
                                    L.tuplify(aggrinv.params),
                                    handler.make_zero_expr())
    
    tree = CompExpander.run(tree, symtab, expand=True)
    
    # Determine the result map's type and define its symbol.
    t_rel = get_rel_type(symtab, aggrinv.rel)
    btypes, _ = L.split_by_mask(aggrinv.mask, t_rel.elt.elts)
    t_key = T.Tuple(btypes)
    t_val = handler.result_type(t_rel)
    t_map = T.Map(t_key, t_val)
    symtab.define_map(aggrinv.map, type=t_map)
    
    return tree
