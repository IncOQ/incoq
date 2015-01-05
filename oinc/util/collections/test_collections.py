###############################################################################
# test_collections.py                                                         #
# Author: Jon Brandvein                                                       #
###############################################################################

"""Unit tests for the collections module."""


import unittest

from .collections import *


class TestRegistry(unittest.TestCase):
    
    def test_strictness(self):
        d = Registry()
        d[1] = 2
        
        with self.assertRaises(KeyError):
            d[1] = 3
        with self.assertRaises(KeyError):
            del d[2]
        with self.assertRaises(KeyError):
            d.update({1:2, 2:2})
        
        del d[1]


class TestSetRegistry(unittest.TestCase):
    
    class DummyRegistry(SetRegistry):
        
        def elem_key(self, elem):
            return elem[0]
    
    def test_strictness(self):
        s = self.DummyRegistry()
        
        s.add('abc')
        s.add('def')
        s.add('xyz')
        s.remove('def')
        
        with self.assertRaises(KeyError):
            s.add('xzx')
        
        s.clear()
        s.add('abc')
        s.discard('123')
        self.assertFalse('456' in s)
    
    def testFrozendict(self):
        d = frozendict({1:2, 3:4})
        with self.assertRaises(TypeError):
            d[3] = 5
        hash(d)
    
    def testFreeze(self):
        val = make_frozen([{1: 2}, {3}])
        exp_val = (frozendict({1: 2}), frozenset({3}))
        self.assertEqual(val, exp_val)


if __name__ == '__main__':
    unittest.main()
