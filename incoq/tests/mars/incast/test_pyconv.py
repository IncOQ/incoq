"""Unit tests for pyconv.py."""


import unittest

from incoq.util.misc import new_namespace
import incoq.mars.incast.nodes as _nodes
import incoq.mars.incast.tools as _tools
import incoq.mars.incast.pynodes as P
from incoq.mars.incast.pyconv import *


L = new_namespace(_nodes, _tools)


class ContextLoadSetter(P.NodeTransformer):
    
    """Set all expression contexts to Load."""
    
    def load_helper(self, node):
        return P.Load()
    
    visit_Store = load_helper
    visit_Del = load_helper


class ImportCase(unittest.TestCase):
    
    # This is just a simple test suite to verify that some
    # importing is actually being done. These tests do not
    # require that the IncAST parser works. More rigorous,
    # source-level tests are done below that test both
    # importing and round-tripping.
    
    def test_name(self):
        tree = import_incast(P.Name('a', P.Load()))
        exp_tree = L.Name('a')
        self.assertEqual(tree, exp_tree)
        
        tree = import_incast(P.Name('a', P.Store()))
        exp_tree = L.Name('a')
        self.assertEqual(tree, exp_tree)
    
    def test_trivial_nodes(self):
        tree = import_incast(P.Pass())
        exp_tree = L.Pass()
        self.assertEqual(tree, exp_tree)
        
        tree = import_incast(P.BinOp(P.Name('a', P.Load()),
                                     P.Add(),
                                     P.Name('b', P.Load())))
        exp_tree = L.BinOp(L.Name('a'), L.Add(), L.Name('b'))
        self.assertEqual(tree, exp_tree)


class ParserCase(unittest.TestCase):
    
    def test_parse(self):
        tree = Parser.pe('a')
        exp_tree = L.Name('a')
        self.assertEqual(tree, exp_tree)
    
    def test_subst(self):
        tree = Parser.pe('a + b', subst={'a': L.Name('c')})
        exp_tree = L.BinOp(L.Name('c'), L.Add(), L.Name('b'))
        self.assertEqual(tree, exp_tree)
    
    def test_unparse_basic(self):
        tree = Parser.pe('a + b')
        source = Parser.ts(tree)
        exp_source = '(a + b)'
        self.assertEqual(source, exp_source)
    
    def test_unparse_comp_bad(self):
        # No clauses.
        node = L.Comp(L.Name('x'), [])
        with self.assertRaises(IncASTConversionError):
            Parser.ts(node)
        
        # Condition clause before membership.
        node = L.Comp(L.Name('x'), [L.Cond(L.NameConstant(True)),
                                    L.Member(L.Name('x'), L.Name('S'))])
        with self.assertRaises(IncASTConversionError):
            Parser.ts(node)
    
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
        
        source = ts(L.Member(pe('(x, y)'), pe('R')))
        exp_source = ' for (x, y) in R'
        self.assertEqual(source, exp_source)
        
        source = ts(L.Cond(pe('True')))
        exp_source = 'True'
        self.assertEqual(source, exp_source)
        
        source = ts(L.SetAdd())
        exp_source = "'<SetAdd>'"
        self.assertEqual(source, exp_source)
        
        source = ts(L.mask('bu'))
        exp_source = "'<Mask: bu>'"
        self.assertEqual(source, exp_source)
        
        source = ts(L.Comment('Text'))
        exp_source = '# Text'
        self.assertEqual(source, exp_source)


