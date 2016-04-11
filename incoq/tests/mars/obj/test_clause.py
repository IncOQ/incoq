"""Unit tests for clause.py."""


import unittest

from incoq.mars.incast import L
from incoq.mars.comp import Priority
from incoq.mars.obj.clause import *


class ClauseCase(unittest.TestCase):
    
    def setUp(self):
        self.visitor = ObjClauseVisitor()
    
    def test_mmember(self):
        v = self.visitor
        
        cl = L.MMember('s', 'e')
        
        self.assertSequenceEqual(v.lhs_vars(cl), ['s', 'e'])
        self.assertEqual(v.rhs_rel(cl), '_M')
        
        self.assertSequenceEqual(v.uncon_vars(cl), ['s'])
        
        # All bound.
        code = v.get_code(cl, ['s', 'e'], (L.Pass(),))
        exp_code = L.Parser.pc('''
            if isset(s):
                if e in s:
                    pass
            ''')
        self.assertEqual(code, exp_code)
        
        # Forward lookup.
        code = v.get_code(cl, ['s'], (L.Pass(),))
        exp_code = L.Parser.pc('''
            if isset(s):
                for e in s:
                    pass
            ''')
        self.assertEqual(code, exp_code)
        
        # Other use.
        code = v.get_code(cl, ['e'], (L.Pass(),))
        exp_code = L.Parser.pc('''
            for s in unwrap(_M.imglookup('ub', (e,))):
                pass
            ''')
        self.assertEqual(code, exp_code)
        
        cl2 = v.rename_lhs_vars(cl, lambda x: '_' + x)
        self.assertEqual(cl2, L.MMember('_s', '_e'))
        cl2 = v.rename_rhs_rel(cl, lambda x: '_' + x)
        self.assertEqual(cl2, L.RelMember(['s', 'e'], '__M'))
    
    def test_fmember(self):
        v = self.visitor
        
        cl = L.FMember('o', 'v', 'f')
        
        self.assertSequenceEqual(v.lhs_vars(cl), ['o', 'v'])
        self.assertEqual(v.rhs_rel(cl), '_F_f')
        
        self.assertSequenceEqual(v.uncon_vars(cl), ['o'])
        
        b = v.functionally_determines(cl, ['o'])
        self.assertTrue(b)
        
        pri = v.get_priority(cl, ['o'])
        self.assertEqual(pri, Priority.Constant)
        
        # All bound.
        code = v.get_code(cl, ['o', 'v'], (L.Pass(),))
        exp_code = L.Parser.pc('''
            if hasfield(o, 'f'):
                if v == o.f:
                    pass
            ''')
        self.assertEqual(code, exp_code)
        
        # Forward lookup.
        code = v.get_code(cl, ['o'], (L.Pass(),))
        exp_code = L.Parser.pc('''
            if hasfield(o, 'f'):
                v = o.f
                pass
            ''')
        self.assertEqual(code, exp_code)
        
        # Other use.
        code = v.get_code(cl, ['v'], (L.Pass(),))
        exp_code = L.Parser.pc('''
            for o in unwrap(_F_f.imglookup('ub', (v,))):
                pass
            ''')
        self.assertEqual(code, exp_code)
        
        cl2 = v.rename_lhs_vars(cl, lambda x: '_' + x)
        self.assertEqual(cl2, L.FMember('_o', '_v', 'f'))
        cl2 = v.rename_rhs_rel(cl, lambda x: '_' + x)
        self.assertEqual(cl2, L.RelMember(['o', 'v'], '__F_f'))
    
    def test_mapmember(self):
        v = self.visitor
        
        cl = L.MAPMember('m', 'k', 'v')
        
        self.assertSequenceEqual(v.lhs_vars(cl), ['m', 'k', 'v'])
        self.assertEqual(v.rhs_rel(cl), '_MAP')
        
        self.assertSequenceEqual(v.uncon_vars(cl), ['m'])
        
        b = v.functionally_determines(cl, ['m', 'k'])
        self.assertTrue(b)
        
        pri = v.get_priority(cl, ['m', 'k'])
        self.assertEqual(pri, Priority.Constant)
        
        # All bound.
        code = v.get_code(cl, ['m', 'k', 'v'], (L.Pass(),))
        exp_code = L.Parser.pc('''
            if ismap(m):
                if v == m[k]:
                    pass
            ''')
        self.assertEqual(code, exp_code)
        
        # Forward lookup.
        code = v.get_code(cl, ['m', 'k'], (L.Pass(),))
        exp_code = L.Parser.pc('''
            if ismap(m):
                v = m[k]
                pass
            ''')
        self.assertEqual(code, exp_code)
        
        # Map iteration.
        code = v.get_code(cl, ['m'], (L.Pass(),))
        exp_code = L.Parser.pc('''
            if ismap(m):
                for (k, v) in m.items():
                    pass
            ''')
        
        # Other use.
        code = v.get_code(cl, ['v'], (L.Pass(),))
        exp_code = L.Parser.pc('''
            for (m, k) in _MAP.imglookup('uub', (v,)):
                pass
            ''')
        self.assertEqual(code, exp_code)
        
        cl2 = v.rename_lhs_vars(cl, lambda x: '_' + x)
        self.assertEqual(cl2, L.MAPMember('_m', '_k', '_v'))
        cl2 = v.rename_rhs_rel(cl, lambda x: '_' + x)
        self.assertEqual(cl2, L.RelMember(['m', 'k', 'v'], '__MAP'))
    
    def test_tupmember(self):
        v = self.visitor
        
        cl = L.TUPMember('t', ['v1', 'v2'])
        
        self.assertSequenceEqual(v.lhs_vars(cl), ['t', 'v1', 'v2'])
        self.assertEqual(v.rhs_rel(cl), '_TUP_2')
        
        self.assertSequenceEqual(v.uncon_vars(cl), ['t'])
        
        b = v.functionally_determines(cl, ['t'])
        self.assertTrue(b)
        
        pri = v.get_priority(cl, ['t', 'v1'])
        self.assertEqual(pri, Priority.Constant)
        
        # All bound.
        code = v.get_code(cl, ['t', 'v1', 'v2'], (L.Pass(),))
        exp_code = L.Parser.pc('''
            if hasarity(t, 2):
                if t == (v1, v2):
                    pass
            ''')
        self.assertEqual(code, exp_code)
        
        # Full forward lookup.
        code = v.get_code(cl, ['t'], (L.Pass(),))
        exp_code = L.Parser.pc('''
            if hasarity(t, 2):
                (v1, v2) = t
                pass
            ''')
        self.assertEqual(code, exp_code)
        
        # Mixed forward lookup.
        code = v.get_code(cl, ['t', 'v1'], (L.Pass(),))
        exp_code = L.Parser.pc('''
            if hasarity(t, 2):
                (_, v2) = t
                if t == (v1, v2):
                    pass
            ''')
        self.assertEqual(code, exp_code)
        
        # Full backward lookup.
        code = v.get_code(cl, ['v1', 'v2'], (L.Pass(),))
        exp_code = L.Parser.pc('''
            t = (v1, v2)
            pass
            ''')
        self.assertEqual(code, exp_code)
        
        # Other use.
        with self.assertRaises(L.TransformationError):
            code = v.get_code(cl, ['v2'], (L.Pass(),))
        
        cl2 = v.rename_lhs_vars(cl, lambda x: '_' + x)
        self.assertEqual(cl2, L.TUPMember('_t', ['_v1', '_v2']))
        cl2 = v.rename_rhs_rel(cl, lambda x: '_' + x)
        self.assertEqual(cl2, L.RelMember(['t', 'v1', 'v2'], '__TUP_2'))
    
    def test_no_typecheck(self):
        v = ObjClauseVisitor_NoTC()
        
        cl = L.MMember('s', 'e')
        
        # All bound.
        code = v.get_code(cl, ['s', 'e'], (L.Pass(),))
        exp_code = L.Parser.pc('''
            if e in s:
                pass
            ''')
        self.assertEqual(code, exp_code)


if __name__ == '__main__':
    unittest.main()
