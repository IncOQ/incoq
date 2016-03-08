"""Unit tests for misc_rewritings.py."""


import unittest

from incoq.mars.incast import L
from incoq.mars.type import T
from incoq.mars.symbol import S
from incoq.mars.transform.misc_rewritings import *
from incoq.mars.transform.misc_rewritings import (
    rewrite_with_unwraps, rewrite_with_wraps)


class MiscRewritingsCase(unittest.TestCase):
    
    def test_rewrite_with_unwraps(self):
        comp1 = L.Parser.pe('''
            {2 * x for x in R}
            ''')
        comp2 = L.Parser.pe('''
            {(2 * x,) for x in R}
            ''')
        comp3 = L.Parser.pe('''
            {2 * y for (y,) in VARS(QUERY('Q1', {2 * x for x in R}))
                   for (y,) in VARS(QUERY('Q2', {(2 * x,) for x in R}))}
            ''')
        symtab = S.SymbolTable()
        symtab.define_query('Q1', node=comp1, type=T.Set(T.Number))
        symtab.define_query('Q2', node=comp2)
        symtab.define_query('Q3', node=comp3)
        tree = L.Parser.p('''
            def main():
                print(QUERY('Q3', _COMP))
            ''', subst={'_COMP': comp3})
        
        tree = rewrite_with_unwraps(tree, symtab)
        exp_tree = L.Parser.p('''
            def main():
                print(unwrap(QUERY('Q3',
                {((2 * y),) for (y,) in VARS(unwrap(QUERY('Q1',
                                {((2 * x),) for x in R})))
                            for (y,) in VARS(QUERY('Q2',
                                {((2 * x),) for x in R}))})))
            ''')
        self.assertEqual(tree, exp_tree)
        t = symtab.get_queries()['Q1'].type
        exp_t = T.Set(T.Tuple([T.Number]))
        self.assertEqual(t, exp_t)
    
    def test_rewrite_with_wraps(self):
        comp = L.Parser.pe('''
            {2 * x for x in R for y in unwrap(R) for (z,) in R}
            ''')
        symtab = S.SymbolTable()
        symtab.define_query('Q', node=comp)
        tree = L.Parser.p('''
            def main():
                print(QUERY('Q', _COMP))
            ''', subst={'_COMP': comp})
        
        tree = rewrite_with_wraps(tree, symtab)
        exp_tree = L.Parser.p('''
            def main():
                print(QUERY('Q', {(2 * x) for (x,) in VARS(wrap(R))
                                          for (y,) in VARS(R)
                                          for (z,) in R}))
            ''')
        self.assertEqual(tree, exp_tree)
    
    def test_rewrite_vars_clauses(self):
        comp1 = L.Parser.pe('{(a, b) for (a, b) in REL(R)}')
        comp2 = L.Parser.pe('''
            {(x,) for (x, y) in QUERY('Q1', {(a, b) for (a, b) in REL(R)})}
            ''')
        symtab = S.SymbolTable()
        symtab.define_query('Q1', node=comp1, impl=S.Inc)
        symtab.define_query('Q2', node=comp2, impl=S.Inc)
        tree = L.Parser.p('''
            def main():
                print(QUERY('Q2', {(x,) for (x, y) in QUERY('Q1',
                    {(a, b) for (a, b) in REL(R)})}))
            ''')
        tree = rewrite_vars_clauses(tree, symtab)
        exp_tree = L.Parser.p('''
            def main():
                print(QUERY('Q2', {(x,) for (x, y) in VARS(QUERY('Q1',
                    {(a, b) for (a, b) in REL(R)}))}))
            ''')
        self.assertEqual(tree, exp_tree)


if __name__ == '__main__':
    unittest.main()
