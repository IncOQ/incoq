"""Unit tests for planner.py."""


import unittest

from incoq.util.planner import *


class FactorState(State):
    
    def __init__(self, n, factors):
        self.factors = factors
        self.n = n
    
    def get_successors(self):
        n = self.n
        states = []
        for i in range(2, n + 1):
            if n % i == 0:
                new_n = n // i
                new_factors = self.factors + (i,)
                states.append(FactorState(new_n, new_factors))
        return states
    
    def get_answer(self):
        return tuple(sorted(self.factors))


class PlannerCase(unittest.TestCase):
    
    def test(self):
        init = FactorState(100, ())
        planner = Planner()
        
        res = planner.get_first_answer(init)
        exp_res = (2, 2, 5, 5)
        self.assertEqual(res, exp_res)
        
        res = planner.get_all_answers(init)
        res = sorted(set(res))
        exp_res = [
            (2, 2, 5, 5),
            (2, 2, 25),
            (2, 5, 10),
            (2, 50),
            (4, 5, 5),
            (4, 25),
            (5, 20),
            (10, 10),
            (100,)
        ]
        self.assertEqual(res, exp_res)


if __name__ == '__main__':
    unittest.main()
