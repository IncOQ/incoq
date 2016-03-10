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
        return True
    
    def get_answer(self):
        """For a successful final state, return the answer. For any
        other state, raise ValueError.
        """
        raise NotImplementedError


class Planner:
    
    """Solver that takes an initial state and searches for reachable
    accepting states.
    """
    
    def process(self, state, *, first_only, backtracking):
        """Return a pair of a list of accepting states that are
        reachable from the given state, and a bool indicating whether
        or not a cut was performed.
        
        If first_only is False, then all reachable accepting states
        are returned, and cuts will never occur. If first_only is True,
        then as soon as the first accepting state is found, it will be
        returned and the cut flag will be True; if no accepting state
        is found then an empty list and False will be returned.
        
        If backtracking is False, a cut will be performed after every
        branch. Thus, either a greedy search finds the answer or the
        search fails.
        """
        if state.final() and state.succeeds():
            cut = first_only or not backtracking
            return [state], cut
        
        results = []
        succ = state.get_successors()
        for state in succ:
            subresults, cut = self.process(state,
                                           first_only=first_only,
                                           backtracking=backtracking)
            if cut:
                # Propagate the lone result and cut flag.
                return subresults, True
            results.extend(subresults)
        
        cut = not backtracking
        return results, cut
    
    def get_all_answers(self, init_state):
        """Return all answers obtained from an initial state.
        (No duplicate elimination is performed.)
        """
        states, _ = self.process(init_state,
                                 first_only=False,
                                 backtracking=True)
        return [s.get_answer() for s in states]
    
    def get_first_answer(self, init_state, *, backtracking=True):
        """As above, but return the first answer instead of a list,
        or raise ValueError if there is no answer.
        """
        states, _ = self.process(init_state,
                                 first_only=True,
                                 backtracking=backtracking)
        if len(states) == 0:
            raise ValueError('No solution found')
        return states[0].get_answer()
    
    def get_greedy_answer(self, init_state):
        return self.get_first_answer(init_state,
                                     backtracking=False)
