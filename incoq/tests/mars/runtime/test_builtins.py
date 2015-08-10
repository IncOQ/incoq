"""Unit tests for the builtins module."""


import unittest
import pickle

from incoq.mars.runtime.builtins import *


class BuiltinsCase(unittest.TestCase):
    
    def test_noops(self):
        OPTIONS(1, 2, a=3)
    
    def test_incoqtype(self):
        value = IncOQType()
        with self.assertRaises(NotImplementedError):
            pickle.dumps(value)
    
    def test_set_identity(self):
        s1 = Set()
        s2 = Set()
        self.assertTrue(s1 == s1)
        self.assertFalse(s1 != s1)
        self.assertFalse(s1 == s2)
        self.assertTrue(s1 != s2)
    
    def test_set_repr(self):
        r = repr(Set())
        exp_r = 'Set({})'
        self.assertEqual(r, exp_r)
        
        r = repr(Set({5}))
        exp_r = 'Set({5})'
        self.assertEqual(r, exp_r)
        
        s = str(Set({5, 6}))
        exp_s = '{5, 6}'
        self.assertEqual(s, exp_s)
    
    def test_set_updates(self):
        # Add/remove.
        s1 = Set()
        s1.add(5)
        s1.add(6)
        s1.remove(5)
        s2 = Set({6})
        self.assertCountEqual(s1, s2)
        
        # Bulk updates.
        s = Set({0})
        s.assign_update({1, 2, 3})
        self.assertCountEqual(s, {1, 2, 3})
        s.update({4, 5})
        self.assertCountEqual(s, {1, 2, 3, 4, 5})
        s.difference_update({1, 2})
        self.assertCountEqual(s, {3, 4, 5})
        s.intersection_update(s, {4, 5, 6})
        self.assertCountEqual(s, {4, 5})
        s.symmetric_difference_update({5, 6})
        self.assertCountEqual(s, {4, 6})
        s.clear()
        self.assertCountEqual(s, set())
        
        # Check edge case.
        s = Set({1, 2})
        s.difference_update(s)
        self.assertCountEqual(s, set())
        s1 = Set({1, 2})
        s2 = Set(s1)
        s1.assign_update(s1)
        self.assertCountEqual(s1, s2)
    
    def test_set_pickle(self):
        s1 = Set({1, 2, 3})
        b = pickle.dumps(s1)
        s2 = pickle.loads(b)
        self.assertEqual(set(s1), set(s2))
    
    def test_set_imgset(self):
        s = Set({(1, 2), (1, 3), (2, 3), (2, 4)})
        img = s.imgset('bu', (1,))
        exp_img = {(2,), (3,)}
        self.assertCountEqual(img, exp_img)
        
        # Degenerate cases.
        s = Set({})
        img = s.imgset('', ())
        exp_img = {}
        self.assertCountEqual(img, exp_img)
        s = Set({()})
        img = s.imgset('', ())
        exp_img = {()}
        self.assertCountEqual(img, exp_img)


if __name__ == '__main__':
    unittest.main()
