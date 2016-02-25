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
        
        tree = Parser.ps('for x, y in S: pass')
        exp_tree = L.DecompFor(['x', 'y'], L.Name('S'), [L.Pass()])
        self.assertEqual(tree, exp_tree)
    
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
    
    def test_assert(self):
        tree = Parser.ps('assert t')
        exp_tree = L.Assert(L.Name('t'))
        self.assertEqual(tree, exp_tree)
    
    def test_setupdates(self):
        tree = Parser.ps('S.add(x)')
        exp_tree = L.SetUpdate(L.Name('S'), L.SetAdd(), L.Name('x'))
        self.assertEqual(tree, exp_tree)
        
        tree = Parser.ps('S.reladd(x)')
        exp_tree = L.RelUpdate('S', L.SetAdd(), 'x')
        self.assertEqual(tree, exp_tree)
        
        tree = Parser.ps('S.inccount(x)')
        exp_tree = L.SetUpdate(L.Name('S'), L.IncCount(), L.Name('x'))
        self.assertEqual(tree, exp_tree)
        
        tree = Parser.ps('S.relinccount(x)')
        exp_tree = L.RelUpdate('S', L.IncCount(), 'x')
        self.assertEqual(tree, exp_tree)
        
        with self.assertRaises(IncASTConversionError):
            Parser.ps('(a + b).reladd(x)')
        with self.assertRaises(IncASTConversionError):
            Parser.ps('S.reladd(x + y)')
        with self.assertRaises(IncASTConversionError):
            Parser.ps('(a + b).relinccount(x)')
    
    def test_setbulkupdates_and_clear(self):
        tree = Parser.pc('''
            S.update(T)
            S.intersection_update(T)
            S.difference_update(T)
            S.symmetric_difference_update(T)
            S.copy_update(T)
            S.clear()
            R.relclear()
            ''')
        exp_tree = (L.SetBulkUpdate(L.Name('S'), L.Union(), L.Name('T')),
                    L.SetBulkUpdate(L.Name('S'), L.Inter(), L.Name('T')),
                    L.SetBulkUpdate(L.Name('S'), L.Diff(), L.Name('T')),
                    L.SetBulkUpdate(L.Name('S'), L.SymDiff(), L.Name('T')),
                    L.SetBulkUpdate(L.Name('S'), L.Copy(), L.Name('T')),
                    L.SetClear(L.Name('S')),
                    L.RelClear('R'))
        self.assertEqual(tree, exp_tree)
    
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
        
        tree = Parser.ps('M.dictclear()')
        exp_tree = L.DictClear(L.Name('M'))
        self.assertEqual(tree, exp_tree)
        
        tree = Parser.ps('M.mapassign(k, v)')
        exp_tree = L.MapAssign('M', 'k', 'v')
        self.assertEqual(tree, exp_tree)
        
        tree = Parser.ps('M.mapdelete(k)')
        exp_tree = L.MapDelete('M', 'k')
        self.assertEqual(tree, exp_tree)
        
        tree = Parser.ps('M.mapclear()')
        exp_tree = L.MapClear('M')
        self.assertEqual(tree, exp_tree)
    
    def test_attrupdates(self):
        tree = Parser.ps('o.f.g = v')
        exp_tree = L.AttrAssign(L.Attribute(L.Name('o'), 'f'), 'g',
                                L.Name('v'))
        self.assertEqual(tree, exp_tree)
        
        tree = Parser.ps('del o.f.g')
        exp_tree = L.AttrDelete(L.Attribute(L.Name('o'), 'f'), 'g')
        self.assertEqual(tree, exp_tree)
    
    def test_set(self):
        tree = Parser.pe('{1, 2}')
        exp_tree = L.Set([L.Num(1), L.Num(2)])
        self.assertEqual(tree, exp_tree)
    
    def test_subscript(self):
        tree = Parser.pe('index(t, i)')
        exp_tree = L.Subscript(L.Name('t'), L.Name('i'))
        self.assertEqual(tree, exp_tree)
    
    def test_dictlookups(self):
        tree = Parser.pe('M.get(k, d)')
        exp_tree = L.DictLookup(L.Name('M'), L.Name('k'), L.Name('d'))
        self.assertEqual(tree, exp_tree)
        
        tree = Parser.pe('M[k]')
        exp_tree = L.DictLookup(L.Name('M'), L.Name('k'), None)
        self.assertEqual(tree, exp_tree)
    
    def test_firstthen(self):
        tree = Parser.pe('FIRSTTHEN(a, b)')
        exp_tree = L.FirstThen(L.Name('a'), L.Name('b'))
        self.assertEqual(tree, exp_tree)
    
    def test_imglookup(self):
        tree = Parser.pe("R.imglookup('bu', (x,))")
        exp_tree = L.ImgLookup(L.Name('R'), L.mask('bu'), ['x'])
        self.assertEqual(tree, exp_tree)
    
    def test_setfrommap(self):
        tree = Parser.pe("M.setfrommap('bu')")
        exp_tree = L.SetFromMap(L.Name('M'), L.mask('bu'))
        self.assertEqual(tree, exp_tree)
    
    def test_unwrap(self):
        tree = Parser.pe('unwrap(R)')
        exp_tree = L.Unwrap(L.Name('R'))
        self.assertEqual(tree, exp_tree)
    
    def test_typechecks(self):
        tree = Parser.pe('isset(s)')
        exp_tree = L.IsSet(L.Name('s'))
        self.assertEqual(tree, exp_tree)
        
        tree = Parser.pe("hasfield(o, 'f')")
        exp_tree = L.HasField(L.Name('o'), 'f')
        self.assertEqual(tree, exp_tree)
        
        tree = Parser.pe('ismap(m)')
        exp_tree = L.IsMap(L.Name('m'))
        self.assertEqual(tree, exp_tree)
        
        tree = Parser.pe('hasarity(t, 5)')
        exp_tree = L.HasArity(L.Name('t'), 5)
        self.assertEqual(tree, exp_tree)
    
    def test_getcount(self):
        tree = Parser.pe('R.getcount(e)')
        exp_tree = L.BinOp(L.Name('R'), L.GetCount(), L.Name('e'))
        self.assertEqual(tree, exp_tree)
    
    def test_query(self):
        tree = Parser.pe("QUERY('A', 5)")
        exp_tree = L.Query('A', L.Num(5), None)
        self.assertEqual(tree, exp_tree)
        
        tree = Parser.pe("QUERY('A', 5, 1 + 1)")
        exp_tree = L.Query('A', L.Num(5), 2)
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
        exp_tree = L.Comp(N('x'), [L.RelMember(['x', 'y'], 'R')])
        self.assertEqual(tree, exp_tree)
        
        # SingMember.
        tree = Parser.pe('{x for (x, y) in SING(e)}')
        exp_tree = L.Comp(N('x'), [L.SingMember(['x', 'y'], N('e'))])
        self.assertEqual(tree, exp_tree)
        
        # WithoutMember.
        tree = Parser.pe('{x for (x, y) in WITHOUT(REL(R), e)}')
        exp_tree = L.Comp(N('x'),
            [L.WithoutMember(L.RelMember(['x', 'y'], 'R'), N('e'))])
        self.assertEqual(tree, exp_tree)
        
        # VarsMember.
        tree = Parser.pe('{x for (x, y) in VARS(1 + 1)}')
        exp_tree = L.Comp(N('x'), [L.VarsMember(['x', 'y'],
                                                Parser.pe('1 + 1'))])
        self.assertEqual(tree, exp_tree)
        
        # SetFromMap.
        tree = Parser.pe("{x for (x, y) in SETFROMMAP(R, M, 'bu')}")
        exp_tree = L.Comp(N('x'), [L.SetFromMapMember(['x', 'y'], 'R', 'M',
                                                      L.mask('bu'))])
        self.assertEqual(tree, exp_tree)
        
        # Object domain clauses.
        tree = Parser.pe('''
            {x for (x, y) in M() for (x, y) in F(f)
               for (x, y, z) in MAP() for (x, y, z) in TUP()}
            ''')
        exp_tree = L.Comp(N('x'), [
            L.MMember('x', 'y'),
            L.FMember('x', 'y', 'f'),
            L.MAPMember('x', 'y', 'z'),
            L.TUPMember('x', ['y', 'z']),
        ])
        self.assertEqual(tree, exp_tree)
    
    def test_aggr(self):
        trees = [
            Parser.pe('count(S)'),
            Parser.pe('sum(S)'),
            Parser.pe('min(S)'),
            Parser.pe('max(S)'),
        ]
        exp_trees = (
            L.Aggr(L.Count(), L.Name('S')),
            L.Aggr(L.Sum(), L.Name('S')),
            L.Aggr(L.Min(), L.Name('S')),
            L.Aggr(L.Max(), L.Name('S')),
        )
        self.assertSequenceEqual(trees, exp_trees)
    
    def test_aggrrestr(self):
        tree = Parser.pe('count(S, (x,), R)')
        exp_tree = L.AggrRestr(L.Count(), L.Name('S'), ('x',), L.Name('R'))
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
    
    def test_assert(self):
        self.trip.ps('assert t')
    
    def test_loops(self):
        self.trip.ps('for x in S: continue')
        self.trip.ps('for x, y in S: pass')
        self.trip.ps('while True: break')
    
    def test_assign(self):
        self.trip.ps('a = b')
        self.trip.ps('a, b = c')
        self.trip.ps('a, = c')
    
    def test_setupdates(self):
        self.trip.ps('S.add(x)')
        self.trip.ps('S.reladd(x)')
        self.trip.ps('S.inccount(x)')
        self.trip.ps('S.relinccount(x)')
    
    def test_setbulkupdates_and_clear(self):
        self.trip.ps('S.update(T)')
        self.trip.ps('S.intersection_update(T)')
        self.trip.ps('S.difference_update(T)')
        self.trip.ps('S.symmetric_difference_update(T)')
        self.trip.ps('S.copy_update(T)')
        self.trip.ps('S.clear()')
        self.trip.ps('R.relclear()')
    
    def test_dictupdates(self):
        self.trip.ps('M[k] = v')
        self.trip.ps('del M[k]')
        self.trip.ps('M.dictclear()')
        self.trip.ps('M.mapassign(k, v)')
        self.trip.ps('M.mapdelete(k)')
        self.trip.ps('M.mapclear()')
    
    def test_attrupdates(self):
        self.trip.ps('o.f.g = v')
        self.trip.ps('del o.f.g')
    
    def test_getcount(self):
        self.trip.pe('S.getcount(x)')
    
    def test_listssets(self):
        self.trip.pe('[1, 2]')
        self.trip.pe('{1, 2}')
    
    def test_set(self):
        self.trip.pe('{1, 2}')
    
    def test_subscript(self):
        self.trip.pe('index(t, i)')
    
    def test_dictlookup(self):
        self.trip.pe('M[k]')
        self.trip.pe('M.get(k, d)')
    
    def test_firstthen(self):
        self.trip.pe('FIRSTTHEN(a, b)')
    
    def test_imglookup(self):
        self.trip.pe("R.imglookup('bu', (x,))")
    
    def test_setfrommap(self):
        self.trip.pe("R.setfrommap('bu')")
    
    def test_unwrap(self):
        self.trip.pe('unwrap(R)')
    
    def test_typechecks(self):
        self.trip.pc('''
            isset(s)
            hasfield(o, 'f')
            ismap(m)
            hasarity(t, 5)
            ''')
    
    def test_query(self):
        self.trip.pe("QUERY('A', 5)")
        self.trip.pe("QUERY('A', 5, 2)")
        self.trip.pe("QUERY('A', 5, {1: (2, 'b')})")
    
    def test_comp(self):
        self.trip.pe('{f(x) for (x, y) in S if y in T}')
        self.trip.pe('{x for (x, y) in REL(R)}')
        self.trip.pe('{x for (x, y) in SING(E)}')
        self.trip.pe('{x for (x, y) in WITHOUT(REL(R), e)}')
        self.trip.pe('{x for (x, y) in VARS(1 + 1)}')
        self.trip.pe("{x for (x, y) in SETFROMMAP(R, M, 'bu')}")
        self.trip.pe('{x for (x, y) in M()}')
        self.trip.pe('{x for (x, y) in F(f)}')
        self.trip.pe('{x for (x, y, z) in MAP()}')
        self.trip.pe('{x for (x, y, z) in TUP()}')
    
    def test_aggr(self):
        self.trip.pc('''
            count(S)
            sum(S)
            min(S)
            max(S)
            ''')
    
    def test_aggrrestr(self):
        self.trip.pc('''
            count(S, (x,), R)
            sum(S, (x, y), R)
            min(S, (x,), R)
            max(S, (x, y), R)
            ''')
    
    def test_unparse_arity(self):
        self.trip.p('''
            def main():
                for (x,) in S:
                    (y,) = x
                    {z for (z,) in S}
            ''')
        self.trip.p('''
            def main():
                for [] in S:
                    [] = x
                    {None for [] in S}
            ''')


if __name__ == '__main__':
    unittest.main()
