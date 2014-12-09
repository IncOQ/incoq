"""Unit tests for compspec.py."""


import unittest

from simplestruct import Field

import oinc.incast as L

from .clause import EnumClause, ClauseFactory as CF, ABCStruct
from .join import Join

from .compspec import *
from .compspec import TupleTreeConstraintMaker


class CompSpecCase(unittest.TestCase):
    
    def make_spec(self, source, params, CF=CF):
        comp = L.pe('COMP({{{}}}, [], {{}})'.format(source))
        comp = comp._replace(params=tuple(params))
        return CompSpec.from_comp(comp, CF)
    
    def test_basic(self):
        cl1 = EnumClause.from_expr(L.pe('(x, y) in R'))
        cl2 = EnumClause.from_expr(L.pe('(y, z) in S'))
        spec = CompSpec(Join([cl1, cl2], CF, None), L.pe('(x, z)'), ['x'])
        
        # AST round-trip.
        comp = spec.to_comp({})
        exp_comp = L.pe('COMP({(x, z) for (x, y) in R for (y, z) in S}, '
                             '[x], {})')
        self.assertEqual(comp, exp_comp)
        spec2 = CompSpec.from_comp(exp_comp, CF)
        self.assertEqual(spec, spec2)
    
    def test_duprc(self):
        spec = self.make_spec(
                    '(x, y, z) for (x, y) in R for (y, z) in R', [])
        self.assertTrue(spec.is_duplicate_safe)
        
        spec = self.make_spec(
                    '(x, z) for (x, y) in R for (y, z) in R', [])
        self.assertFalse(spec.is_duplicate_safe)
        
        spec = self.make_spec(
                    '(x, y) for (x, y) in R for (y, _) in R', [])
        self.assertTrue(spec.is_duplicate_safe)
    
    def test_pattern(self):
        spec = self.make_spec(
            '(a, b, c) for (a, b) in R for (b, c, d, e) in S '
                      'if a == b', ['d'])
        spec = spec.to_pattern()
        exp_spec = self.make_spec(
            '(a, a, c) for (a, a) in R for (a, c, d, _) in S', ['d'])
        self.assertEqual(spec, exp_spec)
        
        spec = spec.to_nonpattern()
        exp_spec = self.make_spec(
            '(a, a, c) for (a, a_2) in R if a == a_2 '
                      'for (a_3, c, d_2, _v1) in S if a_2 == a_3 '
                      'if d == d_2', ['d'])
        self.assertEqual(spec, exp_spec)
    
    def test_without_params(self):
        orig_spec = self.make_spec(
            '(c, d) for (a, b, c, d) in R', ['a', 'b', 'z'])
        spec = orig_spec.without_params()
        exp_spec = self.make_spec(
            '(a, b, z, (c, d)) for (a, b, c, d) in R', [])
        self.assertEqual(spec, exp_spec)
        
        spec = orig_spec.without_params(flat=True)
        exp_spec = self.make_spec(
            '(a, b, z, c, d) for (a, b, c, d) in R', [])
        self.assertEqual(spec, exp_spec)
    
    def test_uset(self):
        spec = self.make_spec(
            '(a, b, c) for (a, b, c) in R', ['a', 'b'])
        spec = spec.with_uset('U', ['a'])
        exp_spec = self.make_spec(
            '(a, b, c) for a in U for (a, b, c) in R', ['a', 'b'])
        self.assertEqual(spec, exp_spec)
    
    def test_iterate_code(self):
        # Test single.
        code = for_rel_code(['a', 'b'], L.pe('R'), L.pc('pass'))
        exp_code = L.pc('''
            for a, b in R:
                pass
            ''')
        self.assertEqual(code, exp_code)
        code = for_rels_union_code(['a', 'b'], [L.pe('R')], L.pc('pass'), '_')
        self.assertEqual(code, exp_code)
        
        # Test union.
        code = for_rels_union_code(['a', 'b'], [L.pe('R'), L.pe('S')],
                                   L.pc('pass'), 'D')
        exp_code = L.pc('''
            D = set()
            for a, b in R:
                D.nsadd((a, b))
            for a, b in S:
                D.nsadd((a, b))
            for a, b in D:
                pass
            del D
            ''')
        self.assertEqual(code, exp_code)
        
        # Test verify disjoint union.
        code = for_rels_union_code(['a', 'b'], [L.pe('R'), L.pe('S')],
                                   L.pc('pass'), 'D', verify_disjoint=True)
        exp_code = L.pc('''
            D = set()
            for a, b in R:
                assert (a, b) not in D
                D.add((a, b))
            for a, b in S:
                assert (a, b) not in D
                D.add((a, b))
            for a, b in D:
                pass
            del D
            ''')
        self.assertEqual(code, exp_code)
        
        # Test disjoint union.
        code = for_rels_union_disjoint_code(
                    ['a', 'b'], [L.pe('R'), L.pe('S')], L.pc('pass'))
        exp_code = L.pc('''
            for a, b in R:
                pass
            for a, b in S:
                pass
            ''')
        self.assertEqual(code, exp_code)
    
    def test_comp_maint_code(self):
        # Basic.
        
        spec = self.make_spec('(x, z) for (x, y) in R for (y, z) in R', [])
        code, comps = make_comp_maint_code(
                        spec, 'Q', 'R', 'add', L.pe('e'), '_',
                        maint_impl='auxonly', rc='safe',
                        selfjoin='sub')
        
        comp1 = L.pe('''
            COMP({(_x, _y, _z) for (_x, _y) in deltamatch(R, 'bb', e, 1)
                               for (_y, _z) in (R - {e})},
                 [], {'impl': 'auxonly',
                      '_deltarel': 'R',
                      '_deltaelem': 'e',
                      '_deltalhs': '(_x, _y)',
                      '_deltaop': 'add'})
            ''')
        comp2 = L.pe('''
            COMP({(_x, _y, _z) for (_x, _y) in R
                               for (_y, _z) in deltamatch(R, 'bb', e, 1)},
                 [], {'impl': 'auxonly',
                      '_deltarel': 'R',
                      '_deltaelem': 'e',
                      '_deltalhs': '(_y, _z)',
                      '_deltaop': 'add'})
            ''')
        exp_code = L.pc('''
            for (_x, _y, _z) in COMP1:
                Q.rcadd((_x, _z))
            for (_x, _y, _z) in COMP2:
                Q.rcadd((_x, _z))
            ''', subst={'COMP1': comp1, 'COMP2': comp2})
        exp_comps = [comp1, comp2]
        
        self.assertEqual(code, exp_code)
        self.assertSequenceEqual(comps, exp_comps)
        
        # Force no refcounts, naive self-joins.
        
        spec = self.make_spec('(x, z) for (x, y) in R for (y, z) in R', [])
        code, comps = make_comp_maint_code(
                        spec, 'Q', 'R', 'add', L.pe('e'), '_',
                        maint_impl='auxonly', rc='no',
                        selfjoin='assume_disjoint')
        
        comp1 = L.pe('''
            COMP({(_x, _y, _z) for (_x, _y) in deltamatch(R, 'bb', e, 1)
                               for (_y, _z) in R},
                 [], {'impl': 'auxonly',
                      '_deltarel': 'R',
                      '_deltaelem': 'e',
                      '_deltalhs': '(_x, _y)',
                      '_deltaop': 'add'})
            ''')
        comp2 = L.pe('''
            COMP({(_x, _y, _z) for (_x, _y) in R
                               for (_y, _z) in deltamatch(R, 'bb', e, 1)},
                 [], {'impl': 'auxonly',
                      '_deltarel': 'R',
                      '_deltaelem': 'e',
                      '_deltalhs': '(_y, _z)',
                      '_deltaop': 'add'})
            ''')
        exp_code = L.pc('''
            for (_x, _y, _z) in COMP1:
                Q.add((_x, _z))
            for (_x, _y, _z) in COMP2:
                Q.add((_x, _z))
            ''', subst={'COMP1': comp1, 'COMP2': comp2})
        exp_comps = [comp1, comp2]
        
        self.assertEqual(code, exp_code)
        self.assertSequenceEqual(comps, exp_comps)
    
    def test_ucon_params(self):
        class DummyClause(EnumClause, ABCStruct):
            lhs = Field()
            rel = Field()
            con_mask = (False, True)
        
        # Basic.
        join = Join([
            DummyClause(['x', 'y'], 'R'),
            DummyClause(['y', 'z'], 'R'),
        ], CF, None)
        spec = CompSpec(join, L.pe('(x, z)'), ['x', 'y', 'z'])
        uncons = spec.get_uncon_params()
        exp_uncons = ['x']
        self.assertSequenceEqual(uncons, exp_uncons)
        
        # Cycle.
        join = Join([
            DummyClause(['x', 'x'], 'R'),
        ], CF, None)
        spec = CompSpec(join, L.pe('x'), ['x'])
        uncons = spec.get_uncon_params()
        exp_uncons = ['x']
        self.assertSequenceEqual(uncons, exp_uncons)
        
        # Cycle with two distinct minimal sets of uncons.
        join = Join([
            DummyClause(['x', 'y'], 'R'),
            DummyClause(['y', 'x'], 'R'),
        ], CF, None)
        spec = CompSpec(join, L.pe('(x, y)'), ['x', 'y'])
        uncons = spec.get_uncon_params()
        exp_uncons = ['x']
        self.assertSequenceEqual(uncons, exp_uncons)
    
    def test_tupletreeconstrs(self):
        expr = L.pe('(a, (b, c), (d + 1, f + 1))')
        constrs = TupleTreeConstraintMaker.run(expr, 'R', '_')
        exp_constrs = {('R', ('<T>', 'R.1', 'R.2', 'R.3')),
                       ('R.1', '_a'),
                       ('R.2', ('<T>', 'R.2.1', 'R.2.2')),
                       ('R.2.1', '_b'),
                       ('R.2.2', '_c'),
                       ('R.3', ('<T>', 'R.3.1', 'R.3.2'))}
        self.assertCountEqual(constrs, exp_constrs)
    
    def test_domains(self):
        spec = self.make_spec('(a, c) for (a, b, b) in R for (b, c) in S '
                                     'for d in T for _ in U for (_, _) in U '
                                     'if a != c', [])
        constrs = spec.get_domain_constraints('Q')
        exp_constrs = [
            ('R', ('<T>', 'R.1', 'R.2', 'R.3')),
            ('R.1', 'Q_a'),
            ('R.2', 'Q_b'),
            ('R.3', 'Q_b'),
            ('S', ('<T>', 'S.1', 'S.2')),
            ('S.1', 'Q_b'),
            ('S.2', 'Q_c'),
            ('T', 'Q_d'),
            ('U', ('<T>', 'U.1', 'U.2')),
            ('Q', ('<T>', 'Q.1', 'Q.2')),
            ('Q.1', 'Q_a'),
            ('Q.2', 'Q_c'),
        ]
        self.assertCountEqual(constrs, exp_constrs)
    
    def test_memberships(self):
        from oinc.tup import TupClauseFactory_Mixin
        spec = self.make_spec('(a, c) for (a, b, tup) in R '
                                     'for (tup, c, d) in _TUP2 '
                                     'for d in T for _ in U for (_, _) in U '
                                     'if a != c', [],
                              CF=TupClauseFactory_Mixin)
        mapping = spec.get_membership_constraints()
        exp_mapping = {
            'a': {'R.1'},
            'b': {'R.2'},
            'c': {'R.3.1'},
            'd': {'R.3.2', 'T'},
            'tup': {'R.3'},
        }
        self.assertCountEqual(mapping, exp_mapping)


if __name__ == '__main__':
    unittest.main()
