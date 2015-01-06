"""Aggregate queries.

An aggregate's operand is either a SetMatch or a SetMatch wrapped in
a DemQuery node. A Name node is also allowed and treated as a SetMatch
with a null tuple as the key. If the operand does not use demand, the
aggregate may or may not use demand. If the operand does use demand,
the aggregate must as well. The parameters to the aggregate are always
exactly the parameters to the operand, and if the aggregate uses demand,
all of its parameters are demand-controlled.

For example when using demand for the aggregate, the queries

    sum(setmatch(R, mask, p))
    sum(R)
    sum(DEMQUERY(R, [p1], setmatch(R, "bbu", (p1, p2))))

are replaced by demand-driven map lookups

    DEMQUERY(A, p, A[p])
    DEMQUERY(A, (), A[()])
    DEMQUERY(A, [p1, p2], A[p1, p2])

If the aggregate does not use demand, then the third case is disallowed
and the first two become

    A[p] if p in A else 0
    A[()] if () in A else 0

For a non-demand-driven aggregate, the invariant is that the map has a
key for every combination of parameter values for which the SetMatch
result is non-empty. For a demand-driven one, the invariant is that
the map keys are exactly the same as the aggregate's demand set.

There is also a third option, "half-demand", for when the aggregate is
demand-driven but not the operand. In this case, the invariant is that
there is a key in the aggregate result map whenever that key is in the
U-set or it is a key of the operand's setmatch. This has the benefit
of having constant-time cost for demanding new values, since the only
time an answer isn't already in the map is when the corresponding set
is empty anyway.
"""


__all__ = [
    'AGGR_PREFIX',
    'is_aggrrel',
    
    'AggrSpec',
    'IncAggr',
    'inc_aggr',
    'aggr_needs_batch',
    'aggr_needs_dem',
    'aggr_canuse_halfdemand',
]


from abc import ABCMeta, abstractmethod

from simplestruct import Struct, Field, TypedField
from simplestruct.type import checktype

import oinc.compiler.incast as L
from oinc.compiler.set import Mask


AGGR_PREFIX = 'Aggr'

def is_aggrrel(rel):
    return rel.startswith(AGGR_PREFIX)


class AggrSpec(Struct):
    
    """Aggregate query specification."""
    
    aggrop = TypedField(str)
    """Aggregate operation."""
    rel = TypedField(str)
    """Operand relation."""
    relmask = TypedField(Mask)
    """Operand setmatch mask (Mask.U if operand is just a variable)."""
    params = TypedField(str, seq=True)
    """Parameters."""
    oper_demname = Field()
    """Operand demand name, or None if operand does not use demand."""
    oper_demparams = Field()
    """Operand demand parameters, or None if operand does not use demand."""
    
    @property
    def has_oper_demand(self):
        return self.oper_demname is not None
    
    @classmethod
    def from_node(cls, node):
        checktype(node, L.Aggregate)
        
        if isinstance(node.value, L.DemQuery):
            assert all(isinstance(a, L.Name) for a in node.value.args)
            oper_demparams = tuple(a.id for a in node.value.args)
            oper_demname = node.value.demname
            oper = node.value.value
        else:
            oper_demparams = None
            oper_demname = None
            oper = node.value
        
        if isinstance(oper, L.Name):
            rel = oper.id
            relmask = Mask.U
            params = ()
        
        elif (isinstance(oper, L.SetMatch) and
              isinstance(oper.target, L.Name) and
              L.is_vartuple(oper.key)):
            rel = oper.target.id
            relmask = Mask(oper.mask)
            params = L.get_vartuple(oper.key)
        
        else:
            raise L.ProgramError('Bad aggregate operand', node=node)
        
        return cls(node.op, rel, relmask, params,
                   oper_demname, oper_demparams)
    
    def __init__(self, aggrop, rel, relmask, params,
                 oper_demname, oper_demparams):
        assert self.aggrop in ['count', 'sum', 'min', 'max']
        
        # AST node representation.
        node = L.ln(rel)
        if len(params) > 0:
            node = L.SetMatch(node, relmask.make_node().s,
                              L.tuplify(params))
        if oper_demname is not None:
            node = L.DemQuery(oper_demname,
                              [L.ln(p) for p in oper_demparams], node)
        node = L.Aggregate(node, aggrop, None)
        self.node = node
    
    def __str__(self):
        return L.ts(self.node)
    
    def get_domain_constraints(self, resultname):
        """As in CompSpec.get_domain_constraints(). Each component of
        our result relation besides the last one is equated to a
        position in the underlying operand relation.
        """
        # Get positions of parameters in underlying operand setmatch.
        positions = [i for i, p in enumerate(self.relmask.parts, 1)
                       if p == 'b']
        assert len(positions) == len(self.params)
         
        constrs = [(resultname + '.' + str(i),
                    self.rel + '.' + str(j))
                   for i, j in enumerate(positions, 1)]
        
        return constrs


