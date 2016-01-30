"""Aggregate invariant transformation."""


__all__ = [
    'AggrInvariant',
]


from simplestruct import Struct, TypedField

from incoq.mars.incast import L
from incoq.mars.symbol import N

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
    handler = handler_for_op[aggrinv.op.__class__]()
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
