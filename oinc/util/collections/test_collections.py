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


if __name__ == '__main__':
    unittest.main()