class IncAggr(Struct):
    
    """Info for incrementalizing an aggregate query."""
    
    aggr = TypedField(L.Aggregate)
    """Aggregate node."""
    spec = TypedField(AggrSpec)
    """Aggregate query info."""
    name = TypedField(str)
    """Result set name."""
    demname = Field()
    """Aggregate demand name, or None if not using demand."""
    uset_lru = Field()
    """None or an integer bound for LRU cache size."""
    half_demand = TypedField(bool)
    """If using demand and this is True, use the "half-demand"
    strategy.
    """
    
    @property
    def has_demand(self):
        return self.demname is not None
    
    @property
    def tracks_counts(self):
        # Counts are needed to know when to remove entries from the
        # aggregate result map. If we're using the normal demand
        # strategy, we only remove entries when keys become undemanded,
        # so counts aren't needed.
        return not (self.has_demand and not self.half_demand)
    
    def __init__(self, aggr, spec, name, demname, uset_lru, half_demand):
        self.params = params = tuple(spec.params)
        """Aggregate parameters (same as operand parameters).
        Also same as aggregate demand parameters.
        """
        
        self.aggrmask = Mask.from_keylen(len(params))
        """Aggregate result retrieval mask."""
        
        self.oper_deltamask = spec.relmask.make_delta_mask()
        """Mask for doing delta test upon change to aggregate operand."""
        
        assert not (spec.has_oper_demand and not self.has_demand), \
            'Can\'t have non-demand-driven aggregate over demand-driven ' \
            'operand'
        
        assert not (half_demand and not self.has_demand), \
            'Can\'t use half-demand strategy when not using demand at all'