class ParseImportCase(unittest.TestCase):
    
    def test_functions(self):
        tree = Parser.p('''
            def f():
                pass
            ''')
        exp_tree = L.Module([L.fun('f', [], [L.Pass()])])
        self.assertEqual(tree, exp_tree)
        
        # Disallow inner functions.
        with self.assertRaises(IncASTConversionError):
            Parser.p('''
                def f():
                    def g():
                        pass
                ''')
        
        # Modules must consist of functions.
        with self.assertRaises(IncASTConversionError):
            Parser.p('x = 1')
    
    def test_comment(self):
        tree = Parser.ps("COMMENT('Text')")
        exp_tree = L.Comment('Text')
        self.assertEqual(tree, exp_tree)
    
    def test_for(self):
        tree = Parser.ps('for x in S: pass')
        exp_tree = L.For('x', L.Name('S'), [L.Pass()])
        self.assertEqual(tree, exp_tree)
        
        with self.assertRaises(IncASTConversionError):
            Parser.ps('for x, y in S: pass')
    
    def test_assign(self):
        tree = Parser.ps('a = b')
        exp_tree = L.Assign('a', L.Name('b'))
        self.assertEqual(tree, exp_tree)
        
        tree = Parser.ps('a, b = c')
        exp_tree = L.DecompAssign(['a', 'b'], L.Name('c'))
        self.assertEqual(tree, exp_tree)
        
        tree = Parser.ps('a, = c')
        exp_tree = L.DecompAssign(['a'], L.Name('c'))
        self.assertEqual(tree, exp_tree)
    
    def test_setupdates(self):
        tree = Parser.ps('S.add(x)')
        exp_tree = L.SetUpdate(L.Name('S'), L.SetAdd(), L.Name('x'))
        self.assertEqual(tree, exp_tree)
        
        tree = Parser.ps('S.reladd(x)')
        exp_tree = L.RelUpdate('S', L.SetAdd(), 'x')
        self.assertEqual(tree, exp_tree)
        
        with self.assertRaises(IncASTConversionError):
            Parser.ps('(a + b).reladd(x)')
        with self.assertRaises(IncASTConversionError):
            Parser.ps('S.reladd(x + y)')
    
    def test_calls(self):
        tree = Parser.pe('f(a)')
        exp_tree = L.Call('f', [L.Name('a')])
        self.assertEqual(tree, exp_tree)
        
        tree = Parser.pe('o.f(a)')
        exp_tree = L.GeneralCall(L.Attribute(L.Name('o'), 'f'),
                                 [L.Name('a')])
        self.assertEqual(tree, exp_tree)
    
    def test_dictupdates(self):
        tree = Parser.ps('M[k] = v')
        exp_tree = L.DictAssign(L.Name('M'), L.Name('k'), L.Name('v'))
        self.assertEqual(tree, exp_tree)
        
        tree = Parser.ps('del M[k]')
        exp_tree = L.DictDelete(L.Name('M'), L.Name('k'))
        self.assertEqual(tree, exp_tree)
        
        tree = Parser.ps('M.mapassign(k, v)')
        exp_tree = L.MapAssign('M', 'k', 'v')
        self.assertEqual(tree, exp_tree)
        
        tree = Parser.ps('M.mapdelete(k)')
        exp_tree = L.MapDelete('M', 'k')
        self.assertEqual(tree, exp_tree)
    
    def test_subscript(self):
        tree = Parser.pe('t.index(i)')
        exp_tree = L.Subscript(L.Name('t'), L.Name('i'))
        self.assertEqual(tree, exp_tree)
    
    def test_dictlookups(self):
        tree = Parser.pe('M.get(k, d)')
        exp_tree = L.DictLookup(L.Name('M'), L.Name('k'), L.Name('d'))
        self.assertEqual(tree, exp_tree)
        
        tree = Parser.pe('M[k]')
        exp_tree = L.DictLookup(L.Name('M'), L.Name('k'), None)
        self.assertEqual(tree, exp_tree)
    
    def test_imgset(self):
        tree = Parser.pe("R.imgset('bu', (x,))")
        exp_tree = L.Imgset('R', L.mask('bu'), ['x'])
        self.assertEqual(tree, exp_tree)
    
    def test_clauses(self):
        N = L.Name
        
        # Member and Cond.
        tree = Parser.pe('{x for x in R if x in S}')
        exp_tree = L.Comp(N('x'), [L.Member(N('x'), N('R')),
                                   L.Cond(L.Compare(N('x'), L.In(), N('S')))])
        self.assertEqual(tree, exp_tree)
        
        # RelMember.
        tree = Parser.pe('{x for (x, y) in REL(R)}')
        exp_tree =L.Comp(N('x'), [L.RelMember(['x', 'y'], 'R')])
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
                exp_tree = ContextLoadSetter.run(exp_tree)
                self.assertEqual(tree, exp_tree)
        
        self.trip = trip
    
    def test_name_and_context(self):
        self.trip.pe('a')
    
    def test_trivial(self):
        self.trip.pe('a + b')
        self.trip.pe('a and b')
        self.trip.pe('o.f.g')
    
    def test_functions(self):
        self.trip.ps('''
            def f(a, b):
                print(a, b)
            ''')
    
    def test_loops(self):
        self.trip.ps('for x in S: continue')
        self.trip.ps('while True: break')
    
    def test_assign(self):
        self.trip.ps('a = b')
        self.trip.ps('a, b = c')
        self.trip.ps('a, = c')
    
    def test_setupdates(self):
        self.trip.ps('S.add(x)')
        self.trip.ps('S.reladd(x)')
    
    def test_dictupdates(self):
        self.trip.ps('M[k] = v')
        self.trip.ps('del M[k]')
        self.trip.ps('M.mapassign(k, v)')
        self.trip.ps('M.mapdelete(k)')
    
    def test_lists(self):
        self.trip.pe('[1, 2]')
    
    def test_subscript(self):
        self.trip.pe('t.index(i)')
    
    def test_dictlookup(self):
        self.trip.pe('M[k]')
        self.trip.pe('M.get(k, d)')
    
    def test_imgset(self):
        self.trip.pe("R.imgset('bu', (x,))")
    
    def test_comp(self):
        self.trip.pe('{f(x) for (x, y) in S if y in T}')
        self.trip.pe('{x for (x, y) in REL(R)}')


if __name__ == '__main__':
    unittest.main()
