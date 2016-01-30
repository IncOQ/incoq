"""Unit tests for aggrop.py."""


import unittest

from incoq.mars.incast import L
from incoq.mars.aggr.aggrop import *


class TransCase(unittest.TestCase):
    
    def test_count(self):
        handler = CountHandler()
        
        expr = handler.make_zero_expr()
        exp_expr = L.Parser.pe('0')
        self.assertEqual(expr, exp_expr)
        
        code = handler.make_update_state_code('_', 'S', L.SetAdd(), 'v')
        exp_code = L.Parser.pc('S = S + 1')
        self.assertEqual(code, exp_code)
        
        code = handler.make_update_state_code('_', 'S', L.SetRemove(), 'v')
        exp_code = L.Parser.pc('S = S - 1')
        self.assertEqual(code, exp_code)
        
        expr = handler.make_projection_expr('S')
        exp_expr = L.Name('S')
        self.assertEqual(code, exp_code)
    
    def test_sum(self):
        handler = SumHandler()
        
        expr = handler.make_zero_expr()
        exp_expr = L.Parser.pe('0')
        self.assertEqual(expr, exp_expr)
        
        code = handler.make_update_state_code('_', 'S', L.SetAdd(), 'v')
        exp_code = L.Parser.pc('S = S + v')
        self.assertEqual(code, exp_code)
        
        code = handler.make_update_state_code('_', 'S', L.SetRemove(), 'v')
        exp_code = L.Parser.pc('S = S - v')
        self.assertEqual(code, exp_code)
        
        expr = handler.make_projection_expr('S')
        exp_expr = L.Name('S')
        self.assertEqual(code, exp_code)


if __name__ == '__main__':
    unittest.main()