class AggrCodegen(metaclass=ABCMeta):
    
    """Abstract base class for aggregate code generation."""
    
    # We maintain in the aggregate result a map from parameters to
    # result state. The case where there are no parameters is
    # handled with the same logic, using the unit tuple as the key.
    #
    # The maintenance code templates are parameterized by code for
    # initializing and updating the result state. The code is provided
    # in subclasses.
    
    # When both the aggregate and operand use demand, the order of
    # events for adding to U is to first bring the aggregate invariant
    # up-to-date with the current contents of the operand (in case the
    # operand is already demanded), and then to propagate demand to
    # the operand. For removing from U it's the opposite order.
    
    # Terminology: A "state" is the information used to incrementally
    # track a single aggregate result for a single set. For simple
    # aggregates this is just the result itself. A "mapval" is
    # an entry in the range of an aggregate result map, which consists
    # of the state possibly paired with a count of how many entries are
    # in the underlying operand set. The count is used to cleanup the
    # map entry in the case that the aggregate is not demand-driven.
    
    def __init__(self, incaggr):
        self.incaggr = incaggr
    
    def make_addu_maint(self, prefix):
        """Generate code for after an addition to U."""
        incaggr = self.incaggr
        assert incaggr.has_demand
        spec = incaggr.spec
        mv_var = prefix + 'val'
        elemvar = prefix + 'elem'
        
        # If we're using half-demand, there's no demand to propagate
        # to the operand. All we need to do is add an entry with count
        # 0 if one is not already there.
        if incaggr.half_demand:
            return L.pc('''
                S_MV = A.smdeflookup(MASK, KEY, None)
                if MV is None:
                    A.smassignkey(MASK, KEY, ZERO, PREFIX)
                ''', subst={'A': L.ln(incaggr.name),
                            'S_MV': L.sn(mv_var),
                            'MV': L.ln(mv_var),
                            'MASK': incaggr.aggrmask.make_node(),
                            'KEY': L.tuplify(incaggr.params),
                            'ZERO': self.make_zero_mapval_expr(),
                            'PREFIX': L.Str(prefix)})
        
        update_code = self.make_update_state_code(
            L.sn(mv_var), L.ln(mv_var), 'add',
            L.ln(elemvar), prefix)
        
        # Make operand demand function call, if operand uses demand.
        if spec.has_oper_demand:
            demfunc = L.N.demfunc(spec.oper_demname)
            call_demfunc = L.Call(L.ln(demfunc),
                                  tuple(L.ln(v) for v in spec.oper_demparams),
                                  (), None, None)
            propagate_code = (L.Expr(call_demfunc),)
        else:
            propagate_code = ()  
        
        code = L.pc('''
            S_MV = ZERO
            for S_ELEM in setmatch(R, RELMASK, PARAMS):
                UPDATE_MAPVAL
            A.smassignkey(AGGRMASK, KEY, MV, PREFIX)
            PROPAGATE_DEMAND
            ''', subst={'S_MV': L.sn(mv_var),
                        'ZERO': self.make_zero_mapval_expr(),
                        'S_ELEM': L.sn(elemvar),
                        'R': spec.rel,
                        'RELMASK': spec.relmask.make_node(),
                        'PARAMS': L.tuplify(spec.params),
                        '<c>UPDATE_MAPVAL': update_code,
                        'A': L.ln(incaggr.name),
                        'AGGRMASK': incaggr.aggrmask.make_node(),
                        'KEY': L.tuplify(incaggr.params),
                        'MV': L.ln(mv_var),
                        'PREFIX': L.Str(prefix),
                        '<c>PROPAGATE_DEMAND': propagate_code})
        
        return code
    
    def make_removeu_maint(self, prefix):
        """Generate code for before a removal from U."""
        incaggr = self.incaggr
        assert incaggr.has_demand
        spec = incaggr.spec
        mv_var = prefix + 'val'
        
        # If we're using half-demand, there's no demand to propagate
        # to the operand. All we need to do is determine whether to
        # do the removal by checking whether the count is 0.
        if incaggr.half_demand:
            return L.pc('''
                S_MV = A.smlookup(MASK, KEY)
                if COUNT == 0:
                    A.smdelkey(MASK, KEY, PREFIX)
                ''', subst={'S_MV': L.sn(mv_var),
                            'COUNT': self.mapval_proj_count(L.ln(mv_var)),
                            'MASK': incaggr.aggrmask.make_node(),
                            'KEY': L.tuplify(incaggr.params),
                            'PREFIX': L.Str(prefix)})
        
        # Generate operand undemand function call, if operand
        # uses demand.
        if spec.has_oper_demand:
            undemfunc = L.N.undemfunc(spec.oper_demname)
            call_undemfunc = L.Call(L.ln(undemfunc),
                                    tuple(L.ln(v) for v in spec.oper_demparams),
                                    (), None, None)
            propagate_code = (L.Expr(call_undemfunc),)
        else:
            propagate_code = ()  
        
        code = L.pc('''
            PROPAGATE_DEMAND
            A.smdelkey(MASK, KEY, PREFIX)
            ''', subst={'A': incaggr.name,
                        'MASK': incaggr.aggrmask.make_node(),
                        'KEY': L.tuplify(incaggr.params),
                        'PREFIX': L.Str(prefix),
                        '<c>PROPAGATE_DEMAND': propagate_code})
        
        return code
    
    def make_oper_maint(self, prefix, op, elem):
        """Generate code for an addition or removal update to the operand."""
        incaggr = self.incaggr
        spec = incaggr.spec
        relmask = spec.relmask
        mv_var = prefix + 'val'
        uset = L.N.uset(incaggr.name)
        vars = tuple(prefix + 'v' + str(i)
                     for i in range(1, len(relmask) + 1))
        bvars, uvars, _ = relmask.split_vars(vars)
        
        nextmapval_code = self.make_update_mapval_code(
                            L.sn(mv_var), L.ln(mv_var),
                            op, L.tuplify(uvars), prefix)
        
        subst = {'S_VARS': L.tuplify(vars, lval=True),
                 'ELEM': elem,
                 'KEY': L.tuplify(bvars),
                 'ZERO': self.make_zero_mapval_expr(),
                 'U': L.ln(uset),
                 'S_MV': L.sn(mv_var),
                 'A': incaggr.name,
                 'MASK': incaggr.aggrmask.make_node(),
                 'KEY': L.tuplify(bvars),
                 '<c>NEXT_MAPVAL': nextmapval_code,
                 'MV': L.ln(mv_var),
                 'PREFIX': L.Str(prefix)}
        
        # We break into different cases based on whether we're using
        # demand or not, because the invariants are different in terms
        # of what keys are in the map.
        
        if incaggr.has_demand and not incaggr.half_demand:
            # If the U-set check passes, the key is definitely in
            # the map, so use strict lookups and updates.
            code = L.pc('''
                S_VARS = ELEM
                if KEY in U:
                    S_MV = A.smlookup(MASK, KEY)
                    NEXT_MAPVAL
                    A.smreassignkey(MASK, KEY, MV, PREFIX)
                ''', subst=subst)
        
        else:
            # The keys in the map should exist iff the corresponding
            # operand set is non-empty. For addition, use non-strict
            # lookups and updates, since we don't know whether it was
            # empty before. For removal, use strict lookup since we
            # know it's non-empty, but check the count to tell whether
            # to delete it or strictly reassign it. When using half-
            # demand, only delete it if it's not demanded.
            
            subst['COUNT'] = self.mapval_proj_count(L.ln(mv_var))
            if incaggr.half_demand:
                # Check for a count of 1, not 0, because it's the value
                # of count before the update.
                delete_cond = L.pe('COUNT == 1 and KEY not in U', subst=subst)
                
            else:
                delete_cond = L.pe('COUNT == 1', subst=subst)
            subst['DELETE_COND'] = delete_cond
            
            if op == 'add':
                code = L.pc('''
                    S_VARS = ELEM
                    S_MV = A.smdeflookup(MASK, KEY, ZERO)
                    NEXT_MAPVAL
                    A.smnsassignkey(MASK, KEY, MV, PREFIX)
                    ''', subst=subst)
            elif op == 'remove':
                code = L.pc('''
                    S_VARS = ELEM
                    S_MV = A.smlookup(MASK, KEY)
                    if DELETE_COND:
                        A.smdelkey(MASK, KEY, PREFIX)
                    else:
                        NEXT_MAPVAL
                        A.smreassignkey(MASK, KEY, MV, PREFIX)
                    ''', subst=subst)
            else:
                assert()
        
        # Guard code in a delta check if necessary.
        if relmask.has_wildcards or relmask.has_equalities:
            code = L.pc('''
                if deltamatch(R, MASK, ELEM, 1):
                    CODE
                ''', subst={'R': spec.rel,
                            'MASK': incaggr.oper_deltamask,
                            'ELEM': elem,
                            '<c>CODE': code})
        
        return code
    
    def make_retrieval_code(self):
        """Make code for retrieving the value of the aggregate result,
        including demanding it.
        """
        incaggr = self.incaggr
        
        params_l = L.List(tuple(L.ln(p) for p in incaggr.params), L.Load())
        
        if incaggr.has_demand:
            code = L.pe('''
                DEMQUERY(NAME, PARAMS_L, RES.smlookup(AGGRMASK, PARAMS_T))
                ''', subst={'NAME': incaggr.name,
                            'PARAMS_L': params_l,
                            'PARAMS_T': L.tuplify(incaggr.params),
                            'RES': incaggr.name,
                            'AGGRMASK': incaggr.aggrmask.make_node()})
        
        else:
            code = L.pe('''
                RES.smdeflookup(AGGRMASK, PARAMS_T, ZERO)
                ''', subst={'RES': incaggr.name,
                            'AGGRMASK': incaggr.aggrmask.make_node(),
                            'PARAMS_T': L.tuplify(incaggr.params),
                            'ZERO': self.make_zero_mapval_expr(),})
        
        code = self.make_proj_mapval_code(code)
        
        return code
    
    def mapval_proj_count(self, mapval_node):
        """Given a node for a mapval, return the count component.
        Requires that we're tracking counts.
        """
        assert self.incaggr.tracks_counts
        return L.pe('MAPVAL[1]', subst={'MAPVAL': mapval_node})
    
    def make_zero_mapval_expr(self):
        """Produce an expression for a map value corresponding to the
        empty set.
        """
        zero_expr = self.make_zero_state_expr()
        # If we don't track counts, return the zero state itself.
        if self.incaggr.tracks_counts:
            return L.pe('(ZERO, 0)', subst={'ZERO': zero_expr})
        else:
            return zero_expr
    
    def make_update_mapval_code(self, mv_snode, mv_lnode,
                               op, val_node, prefix):
        """Produce code to make a new mapval, given an update to
        the corresponding operand. The mapval is read from mv_lnode
        and written to mv_snode.
        """
        # If we don't track counts, the mapvals are the same as
        # the states.
        if not self.incaggr.tracks_counts:
            return self.make_update_state_code(mv_snode, mv_lnode,
                                               op, val_node, prefix)
        
        statevar = prefix + 'state'
        state_lnode = L.ln(statevar)
        state_snode = L.sn(statevar)
        countvar = prefix + 'count'
        
        updatestate_code = self.make_update_state_code(
                            state_snode, state_lnode,
                            op, val_node, prefix)
        
        if op == 'add':
            template = 'COUNTVAR + 1'
        elif op == 'remove':
            template = 'COUNTVAR - 1'
        else:
            assert()
        new_count_node = L.pe(template, subst={'COUNTVAR': L.ln(countvar)})
        
        return L.pc('''
            S_STATE, S_COUNTVAR = MV
            UPDATE_STATE
            S_MV = STATE, NEW_COUNT
            ''', subst={'S_STATE': state_snode,
                        'S_COUNTVAR': L.sn(countvar),
                        'MV': mv_lnode,
                        '<c>UPDATE_STATE': updatestate_code,
                        'STATE': state_lnode,
                        'NEW_COUNT': new_count_node,
                        'S_MV': mv_snode})
    
    def make_proj_mapval_code(self, mapval_node):
        """Given an expression for a mapval, return an expression for
        getting the result value.
        """
        # Fall-through to state proj code if we don't track counts.
        if not self.incaggr.tracks_counts:
            return self.make_proj_state_code(mapval_node)
        
        state_node = L.pe('MAPVAL[0]', subst={'MAPVAL': mapval_node})
        return self.make_proj_state_code(state_node)
    
    @abstractmethod
    def make_zero_state_expr(self):
        """Produce an expression that returns the state corresponding
        to the aggregate's result on an empty set.
        """
    
    @abstractmethod
    def make_update_state_code(self, state_snode, state_lnode,
                              op, val_node, prefix):
        """Produce code to update a state for a given operation and
        value. The state is read from state_lnode and written to
        state_snode.
        """
    
    @abstractmethod
    def make_proj_state_code(self, state_node):
        """Given an expression for a state, return an expression
        for getting the result value.
        """
        return state_node


