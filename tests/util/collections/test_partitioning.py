###############################################################################
# test_partitioning.py                                                        #
# Author: Jon Brandvein                                                       #
###############################################################################

"""Unit tests for the partitioning module."""


import unittest

from incoq.util.collections.partitioning import *

fs = frozenset


class TestPartitioning(unittest.TestCase):
    
    def test_disjoint(self):
        with self.assertRaises(AssertionError):
            Partitioning([['x', 'y'], ['x', 'z']])
    
    def test_equate(self):
        p = Partitioning()
        p.equate('a', 'a')
        p.equate('a', 'b')
        p.equate('c', 'd')
        p.equate('e', 'f')
        p.equate('f', 'g')
        p.equate('b', 'e')
        
        parts = p.to_sets()
        exp_parts = {fs(['a', 'b', 'e', 'f', 'g']),
                     fs(['c', 'd'])}
        self.assertCountEqual(parts, exp_parts)
        p._check_disjointness()
    
    def test_queries(self):
        p = Partitioning([['a', 'b'], ['c']])
        
        exp_elems = ['a', 'b', 'c']
        exp_subst = {'a': 'a', 'b': 'a', 'c': 'c'}
        
        self.assertEqual(p.find('d'), 'd')
        self.assertEqual(p.elements(), exp_elems)
        self.assertEqual(p.to_subst(), exp_subst)
    
    def test_equivs(self):
        p = Partitioning.from_equivs([['a', 'b'], ['b', 'c'], ['e', 'f']])
        parts = p.to_sets()
        exp_parts = {fs(['a', 'b', 'c']), fs(['e', 'f'])}
        self.assertCountEqual(parts, exp_parts)
    
    def test_singleassignmentdict(self):
        d = SingleAssignmentDict({'a': 1, 'b': 2})
        d['c'] = 3
        with self.assertRaises(AssertionError):
            d['a'] = 4


if __name__ == '__main__':
    unittest.main()
