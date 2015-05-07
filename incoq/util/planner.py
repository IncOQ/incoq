"""A naive engine for non-deterministically stepping from an
initial computation state to zero or more final states.
"""


__all__ = [
    'State',
    'Planner',
]


from abc import ABCMeta, abstractmethod

from simplestruct.type import checktype_seq


class State(metaclass=ABCMeta):
    
    """Computation state."""
    
    @abstractmethod
    def accepts(self):
        """If this is a finished state, return True if this state
        has an answer, i.e. has not failed.
        """
    
    @abstractmethod
    def get_answer(self):
        """Return the solution represented by this state.
        Invalid (potentially raising ValueError) if this state
        is not a finished, accepting state.
        """
    
    @abstractmethod
    def successors(self):
        """Return a sequence of non-deterministic successor states
        that may immediately follow this one. For finished states,
        this must be an empty sequence. For other states, the empty
        sequence indicates failure along this computation path.
        """


class Planner:
    
    """Solver that takes an initial state and finds one or more final
    states.
    """
    
    def process(self, states, first_only=False):
        """Given a list of states, return a list of finished accepting
        states that are either immediately contained in this list, or
        that can be recursively derived from the other states.
        
        If first_only is True, only the first successor state for
        each state in the list will be considered.
        """
        checktype_seq(states, State)
        
        results = []
        for state in states:
            succ = state.successors()
            if first_only:
                succ = succ[:1]
                
            if len(succ) == 0 and state.accepts():
                results.append(state)
            else:
                results.extend(self.process(succ))
        
        return results
    
    def get_all_answers(self, init_state):
        """Return all solutions corresponding to final states
        reachable from init_state. No duplicate elimination is
        performed.
        """
        return [s.get_answer() for s in self.process([init_state])]
    
    def get_answer(self, init_state):
        """Return an answer from a deterministic run. If this
        run reaches failure, ValueError is raised. Note that
        this may occur even if a different run contains a solution.
        """
        ans = self.process([init_state], first_only=True)
        if len(ans) == 0:
            raise ValueError('No solution found')
        return ans[0].get_answer()
