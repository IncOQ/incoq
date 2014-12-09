"""Clause ordering algorithm for computing joins."""


__all__ = [
    'Rate',
    'AsymptoticOrderer',
]


from util.type import checktype_seq


class Rate:
    """Constants for the greedy join order heuristic. Lower is better."""
    # Reserved for delta clause.
    FIRST = -10
    # Prioritize constant-time EnumClause over other constant time
    # clauses to help ensure that demand checks get done before
    # otherwise-type-unsafe operations.
    CONSTANT_MEMBERSHIP = -5
    CONSTANT = 0
    NORMAL = 10
    NOTPREFERRED = 20
    LASTRESORT = 100
    UNRUNNABLE = 1000


class AsymptoticOrderer:
    
    """Clause orderer based on the greedy heuristic of minimum-
    asymptotic-cost-first.
    """
    
    class State:
        
        """State of the search algorithm."""
        
        @classmethod
        def get_initial(cls, clauses, init_bounds, overrides):
            return cls(set(init_bounds), [],
                       list(clauses), overrides)
        
        def __init__(self, bindenv, chosen, remaining, overrides):
            self.bindenv = bindenv
            """Set of bound variables."""
            self.chosen = chosen
            """List of selected, ordered clauses."""
            self.remaining = remaining
            """List of remaining clauses, in no particular order."""
            self.overrides = overrides
            """Override mapping."""
        
        def __repr__(self):
            return '({} : {} : {})'.format(
                ', '.join(self.bindenv),
                ', '.join(str(cl) for cl in self.chosen),
                ', '.join(str(cl) for cl in self.remaining))
        
        def __eq__(self, other):
            return (self.bindenv == other.bindenv and
                    self.chosen == other.chosen and
                    self.remaining == other.remaining,
                    self.overrides == other.overrides)
        
        def is_done(self):
            """Return True if no more stepping is possible."""
            return len(self.remaining) == 0
        
        def get_answer(self):
            """Return the order (must be finished)."""
            assert self.is_done()
            # Add bindenv info to the result.
            result = []
            bindenv = set()
            for i, cl in self.chosen:
                result.append((i, cl, set(bindenv)))
                bindenv.update(cl.enumvars)
            return result
        
        def step_clause(self, item):
            """Return the successor state for choosing a specific
            clause.
            """
            assert item in self.remaining
            
            i, clause = item
            
            new_bindenv = set(self.bindenv)
            new_bindenv.update(clause.enumvars)
            new_chosen = list(self.chosen)
            new_chosen.append(item)
            new_remaining = list(self.remaining)
            new_remaining.remove(item)
            
            return type(self)(new_bindenv, new_chosen, new_remaining,
                              self.overrides)
        
        def step(self, deterministic=False):
            """Return a list of successor states."""
            assert not self.is_done()
            
            def rate_func(item):
                _i, clause = item
                
                for k, v in self.overrides.items():
                    if clause.fits_string(self.bindenv, k):
                        return v
                else:
                    return clause.rate(self.bindenv)
            
            # Stable sort by lowest cost.
            remaining = list(self.remaining)
            remaining.sort(key=rate_func)
            # Find those tied for best, ordered left-to-right.
            from itertools import groupby
            groups = groupby(remaining, key=rate_func)
            cost, best_clauses = next(groups)
            best_clauses = list(best_clauses)
            
            # Error if the cost indicates it's unrunnable.
            assert cost is not Rate.UNRUNNABLE, \
                ('Unrunnable clause chosen by join heuristic\n'
                 'State: ' + str(self))
            
            if deterministic:
                best_clauses = best_clauses[0:1]
            
            return [self.step_clause(cl) for cl in best_clauses]
    
    def __init__(self, overrides=None):
        if overrides == None:
            overrides = {}
        self.overrides = overrides
        """Mapping from clauses to priority, to be used in place of
        Clause.rate().
        """
    
    def process(self, states, first_only=False):
        """Given a list of states, return a list of final states
        contained in or derived from states in this list.
        """
        checktype_seq(states, self.State)
        
        results = []
        for state in states:
            if state.is_done():
                results.append(state)
            else:
                next_states = state.step(deterministic=first_only)
                final_states = self.process(next_states)
                results.extend(final_states)
        return results
    
    def get_orders(self, clauses, init_bounds=(), first_only=False):
        """Return all orders satisfying the heuristic.
        Non-deterministic choices are made when clauses are tied.
        """
        init_state = self.State.get_initial(clauses, init_bounds,
                                            self.overrides)
        final_states = self.process([init_state], first_only=first_only)
        assert all(state.is_done() for state in final_states)
        results = [state.get_answer() for state in final_states]
        return results
    
    def get_order(self, clauses, init_bounds=()):
        """Return a single order."""
        return self.get_orders(clauses, init_bounds=init_bounds,
                               first_only=True)[0]
