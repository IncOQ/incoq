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

from .aggrop import get_handler_for_op


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
    
    restr = TypedField(str, or_none=True)
    """Name of demand set, or None if not using demand."""
    
    def get_oper_maint_func_name(self, op):
        op_name = L.set_update_name(op)
        return N.get_maint_func_name(self.map, self.rel, op_name)
    
    def get_restr_maint_func_name(self, op):
        assert self.uses_demand
        op_name = L.set_update_name(op)
        return N.get_maint_func_name(self.map, self.restr, op_name)
    
    def get_handler(self):
        return get_handler_for_op(self.op.__class__, use_demand=False)
    
    @property
    def uses_demand(self):
        return self.restr is not None


def make_aggr_oper_maint_func(fresh_vars, aggrinv, op):
    """Make the maintenance function for an aggregate invariant and a
    given set update operation (add or remove) to the operand.
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
    updatestate_code = handler.make_update_state_code(fresh_var_prefix,
                                                      state, op, value)
    
    subst = {'_KEY': key, '_KEY_EXPR': ktuple,
             '_VALUE': value, '_VALUE_EXPR': vtuple,
             '_MAP': aggrinv.map, '_STATE': state,
             '_ZERO': zero}
    
    if aggrinv.uses_demand:
        subst['_RESTR'] = aggrinv.restr
    else:
        # Empty conditions are only used when we don't have a
        # restriction set.
        subst['_EMPTY'] = handler.make_empty_cond(state)
    
    decomp_code = (L.DecompAssign(vars, L.Name('_elem')),)
    decomp_code += L.Parser.pc('''
        _KEY = _KEY_EXPR
        _VALUE = _VALUE_EXPR
        ''', subst=subst)
    
    # Determine what kind of get/set state code to generate.
    if isinstance(op, L.SetAdd):
        definitely_preexists = aggrinv.uses_demand
        setstate_mayremove = False
    elif isinstance(op, L.SetRemove):
        definitely_preexists = True
        setstate_mayremove = not aggrinv.uses_demand
    else:
        assert()
    
    if definitely_preexists:
        getstate_template = '_STATE = _MAP[_KEY]'
        delstate_template = '_MAP.mapdelete(_KEY)'
    else:
        getstate_template = '_STATE = _MAP.get(_KEY, _ZERO)'
        delstate_template = '''
            if _KEY in _MAP:
                _MAP.mapdelete(_KEY)
            '''
    
    if setstate_mayremove:
        setstate_template = '''
            if not _EMPTY:
                _MAP.mapassign(_KEY, _STATE)
            '''
    else:
        setstate_template = '_MAP.mapassign(_KEY, _STATE)'
    
    getstate_code = L.Parser.pc(getstate_template, subst=subst)
    delstate_code = L.Parser.pc(delstate_template, subst=subst)
    setstate_code = L.Parser.pc(setstate_template, subst=subst)
    
    maint_code = (
        getstate_code +
        updatestate_code +
        delstate_code +
        setstate_code
    )
    
    # Guard in test if we have a restriction set.
    if aggrinv.uses_demand:
        maint_subst = dict(subst)
        maint_subst['<c>_MAINT'] = maint_code
        maint_code = L.Parser.pc('''
            if _KEY in _RESTR:
                _MAINT
            ''', subst=maint_subst)
    
    func_name = aggrinv.get_oper_maint_func_name(op)
    
    func = L.Parser.ps('''
        def _FUNC(_elem):
            _DECOMP
            _MAINT
        ''', subst={'_FUNC': func_name,
                    '<c>_DECOMP': decomp_code,
                    '<c>_MAINT': maint_code})
    
    return func


def make_aggr_restr_maint_func(fresh_vars, aggrinv, op):
    """Make the maintenance function for an aggregate invariant and
    an update to its restriction set.
    """
    assert isinstance(op, (L.SetAdd, L.SetRemove))
    assert aggrinv.uses_demand
    
    if isinstance(op, L.SetAdd):
        fresh_var_prefix = next(fresh_vars)
        value = fresh_var_prefix + '_value'
        state = fresh_var_prefix + '_state'
        
        rellookup = L.ImgLookup(L.Name(aggrinv.rel),
                                aggrinv.mask, aggrinv.params)
        
        handler = aggrinv.get_handler()
        zero = handler.make_zero_expr()
        updatestate_code = handler.make_update_state_code(fresh_var_prefix,
                                                          state, op, value)
        
        maint_code = L.Parser.pc('''
            _STATE = _ZERO
            for _VALUE in _RELLOOKUP:
                _UPDATESTATE
            _MAP[_KEY] = _STATE
            ''', subst={'_MAP': aggrinv.map, '_KEY': '_key',
                        '_STATE': state, '_ZERO': zero,
                        '_VALUE': value, '_RELLOOKUP': rellookup,
                        '<c>_UPDATESTATE': updatestate_code})
    
    else:
        maint_code = L.Parser.pc('''
            del _MAP[_KEY]
            ''', subst={'_MAP': aggrinv.map, '_KEY': '_key'})
    
    func_name = aggrinv.get_restr_maint_func_name(op)
    
    func = L.Parser.ps('''
        def _FUNC(_key):
            _MAINT
        ''', subst={'_FUNC': func_name,
                    '<c>_MAINT': maint_code})
    
    return func


class AggrMaintainer(L.NodeTransformer):
    
    def __init__(self, fresh_vars, aggrinv):
        super().__init__()
        self.fresh_vars = fresh_vars
        self.aggrinv = aggrinv
    
    def visit_Module(self, node):
        node = self.generic_visit(node)
        
        fv = self.fresh_vars
        ops = [L.SetAdd(), L.SetRemove()]
        funcs = []
        for op in ops:
            func = make_aggr_oper_maint_func(fv, self.aggrinv, op)
            funcs.append(func)
        if self.aggrinv.uses_demand:
            for op in ops:
                func = make_aggr_restr_maint_func(fv, self.aggrinv, op)
                funcs.append(func)
        
        node = node._replace(decls=tuple(funcs) + node.decls)
        return node
    
    def visit_RelUpdate(self, node):
        if not isinstance(node.op, (L.SetAdd, L.SetRemove)):
            return node
        
        if node.rel == self.aggrinv.rel:
            func = self.aggrinv.get_oper_maint_func_name(node.op)
            code = L.insert_rel_maint_call(node, func)
        elif self.aggrinv.uses_demand and node.rel == self.aggrinv.restr:
            func = self.aggrinv.get_restr_maint_func_name(node.op)
            code = L.insert_rel_maint_call(node, func)
        else:
            code = node
        
        return code
    
    def visit_RelClear(self, node):
        if not (node.rel == self.aggrinv.rel or
                self.aggrinv.uses_demand and node.rel == self.aggrinv.restr):
            return node
        
        clear_code = (L.MapClear(self.aggrinv.map),)
        code = L.insert_rel_maint((node,), clear_code, L.SetRemove())
        return code


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
    
    assert isinstance(node, (L.Aggr, L.AggrRestr))
    oper = node.value
    op = node.op
    
    # Get rel, mask, and param info.
    if isinstance(oper, L.Name):
        rel = oper.id
        # Mask will be all-unbound, filled in below.
        mask = None
        params = ()
    elif (isinstance(oper, L.ImgLookup) and
          isinstance(oper.set, L.Name)):
        rel = oper.set.id
        mask = oper.mask
        params = oper.bounds
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
    
    if isinstance(node, L.AggrRestr):
        # Check that the restriction parameters match the ImgLookup
        # parameters
        if node.params != params:
            raise L.TransformationError('AggrRestr params do not match '
                                        'ImgLookup params')
        if not isinstance(node.restr, L.Name):
            raise L.ProgramError('Bad AggrRestr restriction expr')
        restr = node.restr.id
    else:
        restr = None
    
    return AggrInvariant(result_var, op, rel, mask, params, restr)


def incrementalize_aggr(tree, symtab, query, result_var):
    # Form the invariant.
    aggrinv = aggrinv_from_query(symtab, query, result_var)
    handler = aggrinv.get_handler()
    
    # Transform to maintain it.
    tree = AggrMaintainer.run(tree, symtab.fresh_names.vars, aggrinv)
    
    # Transform occurrences of the aggregate.
    
    zero = None if aggrinv.uses_demand else handler.make_zero_expr()
    state_expr = L.DictLookup(L.Name(aggrinv.map),
                              L.tuplify(aggrinv.params), zero)
    lookup_expr = handler.make_projection_expr(state_expr)
    
    class CompExpander(S.QueryRewriter):
        def rewrite(self, symbol, name, expr):
            if name == query.name:
                return lookup_expr
    
    tree = CompExpander.run(tree, symtab, expand=True)
    
    # Determine the result map's type and define its symbol.
    t_rel = get_rel_type(symtab, aggrinv.rel)
    btypes, _ = L.split_by_mask(aggrinv.mask, t_rel.elt.elts)
    t_key = T.Tuple(btypes)
    t_val = handler.result_type(t_rel)
    t_map = T.Map(t_key, t_val)
    symtab.define_map(aggrinv.map, type=t_map)
    
    return tree
