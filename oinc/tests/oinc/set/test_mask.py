"""Unit tests for mask.py."""


import unittest

import oinc.compiler.incast as L
from oinc.compiler.central import CentralCase
from oinc.compiler.set.mask import *


class TestMask(CentralCase):
    
    def test_construct(self):
        mask1 = Mask('bubw12u')
        mask2 = Mask.from_vars(['a', 'b', 'c', '_', 'a', 'b', 'z'],
                               {'a', 'c'})
        self.assertEqual(mask1, mask2)
        
        mask3 = Mask('bbbu')
        mask4 = Mask.from_keylen(3)
        self.assertEqual(mask3, mask4)
        
        with self.assertRaises(ValueError):
            Mask('b0')
        Mask(['b', '1'])
        with self.assertRaises(ValueError):
            Mask(['b', '0'])
        with self.assertRaises(ValueError):
            Mask('1')
        
        self.assertEqual(Mask('bu'), Mask.OUT)
    
    def test_derived(self):
        mask1 = Mask('bu')
        mask2 = Mask('b1')
        mask3 = Mask('uw')
        
        self.assertEqual(mask1.maskstr, 'out')
        
        self.assertTrue(mask2.is_allbound)
        self.assertTrue(mask3.is_allunbound)
        self.assertTrue(mask3.has_wildcards)
        self.assertTrue(mask2.has_equalities)
        self.assertTrue(mask1.is_mixed)
        
        self.assertTrue(mask1.is_keymask)
        self.assertTrue(mask1.is_lookupmask)
        self.assertEqual(mask1.lookup_arity, 1)
        self.assertFalse(mask2.is_keymask)
        self.assertFalse(mask3.is_keymask)
        
        self.assertEqual(len(mask1), 2)
    
    def test_makenode(self):
        node = Mask('bu').make_node()
        exp_node = L.Str('bu')
        self.assertEqual(node, exp_node)
    
    def test_splitvars(self):
        mask = Mask('bubw12u')
        bvs, uvs, eqs = mask.split_vars(['a', 'b', 'c', 'd', 'e', 'f', 'g'])
        self.assertEqual(bvs, ('a', 'c'))
        self.assertEqual(uvs, ('b', 'g'))
        self.assertEqual(eqs, (('a', 'e'), ('b', 'f')))
    
    def test_breakkey(self):
        parts = Mask.breakkey(Mask('bbbu'), L.pe('(1, 2, 3)'))
        exp_parts = (L.pe('1'), L.pe('2'), L.pe('3'))
        self.assertEqual(parts, exp_parts)
        
        parts = Mask.breakkey(Mask('bu'), L.pe('1'))
        exp_parts = (L.pe('1'),)
        self.assertEqual(parts, exp_parts)
    
    def test_make_delta_mask(self):
        mask = Mask('bubw12u')
        mask = mask.make_delta_mask()
        exp_mask = Mask('bbbw12b')
        self.assertEqual(mask, exp_mask)
    
    def test_make_interkey_mask(self):
        mask = Mask('bubw12u')
        mask = mask.make_interkey_mask(['a', 'b'], ['a'])
        exp_mask = Mask('bwuw12w')
        self.assertEqual(mask, exp_mask)


if __name__ == '__main__':
    unittest.main()
