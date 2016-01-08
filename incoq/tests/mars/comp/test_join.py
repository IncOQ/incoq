"""Unit tests for join.py."""


import unittest

from incoq.mars.incast import L
from incoq.mars.symtab import N
from incoq.mars.comp.join import *


class JoinCase(unittest.TestCase):
    
    def setUp(self):
        self.ct = CoreClauseTools()
    
    def test_match_member_cond(self):
        cond = L.Cond(L.Parser.pe('(x, y) in R'))
        result = match_member_cond(cond)
        exp_result = (('x', 'y'), 'R')
        self.assertEqual(result, exp_result)
        
        cond = L.Cond(L.Parser.pe('x in R'))
        result = match_member_cond(cond)
        self.assertIsNone(result)
        
        cond = L.Cond(L.Parser.pe('(x, y) in 1 + 1'))
        result = match_member_cond(cond)
        self.assertIsNone(result)
    
    def test_match_eq_cond(self):
        cond = L.Cond(L.Parser.pe('x == y'))
        result = match_eq_cond(cond)
        exp_result = ('x', 'y')
        self.assertEqual(result, exp_result)
        
        cond = L.Cond(L.Parser.pe('x == y + 1'))
        result = match_eq_cond(cond)
        self.assertIsNone(result)
    
    def test_make_eq_cond(self):
        cond = make_eq_cond('x', 'y')
        exp_cond = L.Cond(L.Parser.pe('x == y'))
        self.assertEqual(cond, exp_cond)
    
    def test_lhs_vars(self):
        comp = L.Parser.pe('''{(x, y, z) for (x, y) in REL(R)
                                         for (y, z) in REL(S)}''')
        lhs_vars = self.ct.lhs_vars_from_clauses(comp.clauses)
        self.assertSequenceEqual(lhs_vars, ['x', 'y', 'z'])
        
        lhs_vars = self.ct.lhs_vars_from_comp(comp)
        self.assertSequenceEqual(lhs_vars, ['x', 'y', 'z'])
        
        constr_lhs_vars = self.ct.constr_lhs_vars_from_comp(comp)
        self.assertSequenceEqual(constr_lhs_vars, ['x', 'y', 'z'])
    
    def test_rhs_rels_from_comp(self):
        comp = L.Parser.pe('''{(x, y, z) for (x, y) in REL(R)
                                         for (y, z) in REL(S)
                                         for (z, z) in SING(e)}''')
        rels = self.ct.rhs_rels_from_comp(comp)
        self.assertSequenceEqual(rels, ['R', 'S'])
    
    def test_make_join(self):
        comp = L.Parser.pe('''{(x, y, z) for (x, y) in REL(R)
                                         for (y, z) in REL(S)}''')
        comp2 = self.ct.make_join_from_clauses(comp.clauses)
        self.assertEqual(comp2, comp)
        
        comp3 = L.Parser.pe('''{None for (x, y) in REL(R)
                                     for (y, z) in REL(S)}''')
        comp4 = self.ct.make_join_from_comp(comp3)
        self.assertEqual(comp4, comp)
    
    def test_is_join(self):
        comp = L.Parser.pe('''{(x, y, z) for (x, y) in REL(R)
                                         for (y, z) in REL(S)}''')
        self.assertTrue(self.ct.is_join(comp))
        
        # Wrong order.
        comp = L.Parser.pe('''{(x, z, y) for (x, y) in REL(R)
                                         for (y, z) in REL(S)}''')
        self.assertFalse(self.ct.is_join(comp))
        
        # Not a tuple.
        comp = L.Parser.pe('''{x for (x, y) in REL(R)
                                 for (y, z) in REL(S)}''')
        self.assertFalse(self.ct.is_join(comp))
    
    def test_comp_rename_lhs_vars(self):
        comp = L.Parser.pe('''{(a, x, y, z) for (x, y) in REL(R)
                                            for (y, z) in REL(S)
                                            if a}''')
        comp = self.ct.comp_rename_lhs_vars(comp, lambda x: '_' + x)
        exp_comp = L.Parser.pe('''{(a, _x, _y, _z) for (_x, _y) in REL(R)
                                                   for (_y, _z) in REL(S)
                                                   if a}''')
        self.assertEqual(comp, exp_comp) 
    
    def test_rewrite_with_patterns(self):
        orig_comp = L.Parser.pe('''{a for (a, b) in REL(R)
                                      for (b, c) in REL(R) if a == b}''')
        
        # No keepvars.
        comp = self.ct.rewrite_with_patterns(orig_comp, set())
        exp_comp = L.Parser.pe('''{a for (a, a) in REL(R)
                                     for (a, c) in REL(R)}''')
        self.assertEqual(comp, exp_comp)
        
        # Right side in keepvars.
        comp = self.ct.rewrite_with_patterns(orig_comp, {'b'})
        exp_comp = L.Parser.pe('''{b for (b, b) in REL(R)
                                     for (b, c) in REL(R)}''')
        self.assertEqual(comp, exp_comp)
        
        # Both sides in keepvars.
        comp = self.ct.rewrite_with_patterns(orig_comp, {'a', 'b'})
        self.assertEqual(comp, orig_comp)
    
    def test_elim_sameclause_eqs(self):
        comp = L.Parser.pe('{x for (x, x) in REL(R) for (x, y, x) in REL(R)}')
        comp = self.ct.elim_sameclause_eqs(comp)
        exp_comp = L.Parser.pe('''{x for (x, x_2) in REL(R) if x == x_2
                                     for (x, y, x_3) in REL(R) if x == x_3}''')
        self.assertEqual(comp, exp_comp)
    
    def test_rewrite_resexp_with_params(self):
        comp = L.Parser.pe('''{(2 * y,) for (x, y) in REL(R)}''')
        comp = self.ct.rewrite_resexp_with_params(comp, ('x',))
        exp_comp = L.Parser.pe('''{(x, 2 * y) for (x, y) in REL(R)}''')
        self.assertEqual(comp, exp_comp)
        
        comp = L.Parser.pe('''{y for (x, y) in REL(R)}''')
        with self.assertRaises(AssertionError):
            self.ct.rewrite_resexp_with_params(comp, ('x',))
    
    def test_rewrite_with_uset(self):
        comp = L.Parser.pe('{x for (x, y) in REL(S)}')
        comp = self.ct.rewrite_with_uset(comp, ['x'], 'U')
        exp_comp = L.Parser.pe('{x for (x,) in REL(U) for (x, y) in REL(S)}')
        self.assertEqual(comp, exp_comp)
    
    def test_get_code_for_clauses(self):
        comp = L.Parser.pe('''{z for (x, y) in REL(R)
                                 for (y, z) in REL(S)}''')
        code = self.ct.get_code_for_clauses(comp.clauses, ['x'], (L.Pass(),))
        exp_code = L.Parser.pc('''
            for (y,) in R.imglookup('bu', (x,)):
                for (z,) in S.imglookup('bu', (y,)):
                    pass
            ''')
        self.assertEqual(code, exp_code)
    
    def test_get_loop_for_join(self):
        comp = L.Parser.pe('''{(x, y, z) for (x, y) in REL(R)
                                         for (y, z) in REL(S)}''')
        code = self.ct.get_loop_for_join(comp, (L.Pass(),), 'J')
        exp_code = L.Parser.pc('''
            for (x, y, z) in QUERY('J', {(x, y, z) for (x, y) in REL(R)
                                                   for (y, z) in REL(S)}):
                pass
            ''')
        self.assertEqual(code, exp_code)
    
    def test_get_maint_join(self):
        comp = L.Parser.pe('''
            {(w, x, y, z) for (w, x) in REL(R) for (x, y) in REL(S)
                          for (y, z) in REL(R)}''')
        join = self.ct.get_maint_join(comp, 0, L.Name('e'),
                                      selfjoin=SelfJoin.Without)
        exp_join = L.Parser.pe('''
            {(w, x, y, z) for (w, x) in SING(e) for (x, y) in REL(S)
                          for (y, z) in WITHOUT(REL(R), e)}''')
        self.assertEqual(join, exp_join)
    
    def test_get_maint_join_union(self):
        comp = L.Parser.pe('''
            {(w, x, y, z) for (w, x) in REL(R) for (x, y) in REL(S)
                          for (y, z) in REL(R)}''')
        joins = self.ct.get_maint_join_union(comp, 'R', L.Name('e'),
                                             selfjoin=SelfJoin.Without)
        exp_joins = [
            L.Parser.pe('''
                {(w, x, y, z) for (w, x) in SING(e) for (x, y) in REL(S)
                              for (y, z) in WITHOUT(REL(R), e)}'''),
            L.Parser.pe('''
                {(w, x, y, z) for (w, x) in REL(R) for (x, y) in REL(S)
                              for (y, z) in SING(e)}'''),
        ]
        self.assertSequenceEqual(joins, exp_joins)
    
    def test_get_maint_code(self):
        comp = L.Parser.pe('''
            {w + z for (w, x) in REL(R) for (x, y) in REL(S)
                   for (y, z) in REL(R)}''')
        code = self.ct.get_maint_code(N.fresh_name_generator(),
                                      N.fresh_name_generator('J{}'),
                                      comp, 'Q',
                                      L.RelUpdate('R', L.SetAdd(), 'e'),
                                      counted=True)
        exp_code = L.Parser.pc('''
            for (_v1_w, _v1_x, _v1_y, _v1_z) in \
                    QUERY('J1', {(_v1_w, _v1_x, _v1_y, _v1_z)
                                 for (_v1_w, _v1_x) in SING(e)
                                 for (_v1_x, _v1_y) in REL(S)
                                 for (_v1_y, _v1_z) in WITHOUT(REL(R), e)}):
                _v1_result = (_v1_w + _v1_z)
                if (_v1_result not in Q):
                    Q.reladd(_v1_result)
                else:
                    Q.relinccount(_v1_result)
            for (_v1_w, _v1_x, _v1_y, _v1_z) in \
                    QUERY('J2', {(_v1_w, _v1_x, _v1_y, _v1_z)
                                 for (_v1_w, _v1_x) in REL(R)
                                 for (_v1_x, _v1_y) in REL(S)
                                 for (_v1_y, _v1_z) in SING(e)}):
                _v1_result = (_v1_w + _v1_z)
                if (_v1_result not in Q):
                    Q.reladd(_v1_result)
                else:
                    Q.relinccount(_v1_result)
            ''')
        self.assertEqual(code, exp_code)


if __name__ == '__main__':
    unittest.main()
