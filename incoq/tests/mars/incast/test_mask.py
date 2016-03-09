"""Unit tests for mask.py."""

import unittest

from incoq.mars.incast import nodes as L
from incoq.mars.incast.mask import *
from incoq.mars.incast.pyconv import Parser


class MaskCase(unittest.TestCase):
    
    def test_is_tuple_of_names(self):
        tree = L.Tuple([L.Name('x'), L.Name('y')])
        self.assertTrue(is_tuple_of_names(tree))
        
        tree = L.Name('x')
        self.assertFalse(is_tuple_of_names(tree))
        tree = L.Tuple([L.Tuple([L.Name('x')])])
        self.assertFalse(is_tuple_of_names(tree))
    
    def test_tuplify(self):
        tree = tuplify(['x', 'y'])
        exp_tree = L.Tuple([L.Name('x'), L.Name('y')])
        self.assertEqual(tree, exp_tree)
        
        tree = tuplify(['x'], unwrap=True)
        exp_tree = L.Name('x')
        self.assertEqual(tree, exp_tree)
        
        with self.assertRaises(AssertionError):
            tuplify(['x', 'y'], unwrap=True)
    
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
    
    def test_keymask(self):
        mask = keymask_from_len(2, 3)
        exp_mask = L.mask('bbuuu')
        self.assertEqual(mask, exp_mask)
        
        self.assertTrue(is_keymask(mask))
        self.assertFalse(is_keymask(L.mask('bub')))
        
        result = break_keymask(mask)
        self.assertEqual(result, (2, 3))
        with self.assertRaises(ValueError):
            break_keymask(L.mask('bub'))
    
    def test_mapmask(self):
        mask = mapmask_from_len(2)
        exp_mask = L.mask('bbu')
        self.assertEqual(mask, exp_mask)
        
        self.assertTrue(is_mapmask(mask))
        self.assertFalse(is_mapmask(L.mask('bub')))
        self.assertFalse(is_mapmask(L.mask('buu')))
        
        result = break_mapmask(mask)
        self.assertEqual(result, 2)
        with self.assertRaises(ValueError):
            break_mapmask(L.mask('bub'))
    
    def test_allboundunbound(self):
        mask1 = L.mask('bub')
        mask2 = L.mask('bb')
        mask3 = L.mask('uu')
        
        self.assertFalse(mask_is_allbound(mask1))
        self.assertTrue(mask_is_allbound(mask2))
        self.assertFalse(mask_is_allbound(mask3))
        
        self.assertFalse(mask_is_allunbound(mask1))
        self.assertFalse(mask_is_allunbound(mask2))
        self.assertTrue(mask_is_allunbound(mask3))
    
    def test_split_by_mask(self):
        mask = L.mask('bub')
        bounds, unbounds = split_by_mask(mask, ['x', 'y', 'z'])
        exp_bounds = ['x', 'z']
        exp_unbounds = ['y']
        self.assertEqual(bounds, exp_bounds)
        self.assertEqual(unbounds, exp_unbounds)
    
    def test_combine_by_mask(self):
        mask = L.mask('bubu')
        bounds = ['a', 'b']
        unbounds = ['c', 'd']
        result = combine_by_mask(mask, bounds, unbounds)
        exp_result = ['a', 'c', 'b', 'd']
        self.assertEqual(result, exp_result)
        
        bounds2, unbounds2 = split_by_mask(mask, result)
        self.assertEqual(bounds2, bounds)
        self.assertEqual(unbounds2, unbounds)
    
    def test_bind_by_mask(self):
        mask = L.mask('bubu')
        code = bind_by_mask(mask, ['w', 'x', 'y', 'z'], L.Name('e'))
        exp_code = Parser.pc('''
            _, x, _, z = e
            ''')
        self.assertEqual(code, exp_code)


if __name__ == '__main__':
    unittest.main()
