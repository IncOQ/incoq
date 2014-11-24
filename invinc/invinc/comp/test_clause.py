"""Unit tests for clause.py."""


import unittest

import invinc.incast as L
from invinc.comp import Rate

from .clause import *


class DummyFactory(ClauseFactory):
    @classmethod
    def from_AST(cls, node):
        return EnumClause.from_AST(node, cls)


class ClauseCase(unittest.TestCase):
    
    def test_subst(self):
        res = apply_subst_tuple(('a', 'b', 'c'),
                                {'a': 'z', 'b': lambda s: s * 2})
        exp_res = ('z', 'bb', 'c')
        self.assertEqual(res, exp_res)
    
    def test_inst_wildcards(self):
        vars = ('a', '_', 'b', '_')
        vars = inst_wildcards(vars)
        exp_vars = ('a', '_v1', 'b', '_v2')
        self.assertEqual(vars, exp_vars)
    
    def test_enumclause_basic(self):
        cl = EnumClause(('x', 'y', 'x', '_'), 'R')
        
        # From expression.
        cl2 = EnumClause.from_expr(L.pe('(x, y, x, _) in R'))
        self.assertEqual(cl2, cl)
        
        # AST round-trip.
        clast = cl.to_AST()
        exp_clast = \
            L.Enumerator(L.tuplify(['x', 'y', 'x', '_'], lval=True),
                         L.ln('R'))
        self.assertEqual(clast, exp_clast)
        cl2 = EnumClause.from_AST(exp_clast, DummyFactory)
        self.assertEqual(cl2, cl)
        
        # Attributes.
        
        self.assertFalse(cl.isdelta)
        
        self.assertEqual(cl.enumlhs, ('x', 'y', 'x', '_'))
        self.assertEqual(cl.enumvars, ('x', 'y'))
        self.assertEqual(cl.pat_mask, (True, True, True, True))
        self.assertEqual(cl.enumrel, 'R')
        self.assertTrue(cl.has_wildcards)
        
        self.assertEqual(cl.vars, ('x', 'y'))
        self.assertEqual(cl.eqvars, None)
        
        self.assertTrue(cl.robust)
        self.assertEqual(cl.demname, None)
        self.assertEqual(cl.demparams, ())
    
    def test_enumclause_manipulate(self):
        cl = EnumClause(('x', 'y', 'x', '_'), 'R')
        
        # rewrite_rel().
        cl3 = cl.rewrite_rel('S', ClauseFactory)
        exp_cl3 = EnumClause(('x', 'y', 'x', '_'), 'S')
        self.assertEqual(cl3, exp_cl3)
    
    def test_enumclause_code(self):
        cl = EnumClause(('x', 'y'), 'R')
        
        # fits_string().
        self.assertTrue(cl.fits_string(['x'], 'R_out'))
        
        # Rating.
        self.assertEqual(cl.rate(['x']), Rate.NORMAL)
        self.assertEqual(cl.rate(['x', 'y']), Rate.CONSTANT_MEMBERSHIP)
        self.assertEqual(cl.rate([]), Rate.NOTPREFERRED)
        
        # Code generation.
        code = cl.get_code(['x'], L.pc('pass'))
        exp_code = L.pc('''
            for y in setmatch(R, 'bu', x):
                pass
            ''')
        self.assertEqual(code, exp_code)
    
    def test_enumclause_setmatch(self):
        # Make sure we can convert clauses over setmatches.
        cl = EnumClause.from_AST(
                L.Enumerator(L.tuplify(['y'], lval=True),
                             L.SetMatch(L.ln('R'), 'bu', L.ln('x'))),
                DummyFactory)
        exp_cl = EnumClause(('x', 'y'), 'R')
        self.assertEqual(cl, exp_cl)
    
    def test_subclause(self):
        cl = SubClause(EnumClause(('x', 'y'), 'R'), L.pe('e'))
        
        # AST round-trip.
        clast = cl.to_AST()
        exp_clast = L.Enumerator(L.tuplify(['x', 'y'], lval=True),
                                 L.pe('R - {e}'))
        self.assertEqual(clast, exp_clast)
        cl2 = SubClause.from_AST(exp_clast, DummyFactory)
        self.assertEqual(cl2, cl)
        
        # Attributes.
        self.assertEqual(cl.enumlhs, ('x', 'y'))
        self.assertFalse(cl.robust)
        
        # Code generation.
        code = cl.get_code([], L.pc('pass'))
        exp_code = L.pc('''
            for (x, y) in R:
                if (x, y) != e:
                    pass
            ''')
        self.assertEqual(code, exp_code)
    
    def test_augclause(self):
        cl = AugClause(EnumClause(('x', 'y'), 'R'), L.pe('e'))
        
        # AST round-trip.
        clast = cl.to_AST()
        exp_clast = L.Enumerator(L.tuplify(['x', 'y'], lval=True),
                                 L.pe('R + {e}'))
        self.assertEqual(clast, exp_clast)
        cl2 = AugClause.from_AST(exp_clast, DummyFactory)
        self.assertEqual(cl2, cl)
        
        # Attributes.
        self.assertEqual(cl.enumlhs, ('x', 'y'))
        self.assertFalse(cl.robust)
        
        # Code generation.
        code = cl.get_code([], L.pc('pass'))
        exp_code = L.pc('''
            for (x, y) in R:
                pass
            (x, y) = e
            pass
            ''')
        self.assertEqual(code, exp_code)
    
    def test_lookupclause(self):
        cl = LookupClause(('x', 'y', 'z'), 'R')
        
        # AST round-trip.
        clast = cl.to_AST()
        sm = L.SMLookup(L.ln('R'), 'bbu', L.tuplify(['x', 'y']), None)
        exp_clast = L.Enumerator(L.sn('z'), L.Set((sm,)))
        self.assertEqual(clast, exp_clast)
        cl2 = LookupClause.from_AST(exp_clast, DummyFactory)
        self.assertEqual(cl2, cl)
        
        # Attributes.
        self.assertEqual(cl.enumvars, ('x', 'y', 'z'))
        
        # Rewriting.
        cl2 = cl.rewrite_subst({'x': 'xx', 'z': 'zz'}, DummyFactory)
        self.assertEqual(cl2, LookupClause(('xx', 'y', 'zz'), 'R'))
        
        # Rating.
        self.assertEqual(cl.rate(['x']), Rate.NORMAL)
        self.assertEqual(cl.rate(['x', 'y']), Rate.CONSTANT)
    
    def test_singletonclause(self):
        cl = SingletonClause(('x', 'y'), L.pe('e'))
        
        # From expression.
        cl2 = SingletonClause.from_expr(L.pe('(x, y) == e'))
        self.assertEqual(cl, cl2)
        
        # AST round-trip.
        clast = cl.to_AST()
        exp_clast = L.Enumerator(L.tuplify(['x', 'y'], lval=True),
                                 L.pe('{e}'))
        self.assertEqual(clast, exp_clast)
        cl2 = SingletonClause.from_AST(exp_clast, DummyFactory)
        self.assertEqual(cl2, cl)
        
        # Attributes.
        self.assertEqual(cl.enumvars, ('x', 'y'))
        
        # Code generation.
        code = cl.get_code([], L.pc('pass'))
        exp_code = L.pc('''
            x, y = e
            pass
            ''')
        self.assertEqual(code, exp_code)
    
    def test_deltaclause(self):
        cl = DeltaClause(('x', 'y'), 'R', L.pe('e'), 1)
        
        # AST round-trip.
        clast = cl.to_AST()
        exp_clast = L.Enumerator(L.tuplify(['x', 'y'], lval=True),
                                 L.pe('deltamatch(R, "bb", e, 1)'))
        self.assertEqual(clast, exp_clast)
        cl2 = DeltaClause.from_AST(exp_clast, DummyFactory)
        self.assertEqual(cl2, cl)
        
        # Attributes.
        self.assertEqual(cl.rel, 'R')
        
        # Code generation, no fancy mask.
        code = cl.get_code([], L.pc('pass'))
        exp_code = L.pc('''
            x, y = e
            pass
            ''')
        self.assertEqual(code, exp_code)
        
        # Code generation, fancy mask.
        cl2 = DeltaClause(('x', 'x', '_'), 'R', L.pe('e'), 1)
        code = cl2.get_code([], L.pc('pass'))
        exp_code = L.pc('''
            for x in setmatch(deltamatch(R, 'b1w', e, 1), 'u1w', ()):
                pass
            ''')
        self.assertEqual(code, exp_code)
    
    def test_condclause(self):
        cl = CondClause(L.pe('f(a) or g(b)'))
        
        # AST round-trip.
        clast = cl.to_AST()
        exp_clast = L.pe('f(a) or g(b)')
        self.assertEqual(clast, exp_clast)
        cl2 = CondClause.from_AST(exp_clast, DummyFactory)
        self.assertEqual(cl2, cl)
        
        # fits_string().
        self.assertTrue(cl.fits_string(['a', 'b'], 'f(a) or g(b)'))
        
        # Attributes.
        self.assertEqual(cl.enumvars, ())
        self.assertEqual(cl.vars, ('a', 'b'))
        cl2 = CondClause(L.pe('a == b'))
        self.assertEqual(cl2.eqvars, ('a', 'b'))
        
        # Rating.
        self.assertEqual(cl.rate(['a', 'b']), Rate.CONSTANT)
        self.assertEqual(cl.rate(['a']), Rate.UNRUNNABLE)
        
        # Code generation.
        code = cl.get_code(['a', 'b'], L.pc('pass'))
        exp_code = L.pc('''
            if f(a) or g(b):
                pass
            ''')
        self.assertEqual(code, exp_code)
    
    def test_clausefactory(self):
        # Construct from AST.
        clast = L.Enumerator(L.tuplify(['x', 'y'], lval=True),
                             L.pe('R - {e}'))
        cl = ClauseFactory.from_AST(clast)
        exp_cl = SubClause(EnumClause(('x', 'y'), 'R'), L.pe('e'))
        self.assertEqual(cl, exp_cl)
        
        # rewrite_subst().
        cl = SubClause(EnumClause(('x', 'y'), 'R'), L.pe('e'))
        cl = ClauseFactory.rewrite_subst(cl, {'x': 'z'})
        exp_cl = SubClause(EnumClause(('z', 'y'), 'R'), L.pe('e'))
        self.assertEqual(cl, exp_cl)
        
        # bind().
        cl = EnumClause(('x', 'y'), 'R')
        cl = ClauseFactory.bind(cl, L.pe('e'), augmented=False)
        exp_cl = DeltaClause(['x', 'y'], 'R', L.pe('e'), 1)
        self.assertEqual(cl, exp_cl)
        
        # subtract().
        cl = EnumClause(('x', 'y'), 'R')
        cl = ClauseFactory.subtract(cl, L.pe('e'))
        exp_cl = SubClause(EnumClause(('x', 'y'), 'R'), L.pe('e'))
        self.assertEqual(cl, exp_cl)
        
        # augment().
        cl = EnumClause(['x', 'y'], 'R')
        cl = ClauseFactory.augment(cl, L.pe('e'))
        exp_cl = AugClause(EnumClause(['x', 'y'], 'R'), L.pe('e'))
        self.assertEqual(cl, exp_cl)
        
        # rewrite_rel().
        cl = SubClause(EnumClause(('x', 'y'), 'R'), L.pe('e'))
        cl = ClauseFactory.rewrite_rel(cl, 'S')
        exp_cl = SubClause(EnumClause(('x', 'y'), 'S'), L.pe('e'))
        self.assertEqual(cl, exp_cl)
        
        # membercond_to_enum().
        cl = CondClause(L.pe('(x, y) in R'))
        cl = ClauseFactory.membercond_to_enum(cl)
        exp_cl = EnumClause(('x', 'y'), 'R')
        self.assertEqual(cl, exp_cl)
        
        # enum_to_membercond().
        cl = EnumClause(('x', 'y'), 'R')
        cl = ClauseFactory.enum_to_membercond(cl)
        exp_cl = CondClause(L.pe('(x, y) in R'))
        self.assertEqual(cl, exp_cl)


if __name__ == '__main__':
    unittest.main()
