###############################################################################
# test_runtimelib.py                                                          #
# Author: Jon Brandvein                                                       #
###############################################################################

"""Unit tests for the runtimelib module."""


import unittest
import pickle

from incoq.runtime import *
from incoq.runtime.runtimelib import tupify


class TestRuntimelib(unittest.TestCase):
    
    def test_tupify(self):
        val1 = 1
        val2 = tupify([1])
        self.assertEqual(val1, val2)
        
        val3 = (1, 2)
        val4 = tupify([1, 2])
        self.assertEqual(val3, val4)
    
    def test_setmatch(self):
        rel = {(1, 2), (1, 3), (2, 3), 'foo', (1, 4, 5)}
        
        res1 = setmatch(rel, 'bu', 1)
        exp_res1 = {2, 3}
        self.assertEqual(res1, exp_res1)
        
        res1a = setmatch(rel, 'out', 1)
        self.assertEqual(res1a, exp_res1)
        
        res2 = setmatch(rel, 'bu', 2)
        exp_res2 = {3}
        self.assertEqual(res2, exp_res2)
        
        res3 = setmatch(rel, 'uu', ())
        exp_res3 = {(1, 2), (1, 3), (2, 3)}
        self.assertEqual(res3, exp_res3)
    
    def test_minmax(self):
        self.assertEqual(max2(3, 5, 2), 5)
        self.assertEqual(max2(None, 5, None), 5)
        self.assertEqual(max2(None, None, None), None)
        self.assertEqual(max2(), None)
        self.assertEqual(min2(3, 1, 2), 1)
        self.assertEqual(min2(None, 5, None), 5)
        self.assertEqual(min2(None, None, None), None)
        self.assertEqual(min2(), None)
    
    def test_rcset(self):
        s1 = RCSet()
        s1.add(1)
        s1.incref(1)
        self.assertCountEqual(s1, {1})
        s1.decref(1)
        s1.remove(1)
        
        s2 = RCSet()
        with self.assertRaises(AssertionError):
            s2.incref(1) 
        
        s3 = RCSet()
        s3.add(1)
        s3.incref(1)
        with self.assertRaises(AssertionError):
            s3.remove(1)
    
    def test_pickle(self):
        o1 = Obj()
        o1.a = 'a'
        b = pickle.dumps(o1)
        o2 = pickle.loads(b)
        self.assertEqual(getattr(o1, 'a', None), 'a')
        self.assertEqual(getattr(o2, 'a', None), 'a')
        
        s1 = Set()
        s1.add(1)
        b = pickle.dumps(s1)
        s2 = pickle.loads(b)
        self.assertIn(1, s1)
        self.assertIn(1, s2)
        
        s1 = RCSet()
        s1.add(1)
        s1.add(2)
        s1.incref(2)
        b = pickle.dumps(s1)
        s2 = pickle.loads(b)
        self.assertIn(1, s1)
        self.assertEqual(s1.getref(2), 2)
        self.assertIn(1, s2)
        self.assertEqual(s2.getref(2), 2)
        
        m1 = Map()
        m1[1] = 2
        b = pickle.dumps(m1)
        m2 = pickle.loads(b)
        self.assertEqual(m1.get(1, None), 2)
        self.assertEqual(m2.get(1, None), 2)


if __name__ == '__main__':
    unittest.main()