class CountSumCodegen(AggrCodegen):
    
    """Base class for count and sum aggregates, both of which
    use a simple number as their state.
    """
    
    kind = None
    
    def make_zero_state_expr(self):
        return L.pe('0')
    
    def make_update_state_code(self, state_snode, state_lnode,
                         op, val_node, prefix):
        opstr = {'add': '+', 'remove': '-'}[op]
        bystr = {'count': '1', 'sum': 'VAL'}[self.kind]
        template = L.trim('''
            S_STATE = STATE {OP} {BY}
            '''.format(OP=opstr, BY=bystr))
        return L.pc(template, subst={'S_STATE': state_snode,
                                     'STATE': state_lnode,
                                     'VAL': val_node})
    
    def make_proj_state_code(self, state_node):
        return state_node

class CountCodegen(CountSumCodegen):
    kind = 'count'

class SumCodegen(CountSumCodegen):
    kind = 'sum'


class MinMaxCodegen(AggrCodegen):
    
    """Base class for min and max aggregates, both of which
    use a pair of a tree and a saved number as their state.
    """
    
    kind = None
    
    def make_zero_state_expr(self):
        return L.pe('(Tree(), None)')
    
    def make_update_state_code(self, state_snode, state_lnode,
                         op, val_node, prefix):
        add_template = L.trim('''
            S_TREE, _ = STATE
            TREE[VAL] = None
            S_STATE = (TREE, TREE.MINMAX())
            ''')
        
        remove_template = L.trim('''
            S_TREE, _ = STATE
            del TREE[VAL]
            S_STATE = (TREE, TREE.MINMAX())
            ''')
        
        template = {'add': add_template, 'remove': remove_template}[op]
        
        treevar = prefix + 'tree'
        minmax = {'min': '__min__', 'max': '__max__'}[self.kind] 
        code = L.pc(template,
                    subst={'S_TREE': L.sn(treevar),
                           'TREE': L.ln(treevar),
                           '@MINMAX': minmax,
                           'STATE': state_lnode,
                           'S_STATE': state_snode,
                           'VAL': val_node})
        return code
    
    def make_proj_state_code(self, state_node):
        return L.pe('STATE[1]',
                    subst={'STATE': state_node})

