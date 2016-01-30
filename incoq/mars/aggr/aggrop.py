"""Aggregate operator logic."""


__all__ = [
    'AggrOpHandler',
    'CountHandler',
    'SumHandler',
#    'MinHandler',
#    'MaxHandler',
    'handler_for_op',
]


from incoq.mars.incast import L


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
        """Given the name of a variable holding state, return an
        expression projecting the state down to an answer.
        """
        raise NotImplementedError


class CountSumHandler(AggrOpHandler):
    
    """Common code for count and sum."""
    
    kind = None
    
    def make_zero_expr(self):
        return L.Parser.pe('0')
    
    def make_update_state_code(self, prefix, state, op, value):
        opcls = {L.SetAdd: L.Add, L.SetRemove: L.Sub}[op.__class__]
        by = {'count': L.Num(1), 'sum': L.Name(value)}[self.kind]
        return (L.Assign(state, L.BinOp(L.Name(state), opcls(), by)),)
    
    def make_projection_expr(self, state):
        return L.Name(state)

class CountHandler(CountSumHandler):
    kind = 'count'

class SumHandler(CountSumHandler):
    kind = 'sum'


handler_for_op = {
    L.Count: CountHandler,
    L.Sum: SumHandler,
#    L.Min: MinHandler,
#    L.max: MaxHandler,
}
