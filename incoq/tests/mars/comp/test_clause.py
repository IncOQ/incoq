"""Unit tests for test_clause.py."""


import unittest

from incoq.mars.incast import L
from incoq.mars.comp.clause import *


class ClauseCase(unittest.TestCase):
    
    def test_relmember(self):
        cl_info = RelMemberInfo(L.RelMember(['x', 'y', 'z'], 'R'))
        self.assertSequenceEqual(cl_info.vars, ['x', 'y', 'z'])
        self.assertEqual(cl_info.rel, 'R')
        
        self.assertSequenceEqual(cl_info.lhs_vars, ['x', 'y', 'z'])
        
        code = cl_info.get_code(['a', 'x'], [L.Pass()])
        exp_code = L.Parser.pc('''
            for (y, z) in R.imglookup('buu', (x,)):
                pass
            ''')
        self.assertEqual(code, exp_code)
    
    def test_singmember(self):
        cl_info = SingMemberInfo(L.SingMember(['x', 'y', 'z'], L.Name('e')))
        self.assertSequenceEqual(cl_info.vars, ['x', 'y', 'z'])
        self.assertEqual(cl_info.value, L.Name('e'))
        
        self.assertSequenceEqual(cl_info.lhs_vars, ['x', 'y', 'z'])
        
        code = cl_info.get_code(['x'], (L.Pass(),))
        exp_code = L.Parser.pc('''
            (_, y, z) = e
            pass
            ''')
        self.assertEqual(code, exp_code)
    
    def test_withoutmember(self):
        inner_cl_ast = L.RelMember(['x', 'y', 'z'], 'R')
        inner_cl_info = RelMemberInfo(inner_cl_ast)
        cl_info = WithoutMemberInfo(
                    L.WithoutMember(inner_cl_ast, L.Name('e')),
                    inner_cl_info)
        self.assertEqual(cl_info.value, L.Name('e'))
        
        self.assertSequenceEqual(cl_info.lhs_vars, ['x', 'y', 'z'])
        
        code = cl_info.get_code(['x'], (L.Pass(),))
        exp_code = L.Parser.pc('''
            for (y, z) in R.imglookup('buu', (x,)):
                if ((x, y, z) != e):
                    pass
            ''')
        self.assertEqual(code, exp_code)
    
    def test_cond(self):
        cl_info = CondInfo(L.Cond(L.Parser.pe('x == y')))
        self.assertEqual(cl_info.cond, L.Parser.pe('x == y'))
        
        self.assertSequenceEqual(cl_info.lhs_vars, [])
        
        code = cl_info.get_code(['a', 'x', 'y'], [L.Pass()])
        exp_code = L.Parser.pc('''
            if x == y:
                pass
            ''')
        self.assertEqual(code, exp_code)
    
    def test_factory(self):
        # Basic case.
        cl_ast = L.RelMember(['x', 'y', 'z'], 'R')
        cl_info = ClauseInfoFactory().make_clause_info(cl_ast)
        self.assertEqual(cl_info, RelMemberInfo(cl_ast))
        
        # Nested clause case (WithoutMember).
        inner_cl_ast = L.RelMember(['x', 'y', 'z'], 'R')
        cl_ast = L.WithoutMember(inner_cl_ast, L.Name('e'))
        cl_info = ClauseInfoFactory().make_clause_info(cl_ast)
        exp_inner_cl_info = RelMemberInfo(inner_cl_ast)
        exp_cl_info = WithoutMemberInfo(cl_ast, exp_inner_cl_info)
        self.assertEqual(cl_info, exp_cl_info)


if __name__ == '__main__':
    unittest.main()
