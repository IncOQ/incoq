"""Unit tests for join.py."""


import unittest

import oinc.incast as L

from .clause import EnumClause, CondClause, ClauseFactory as CF

from .join import *


class JoinCase(unittest.TestCase):
    
    def make_join(self, source, delta=None):
        join = Join.from_comp(L.pe(
                    'COMP({{... {}}}, [], {{}})'.format(source)),
                    CF)
        join = join._replace(delta=delta)
        return join
    
    def test_basic(self):
        cl1 = EnumClause(('a', 'b'), 'R')
        cl2 = EnumClause(('b', 'c'), 'S')
        cl3 = CondClause(L.pe('a != c'))
        join = Join([cl1, cl2, cl3], CF, None)
        
        # AST round-trip.
        comp = join.to_comp({})
        exp_comp = L.Comp(L.pe('(a, b, c)'),
                          (cl1.to_AST(), cl2.to_AST(), cl3.to_AST()),
                          (), {})
        self.assertEqual(comp, exp_comp)
        join2 = Join.from_comp(exp_comp, CF)
        self.assertEqual(join, join2)
        
        # Attributes.
        self.assertEqual(join.enumvars, ('a', 'b', 'c'))
        self.assertEqual(join.vars, ('a', 'b', 'c'))
        self.assertEqual(join.rels, ('R', 'S'))
        self.assertTrue(join.robust)
        self.assertEqual(join.has_wildcards, False)
        self.assertIs(join.delta, None)
        
        # Rewriting/prefixing.
        
        cl1a = EnumClause(('z', 'b'), 'R')
        cl3a = CondClause(L.pe('z != c'))
        join2 = join.rewrite_subst({'a': 'z'})
        self.assertEqual(join2, Join([cl1a, cl2, cl3a], CF, None))
        
        cl1b = EnumClause(('_a', '_b'), 'R')
        cl2b = EnumClause(('_b', '_c'), 'S')
        cl3b = CondClause(L.pe('_a != _c'))
        join3 = join.prefix_enumvars('_')
        self.assertEqual(join3, Join([cl1b, cl2b, cl3b], CF, None))
    
    def test_elimeq(self):
        # Basic.
        join = self.make_join('for (a, b) in R for (b, c) in R if a == b')
        join, subst = join.elim_equalities([])
        exp_join = self.make_join('for (a, a) in R for (a, c) in R')
        exp_subst = {'a': 'a', 'b': 'a'}
        self.assertEqual(join, exp_join)
        self.assertEqual(subst, exp_subst)
        
        # Keepvars.
        join = self.make_join('for (p1, p2, v1, v2, v3) in S '
                              'if p1 == p2 if p2 == v1 if v2 == v3')
        join, subst = join.elim_equalities(['p1', 'p2'])
        exp_join = self.make_join('for (p1, p2, p2, v2, v2) in S '
                                  'if p1 == p2')
        exp_subst = {'p2': 'p2', 'v1': 'p2', 'v2': 'v2', 'v3': 'v2'}
        self.assertEqual(join, exp_join)
        self.assertEqual(subst, exp_subst)
        
        # Convert membership condition clauses to enumerators.
        join = self.make_join('for (x, y) in S if x in T')
        join, subst = join.elim_equalities([])
        exp_join = self.make_join('for (x, y) in S for x in T')
        exp_subst = {}
        self.assertEqual(join, exp_join)
        self.assertEqual(subst, exp_subst)
    
    def test_makewild(self):
        join = self.make_join(
                    'for (a, a, b, c, d, e) in R for b in S if c')
        join = join.make_wildcards(['d'])
        exp_join = self.make_join(
                    'for (a, a, b, c, d, _) in R for b in S if c')
        self.assertEqual(join, exp_join)
    
    def test_makeeq(self):
        join = self.make_join(
            'for (a, a) in R for (a, b, c) in S '
            'for (a, b) in T if f(a) == g(b)')
        join = join.make_equalities(['b'])
        
        exp_join = self.make_join(
            'for (a, a_2) in R if a == a_2 '
            'for (a_3, b_2, c) in S if a_2 == a_3 if b == b_2 '
            'if (a, b) in T if f(a) == g(b)')
        
        self.assertEqual(join, exp_join)
    
    def test_elimwild(self):
        join = self.make_join('for _ in R for _ in S')
        join = join.elim_wildcards()
        exp_join = self.make_join('for _v1 in R for _v2 in S')
        self.assertEqual(join, exp_join)
    
    def test_maintjoins(self):
        join = self.make_join('for (a, b) in R for (b, c) in R')
        
        # Disjoint, subtractive.
        mjoins = join.get_maint_joins(L.pe('e'), 'R', 'add', '',
                                      disjoint_strat='sub')
        exp_mjoin1 = self.make_join('''
            for (a, b) in deltamatch(R, "bb", e, 1)
            for (b, c) in R - {e}''',
            DeltaInfo('R', L.pe('e'), ('a', 'b'), 'add'))
        exp_mjoin2 = self.make_join('''
            for (a, b) in R
            for (b, c) in deltamatch(R, "bb", e, 1)''',
            DeltaInfo('R', L.pe('e'), ('b', 'c'), 'add'))
        self.assertSequenceEqual(mjoins, [exp_mjoin1, exp_mjoin2])
        
        # Disjoint, augmented.
        mjoins = join.get_maint_joins(L.pe('e'), 'R', 'add', '',
                                      disjoint_strat='aug')
        exp_mjoin1 = self.make_join('''
            for (a, b) in deltamatch(R, "bb", e, 0)
            for (b, c) in R + {e}''',
            DeltaInfo('R', L.pe('e'), ('a', 'b'), 'add'))
        exp_mjoin2 = self.make_join('''
            for (a, b) in R
            for (b, c) in deltamatch(R, "bb", e, 0)''',
            DeltaInfo('R', L.pe('e'), ('b', 'c'), 'add'))
        self.assertSequenceEqual(mjoins, [exp_mjoin1, exp_mjoin2])
        
        # Not disjoint. With prefix.
        mjoins = join.get_maint_joins(L.pe('e'), 'R', 'add', '_',
                                      disjoint_strat='das')
        exp_mjoin1 = self.make_join('''
            for (_a, _b) in deltamatch(R, "bb", e, 1)
            for (_b, _c) in R''',
            DeltaInfo('R', L.pe('e'), ('_a', '_b'), 'add'))
        exp_mjoin2 = self.make_join('''
            for (_a, _b) in R
            for (_b, _c) in deltamatch(R, "bb", e, 1)''',
            DeltaInfo('R', L.pe('e'), ('_b', '_c'), 'add'))
        self.assertSequenceEqual(mjoins, [exp_mjoin1, exp_mjoin2])
    
    def test_memberconds(self):
        # Make sure nothing strange happens when converting between
        # membership conditions and enumerators, when the enumerators
        # aren't ordinary EnumClauses.
        
        # Round-trip SubClause.
        
        orig_join = self.make_join('for (x, y) in S if x in T - {e}')
        join, _subst = orig_join.elim_equalities([])
        exp_join = self.make_join('for (x, y) in S for x in T - {e}')
        self.assertEqual(join, exp_join)
        
        join = exp_join.make_equalities([])
        self.assertEqual(join, orig_join)
        
        # Round-trip SingletonClause.
        
        orig_join = self.make_join('for (x, y) in S if x in {e}')
        join, _subst = orig_join.elim_equalities([])
        exp_join = self.make_join('for (x, y) in S for x in {e}')
        self.assertEqual(join, exp_join)
        
        join = exp_join.make_equalities([])
        self.assertEqual(join, orig_join)
    
    def test_code(self):
        join = self.make_join('for (a, b) in R for (b, c) in S')
        code = join.get_code(['c'], L.pc('pass'), augmented=False)
        
        exp_code = L.pc('''
            for b in setmatch(S, 'ub', c):
                for a in setmatch(R, 'ub', b):
                    pass
            ''')
        
        self.assertEqual(code, exp_code)


if __name__ == '__main__':
    unittest.main()
