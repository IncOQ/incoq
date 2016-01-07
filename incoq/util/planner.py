"""A simple engine for non-deterministic search, based on user-defined
states.
"""


__all__ = [
    'State',
    'Planner',
]


class State:
    
    """Base class for user-defined search state.
    
    Each state has zero or more successor states arranged in some order.
    A state is final if it has zero successors. A final state is either
    a success or failure. If it succeeds then it has a defined answer.
    """
    
    def get_successors(self):
        """Sequence of successor states."""
        raise NotImplementedError
    
    def final(self):
        """Return whether this is a final state."""
        return len(self.get_successors()) == 0
    
    def succeeds(self):
        """For a final state, return whether this state succeeds."""
        raise NotImplementedError
    
    def get_answer(self):
        """For a successful final state, return the answer. For any
        other state, raise ValueError.
        """
        raise NotImplementedError


class Planner:
    
    """Solver that takes an initial state and searches for reachable
    accepting states.
    """
    
    def process(self, state, first_only=False):
        """Return a list of accepting states that are reachable from
        the given state.
        
        If first_only is True, stop as soon as one answer is found.
        """
        results = []
        succ = state.get_successors()
        
        for state in succ:
            if state.final() and state.succeeds():
                subresults = [state]
            else:
                subresults = self.process(state)
            
            if first_only:
                if len(subresults) > 0:
                    return [subresults[0]]
            
            results.extend(subresults)
        
        return results
    
    def get_all_answers(self, init_state):
        """Return all answers obtained from an initial state.
        (No duplicate elimination is performed.)
        """
        return [s.get_answer() for s in self.process(init_state)]
    
    def get_first_answer(self, init_state):
        """As above, but return the first answer instead of a list,
        or raise ValueError if there is no answer.
        """
        states = self.process(init_state, first_only=True)
        if len(states) == 0:
            raise ValueError('No solution found')
        return states[0].get_answer()