class MinCodegen(MinMaxCodegen):
    kind = 'min'

class MaxCodegen(MinMaxCodegen):
    kind = 'max'


def get_cg_class(aggrop):
    return {'count': CountCodegen,
            'sum': SumCodegen,
            'min': MinCodegen,
            'max': MaxCodegen}[aggrop]


class AggrMaintainer(L.NodeTransformer):
    
    """Maintain an aggregate invariant."""
    
    def __init__(self, manager, incaggr):
        super().__init__()
        self.manager = manager
        self.incaggr = incaggr
        
        cgcls = get_cg_class(incaggr.spec.aggrop)
        self.cg = cgcls(incaggr)
        
        name = self.incaggr.name
        self.addfunc = '_maint_{}_add'.format(name)
        self.removefunc = '_maint_{}_remove'.format(name)
    
    def visit_Module(self, node):
        incaggr = self.incaggr
        self.manager.add_invariant(incaggr.name, incaggr)
        
        add_prefix = self.manager.namegen.next_prefix()
        remove_prefix = self.manager.namegen.next_prefix()
        addcode = self.cg.make_oper_maint(add_prefix, 'add', L.pe('_e'))
        removecode = self.cg.make_oper_maint(remove_prefix,
                                             'remove', L.pe('_e'))
        
        code = L.pc('''
            RES = Set()
            def ADDFUNC(_e):
                ADDCODE
            def REMOVEFUNC(_e):
                REMOVECODE
            ''', subst={'RES': incaggr.name,
                        '<def>ADDFUNC': self.addfunc,
                        '<c>ADDCODE': addcode,
                        '<def>REMOVEFUNC': self.removefunc,
                        '<c>REMOVECODE': removecode})
        node = node._replace(body=code + node.body)
        
        node = self.generic_visit(node)
        
        return node
    
    def visit_SetUpdate(self, node):
        spec = self.incaggr.spec
        
        node = self.generic_visit(node)
        
        if not node.is_varupdate():
            return node
        var, op, elem = node.get_varupdate()
        
        if var == spec.rel:
            precode = postcode = ()
            if op == 'add':
                postcode = L.pc('ADDFUNC(ELEM)',
                                subst={'ADDFUNC': self.addfunc,
                                       'ELEM': elem})
            elif op == 'remove':
                precode = L.pc('REMOVEFUNC(ELEM)',
                                subst={'REMOVEFUNC': self.removefunc,
                                       'ELEM': elem})
            else:
                assert()
            
            code = L.Maintenance(self.incaggr.name, L.ts(node),
                                 precode, (node,), postcode)
        
        elif var == L.N.uset(self.incaggr.name):
            prefix = self.manager.namegen.next_prefix()
            precode = postcode = ()
            if op == 'add':
                postcode = self.cg.make_addu_maint(prefix)
            elif op == 'remove':
                precode = self.cg.make_removeu_maint(prefix)
            else:
                assert()
            
            code = L.Maintenance(self.incaggr.name, L.ts(node),
                                 precode, (node,), postcode)
        
        else:
            code = node
        
        return code


