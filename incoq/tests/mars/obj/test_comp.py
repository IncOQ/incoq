"""Unit tests for clause.py."""


import unittest

from incoq.mars.incast import L
from incoq.mars.symbol import N
from incoq.mars.obj.comp import *


class ClauseCase(unittest.TestCase):
    
    def test_replaceablerewriter(self):
        namers = [
            lambda o, f: 'F' + o + f,
            lambda m, k: 'MAP' + m + k,
            lambda elts: 'TUP' + str(len(elts)) + ''.join(elts),
        ]
        rewriter = ReplaceableRewriter(*namers)
        
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


if __name__ == '__main__':
    unittest.main()
