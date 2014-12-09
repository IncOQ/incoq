"""Unit tests for flatten.py."""


import unittest

import oinc.incast as L

from .flatten import *
from .flatten import (tuptree_to_type, tuptype_leaves, make_flattup_code,
                      UpdateFlattener, get_clause_vars, ClauseFlattener,
                      ReltypeGetter)


class FlattenCase(unittest.TestCase):
    
    def setUp(self):
        super().setUp()
        self.tuptype = ('<T>', 'a', ('<T>', 'b', 'c'))
        self.namegen = L.NameGenerator('v{}')
    
    def test_tuptree_type(self):
        tree = L.pe('(x, (y, z))')
        tuptype = tuptree_to_type(tree)
        exp_tuptype = ('<T>', 'x', ('<T>', 'y', 'z'))
        self.assertEqual(tuptype, exp_tuptype)
    
    def test_leaves(self):
        leaves = tuptype_leaves(self.tuptype)
        exp_leaves = [(0,), (1, 0), (1, 1)]
        self.assertEqual(leaves, exp_leaves)
    
    def test_flattup_code(self):
        in_node = L.ln('x')
        out_node = L.sn('y')
        code = make_flattup_code(self.tuptype, in_node, out_node, 't')
        exp_code = L.pc('''
            y = (x[0], x[1][0], x[1][1])
            ''')
        self.assertEqual(code, exp_code)
        
        in_node = L.pe('x.a')
        code = make_flattup_code(self.tuptype, in_node, out_node, 't')
        exp_code = L.pc('''
            t = x.a
            y = (t[0], t[1][0], t[1][1])
            ''')
        self.assertEqual(code, exp_code)
    
    def test_updateflattener(self):
        tree = L.p('''
            R.add((1, (2, 3)))
            ''')
        tree = UpdateFlattener.run(tree, 'R', self.tuptype, self.namegen)
        exp_tree = L.p('''
            _tv1 = (1, (2, 3))
            _ftv1 = (_tv1[0], _tv1[1][0], _tv1[1][1])
            R.add(_ftv1)
            ''')
        self.assertEqual(tree, exp_tree)
    
    def test_getclausevars(self):
        lhs = L.Tuple((L.sn('x'), L.Tuple((L.sn('y'), L.sn('z')), L.Store())),
                       L.Store())
        vars = get_clause_vars(L.Enumerator(lhs, L.ln('R')), self.tuptype)
        exp_vars = ['x', 'y', 'z']
        self.assertEqual(vars, exp_vars)
    
    def test_clauseflattener(self):
        code = L.pc('''
            COMP({x for x in S for (x, (y, z)) in R}, [], {})
            ''')
        code = ClauseFlattener.run(code, 'R', self.tuptype)
        exp_code = L.pc('''
            COMP({x for x in S for (x, y, z) in R}, [], {})
            ''')
        self.assertEqual(code, exp_code)
    
    def test_reltypegetter(self):
        tree = L.pc('''
            print(COMP({x for x in S for (x, (y, z)) in R}, [], {}))
            ''')
        tuptype = ReltypeGetter.run(tree, 'R')
        exp_tuptype = ('<T>', 'x', ('<T>', 'y', 'z'))
        self.assertEqual(tuptype, exp_tuptype)
        
        tree = L.pc('''
            print(COMP({x for x in R for (x, (y, z)) in R}, [], {}))
            ''')
        with self.assertRaises(AssertionError):
            ReltypeGetter.run(tree, 'R')
    
    def test_flatten(self):
        namegen = L.NameGenerator('v{}')
        code = L.p('''
            R.add((1, (2, 3)))
            print(COMP({x for x in S for (x, (y, z)) in R}, [], {}))
            ''')
        code = flatten_relations(code, ['R'], namegen)
        exp_code = L.p('''
            _tv1 = (1, (2, 3))
            _ftv1 = (_tv1[0], _tv1[1][0], _tv1[1][1])
            R.add(_ftv1)
            print(COMP({x for x in S for (x, y, z) in R}, [], {}))
            ''')
        self.assertEqual(code, exp_code)


if __name__ == '__main__':
    unittest.main()

