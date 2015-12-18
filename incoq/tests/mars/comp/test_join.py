"""Unit tests for test_join.py."""


import unittest

from incoq.mars.incast import L
from incoq.mars.comp.clause import *
from incoq.mars.comp.join import *


class JoinCase(unittest.TestCase):
    
    def setUp(self):
        self.ct = CoreClauseTools()
    
    def test_lhs_vars(self):
        comp = L.Parser.pe('''{(x, y, z) for (x, y) in REL(R)
                                         for (y, z) in REL(S)}''')
        lhs_vars = self.ct.lhs_vars_from_clauses(comp.clauses)
        self.assertSequenceEqual(lhs_vars, ['x', 'y', 'z'])
        
        lhs_vars = self.ct.lhs_vars_from_comp(comp)
        self.assertSequenceEqual(lhs_vars, ['x', 'y', 'z'])
    
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
        code = self.ct.get_loop_for_join(comp, (L.Pass(),))
        exp_code = L.Parser.pc('''
            for (x, y, z) in {(x, y, z) for (x, y) in REL(R)
                                        for (y, z) in REL(S)}:
                pass
            ''')
        self.assertEqual(code, exp_code)
    
    def test_get_maint_join(self):
        comp = L.Parser.pe('''
            {(w, x, y ,z) for (w, x) in REL(R) for (x, y) in REL(S)
                          for (y, z) in REL(R)}''')
        join = self.ct.get_maint_join(comp, 0, L.Name('e'),
                                      selfjoin=SelfJoin.Without)
        exp_join = L.Parser.pe('''
            {(w, x, y ,z) for (w, x) in SING(e) for (x, y) in REL(S)
                          for (y, z) in WITHOUT(REL(R), e)}''')
        self.assertEqual(join, exp_join)
    
    def test_get_maint_join_union(self):
        comp = L.Parser.pe('''
            {(w, x, y ,z) for (w, x) in REL(R) for (x, y) in REL(S)
                          for (y, z) in REL(R)}''')
        joins = self.ct.get_maint_join_union(comp, 'R', L.Name('e'),
                                             selfjoin=SelfJoin.Without)
        exp_joins = [
            L.Parser.pe('''
                {(w, x, y ,z) for (w, x) in SING(e) for (x, y) in REL(S)
                              for (y, z) in WITHOUT(REL(R), e)}'''),
            L.Parser.pe('''
                {(w, x, y, z) for (w, x) in REL(R) for (x, y) in REL(S)
                              for (y, z) in SING(e)}'''),
        ]
        self.assertSequenceEqual(joins, exp_joins)
    
    def test_join_expander(self):
        Q1 = L.Parser.pe('''{(x, y, z) for (x, y) in REL(R)
                                       for (y, z) in REL(S)}''')
        Q2 = L.Parser.pe('{(x,) for (x,) in REL(R)}')
        Q3 = L.Parser.pe('{True for (x,) in REL(R)}')
        query_params = {'Q1': ('x',), 'Q2': (), 'Q3': ()}
        
        tree = L.Parser.p('''
            def main():
                for (x, y, z) in QUERY('Q1', _Q1):
                    pass
                for z in QUERY('Q2', _Q2):
                    pass
                for z in QUERY('Q3', _Q3):
                    pass
            ''', subst={'_Q1': Q1, '_Q2': Q2, '_Q3': Q3})
        
        tree = JoinExpander.run(tree, self.ct, ['Q1', 'Q2', 'Q3'],
                                query_params)
        exp_tree = L.Parser.p('''
            def main():
                for (y,) in R.imglookup('bu', (x,)):
                    for (z,) in S.imglookup('bu', (y,)):
                        pass
                for z in QUERY('Q2', {(x,) for (x,) in REL(R)}):
                    pass
                for z in QUERY('Q3', {True for (x,) in REL(R)}):
                    pass
            ''')
        self.assertEqual(tree, exp_tree)


if __name__ == '__main__':
    unittest.main()
