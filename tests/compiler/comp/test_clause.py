"""Unit tests for clause.py."""


import unittest

from incoq.compiler.incast import L
from incoq.compiler.comp.clause import *


class ClauseCase(unittest.TestCase):
    
    def setUp(self):
        self.visitor = CoreClauseVisitor()
    
    def test_constrained(self):
        v = self.visitor
        
        # Mock up a handler with a different constrained mask.
        class DummyHandler(RelMemberHandler):
            def constrained_mask(self, cl):
                return [True, False, True]
        v.handle_RelMember = DummyHandler(v)
        
        cl = L.RelMember(['x', 'y', 'z'], 'R')
        self.assertSequenceEqual(v.constrained_mask(cl), [True, False, True])
        self.assertSequenceEqual(v.con_lhs_vars(cl), ['x', 'z'])
        self.assertSequenceEqual(v.uncon_lhs_vars(cl), ['y'])
        self.assertSequenceEqual(v.uncon_vars(cl), ['y'])
    
    def test_tags(self):
        v = self.visitor
        
        cl = L.RelMember(['x', 'y', 'z'], 'R')
        self.assertSequenceEqual(v.tagsin_mask(cl), [True, True, True])
        self.assertSequenceEqual(v.tagsout_mask(cl), [True, True, True])
        self.assertIs(v.should_filter(cl, ['x', 'y']), ShouldFilter.Yes)
        self.assertIs(v.should_filter(cl, ['x', 'y', 'z']), ShouldFilter.No)
        self.assertFalse(v.filter_needs_preds(cl))
        
        class DummyHandler(RelMemberHandler):
            def constrained_mask(self, cl):
                return [True, False, True]
        v.handle_RelMember = DummyHandler(v)
        
        self.assertSequenceEqual(v.tagsin_mask(cl), [False, True, False])
        self.assertSequenceEqual(v.tagsout_mask(cl), [True, False, True])
        self.assertIs(v.should_filter(cl, ['x', 'z']), ShouldFilter.Yes)
        self.assertIs(v.should_filter(cl, ['y']), ShouldFilter.No)
        self.assertIs(v.should_filter(cl, ['x', 'y']), ShouldFilter.No)
        
        cl = L.Cond(L.Parser.pe('True'))
        self.assertIs(v.should_filter(cl, []), ShouldFilter.No)
    
    def check_rename(self, cl):
        v = self.visitor
        
        # lhs_vars.
        init_vars = v.lhs_vars(cl)
        cl2 = v.rename_lhs_vars(cl, lambda x: '_' + x)
        exp_vars = tuple('_' + x for x in init_vars)
        self.assertSequenceEqual(v.lhs_vars(cl2), exp_vars)
        
        # rhs_rel.
        init_rel = v.rhs_rel(cl)
        cl2 = v.rename_rhs_rel(cl, lambda x: '_' + x)
        exp_rel = '_' + init_rel if init_rel is not None else None
        self.assertEqual(v.rhs_rel(cl2), exp_rel)
    
    def test_handler(self):
        self.assertIsInstance(self.visitor.handle_RelMember,
                              RelMemberHandler)
    
    def test_subtract(self):
        v = self.visitor
        
        cl = L.RelMember(['x', 'y', 'z'], 'R')
        cl2 = v.subtract(cl, L.Name('e'))
        exp_cl2 = L.WithoutMember(cl, L.Name('e'))
        self.assertEqual(cl2, exp_cl2)
        
        cl = L.Cond(L.Parser.pe('True'))
        with self.assertRaises(NotImplementedError):
            v.subtract(cl, L.Name('e'))
    
    def test_assert_unique(self):
        assert_unique(['x', 'y', 'z'])
        with self.assertRaises(AssertionError):
            assert_unique(['x', 'y', 'x'])
    
    def test_relmember(self):
        v = self.visitor
        
        cl = L.RelMember(['x', 'y', 'z'], 'R')
        
        self.assertIs(v.kind(cl), Kind.Member)
        self.assertSequenceEqual(v.lhs_vars(cl), ['x', 'y', 'z'])
        self.assertEqual(v.rhs_rel(cl), 'R')
        
        b = v.functionally_determines(cl, ['x', 'y'])
        self.assertFalse(b)
        b = v.functionally_determines(cl, ['x', 'y', 'z'])
        self.assertTrue(b)
        
        pri = v.get_priority(cl, ['a', 'x', 'y', 'z'])
        self.assertEqual(pri, Priority.Constant)
        pri = v.get_priority(cl, ['a', 'x'])
        self.assertEqual(pri, Priority.Normal)
        pri = v.get_priority(cl, ['a'])
        self.assertEqual(pri, Priority.Unpreferred)
        
        # All bound.
        code = v.get_code(cl, ['a', 'x', 'y', 'z'], (L.Pass(),))
        exp_code = L.Parser.pc('''
            if (x, y, z) in R:
                pass
            ''')
        self.assertEqual(code, exp_code)
        
        # All unbound.
        code = v.get_code(cl, ['a'], (L.Pass(),))
        exp_code = L.Parser.pc('''
            for (x, y, z) in R:
                pass
            ''')
        self.assertEqual(code, exp_code)
        
        # Mixed.
        code = v.get_code(cl, ['a', 'x'], (L.Pass(),))
        exp_code = L.Parser.pc('''
            for (y, z) in R.imglookup('buu', (x,)):
                pass
            ''')
        self.assertEqual(code, exp_code)
        
        # Mixed, one unbound.
        code = v.get_code(cl, ['a', 'x', 'y'], (L.Pass(),))
        exp_code = L.Parser.pc('''
            for z in unwrap(R.imglookup('bbu', (x, y))):
                pass
            ''')
        self.assertEqual(code, exp_code)
        
        self.check_rename(cl)
        
        cl2 = v.singletonize(cl, L.Name('e'))
        exp_cl2 = L.SingMember(['x', 'y', 'z'], L.Name('e'))
        self.assertEqual(cl2, exp_cl2)
    
    def test_singmember(self):
        v = self.visitor
        
        cl = L.SingMember(['x', 'y', 'z'], L.Name('e'))
        
        self.assertIs(v.kind(cl), Kind.Member)
        self.assertSequenceEqual(v.lhs_vars(cl), ['x', 'y', 'z'])
        self.assertEqual(v.rhs_rel(cl), None)
        self.assertSequenceEqual(v.uncon_vars(cl), ['e'])
        
        self.assertIs(v.should_filter(cl, []), ShouldFilter.Intersect)
        
        b = v.functionally_determines(cl, ['x'])
        self.assertTrue(b)
        
        pri = v.get_priority(cl, ['a', 'x', 'y'])
        self.assertEqual(pri, Priority.Constant)
        
        # All bound.
        code = v.get_code(cl, ['a', 'x', 'y', 'z'], (L.Pass(),))
        exp_code = L.Parser.pc('''
            if (x, y, z) == e:
                pass
            ''')
        self.assertEqual(code, exp_code)
        
        # All unbound.
        code = v.get_code(cl, ['a'], (L.Pass(),))
        exp_code = L.Parser.pc('''
            x, y, z = e
            pass
            ''')
        self.assertEqual(code, exp_code)
        
        # Mixed.
        code = v.get_code(cl, ['a', 'x'], (L.Pass(),))
        exp_code = L.Parser.pc('''
            (_, y, z) = e
            if (x, y, z) == e:
                pass
            ''')
        self.assertEqual(code, exp_code)
        
        self.check_rename(cl)
        
        with self.assertRaises(NotImplementedError):
            v.singletonize(cl, L.Name('f'))
    
    def test_withoutmember(self):
        v = self.visitor
        
        cl = L.WithoutMember(L.RelMember(['x', 'y', 'z'], 'R'),
                             L.Name('e'))
        
        self.assertIs(v.kind(cl), Kind.Member)
        self.assertSequenceEqual(v.lhs_vars(cl), ['x', 'y', 'z'])
        self.assertEqual(v.rhs_rel(cl), 'R')
        self.assertSequenceEqual(v.uncon_vars(cl), ['e'])
        
        b = v.functionally_determines(cl, ['b'])
        self.assertFalse(b)
        
        pri = v.get_priority(cl, ['a', 'x'])
        self.assertEqual(pri, Priority.Normal)
        
        code = v.get_code(cl, ['a', 'x'], (L.Pass(),))
        exp_code = L.Parser.pc('''
            for (y, z) in R.imglookup('buu', (x,)):
                if ((x, y, z) != e):
                    pass
            ''')
        self.assertEqual(code, exp_code)
        
        self.check_rename(cl)
        
        cl2 = v.singletonize(cl, L.Name('f'))
        exp_cl2 = L.WithoutMember(L.SingMember(['x', 'y', 'z'], L.Name('f')),
                                  L.Name('e'))
        self.assertEqual(cl2, exp_cl2)
        self.assertIs(v.should_filter(cl2, []), ShouldFilter.Intersect)
    
    def test_varsmember(self):
        v = self.visitor
        
        expr = L.Parser.pe('1 + a')
        cl = L.VarsMember(['x', 'y', 'z'], expr)
        
        self.assertIs(v.kind(cl), Kind.Member)
        self.assertSequenceEqual(v.lhs_vars(cl), ['x', 'y', 'z'])
        self.assertEqual(v.rhs_rel(cl), None)
        self.assertSequenceEqual(v.uncon_vars(cl), ['a'])
        
        with self.assertRaises(NotImplementedError):
            v.functionally_determines(cl, [])
        with self.assertRaises(NotImplementedError):
            v.get_priority(cl, [])
        with self.assertRaises(NotImplementedError):
            v.get_code(cl, [], (L.Pass(),))
        
        self.check_rename(cl)
        
        with self.assertRaises(NotImplementedError):
            v.singletonize(cl, L.Name('f'))
    
    def test_setfrommapmember(self):
        v = self.visitor
        
        cl = L.SetFromMapMember(['x', 'y', 'z'], 'R', 'M', L.mask('bbu'))
        
        b = v.functionally_determines(cl, ['x', 'y'])
        self.assertTrue(b)
        b = v.functionally_determines(cl, ['x'])
        self.assertFalse(b)
        
        pri = v.get_priority(cl, ['a', 'x', 'y'])
        self.assertEqual(pri, Priority.Constant)
        pri = v.get_priority(cl, ['a', 'x'])
        self.assertEqual(pri, Priority.Normal)
        
        # All bound.
        code = v.get_code(cl, ['a', 'x', 'y', 'z'], (L.Pass(),))
        exp_code = L.Parser.pc('''
            if (x, y) in M and M[(x, y)] == z:
                pass
            ''')
        self.assertEqual(code, exp_code)
        
        # Map lookup.
        code = v.get_code(cl, ['a', 'x', 'y'], (L.Pass(),))
        exp_code = L.Parser.pc('''
            if (x, y) in M:
                z = M[(x, y)]
                pass
            ''')
        self.assertEqual(code, exp_code)
        
        # Mixed.
        code = v.get_code(cl, ['a', 'x'], (L.Pass(),))
        exp_code = L.Parser.pc('''
            for (y, z) in R.imglookup('buu', (x,)):
                pass
            ''')
        self.assertEqual(code, exp_code)
    
    def test_cond(self):
        v = self.visitor
        
        cl = L.Cond(L.Parser.pe('x == y'))
        
        self.assertIs(v.kind(cl), Kind.Cond)
        self.assertSequenceEqual(v.lhs_vars(cl), [])
        self.assertEqual(v.rhs_rel(cl), None)
        self.assertSequenceEqual(v.uncon_vars(cl), ['x', 'y'])
        
        b = v.functionally_determines(cl, ['x'])
        self.assertTrue(b)
        
        pri = v.get_priority(cl, ['a', 'x', 'y'])
        self.assertEqual(pri, Priority.Constant)
        pri = v.get_priority(cl, ['a', 'x'])
        self.assertEqual(pri, None)
        
        code = v.get_code(cl, ['a', 'x', 'y'], (L.Pass(),))
        exp_code = L.Parser.pc('''
            if (x == y):
                pass
            ''')
        self.assertEqual(code, exp_code)
        
        cl2 = v.rename_lhs_vars(cl, lambda x: '_' + x)
        exp_cl2 = L.Cond(L.Parser.pe('_x == _y'))
        self.assertEqual(cl2, exp_cl2)
        
        with self.assertRaises(NotImplementedError):
            v.singletonize(cl, L.Name('e'))


if __name__ == '__main__':
    unittest.main()
