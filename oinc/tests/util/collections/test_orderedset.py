###############################################################################
# test_orderedset.py                                                          #
# Author: Jon Brandvein                                                       #
###############################################################################

"""Unit tests for the orderedset module."""


import unittest

from oinc.util.collections.orderedset import *


class TestOrderedSet(unittest.TestCase):
    
    def test_update(self):
        s = OrderedSet('abc')
        s.update('def')
        self.assertEqual(s, 'abcdef')
        
        s.update_union(['ghi', 'jkl'])
        self.assertEqual(s, 'abcdefghijkl')
        
        s2 = OrderedSet.from_union(['abc', 'def', 'ghi', 'jkl'])
        self.assertEqual(s, s2)
    
    def test_reverse_operator(self):
        s = set('abc')
        t = OrderedSet('def')
        
        r = s | t
        self.assertCountEqual(r, 'abcdef')
    
    def test_and(self):
        # Tests the fix for ensuring the order of a & b is taken from
        # a rather than b.
        a = OrderedSet('abcdefghij')
        b = 'jceibhdafg'
        
        r = a & b
        
        self.assertEqual(''.join(r), 'abcdefghij')


if __name__ == '__main__':
    unittest.main()