class AggrReplacer(L.NodeTransformer):
    
    """Replace occurrences of an aggregate query."""
    
    def __init__(self, manager, incaggr):
        super().__init__()
        self.manager = manager
        self.incaggr = incaggr
        
        cgcls = get_cg_class(incaggr.spec.aggrop)
        self.cg = cgcls(incaggr)
    
    def visit_Module(self, node):
        incaggr = self.incaggr
        
        # Emit demand function if we use demand.
        if incaggr.has_demand:
            maker = L.DemfuncMaker(incaggr.name, str(incaggr.spec),
                                   incaggr.params, incaggr.uset_lru)
            header_code = maker.make_alldem()
            node = node._replace(body=header_code + node.body)
        
        return self.generic_visit(node)
    
    def visit_Aggregate(self, node):
        node = self.generic_visit(node)
        
        if node != self.incaggr.aggr:
            return node
        
        return self.cg.make_retrieval_code()


class AggrFallbacker(L.NodeTransformer):
    
    """Mark occurrences of a query with the option 'impl' set to
    'batch'.
    """
    
    def __init__(self, aggr):
        super().__init__()
        self.aggr = aggr
    
    def visit_Aggregate(self, node):
        node = self.generic_visit(node)
        
        if node == self.aggr:
            new_opts = dict(node.options)
            new_opts['impl'] = 'batch'
            node = node._replace(options=new_opts)
        
        return node


