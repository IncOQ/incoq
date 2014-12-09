"""Unit tests for order.py."""


import unittest

import invinc.incast as L

from .clause import EnumClause, CondClause

from .order import *
State = AsymptoticOrderer.State


class TestOrder(unittest.TestCase):
    
    @classmethod
    def setUpClass(self):
        def ec(source):
            return EnumClause.from_expr(L.pe(source))
        def cc(source):
            return CondClause(L.pe(source))
        
        self.clauses = [
            ec('(a, b) in R'),
            ec('(a, c) in R'),
            ec('(b, c) in R'),
            cc('a != 5'),
            cc('d != 5'),
        ]
         
        self.bindenv = {'a', 'b'}
    
    def test_rate(self):
        rates = [cl.rate(self.bindenv) for cl in self.clauses]
        expected = [
            Rate.CONSTANT_MEMBERSHIP,
            Rate.NORMAL,
            Rate.NORMAL,
            Rate.CONSTANT,
            Rate.UNRUNNABLE,
        ]
        
        self.assertEqual(rates, expected)
    
    def test_step(self):
        def chosen_list(*args):
            return list(map(lambda i: (i, self.clauses[i]), args))
        def remaining_list(*args):
            return list(map(lambda i: (i, self.clauses[i]), args))
        
        state = State({'a', 'b'},
                      chosen_list(0, 3),
                      remaining_list(1, 2, 4),
                      {})
        
        exp_state1 = State({'a', 'b', 'c'},
                           chosen_list(0, 3, 1),
                           remaining_list(2, 4),
                           {})
        exp_state2 = State({'a', 'b', 'c'},
                           chosen_list(0, 3, 2),
                           remaining_list(1, 4),
                           {})
        
        self.assertEqual(state.step(deterministic=False),
                         [exp_state1, exp_state2])
        self.assertEqual(state.step(deterministic=True),
                         [exp_state1])
    
    def test_get_orders(self):
        cl = self.clauses
        order = AsymptoticOrderer().get_order(enumerate(self.clauses[0:4]))
        
        exp_order = [
            (0, cl[0], set()),
            (3, cl[3], {'a', 'b'}),
            (1, cl[1], {'a', 'b'}),
            (2, cl[2], {'a', 'b', 'c'}),
        ]
        
        self.assertEqual(order, exp_order)
    
    def test_init_bounds(self):
        AsymptoticOrderer().get_order(enumerate(self.clauses),
                                      init_bounds=('d',))
        
        with self.assertRaises(AssertionError):
            AsymptoticOrderer().get_order(enumerate(self.clauses))
    
    def test_overrides(self):
        orderer = AsymptoticOrderer({'(d != 5)': -1})
        order = orderer.get_order(enumerate(self.clauses))
        
        self.assertEqual(order[0], (4, self.clauses[4], set()))


if __name__ == '__main__':
    unittest.main()
