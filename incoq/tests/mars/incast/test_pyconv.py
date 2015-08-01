"""Unit tests for pyconv.py."""


import unittest

import incoq.mars.incast.nodes as L
import incoq.mars.incast.pynodes as P
from incoq.mars.incast.pyconv import *
from incoq.mars.incast.pyconv import IncLangNodeImporter


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


class NodeImporterCase(unittest.TestCase):
    
    # This is just a simple test suite to verify that some
    # importing is actually being done. More rigorous tests
    # that are source-level are done below in the round-tripper.
    
    def test_name_and_context(self):
        run = IncLangNodeImporter.run
        
        tree = run(P.Name('a', P.Load()))
        exp_tree = L.Name('a', L.Read())
        self.assertEqual(tree, exp_tree)
        
        tree = run(P.Name('a', P.Store()))
        exp_tree = L.Name('a', L.Write())
        self.assertEqual(tree, exp_tree)
        
        tree = run(P.Name('a', P.Del()))
        exp_tree = L.Name('a', L.Write())
        self.assertEqual(tree, exp_tree)
    
    def test_trivial_nodes(self):
        run = IncLangNodeImporter.run
        
        tree = run(P.Pass())
        exp_tree = L.Pass()
        self.assertEqual(tree, exp_tree)
        
        tree = run(P.BinOp(P.Name('a', P.Load()),
                           P.Add(),
                           P.Name('b', P.Load())))
        exp_tree = L.BinOp(L.Name('a', L.Read()),
                           L.Add(),
                           L.Name('b', L.Read()))
        self.assertEqual(tree, exp_tree)


class RoundTripCase(unittest.TestCase):
    
    def setUp(self):
        class trip(P.ExtractMixin):
            """Parse source as Python code, round-trip it through
            importing and exporting, then compare that it matches
            the tree parsed from exp_source.
            """
            @classmethod
            def action(cls, source, exp_source=None, *, mode=None):
                if exp_source is None:
                    exp_source = source
                tree = P.Parser.action(source, mode=mode)
                tree = import_incast(tree)
                tree = export_incast(tree)
                exp_tree = P.Parser.action(exp_source, mode=mode)
                self.assertEqual(tree, exp_tree)
        
        self.trip = trip
    
    def test_name_and_context(self):
        self.trip.pe('a')
    
    def test_trivial(self):
        self.trip.pe('a + b')
        self.trip.pe('a and b')
        self.trip.pe('o.f.g')
    
    def test_functions(self):
        # Basic definition and call.
        self.trip.ps('''
            def f(a, b):
                print(a, b)
            ''')
        
        # Disallow inner functions.
        with self.assertRaises(TypeError):
            self.trip.ps('''
                def f():
                    def g():
                        pass
                ''')
        
        # Disallow general calls.
        with self.assertRaises(TypeError):
            self.trip.ps('f.g(x)')
        
        # Modules must consist of functions.
        self.trip.p('''
            def f():
                pass
            ''')
        with self.assertRaises(TypeError):
            self.trip.p('x = 1')
    
    def test_loops(self):
        self.trip.ps('for x in S: continue')
        self.trip.ps('while True: break')
    
    def test_setupdates(self):
        self.trip.ps('S.add(x)')
        self.trip.ps('S.reladd(x)')
        with self.assertRaises(TypeError):
            self.trip.ps('(a + b).reladd(x)')
    
    def test_comp(self):
        self.trip.pe('{f(x) for (x, y) in S if y in T}')


class ParserCase(unittest.TestCase):
    
    def test_parse(self):
        tree = Parser.pe('a')
        exp_tree = L.Name('a', L.Read())
        self.assertEqual(tree, exp_tree)
    
    def test_unparse_basic(self):
        tree = Parser.pe('a + b')
        source = Parser.ts(tree)
        exp_source = '(a + b)'
        self.assertEqual(source, exp_source)
    
    def test_unparse_extras(self):
        # Also check cases of unparsing IncAST nodes that normally
        # don't appear (at least not by themselves) in complete
        # programs.
        ps = Parser.ps
        pe = Parser.pe
        ts = Parser.ts
        
        source = ts(L.GeneralCall(pe('a + b'), [pe('c')]))
        exp_source = '(a + b)(c)'
        self.assertEqual(source, exp_source)
        
        source = ts(L.Member(['x', 'y'], 'R'))
        exp_source = ' for (x, y) in R'
        self.assertEqual(source, exp_source)
        
        source = ts(L.Cond(pe('True')))
        exp_source = 'True'
        self.assertEqual(source, exp_source)
        
        source = ts(L.Read())
        exp_source = '<Unknown node "Load">'
        self.assertEqual(source, exp_source)
        
        source = ts(L.SetAdd())
        exp_source = "'<SetAdd>'"
        self.assertEqual(source, exp_source)


if __name__ == '__main__':
    unittest.main()