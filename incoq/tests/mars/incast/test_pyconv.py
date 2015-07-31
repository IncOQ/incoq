"""Unit tests for pyconv.py."""


import unittest

import incoq.mars.incast.nodes as L
import incoq.mars.incast.pynodes as P
from incoq.mars.incast.pyconv import *
from incoq.mars.incast.pyconv import IncLangNodeImporter


class IncLangNodeParser(P.Parser):
    
    @classmethod
    def parse(cls, *args, **kargs):
        tree = super().parse(*args, **kargs)
        tree = IncLangNodeImporter.run(tree)
        return tree


# We have a simple suite for the node importer, just to verify
# that some importing is actually being done, and a more complex
# round-tripper whose test cases are source-level.


class NodeImporterCase(unittest.TestCase):
    
    p = P.Parser
    i = IncLangNodeParser
    
    def test_name_and_context(self):
        tree = self.i.pe('a')
        exp_tree = L.Name('a', L.Read())
        self.assertEqual(tree, exp_tree)
        
        run = IncLangNodeImporter.run
        
        tree = run(P.Name('a', P.Store()))
        exp_tree = L.Name('a', L.Write())
        self.assertEqual(tree, exp_tree)
        
        tree = run(P.Name('a', P.Del()))
        exp_tree = L.Name('a', L.Write())
        self.assertEqual(tree, exp_tree)
    
    def test_trivial_nodes(self):
        node = self.i.ps('pass')
        exp_node = L.Pass()
        self.assertEqual(node, exp_node)
        
        tree = self.i.pe('a + b')
        exp_tree = L.BinOp(L.Name('a', L.Read()),
                           L.Add(),
                           L.Name('b', L.Read()))
        self.assertEqual(tree, exp_tree)


class RoundTripCase(unittest.TestCase):
    
    def setUp(self):
        class trip(P.Parser):
            @classmethod
            def p(cls, source, exp_source=None, *, mode=None):
                """Parse source as Python code, round-trip it through
                importing and exporting, then compare that it matches
                the tree parsed from exp_source.
                """
                if exp_source is None:
                    exp_source = source
                tree = super().p(source, mode=mode)
                tree = import_incast(tree)
                tree = export_incast(tree)
                exp_tree = super().p(exp_source, mode=mode)
                self.assertEqual(tree, exp_tree)
        
        self.trip = trip
    
    def test_name_and_context(self):
        self.trip.pe('a')
    
    def test_trivial(self):
        self.trip.pe('a + b')
        self.trip.pe('a and b')
    
    def test_functions(self):
        self.trip.ps('''
            def f(a, b):
                print(a, b)
            ''')
        with self.assertRaises(TypeError):
            self.trip.ps('''
                def f():
                    def g():
                        pass
                ''')
    
    def test_assignment(self):
        self.trip.pc('a = b')
        self.trip.pc('a, b = c')
        self.trip.pc('a = b = c', 'b = c; a = b')
    
    def test_loops(self):
        self.trip.ps('for x in S: continue')
        self.trip.ps('while True: break')
    
    def test_comparisons(self):
        self.trip.pe('a < b')
        self.trip.pe('a < b < c', 'a < b and b < c')
    
    def test_comp(self):
        self.trip.pe('{f(x) for (x, y) in S if y in T}')


class ParserCase(unittest.TestCase):
    
    def test_parse(self):
        tree = Parser.pe('a')
        exp_tree = L.Name('a', L.Read())
        self.assertEqual(tree, exp_tree)
    
    def test_unparse(self):
        tree = Parser.pe('a + b')
        source = Parser.ts(tree)
        exp_source = '(a + b)'
        self.assertEqual(source, exp_source)


if __name__ == '__main__':
    unittest.main()
