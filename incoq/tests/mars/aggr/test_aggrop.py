"""Unit tests for aggrop.py."""


import unittest

from incoq.mars.incast import L
from incoq.mars.type import T
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
        
        expr = handler.make_projection_expr(L.Name('S'))
        exp_expr = L.Name('S')
        self.assertEqual(expr, exp_expr)
        
        expr = handler.make_empty_cond('S')
        exp_expr = L.Parser.pe('S == 0')
        self.assertEqual(expr, exp_expr)
        
        t_result = handler.result_type(T.Set(T.Tuple([T.String, T.String])))
        self.assertEqual(t_result, T.Number)
    
    def test_sum(self):
        handler = SumHandler()
        
        expr = handler.make_zero_expr()
        exp_expr = L.Parser.pe('0')
        self.assertEqual(expr, exp_expr)
        
        code = handler.make_update_state_code('_', 'S', L.SetAdd(), 'v')
        exp_code = L.Parser.pc('S = S + index(v, 0)')
        self.assertEqual(code, exp_code)
        
        code = handler.make_update_state_code('_', 'S', L.SetRemove(), 'v')
        exp_code = L.Parser.pc('S = S - index(v, 0)')
        self.assertEqual(code, exp_code)
        
        expr = handler.make_projection_expr(L.Name('S'))
        exp_expr = L.Name('S')
        self.assertEqual(expr, exp_expr)
        
        # No implementation of make_empty_cond().
        
        t_result = handler.result_type(T.Set(T.Tuple([T.String, T.String])))
        self.assertEqual(t_result, T.Number)
    
    def test_countedsum(self):
        handler = CountedSumHandler()
        
        expr = handler.make_zero_expr()
        exp_expr = L.Parser.pe('(0, 0)')
        self.assertEqual(expr, exp_expr)
        
        code = handler.make_update_state_code('_', 'S', L.SetAdd(), 'v')
        exp_code = L.Parser.pc('S = (index(S, 0) + index(v, 0), '
                                    'index(S, 1) + 1)')
        self.assertEqual(code, exp_code)
        
        code = handler.make_update_state_code('_', 'S', L.SetRemove(), 'v')
        exp_code = L.Parser.pc('S = (index(S, 0) - index(v, 0), '
                                    'index(S, 1) - 1)')
        self.assertEqual(code, exp_code)
        
        expr = handler.make_projection_expr(L.Name('S'))
        exp_expr = L.Parser.pe('index(S, 0)')
        self.assertEqual(expr, exp_expr)
        
        expr = handler.make_empty_cond('S')
        exp_expr = L.Parser.pe('index(S, 1) == 0')
        self.assertEqual(expr, exp_expr)
        
        t_result = handler.result_type(T.Set(T.Tuple([T.String, T.String])))
        self.assertEqual(t_result, T.Number)
    
    def test_min(self):
        handler = MinHandler()
        
        expr = handler.make_zero_expr()
        exp_expr = L.Parser.pe('(Tree(), None)')
        self.assertEqual(expr, exp_expr)
        
        code = handler.make_update_state_code('_', 'S', L.SetAdd(), 'v')
        exp_code = L.Parser.pc('''
            _tree, _ = S
            _tree[v] = None
            S = (_tree, _tree.__min__())
            ''')
        self.assertEqual(code, exp_code)
        
        code = handler.make_update_state_code('_', 'S', L.SetRemove(), 'v')
        exp_code = L.Parser.pc('''
            _tree, _ = S
            del _tree[v]
            S = (_tree, _tree.__min__())
            ''')
        self.assertEqual(code, exp_code)
        
        expr = handler.make_projection_expr(L.Name('S'))
        exp_expr = L.Parser.pe('index(S, 1)')
        self.assertEqual(expr, exp_expr)
        
        expr = handler.make_empty_cond('S')
        exp_expr = L.Parser.pe('len(index(S, 0)) == 0')
        self.assertEqual(expr, exp_expr)
        
        t_result = handler.result_type(T.Set(T.Tuple([T.String, T.String])))
        self.assertEqual(t_result, T.Tuple([T.String, T.String]))
    
    def test_max(self):
        handler = MaxHandler()
        
        expr = handler.make_zero_expr()
        exp_expr = L.Parser.pe('(Tree(), None)')
        self.assertEqual(expr, exp_expr)
        
        code = handler.make_update_state_code('_', 'S', L.SetAdd(), 'v')
        exp_code = L.Parser.pc('''
            _tree, _ = S
            _tree[v] = None
            S = (_tree, _tree.__max__())
            ''')
        self.assertEqual(code, exp_code)
        
        code = handler.make_update_state_code('_', 'S', L.SetRemove(), 'v')
        exp_code = L.Parser.pc('''
            _tree, _ = S
            del _tree[v]
            S = (_tree, _tree.__max__())
            ''')
        self.assertEqual(code, exp_code)
        
        expr = handler.make_projection_expr(L.Name('S'))
        exp_expr = L.Parser.pe('index(S, 1)')
        self.assertEqual(expr, exp_expr)
        
        expr = handler.make_empty_cond('S')
        exp_expr = L.Parser.pe('len(index(S, 0)) == 0')
        self.assertEqual(expr, exp_expr)
        
        t_result = handler.result_type(T.Set(T.Tuple([T.String, T.String])))
        self.assertEqual(t_result, T.Tuple([T.String, T.String]))


if __name__ == '__main__':
    unittest.main()
