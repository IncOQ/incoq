"""Unit tests for misc_rewritings.py."""


import unittest

from incoq.mars.incast import L
from incoq.mars.type import T
from incoq.mars.symbol import S
from incoq.mars.transform.misc_rewritings import *


class MiscRewritingsCase(unittest.TestCase):
    
    def test_relationalize_comp_queries(self):
        comp1 = L.Parser.pe('{2 * y for (x, y) in REL(R)}')
        comp2 = L.Parser.pe('{(y,) for (x, y) in REL(R)}')
        symtab = S.SymbolTable()
        query_sym1 = symtab.define_query('Q1', node=comp1,
                                         type=T.Set(T.Number))
        query_sym2 = symtab.define_query('Q2', node=comp2)
        tree = L.Parser.p('''
            def main():
                print(QUERY('Q1', {2 * y for (x, y) in REL(R)}))
                print(QUERY('Q2', {(y,) for (x, y) in REL(R)}))
            ''')
        tree = relationalize_comp_queries(tree, symtab)
        exp_tree = L.Parser.p('''
            def main():
                print(unwrap(QUERY('Q1', {(2 * y,) for (x, y) in REL(R)})))
                print(QUERY('Q2', {(y,) for (x, y) in REL(R)}))
            ''')
        self.assertEqual(tree, exp_tree)
        exp_comp1 = L.Parser.pe('{(2 * y,) for (x, y) in REL(R)}')
        self.assertEqual(query_sym1.node, exp_comp1)
        self.assertEqual(query_sym1.type, T.Set(T.Tuple([T.Number])))
    
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
