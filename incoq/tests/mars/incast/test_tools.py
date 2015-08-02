"""Unit tests for tools.py."""


import unittest

from incoq.mars.incast import nodes as L
from incoq.mars.incast.tools import *
from incoq.mars.incast import pynodes as P
from incoq.mars.incast.pyconv import Parser, IncLangNodeImporter


class TemplaterCase(unittest.TestCase):
    
    def test_name(self):
        tree = Parser.pc('''
            a = a + b
            ''')
        tree = Templater.run(tree, subst={'a': L.Name('c', L.Read())})
        exp_tree = Parser.pc('''
            a = c + b
            ''')
        self.assertEqual(tree, exp_tree)
    
    def test_ident(self):
        tree = Parser.pc('''
            def a(a):
                for a, b in a:
                    a, b = a
                    a.add(a)
                    a.reladd(a)
                    a(a.a)
                    {a for a in a if a}
            ''')
        tree = Templater.run(tree, subst={'a': 'c'})
        exp_tree = Parser.pc('''
            def c(c):
                for c, b in c:
                    c, b = c
                    c.add(c)
                    c.reladd(c)
                    c(c.c)
                    {c for c in c if c}
            ''')
        self.assertEqual(tree, exp_tree)
    
    def test_code(self):
        tree = Parser.pc('''
            a
            C
            ''')
        tree = Templater.run(tree, subst={'<c>C':
                                          L.Expr(L.Name('b', L.Read()))})
        exp_tree = Parser.pc('''
            a
            b
            ''')
        self.assertEqual(tree, exp_tree)
        
        tree = Parser.pc('''
            a
            C
            ''')
        tree = Templater.run(tree, subst={'<c>C':
                                          (L.Expr(L.Name('b', L.Read())),
                                           L.Expr(L.Name('c', L.Read())))})
        exp_tree = Parser.pc('''
            a
            b
            c
            ''')
        self.assertEqual(tree, exp_tree)


class MacroExpanderCase(unittest.TestCase):
    
    def test_expansion(self):
        class A(MacroExpander):
            def handle_ms_add(self_, func, a, b):
                self.assertEqual(func, 'add')
                assert isinstance(a, L.Num)
                assert isinstance(b, L.Num)
                return L.Num(a.n + b.n)
        
        tree = P.Parser.ps('(2).add(3)')
        tree = IncLangNodeImporter.run(tree)
        tree = A.run(tree)
        exp_tree = L.Num(5)
        self.assertEqual(tree, exp_tree)


if __name__ == '__main__':
    unittest.main()
