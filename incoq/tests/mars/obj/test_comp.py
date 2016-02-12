"""Unit tests for clause.py."""


import unittest

from incoq.mars.incast import L
from incoq.mars.symbol import S, N
from incoq.mars.obj.comp import *


class ClauseCase(unittest.TestCase):
    
    def setUp(self):
        self.namers = [
            lambda o, f: 'F' + o + f,
            lambda m, k: 'MAP' + m + k,
            lambda elts: 'TUP' + str(len(elts)) + ''.join(elts),
        ]
    
    def test_replaceablerewriter_basic(self):
        rewriter = ReplaceableRewriter(*self.namers)
        
        tree = L.Parser.pe('a.b + c[(d[e], f)]')
        tree, clauses = rewriter.process(tree)
        exp_tree = L.Parser.pe('Fab + MAPcTUP2MAPdef')
        exp_clauses = L.Parser.pe('''{None
            for (a, Fab) in F(b)
            for (d, e, MAPde) in MAP()
            for (TUP2MAPdef, MAPde, f) in TUP()
            for (c, TUP2MAPdef, MAPcTUP2MAPdef) in MAP()
            }''').clauses
        self.assertEqual(tree, exp_tree)
        self.assertSequenceEqual(clauses, exp_clauses)
        
        tree = L.Parser.pe('(a.b.c,)')
        tree, clauses = rewriter.process(tree)
        exp_tree = L.Parser.pe('TUP1FFabc')
        exp_clauses = L.Parser.pe('''{None
            for (Fab, FFabc) in F(c)
            for (TUP1FFabc, FFabc) in TUP()
            }''').clauses
        self.assertEqual(tree, exp_tree)
        self.assertSequenceEqual(clauses, exp_clauses)
    
    def test_replaceablerewriter_subquery(self):
        # Don't rewrite subqueries.
        orig_tree = L.VarsMember(['x'], L.Parser.pe('''
            QUERY('Q1', {p.f for p in S})
            '''))
        tree, _clauses = ReplaceableRewriter.run(orig_tree, *self.namers)
        self.assertEqual(tree, orig_tree)
    
    def test_replaceablerewriter_tuples(self):
        rewriter = ReplaceableRewriter(*self.namers)
        rewriter.rewrite_tuples = False
        tree = L.Parser.pe('(o.f,)')
        tree, _clauses = rewriter.process(tree)
        exp_tree = L.Parser.pe('(Fof,)')
        self.assertEqual(tree, exp_tree)


if __name__ == '__main__':
    unittest.main()
