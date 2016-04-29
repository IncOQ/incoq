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
        aggr = L.Parser.pe('''
            count({(b,) for (b,) in REL(R)})
            ''')
        symtab = S.SymbolTable()
        symtab.define_query('Q', node=comp)
        symtab.define_query('A', node=aggr)
        tree = L.Parser.p('''
            def main():
                print(QUERY('Q', {(a,) for (a,) in VARS(
                                       {(b,) for (b,) in REL(R)})}))
                print({(b,) for (b,) in REL(R)})
                print(QUERY('A', count({(b,) for (b,) in REL(R)})))
            ''')
        tree = mark_query_forms(tree, symtab)
        exp_tree = L.Parser.p('''
            def main():
                print(QUERY('Q', {(a,) for (a,) in VARS(QUERY('Query1',
                                       {(b,) for (b,) in REL(R)}))}))
                print(QUERY('Query3', {(b,) for (b,) in REL(R)}))
                print(QUERY('A', count(QUERY('Query2',
                    {(b,) for (b,) in REL(R)}))))
            ''')
        self.assertEqual(tree, exp_tree)
        # Check consistency.
        S.QueryRewriter.run(tree, symtab)
    
    def test_unmark_normal_impl(self):
        comp1 = L.Parser.pe('''
            {(a,) for (a,) in REL(R)}
            ''')
        comp2 = L.Parser.pe('''
            count(QUERY('Q1', {(a,) for (a,) in REL(R)}))
            ''')
        symtab = S.SymbolTable()
        symtab.define_query('Q1', node=comp1, impl=S.Inc)
        symtab.define_query('Q2', node=comp2, impl=S.Normal)
        tree = L.Parser.p('''
            def main():
                print(QUERY('Q2', count(QUERY('Q1',
                    {(a,) for (a,) in REL(R)}))))
            ''')
        
        tree = unmark_normal_impl(tree, symtab)
        exp_tree = L.Parser.p('''
            def main():
                print(count(QUERY('Q1',
                    {(a,) for (a,) in REL(R)})))
            ''')
        self.assertEqual(tree, exp_tree)
        self.assertNotIn('Q2', symtab.get_queries())
    
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
    
    def test_rewrite_aggregates(self):
        symtab = S.SymbolTable()
        aggr = L.Parser.pe('max(A | {1, 2} | {3})')
        query = symtab.define_query('Q', node=aggr)
        tree = L.Parser.p('''
            def main():
                print(QUERY('Q', max(A | {1, 2} | {3})))
            ''')
        tree = rewrite_aggregates(tree, symtab)
        exp_tree = L.Parser.p('''
            def main():
                print(max2(QUERY('Q', max(A)), 1, 2, 3))
            ''')
        self.assertEqual(tree, exp_tree)
        exp_aggr = L.Parser.pe('max(A)')
        self.assertEqual(query.node, exp_aggr)
        
        # Don't fire where inapplicable.
        symtab = S.SymbolTable()
        aggr1 = L.Parser.pe('max(A)')
        query1 = symtab.define_query('Q1', node=aggr1)
        aggr2 = L.Parser.pe('max(A | {1} | B)')
        query2 = symtab.define_query('Q2', node=aggr2)
        tree = L.Parser.p('''
            def main():
                print(QUERY('Q1', max(A)))
                print(QUERY('Q2', max(A | {1} | B)))
            ''')
        exp_tree = tree
        tree = rewrite_aggregates(tree, symtab)
        self.assertEqual(tree, exp_tree)


if __name__ == '__main__':
    unittest.main()
