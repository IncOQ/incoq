"""Unit tests for the builtins module."""


import unittest
import pickle

from incoq.mars.runtime.builtins import *


class BuiltinsCase(unittest.TestCase):
    
    def test_noops(self):
        OPTIONS(1, 2, a=3)
        INFO(1, a=2, b=3)
    
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
    
    def test_rcset_repr(self):
        r = repr(RCSet())
        exp_r = 'RCSet({})'
        self.assertEqual(r, exp_r)
        
        r = repr(RCSet({5}))
        exp_r = 'RCSet({5: 1})'
        self.assertEqual(r, exp_r)
        
        s = str(RCSet({5, 6}))
        exp_s = '{5, 6}'
        self.assertEqual(s, exp_s)
    
    def test_rcset_updates(self):
        s = RCSet({'a': 1, 'b': 2})
        
        # incref, decref, getref.
        s.incref('a')
        s.decref('b')
        self.assertCountEqual(dict(s), {'a': 2, 'b': 1})
        self.assertEqual(s.getref('a'), 2)
        
        # add, remove.
        s.add('c')
        self.assertCountEqual(dict(s), {'a': 2, 'b': 1, 'c': 1})
        s.remove('c')
        self.assertCountEqual(dict(s), {'a': 2, 'b': 1})
        
        # clear, update.
        s.clear()
        self.assertCountEqual(dict(s), {})
        s.add('a')
        s.update({'a': 2})
        self.assertCountEqual(dict(s), {'a': 3})
        
        # Strictness.
        with self.assertRaises(AssertionError):
            s.add('a')
        with self.assertRaises(AssertionError):
            s.remove('b')
        # Remove at refcount 1 only.
        with self.assertRaises(AssertionError):
            s.remove('a')
    
    def test_rcset_pickle(self):
        s1 = RCSet({1, 2, 3})
        b = pickle.dumps(s1)
        s2 = pickle.loads(b)
        self.assertEqual(dict(s1), dict(s2))
    
    def test_rcset_imgset(self):
        # Throw in some reference counts for the heck of it.
        # No effect on result.
        s = RCSet({(1, 2): 3, (1, 3): 2, (2, 3) : 2, (2, 4) :1})
        img = s.imgset('bu', (1,))
        exp_img = {(2,), (3,)}
        self.assertCountEqual(img, exp_img)
    
    def test_map_repr(self):
        r = repr(Map())
        exp_r = 'Map({})'
        self.assertEqual(r, exp_r)
        
        r = repr(Map({'a': 1}))
        exp_r = "Map({'a': 1})"
        self.assertEqual(r, exp_r)
        
        s = str(Map({'a': 1}))
        exp_s = '{a: 1}'
        self.assertEqual(s, exp_s)
    
    def test_map_pickle(self):
        m1 = Map({'a': 1, 'b': 2})
        b = pickle.dumps(m1)
        m2 = pickle.loads(b)
        self.assertEqual(dict(m1), dict(m2))


if __name__ == '__main__':
    unittest.main()