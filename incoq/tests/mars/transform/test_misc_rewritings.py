"""Unit tests for misc_rewritings.py."""


import unittest

from incoq.mars.incast import L
from incoq.mars.symtab import SymbolTable
from incoq.mars.transform.misc_rewritings import *


class MiscRewritingsCase(unittest.TestCase):
    
    def test_relationalize_comp_queires(self):
        comp1 = L.Parser.pe('{2 * y for (x, y) in REL(R)}')
        comp2 = L.Parser.pe('{(y,) for (x, y) in REL(R)}')
        symtab = SymbolTable()
        query_sym1 = symtab.define_query('Q1', node=comp1)
        _query_sym2 = symtab.define_query('Q2', node=comp2)
        tree = L.Parser.p('''
            def main():
                print(QUERY('Q1', {2 * y for (x, y) in REL(R)}))
                print(QUERY('Q2', {(y,) for (x, y) in REL(R)}))
            ''')
        tree = relationalize_comp_queries(tree, symtab)
        exp_tree = L.Parser.p('''
            def main():
                print(QUERY('Q1', {(2 * y,) for (x, y) in REL(R)}).unwrap())
                print(QUERY('Q2', {(y,) for (x, y) in REL(R)}))
            ''')
        self.assertEqual(tree, exp_tree)
        exp_comp1 = L.Parser.pe('{(2 * y,) for (x, y) in REL(R)}')
        self.assertEqual(query_sym1.node, exp_comp1)


if __name__ == '__main__':
    unittest.main()
