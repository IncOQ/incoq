"""Clause ordering heuristic."""


__all__ = [
    'order_clauses',
]


from incoq.util.collections import OrderedSet
from incoq.util.planner import State, Planner
from incoq.compiler.incast import L


class OrderState(State):
    
    def __init__(self, clausevisitor, bindenv, chosen, remaining):
        self.clv = clausevisitor
        """Clause visitor for determining priorities and LHS vars."""
        self.bindenv = bindenv
        """Set of bound variables."""
        self.chosen = chosen
        """List of determined clauses, in order."""
        self.remaining = remaining
        """OrderedSet of clauses remaining to be ordered."""
    
    def get_successors(self):
        # Sort by priority under the current binding environment.
        def keyfunc(cl):
            return self.clv.get_priority(cl, self.bindenv)
        def allowed(cl):
            return keyfunc(cl) is not None
        clauses = [cl for cl in self.remaining if allowed(cl)]
        clauses = sorted(clauses, key=keyfunc)
        
        # For each, produce a successor state picking that clause,
        # with an updated binding environment.
        succ = []
        for cl in clauses:
            new_bindenv = self.bindenv | set(self.clv.lhs_vars(cl))
            new_chosen = self.chosen + [cl]
            new_remaining = self.remaining - {cl}
            state = OrderState(self.clv, new_bindenv,
                               new_chosen, new_remaining)
            succ.append(state)
        
        return succ
    
    def final(self):
        return len(self.remaining) == 0
    
    def get_answer(self):
        return self.chosen


def order_clauses(clausevisitor, clauses):
    """Order clauses according to their reported priorities.
    
    Use a greedy heuristic: Choose the leftmost clause whose priority
    is best (lowest number). Return the ordered clauses as a list.
    """
    init = OrderState(clausevisitor, set(), [], OrderedSet(clauses))
    try:
        answer = Planner().get_greedy_answer(init)
    except ValueError:
        s = ', '.join(L.Parser.ts(cl) for cl in clauses)
        raise L.TransformationError('No valid order found for clauses: {}'
                                    .format(s))
    return answer
