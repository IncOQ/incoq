"""Unit tests for tools.py."""

# Note that since the IncAST parser depends on the MacroExpander,
# if the MacroExpander breaks a bunch of unrelated tests will also
# break.


import unittest
import string
from random import shuffle

from incoq.util.collections import frozendict
from incoq.compiler.incast import nodes as L
from incoq.compiler.incast.tools import *
from incoq.compiler.incast import pynodes as P
from incoq.compiler.incast.pyconv import Parser, IncLangNodeImporter


class IdentFinderCase(unittest.TestCase):
    
    def test_literal_unparse(self):
        tree = literal_unparse([(1, 2), {'a': {True}}])
        exp_tree = Parser.pe("[(1, 2), {'a': {True}}]")
        self.assertEqual(tree, exp_tree)
        
        tree = literal_unparse(frozenset({frozendict({1: 2})}))
        exp_tree = Parser.pe('{{1:2}}')
        self.assertEqual(tree, exp_tree)
    
    def test_identfinder(self):
        # Exclude function name main, updated relation R,
        # and query Q.
        tree = Parser.p('''
            def main():
                a = b
                c, d = e
                for f in g:
                    {h for i in j}
                R.reladd(a)
                QUERY('Q', a)
            ''')
        contexts = ['RelUpdate.rel', 'Fun.name', 'Query.name']
        vars = sorted(IdentFinder.run(tree, contexts=contexts, invert=True))
        exp_vars = list(string.ascii_lowercase)[:10]
        self.assertEqual(vars, exp_vars)


class BindingFinderCase(unittest.TestCase):
    
    def test_find(self):
        tree = Parser.p('''
            def main(w):
                for x in S:
                    for (y, z) in R:
                        print(a)
                    u = v
                    (p,) = (q,)
            ''')
        vars = BindingFinder.run(tree)
        exp_vars = ['w', 'x', 'y', 'z', 'u', 'p']
        self.assertSequenceEqual(list(vars), exp_vars)


class TemplaterCase(unittest.TestCase):
    
    def test_name(self):
        # This test eschews the parser in case the parser breaks.
        # a = a + b
        tree = L.Assign('a', L.BinOp(L.Name('a'), L.Add(), L.Name('b')))
        tree = Templater.run(tree, subst={'a': L.Name('c')})
        # a = c + b
        exp_tree = L.Assign('a', L.BinOp(L.Name('c'), L.Add(), L.Name('b')))
        self.assertEqual(tree, exp_tree)
    
    def test_ident(self):
        tree = Parser.pc('''
            def a(a):
                for a in a:
                    a = a
                    a, b = a
                    a.add(a)
                    a.reladd(a)
                    a[a] = a
                    del a[a]
                    a.mapassign(a, a)
                    a.mapdelete(a)
                    a(a.a)
                    a.get(a, a)
                    a.imglookup('bu', (a,))
                    {a for a in a if a}
            ''')
        tree = Templater.run(tree, subst={'a': 'c'})
        exp_tree = Parser.pc('''
            def c(c):
                for c in c:
                    c = c
                    c, b = c
                    c.add(c)
                    c.reladd(c)
                    c[c] = c
                    del c[c]
                    c.mapassign(c, c)
                    c.mapdelete(c)
                    c(c.c)
                    c.get(c, c)
                    c.imglookup('bu', (c,))
                    {c for c in c if c}
            ''')
        self.assertEqual(tree, exp_tree)
    
    def test_code(self):
        tree = Parser.pc('a; C')
        tree = Templater.run(tree, subst={'<c>C':
                                          L.Expr(L.Name('b'))})
        exp_tree = Parser.pc('a; b')
        self.assertEqual(tree, exp_tree)
        
        tree = Parser.pc('a; C')
        tree = Templater.run(tree, subst={'<c>C':
                                          (L.Expr(L.Name('b')),
                                           L.Expr(L.Name('c')))})
        exp_tree = Parser.pc('a; b; c')
        self.assertEqual(tree, exp_tree)


class MacroExpanderCase(unittest.TestCase):
    
    def test_expansion(self):
        # This test uses IncLangNodeImporter while bypassing
        # the overall IncAST parser.
        class A(MacroExpander):
            def handle_ms_plus(self_, func, a, b):
                self.assertEqual(func, 'plus')
                assert isinstance(a, L.Num)
                assert isinstance(b, L.Num)
                return L.Num(a.n + b.n)
        
        tree = P.Parser.ps('(2).plus(3)')
        tree = IncLangNodeImporter.run(tree)
        tree = A.run(tree)
        exp_tree = L.Num(5)
        self.assertEqual(tree, exp_tree)


