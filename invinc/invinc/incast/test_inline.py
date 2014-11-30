"""Unit tests for inline.py."""


import unittest

from .inline import *
from .structconv import parse_structast
from .nodeconv import IncLangImporter


class InlineCase(unittest.TestCase):
    
    def p(self, source, subst=None, mode=None):
        return IncLangImporter.run(
                    parse_structast(source, mode=mode, subst=subst))
    
    def pc(self, source, **kargs):
        return self.p(source, mode='code', **kargs)
    
    def ps(self, source, **kargs):
        return self.p(source, mode='stmt', **kargs)
    
    def pe(self, source, **kargs):
        return self.p(source, mode='expr', **kargs)
    
    def test_finder(self):
        code = self.pc('''
            def f(x):
                g(x)
            def g(y):
                print(h(y))
            def h(z):
                return w
            def m(k=1):
                pass
            f(a)
            ''')
        
        funcs = PlainFunctionFinder.run(code, stmt_only=False)
        exp_funcs = ['f', 'g', 'h']
        self.assertSequenceEqual(funcs, exp_funcs)
        
        funcs = PlainFunctionFinder.run(code, stmt_only=True)
        exp_funcs = ['f', 'g']
        self.assertSequenceEqual(funcs, exp_funcs)
        
        code = self.pc('''
            def f(x):
                f(x)
            def f(y):
                f(y)
            ''')
        with self.assertRaises(AssertionError):
            PlainFunctionFinder.run(code, stmt_only=False)
    
    def test_infogetter(self):
        code = self.pc('''
            def f(x):
                g(x)
            def g(y):
                print(h(y))
            def h(z):
                return w
            def m(k=1):
                pass
            f(a)
            ''')
        
        param_map, body_map, edges, order = FunctionInfoGetter.run(
                        code, ['f', 'g', 'h'], require_nonrecursive=True)
        exp_param_map = {'f': ('x',),
                         'g': ('y',),
                         'h': ('z',)}
        exp_body_map = {'f': self.pc('g(x)'),
                        'g': self.pc('print(h(y))'),
                        'h': self.pc('return w')}
        exp_edges = {('f', 'g'), ('g', 'h')}
        exp_order = ['h', 'g', 'f']
        self.assertEqual(param_map, exp_param_map)
        self.assertEqual(body_map, exp_body_map)
        self.assertEqual(edges, exp_edges)
        self.assertEqual(order, exp_order)
        
        code = self.pc('''
            def f(x):
                g(x)
            def g(x):
                f(x)
            ''')
        with self.assertRaises(AssertionError):
            FunctionInfoGetter.run(code, ['f', 'g'],
                                   require_nonrecursive=True)
    
    def test_callinliner(self):
        code = self.pc('''
            f(a)
            print(f(a))
            ''')
        param_map = {'f': ('x',)}
        body_map = {'f': self.pc('foo(x, y)')}
        code = CallInliner.run(code, param_map, body_map)
        exp_code = self.pc('''
            foo(a, y)
            print(f(a))
            ''')
        self.assertEqual(code, exp_code)
    
    def test_inline(self):
        code = self.p('''
            def f(x):
                g(x)
            def g(y):
                print(h(y))
            def h(z):
                return w
            f(a)
            g(b)
            ''')
        code = inline_functions(code, {'f', 'g'})
        exp_code = self.p('''
            def h(z):
                return w
            print(h(a))
            print(h(b))
            ''')
        self.assertEqual(code, exp_code)


if __name__ == '__main__':
    unittest.main()