def inc_aggr(tree, manager, aggr, name,
             *, demand, half_demand):
    """Incrementalize an aggregate query.
    
    If the aggregate is not of the right form, then, if the global
    options permit it, skip transforming this query. In this case,
    the query gets marked with 'impl' = 'batch' to prevent handling
    it again. If the options don't permit it, raise an exception.
    """
    if manager.options.get_opt('verbose'):
        s = ('Incrementalizing ' + name + ': ').ljust(45)
        s += L.ts(aggr)
        print(s)
    
    spec = AggrSpec.from_node(aggr)
    
    uset_lru = manager.options.get_queryopt(aggr, 'uset_lru')
    demname = name if demand else None
    if not demand:
        half_demand = False
    incaggr = IncAggr(aggr, spec, name, demname, uset_lru, half_demand)
    
    tree = AggrReplacer.run(tree, manager, incaggr)
    tree = AggrMaintainer.run(tree, manager, incaggr)
    
    if 'in_original' in aggr.options:
        manager.original_queryinvs.add(name)
    
    return tree


def aggr_needs_batch(aggr):
    """Given an Aggregate node, return True if it must be implemented
    as a batch computation because its form can't be handled
    incrementally.
    """
    try:
        AggrSpec.from_node(aggr)
    except L.ProgramError:
        return True
    else:
        return False

def aggr_needs_dem(aggr):
    """Given an Aggregate node, return True if it must use demand in
    order to be incrementalized.
    """
    return isinstance(aggr.value, L.DemQuery)

def aggr_canuse_halfdemand(aggr):
    """Given an Aggregate node, return True if it may use the half-
    demand strategy.
    """
    # Can't be DemQuery.
    return isinstance(aggr.value, (L.Name, L.SetMatch))