class TreeCase(unittest.TestCase):
    
    def test_tree_size(self):
        tree = Parser.pe('1 + 2')
        self.assertEqual(tree_size(tree), 4)
        
        tree = Parser.ps('A')
        self.assertEqual(tree_size(tree), 2)
    
    def test_tree_topsort(self):
        # Create some trees.
        pe = Parser.pe
        t1223 = pe('(1 + 2) + (2 + 3)')
        t12 = pe('1 + 2')
        t23 = pe('2 + 3')
        t1 = pe('1')
        t2 = pe('2')
        trees = [t1223, t12, t23, t1, t2]
        # Partial order of containment.
        exp_order = [
            (t1, t12),
            (t1, t1223),
            (t2, t12),
            (t2, t23),
            (t2, t1223),
            (t12, t1223),
            (t23, t1223),
        ]
        
        # Shuffle randomly, topsort, and confirm the partial order.
        # Repeat 10 times.
        for _ in range(10):
            shuffle(trees)
            result = sorted(trees, key=tree_size)
            for tleft, tright in exp_order:
                self.assertTrue(result.index(tleft) < result.index(tright))


class RewriteCompCase(unittest.TestCase):
    
    def test_basic(self):
        class Rewriter(L.NodeTransformer):
            def process(self, tree):
                self.new_clauses = []
                tree = super().process(tree)
                return tree, self.new_clauses, []
            def visit_Name(self, node):
                if node.id.islower():
                    new_id = '_' + node.id
                    new_clause = L.RelMember([new_id], 'R')
                    self.new_clauses.append(new_clause)
                    return node._replace(id=new_id)
        class AfterRewriter(Rewriter):
            def process(self, tree):
                tree, before, after = super().process(tree)
                return tree, after, before
        
        # Normal.
        comp = Parser.pe('{(x, z) for (x,) in S if y > 1}')
        comp = rewrite_comp(comp, Rewriter.run)
        exp_comp = Parser.pe('''
            {(_x, _z) for (_x,) in REL(R) for (_x,) in S
                      for (_y,) in REL(R) if _y > 1
                      for (_x,) in REL(R) for (_z,) in REL(R)}
            ''')
        self.assertEqual(comp, exp_comp)
        
        # After.
        comp = Parser.pe('{(x, z) for (x,) in S if y > 1}')
        comp = rewrite_comp(comp, AfterRewriter.run)
        exp_comp = Parser.pe('''
            {(_x, _z) for (_x,) in S for (_x,) in REL(R)
                      if _y > 1 for (_y,) in REL(R)
                      for (_x,) in REL(R) for (_z,) in REL(R)}
            ''')
        self.assertEqual(comp, exp_comp)
        
        # Member only.
        comp = Parser.pe('{(x, z) for (x,) in S if y > 1}')
        comp = rewrite_comp(comp, Rewriter.run, member_only=True)
        exp_comp = Parser.pe('''
            {(x, z) for (_x,) in REL(R) for (_x,) in S
                    if y > 1}
            ''')
        self.assertEqual(comp, exp_comp)
        
        # No result expression.
        comp = Parser.pe('{(x, z) for (x,) in S if y > 1}')
        comp = rewrite_comp(comp, Rewriter.run, resexp=False)
        exp_comp = Parser.pe('''
            {(x, z) for (_x,) in REL(R) for (_x,) in S
                    for (_y,) in REL(R) if _y > 1}
            ''')
        self.assertEqual(comp, exp_comp)
        
        # None return.
        comp = Parser.pe('{(x, z) for (x,) in S if y > 1}')
        comp = rewrite_comp(comp, lambda x: None)
        exp_comp = Parser.pe('''
            {(x, z) for (x,) in S if y > 1}
            ''')
        self.assertEqual(comp, exp_comp)
    
    def test_recursive(self):
        class Rewriter(L.NodeTransformer):
            def process(self, tree):
                self.new_clauses = []
                tree = super().process(tree)
                return tree, self.new_clauses, []
            def visit_Name(self, node):
                if node.id not in ['x', 'y']:
                    return node
                new_id = {'x': 'y', 'y': 'z'}[node.id]
                new_clause = L.Member(L.Name(new_id), L.Name('R'))
                self.new_clauses.append(new_clause)
                return node._replace(id=node.id * 2)
        
        comp = Parser.pe('{x for x in S}')
        comp = rewrite_comp(comp, Rewriter.run,
                            member_only=True, recursive=True)
        exp_comp = Parser.pe('''
            {x for z in R for yy in R for xx in S}
            ''')
        self.assertEqual(comp, exp_comp)


if __name__ == '__main__':
    unittest.main()
