"""Unit tests for comp.py."""


import unittest

from incoq.mars.incast import L
from incoq.mars.symbol import S, N
from incoq.mars.obj.comp import *
from incoq.mars.obj.comp import ReplaceableRewriterBase, MutableObjRelations


class ClauseCase(unittest.TestCase):
    
    def setUp(self):
        self.namers = [
            lambda o, f: 'F' + o + f,
            lambda m, k: 'MAP' + m + k,
            lambda elts: 'TUP' + str(len(elts)) + ''.join(elts),
        ]
    
    def test_objrelations(self):
        objrels1 = ObjRelations(True, ['f'], False, [2])
        objrels2 = ObjRelations(False, ['g', 'f'], True, [3])
        objrels = objrels1.union(objrels2)
        exp_objrels = ObjRelations(True, ['f', 'g'], True, [2, 3])
        self.assertEqual(objrels, exp_objrels)
    
    def test_replaceablerewriterbase(self):
        rewriter = ReplaceableRewriterBase(*self.namers)
        
        # Test all kinds of expressions.
        tree = L.Parser.pe('a.b + c[(d[e], f)]')
        tree, before_clauses, after_clauses = rewriter.process(tree)
        exp_tree = L.Parser.pe('Fab + MAPcTUP2MAPdef')
        exp_before_clauses = L.Parser.pe('''{None
            for (a, Fab) in F(b)
            for (d, e, MAPde) in MAP()
            for (c, TUP2MAPdef, MAPcTUP2MAPdef) in MAP()
            }''').clauses
        exp_after_clauses = L.Parser.pe('''{None
            for (TUP2MAPdef, MAPde, f) in TUP()
            }''').clauses
        self.assertEqual(tree, exp_tree)
        self.assertSequenceEqual(before_clauses, exp_before_clauses)
        self.assertSequenceEqual(after_clauses, exp_after_clauses)
        
        
        # a.b should already be there from the above run.
        tree = L.Parser.pe('(a.b.c,)')
        tree, before_clauses, after_clauses = rewriter.process(tree)
        exp_tree = L.Parser.pe('TUP1FFabc')
        exp_before_clauses = L.Parser.pe('''{None
            for (Fab, FFabc) in F(c)
            }''').clauses
        exp_after_clauses = L.Parser.pe('''{None
            for (TUP1FFabc, FFabc) in TUP()
            }''').clauses
        self.assertEqual(tree, exp_tree)
        self.assertSequenceEqual(before_clauses, exp_before_clauses)
        self.assertSequenceEqual(after_clauses, exp_after_clauses)
        
        exp_objrels = MutableObjRelations(False, ['b', 'c'], True, [2, 1])
        self.assertEqual(rewriter.objrels, exp_objrels)
        
        # Don't rewrite subqueries.
        orig_tree = L.VarsMember(['x'], L.Parser.pe('''
            QUERY('Q1', {p.f for p in S})
            '''))
        tree, _, _ = ReplaceableRewriterBase.run(orig_tree, *self.namers)
        self.assertEqual(tree, orig_tree)
    
    def test_replaceablerewriter(self):
        rewriter = ReplaceableRewriter(*self.namers)
        
        # Membership clause, transform.
        tree = L.Member(L.Parser.pe('o.f'), L.Name('s'))
        tree, _, _ = rewriter.process(tree)
        exp_tree = L.Member(L.Name('Fof'), L.Name('s'))
        self.assertEqual(tree, exp_tree)
        
        # Expression, don't transform.
        tree = L.Parser.pe('(o.f,)')
        tree, _, _ = rewriter.process(tree)
        exp_tree = L.Parser.pe('(Fof,)')
        self.assertEqual(tree, exp_tree)
    
    def test_flatten_replaceables(self):
        comp = L.Parser.pe('{o.f for o in P.s if m[o] > o.f}')
        comp, objrels = flatten_replaceables(comp)
        exp_comp = L.Parser.pe('''
            {o_f for (P, P_s) in F(s) for o in P_s
                 for (m, o, m_o) in MAP() for (o, o_f) in F(f)
                 if (m_o > o_f)}
            ''')
        exp_objrels = ObjRelations(False, ['s', 'f'], True, [])
        self.assertEqual(comp, exp_comp)
        self.assertEqual(objrels, exp_objrels)
    
    def test_flatten_memberships(self):
        comp = L.Parser.pe('''
            {o_f for o in S for (o, o_f) in F(f) if o_f > 5}
            ''')
        comp, objrels = flatten_memberships(comp)
        exp_comp = L.Parser.pe('''
            {o_f for (S, o) in M() for (o, o_f) in F(f) if o_f > 5}
            ''')
        exp_objrels = ObjRelations(True, [], False, [])
        self.assertEqual(comp, exp_comp)
        self.assertEqual(objrels, exp_objrels)
    
    def test_flatten_all_comps(self):
        comp1 = L.Parser.pe('''
            {(z,) for z in T}
            ''')
        comp2 = L.Parser.pe('''
            {x + o.f for o in S for (x,) in VARS(QUERY('Q1',
                {(z,) for z in T}))}
            ''')
        symtab = S.SymbolTable()
        symtab.define_query('Q1', node=comp1, impl=S.Inc)
        symtab.define_query('Q2', node=comp2, impl=S.Inc)
        tree = L.Parser.p('''
            def main():
                print(QUERY('Q2', {x + o.f for o in S
                    for (x,) in VARS(QUERY('Q1', {(z,) for z in T}))}))
            ''')
        tree, objrels = flatten_all_comps(tree, symtab)
        exp_tree = L.Parser.p('''
            def main():
                print(QUERY('Q2', {(x + o_f) for (S, o) in M()
                    for (x,) in VARS(QUERY('Q1', {(z,) for (T, z) in M()}))
                    for (o, o_f) in F(f)}))
            ''')
        exp_objrels = ObjRelations(True, ['f'], False, [])
        self.assertEqual(tree, exp_tree)
        self.assertEqual(objrels, exp_objrels)
    
    def test_flatten_all_comps_impl(self):
        # Ignore queries with Normal impl.
        comp1 = L.Parser.pe('''
            {(z,) for z in T}
            ''')
        comp2 = L.Parser.pe('''
            {x + o.f for o in S for (x,) in VARS(QUERY('Q1',
                {(z,) for z in T}))}
            ''')
        symtab = S.SymbolTable()
        symtab.define_query('Q1', node=comp1, impl=S.Inc)
        symtab.define_query('Q2', node=comp2, impl=S.Normal)
        tree = L.Parser.p('''
            def main():
                print(QUERY('Q2', {x + o.f for o in S
                    for (x,) in VARS(QUERY('Q1', {(z,) for z in T}))}))
            ''')
        tree, objrels = flatten_all_comps(tree, symtab)
        exp_tree = L.Parser.p('''
            def main():
                print(QUERY('Q2', {x + o.f for o in S
                    for (x,) in VARS(QUERY('Q1', {(z,) for (T, z) in M()}))}))
            ''')
        exp_objrels = ObjRelations(True, [], False, [])
        self.assertEqual(tree, exp_tree)
        self.assertEqual(objrels, exp_objrels)


if __name__ == '__main__':
    unittest.main()
