"""Aggregate operator logic."""


__all__ = [
    'AggrOpHandler',
    'CountHandler',
    'SumHandler',
    'CountedSumHandler',
    'MinHandler',
    'MaxHandler',
    'get_handler_for_op',
]


from incoq.compiler.incast import L
from incoq.compiler.type import T


class AggrOpHandler:
    
    """Base class for aggregate operator logic handlers."""
    
    def make_zero_expr(self):
        """Return an expression for constructing a zero state, i.e.,
        the state associated with running the aggregate on an empty
        set.
        """
        raise NotImplementedError
    
    def make_update_state_code(self, prefix, state, op, value):
        """Given names for variables holding the state and an added or
        removed value, return code for updating the state.
        """
        raise NotImplementedError
    
    def make_projection_expr(self, state):
        """Given an expression that evaluates to a state, return an
        expression projecting this state down to an answer.
        """
        raise NotImplementedError
    
    def make_empty_cond(self, state):
        """Given the name of a variable holding state, return an
        expression that determines whether the state corresponds to an
        empty argument set.
        """
        raise NotImplementedError
    
    def result_type(self, t_oper):
        """Return the type of the aggregate result, given the type of
        the operand.
        """
        raise NotImplementedError


class CountSumHandler(AggrOpHandler):
    
    """Common code for count and sum."""
    
    kind = None
    
    def make_zero_expr(self):
        return L.Parser.pe('0')
    
    def make_update_state_code(self, prefix, state, op, value):
        opcls = {L.SetAdd: L.Add, L.SetRemove: L.Sub}[op.__class__]
        by = {'count': L.Num(1),
              'sum': L.Name(value)}[self.kind]
        return (L.Assign(state, L.BinOp(L.Name(state), opcls(), by)),)
    
    def make_projection_expr(self, state):
        return state
    
    def result_type(self, t_oper):
        return T.Number

class CountHandler(CountSumHandler):
    kind = 'count'
    
    def make_empty_cond(self, state):
        return L.Parser.pe('_STATE == 0', subst={'_STATE': state})

class SumHandler(CountSumHandler):
    kind = 'sum'


class CountedSumHandler(AggrOpHandler):
    
    def make_zero_expr(self):
        return L.Parser.pe('(0, 0)')
    
    def make_update_state_code(self, prefix, state, op, value):
        value = L.Name(value)
        if isinstance(op, L.SetAdd):
            template = '''
                _STATE = (index(_STATE, 0) + _VALUE, index(_STATE, 1) + 1)
                '''
        elif isinstance(op, L.SetRemove):
            template = '''
                _STATE = (index(_STATE, 0) - _VALUE, index(_STATE, 1) - 1)
                '''
        return L.Parser.pc(template, subst={'_STATE': state, '_VALUE': value})
    
    def make_projection_expr(self, state):
        return L.Subscript(state, L.Num(0))
    
    def make_empty_cond(self, state):
        return L.Parser.pe('index(_STATE, 1) == 0', subst={'_STATE': state})
    
    def result_type(self, t_oper):
        return T.Number


class MinMaxHandler(AggrOpHandler):
    
    """Common code for min and max."""
    
    # State is a pair of a tree and a saved value. The zero state is a
    # pair of an empty tree and None.
    
    kind = None
    
    def make_zero_expr(self):
        # This is an example of why we have to construct a fresh zero
        # state each time it's requested. We wouldn't want the tree that
        # this code constructs to get aliased with the tree of any other
        # state.
        return L.Parser.pe('(Tree(), None)')
    
    def make_update_state_code(self, prefix, state, op, value):
        add_template = '''
            _TREE, _ = _STATE
            _TREE[_VAL] = None
            _STATE = (_TREE, _TREE._MINMAX())
            '''
        remove_template = '''
            _TREE, _ = _STATE
            del _TREE[_VAL]
            _STATE = (_TREE, _TREE._MINMAX())
            '''
        template = {L.SetAdd: add_template,
                    L.SetRemove: remove_template}[op.__class__]
        treevar = prefix + 'tree'
        minmax = {'min': '__min__', 'max': '__max__'}[self.kind]
        code = L.Parser.pc(template, subst={'_TREE': treevar, '_STATE': state,
                                            '_VAL': value, '_MINMAX': minmax})
        return code
    
    def make_projection_expr(self, state):
        return L.Subscript(state, L.Num(1))
    
    def make_empty_cond(self, state):
        return L.Parser.pe('len(index(_STATE, 0)) == 0',
                           subst={'_STATE': state})
    
    def result_type(self, t_oper):
        t_oper = t_oper.join(T.Set(T.Bottom))
        assert t_oper.issmaller(T.Set(T.Top))
        return t_oper.elt

class MinHandler(MinMaxHandler):
    kind = 'min'

class MaxHandler(MinMaxHandler):
    kind = 'max'


def get_handler_for_op(op, *, use_demand):
    if op is L.Sum:
        handlercls = SumHandler if use_demand else CountedSumHandler
    else:
        handlercls = {L.Count: CountHandler,
                      L.Min: MinHandler,
                      L.Max: MaxHandler}[op]
    return handlercls()
