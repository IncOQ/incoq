"""Unit tests for functions.py."""

import unittest

from incoq.util.collections import OrderedSet

from incoq.mars.incast import nodes as L
from incoq.mars.incast.functions import *
from incoq.mars.incast.pyconv import Parser


class FunctionsCase(unittest.TestCase):
    
    def test_analyze_functions(self):
        tree = Parser.p('''
            def a():
                print(b(y))
            
            def b(y):
                c(d(y))
                return 0
            
            def c(u):
                d(v)
            
            def d(w):
                pass
            
            def e():
                pass
            ''')
        graph = analyze_functions(tree, ['a', 'b', 'c', 'd'])
        
        exp_param_map = {
            'a': (),
            'b': ('y',),
            'c': ('u',),
            'd': ('w',),
        }
        exp_body_map = {
            'a': Parser.pc('print(b(y))'),
            'b': Parser.pc('c(d(y)); return 0'),
            'c': Parser.pc('d(v)'),
            'd': Parser.pc('pass'),
        }
        exp_calls_map = {
            'a': OrderedSet(['b']),
            'b': OrderedSet(['d', 'c']),
            'c': OrderedSet(['d']),
            'd': OrderedSet([]),
            }
        exp_calledby_map = {
            'a': OrderedSet([]),
            'b': OrderedSet(['a']),
            'c': OrderedSet(['b']),
            'd': OrderedSet(['b', 'c']),
            }
        exp_order = ['d', 'c', 'b', 'a']
        self.assertEqual(graph.param_map, exp_param_map)
        self.assertEqual(graph.body_map, exp_body_map)
        self.assertEqual(graph.calls_map, exp_calls_map)
        self.assertEqual(graph.calledby_map, exp_calledby_map)
        self.assertEqual(graph.order, exp_order)


if __name__ == '__main__':
    unittest.main()
