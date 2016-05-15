"""Unit tests for functions.py."""

import unittest
from itertools import repeat

from incoq.util.collections import OrderedSet

from incoq.mars.incast import nodes as L
from incoq.mars.incast.functions import *
from incoq.mars.incast.pyconv import Parser


class FunctionsCase(unittest.TestCase):
    
    def test_prefix_locals(self):
        tree = Parser.p('''
            def a():
                b = c
                for d in S:
                    print(d, e)
            ''')
        tree = prefix_locals(tree, '_', ['e'])
        exp_tree = Parser.p('''
            def a():
                _b = c
                for _d in S:
                    print(_d, _e)
            ''')
        self.assertEqual(tree, exp_tree)
    
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
    
    def test_inliner(self):
        param_map = {'f': ('a', 'b')}
        body_map = {'f': Parser.pc('a = a + 1; print(a + b + x)')}
        tree = Parser.p('''
            def main():
                f(c, d)
                print(f(c, d))
            ''')
        prefixes = repeat('_')
        tree = Inliner.run(tree, param_map, body_map, prefixes,
                           comment_markers=True)
        exp_tree = Parser.p('''
            def main():
                COMMENT('Begin inlined f.')
                (_a, _b) = (c, d)
                _a = _a + 1
                print(_a + _b + x)
                COMMENT('End inlined f.')
                print(f(c, d))
            ''')
        self.assertEqual(tree, exp_tree)
    
    def test_inline_functions(self):
        tree = Parser.p('''
            def a():
                print(1)
                y = 1
                b(y)
            
            def b(y):
                print(2)
                z = 2
                c(y)
                d(z)
            
            def c(u):
                print(3)
                d(u)
            
            def d(w):
                print(4)
            
            def e():
                a()
            ''')
        exp_tree = Parser.p('''
            def e():
                print(1)
                _y = 1
                (__y,) = (_y,)
                print(2)
                __z = 2
                (___u,) = (__y,)
                print(3)
                (____w,) = (___u,)
                print(4)
                (___w,) = (__z,)
                print(4)
            ''')
        prefixes = repeat('_')
        tree = inline_functions(tree, ['a', 'b', 'c', 'd'], prefixes)
        self.assertEqual(tree, exp_tree)


if __name__ == '__main__':
    unittest.main()
