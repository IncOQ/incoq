"""Unit tests for misc_rewritings.py."""


import unittest

from incoq.mars.incast import L
from incoq.mars.symbol import S
from incoq.mars.transform.misc_rewritings import *


class MiscRewritingsCase(unittest.TestCase):
    
    def test_mark_query_forms(self):
        comp = L.Parser.pe('''
            {(a,) for (a,) in VARS({(b,) for (b,) in REL(R)})}
            ''')
        symtab = S.SymbolTable()
        symtab.define_query('Q', node=comp)
        tree = L.Parser.p('''
            def main():
                print(QUERY('Q', {(a,) for (a,) in VARS(
                                       {(b,) for (b,) in REL(R)})}))
                print({(b,) for (b,) in REL(R)})
            ''')
        tree = mark_query_forms(tree, symtab)
        exp_tree = L.Parser.p('''
            def main():
                print(QUERY('Q', {(a,) for (a,) in VARS(QUERY('Query1',
                                       {(b,) for (b,) in REL(R)}))}))
                print(QUERY('Query2', {(b,) for (b,) in REL(R)}))
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
    
    def test_lift_firstthen(self):
        symtab = S.SymbolTable()
        tree = L.Parser.p('''
            def main():
                unwrap(FIRSTTHEN(a, b))
            ''')
        tree = lift_firstthen(tree, symtab)
        exp_tree = L.Parser.p('''
            def main():
                FIRSTTHEN(a, unwrap(b))
            ''')
        self.assertEqual(tree, exp_tree)


if __name__ == '__main__':
    unittest.main()
