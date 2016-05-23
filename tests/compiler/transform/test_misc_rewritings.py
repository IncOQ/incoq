"""Unit tests for misc_rewritings.py."""


import unittest

from incoq.compiler.incast import L
from incoq.compiler.symbol import S
from incoq.compiler.transform.misc_rewritings import *


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
        
        symtab = S.SymbolTable()
        aggr = L.Parser.pe('max(A | B | {0})')
        query = symtab.define_query('Q', node=aggr, impl=S.Inc)
        tree = L.Parser.p('''
            def main():
                print(QUERY('Q', max(A | B | {0})))
            ''')
        tree = rewrite_aggregates(tree, symtab)
        exp_tree = L.Parser.p('''
            def main():
                print(max2(QUERY('Q', max(A)),
                           QUERY('Q_aggrop2', max(B)),
                           0))
            ''')
        self.assertEqual(tree, exp_tree)
        exp_aggr1 = L.Parser.pe('max(A)')
        exp_aggr2 = L.Parser.pe('max(B)')
        q2 = symtab.get_queries()['Q_aggrop2']
        self.assertEqual(query.node, exp_aggr1)
        self.assertEqual(query.impl, S.Inc)
        self.assertEqual(q2.node, exp_aggr2)
        self.assertEqual(q2.impl, S.Inc)
        
        # Don't fire where inapplicable.
        symtab = S.SymbolTable()
        aggr1 = L.Parser.pe('max(A)')
        query1 = symtab.define_query('Q1', node=aggr1)
        aggr2 = L.Parser.pe('max((A | {1}) + B)')
        query2 = symtab.define_query('Q2', node=aggr2)
        tree = L.Parser.p('''
            def main():
                print(QUERY('Q1', max(A)))
                print(QUERY('Q2', max((A | {1}) + B)))
            ''')
        exp_tree = tree
        tree = rewrite_aggregates(tree, symtab)
        self.assertEqual(tree, exp_tree)
    
    def test_elim_dead_funcs(self):
        symtab = S.SymbolTable()
        symtab.maint_funcs = ['foo', 'bar']
        tree = L.Parser.p('''
            def foo():
                pass
            
            def bar():
                pass
            
            def baz():
                pass
            
            def main():
                foo()
            ''')
        tree = elim_dead_funcs(tree, symtab)
        exp_tree = L.Parser.p('''
            def foo():
                pass
            
            def baz():
                pass
            
            def main():
                foo()
            ''')
        self.assertEqual(tree, exp_tree)
    
    def test_make_updates_strict(self):
        symtab = S.SymbolTable()
        tree = L.Parser.p('''
            def main():
                s.add(x)
                s.remove(x)
                R.reladd(x)
                R.relremove(x)
                m[k] = v
                del m[k]
                M.mapassign(k, v)
                M.mapdelete(k)
                o.f = v
                del o.f
            ''')
        tree = make_updates_strict(tree, symtab)
        exp_tree = L.Parser.p('''
            def main():
                if (x not in s):
                    s.add(x)
                if (x in s):
                    s.remove(x)
                if (x not in R):
                    R.reladd(x)
                if (x in R):
                    R.relremove(x)
                if (k in m):
                    del m[k]
                m[k] = v
                if (k in m):
                    del m[k]
                if (k in M):
                    M.mapdelete(k)
                M.mapassign(k, v)
                if (k in M):
                    M.mapdelete(k)
                if hasfield(o, 'f'):
                    del o.f
                o.f = v
                if hasfield(o, 'f'):
                    del o.f
            ''')
        self.assertEqual(tree, exp_tree)


if __name__ == '__main__':
    unittest.main()
