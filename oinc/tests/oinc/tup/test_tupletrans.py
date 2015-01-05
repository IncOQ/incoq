"""Unit tests for tupletrans.py."""


import unittest

import oinc.incast as L
from oinc.tup.tupletrans import *


class TupletransCase(unittest.TestCase):
    
    def test_flatten_tuples_comp(self):
        comp = L.pe('COMP({(a, c) for (a, (b, c)) in R if f((a, (b, c))) '
                                 'for ((a, b), (a, b, c)) in S}, '
                    '[], {})')
        comp, trels = flatten_tuples_comp(comp)
        
        exp_comp = L.pe('''
            COMP({(a, c) for (a, _tup1) in R
                  for (_tup1, b, c) in _TUP2
                  if f((a, (b, c)))
                  for (_tup2, _tup3) in S
                  for (_tup2, a, b) in _TUP2
                  for (_tup3, a, b, c) in _TUP3},
                 [], {})
            ''')
        exp_trels = ['_TUP2', '_TUP3']
        
        self.assertEqual(comp, exp_comp)
        self.assertSequenceEqual(trels, exp_trels)
    
    def test_flatten_tuples(self):
        tree = L.p('''
            print(COMP({(a, c) for (a, (b, c)) in R}, [], {}))
            ''')
        tree = flatten_tuples(tree)
        
        exp_tree = L.p('''
            print(COMP({(a, c) for (a, _tup1) in R
                               for (_tup1, b, c) in _TUP2},
                  [], {}))
            ''')
        
        self.assertEqual(tree, exp_tree)


if __name__ == '__main__':
    unittest.main()

