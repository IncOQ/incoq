"""Unit tests for util.py."""

import unittest

from incoq.mars.incast import nodes as L
from incoq.mars.incast.util import *
from incoq.mars.incast.pyconv import Parser


class MaskCase(unittest.TestCase):
    
    def test_tuplify(self):
        tree = tuplify(['x', 'y'])
        exp_tree = L.Tuple([L.Name('x'), L.Name('y')])
        self.assertEqual(tree, exp_tree)
    
    def test_detuplify(self):
        tree = L.Tuple([L.Name('x'), L.Name('y')])
        vars = detuplify(tree)
        exp_vars = ['x', 'y']
        self.assertSequenceEqual(vars, exp_vars)
        
        with self.assertRaises(ValueError):
            detuplify(L.Name('x'))
        with self.assertRaises(ValueError):
            detuplify(L.Tuple([L.Tuple([L.Name('x')])]))
    
    def test_from_bounds(self):
        mask = mask_from_bounds(['x', 'y', 'z'], ['x', 'z'])
        exp_mask = L.mask('bub')
        self.assertEqual(mask, exp_mask)
    
    def test_split(self):
        mask = L.mask('bub')
        bounds, unbounds = split_by_mask(mask, ['x', 'y', 'z'])
        exp_bounds = ['x', 'z']
        exp_unbounds = ['y']
        self.assertEqual(bounds, exp_bounds)
        self.assertEqual(unbounds, exp_unbounds)
    
    def test_bind_by_mask(self):
        mask = L.mask('bubu')
        code = bind_by_mask(mask, ['w', 'x', 'y', 'z'], L.Name('e'))
        exp_code = Parser.pc('''
            _, x, _, z = e
            ''')
        self.assertEqual(code, exp_code)


class MiscCase(unittest.TestCase):
    
    def test_uncounted_set_rel_update(self):
        # Set update.
        code = set_update(L.Name('S'), L.SetAdd(), L.Name('x'),
                          counted=False)
        exp_code = Parser.pc('S.add(x)')
        self.assertEqual(code, exp_code)
        code = set_update(L.Name('S'), L.SetRemove(), L.Name('x'),
                          counted=False)
        exp_code = Parser.pc('S.remove(x)')
        self.assertEqual(code, exp_code)
        
        # Rel update.
        code = rel_update('S', L.SetAdd(), 'x',
                          counted=False)
        exp_code = Parser.pc('S.reladd(x)')
        self.assertEqual(code, exp_code)
        code = rel_update('S', L.SetRemove(), 'x',
                          counted=False)
        exp_code = Parser.pc('S.relremove(x)')
        self.assertEqual(code, exp_code)
    
    def test_counted_set_rel_update(self):
        # Set update.
        code = set_update(L.Name('S'), L.SetAdd(), L.Name('x'),
                          counted=True)
        exp_code = Parser.pc('''
            if x not in S:
                S.add(x)
            else:
                S.inccount(x)
            ''')
        self.assertEqual(code, exp_code)
        code = set_update(L.Name('S'), L.SetRemove(), L.Name('x'),
                          counted=True)
        exp_code = Parser.pc('''
            if S.getcount(x) == 1:
                S.remove(x)
            else:
                S.deccount(x)
            ''')
        self.assertEqual(code, exp_code)
        
        # Rel update.
        code = rel_update('S', L.SetAdd(), 'x',
                          counted=True)
        exp_code = Parser.pc('''
            if x not in S:
                S.reladd(x)
            else:
                S.relinccount(x)
            ''')
        self.assertEqual(code, exp_code)
        code = rel_update('S', L.SetRemove(), 'x',
                          counted=True)
        exp_code = Parser.pc('''
            if S.getcount(x) == 1:
                S.relremove(x)
            else:
                S.reldeccount(x)
            ''')
        self.assertEqual(code, exp_code)
    
    def test_insert_rel_maint(self):
        update_code = Parser.pc('R.reladd(x)')
        maint_code = Parser.pc('pass')
        code = insert_rel_maint(update_code, maint_code, L.SetAdd())
        exp_code = Parser.pc('''
            R.reladd(x)
            pass
            ''')
        self.assertEqual(code, exp_code)
        
        update_code = Parser.pc('R.relremove(x)')
        maint_code = Parser.pc('pass')
        code = insert_rel_maint(update_code, maint_code, L.SetRemove())
        exp_code = Parser.pc('''
            pass
            R.relremove(x)
            ''')
        self.assertEqual(code, exp_code)
    
    def test_set_update_name(self):
        self.assertEqual(set_update_name(L.SetAdd()), 'add')
        self.assertEqual(set_update_name(L.SetRemove()), 'remove')
        self.assertEqual(set_update_name(L.IncCount()), 'inccount')
        self.assertEqual(set_update_name(L.DecCount()), 'deccount')
