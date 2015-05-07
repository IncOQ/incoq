"""Unit tests for helpers.py."""


import unittest

from incoq.compiler.incast.nodes import *
from incoq.compiler.incast.structconv import parse_structast
from incoq.compiler.incast.helpers import *


class HelpersCase(unittest.TestCase):
    
    def p(self, source, mode=None, **kargs):
        return parse_structast(source, mode=mode, **kargs)
    
    def pc(self, source, **kargs):
        return self.p(source, mode='code', **kargs)
    
    def ps(self, source, **kargs):
        return self.p(source, mode='stmt', **kargs)
    
    def pe(self, source, **kargs):
        return self.p(source, mode='expr', **kargs)
    
    def test_ln(self):
        node = ln('foo')
        exp_node = Name('foo', Load())
        self.assertEqual(node, exp_node)
    
    def test_tuplify(self):
        tree = tuplify(['foo', 'bar', Num(n=0)])
        exp_tree = self.pe('(foo, bar, 0)')
        self.assertEqual(tree, exp_tree)
        
        tree = tuplify(['foo'])
        exp_tree = ln('foo')
        self.assertEqual(tree, exp_tree)
        
        tree = tuplify([])
        exp_tree = Tuple((), Load())
        self.assertEqual(tree, exp_tree)
        
        tree = tuplify(['foo', 'bar', Num(n=0)], lval=True)
        exp_tree = self.p('(foo, bar, 0)', mode='lval')
        self.assertEqual(tree, exp_tree)
        
        tree = tuplify([], lval=True)
        exp_tree = sn('_')
        self.assertEqual(tree, exp_tree)
    
    def test_cmp(self):
        tree = self.pe('a in b')
        exp_tree = cmpin(ln('a'), ln('b'))
        self.assertEqual(tree, exp_tree)
    
    def test_plainfunc(self):
        func = self.ps('def foo(x): pass')
        self.assertTrue(is_plainfuncdef(func))
        
        func2 = plainfuncdef('foo', ['x'], self.pc('pass'))[0]
        self.assertEqual(func, func2)
        
        res = get_plainfuncdef(func2)
        self.assertEqual(res, ('foo', ('x',), self.pc('pass')))
        
        func = self.ps('def foo(x:y): pass')
        self.assertFalse(is_plainfuncdef(func))
    
    def test_varassign(self):
        tree = self.p('a = b + c', mode='stmt')
        id, val = get_varassign(tree)
        self.assertEqual(id, 'a')
        self.assertEqual(val, self.pe('b + c'))
        
        # Try failure.
        tree = self.p('a + b', mode='stmt')
        with self.assertRaises(TypeError):
            get_varassign(tree)
        self.assertFalse(is_varassign(tree))
    
    def test_vartuple(self):
        tree = self.pe('(a, b)')
        res = get_vartuple(tree)
        self.assertEqual(res, ('a', 'b'))
        
        tree = self.pe('a')
        res = get_vartuple(tree)
        self.assertEqual(res, ('a',))
    
    def test_is(self):
        self.assertTrue(is_vartuple(self.pe('(a, b)')))
        self.assertFalse(is_vartuple(self.pe('(a + b, c)')))
    
    def test_name(self):
        tree = self.pe('a')
        res = get_name(tree)
        self.assertEqual(res, 'a')
    
    def test_pat_cmp(self):
        tree = self.pe('a < b')
        left, op, right = get_cmp(tree)
        self.assertEqual(left, self.pe('a'))
        self.assertIsInstance(op, Lt)
        self.assertEqual(right, self.pe('b'))
    
    def test_vareqcmp(self):
        tree = self.pe('a == b == c')
        vars = get_vareqcmp(tree)
        self.assertEqual(vars, ('a', 'b', 'c'))
    
    def test_singletonset(self):
        tree = self.pe('{1}')
        res = get_singletonset(tree)
        self.assertEqual(res, self.pe('1'))
    
    def test_singadd(self):
        tree = self.pe('R + {e}')
        left, right = get_singadd(tree)
        self.assertEqual(left, self.pe('R'))
        self.assertEqual(right, self.pe('e'))
    
    def test_singsub(self):
        tree = self.pe('R - {e}')
        left, right = get_singsub(tree)
        self.assertEqual(left, self.pe('R'))
        self.assertEqual(right, self.pe('e'))
    
    def test_namematch(self):
        tree = SetMatch(self.pe('R'), 'bu', self.pe('a'))
        id, mask, key = get_namematch(tree)
        self.assertEqual(id, 'R')
        self.assertEqual(mask, 'bu')
        self.assertEqual(key, self.pe('a'))
    
    def test_namesmlookup(self):
        tree = SMLookup(self.pe('R'), 'bu', self.pe('a'), None)
        id, mask, key = get_namesmlookup(tree)
        self.assertEqual(id, 'R')
        self.assertEqual(mask, 'bu')
        self.assertEqual(key, self.pe('a'))
    
    def test_attrassign(self):
        tree = self.ps('a.b.c = 5')
        rec, attr, val = get_attrassign(tree)
        self.assertEqual(rec, self.pe('a.b'))
        self.assertEqual(attr, 'c')
        self.assertEqual(val, self.pe('5'))
    
    def test_delattr(self):
        tree = self.ps('del a.b.c')
        rec, attr = get_delattr(tree)
        self.assertEqual(rec, self.pe('a.b'))
        self.assertEqual(attr, 'c')
    
    def test_mapassign(self):
        tree = self.ps('a[b.c] = 5')
        map, key, val = get_mapassign(tree)
        self.assertEqual(map, self.pe('a'))
        self.assertEqual(key, self.pe('b.c'))
        self.assertEqual(val, self.pe('5'))
        
        tree = self.ps('globals()[a] = 5')
        self.assertFalse(is_mapassign(tree))
    
    def test_delmap(self):
        tree = self.ps('del a[b.c]')
        map, key = get_delmap(tree)
        self.assertEqual(map, self.pe('a'))
        self.assertEqual(key, self.pe('b.c'))
        
        tree = self.ps('del globals()[a]')
        self.assertFalse(is_delmap(tree))
    
    def test_importstar(self):
        tree = self.ps('from foo import *')
        mod = get_importstar(tree)
        self.assertEqual(mod, 'foo')
    
    def test_setunion(self):
        comp = Comp(Name('b', Load()),
                    (Enumerator(Name('b', Store()),
                                Name('S', Load())),),
                    (), {})
        tree = self.pe('{a} | COMP | S', subst={'COMP': comp})
        parts = get_setunion(tree)
        exp_parts = (self.pe('{a}'), comp, self.pe('S'))
        self.assertEqual(parts, exp_parts)
        
        tree = self.pe('{1} | 2')
        self.assertFalse(is_setunion(tree))
    
    def test_simplecall(self):
        tree = self.pe('f(a, b + c)')
        func, args = get_plaincall(tree)
        self.assertEqual(func, 'f')
        self.assertEqual(args, (self.pe('a'), self.pe('b + c')))


if __name__ == '__main__':
    unittest.main()
