"""Unit tests for topsort.py."""


import unittest

from .topsort import *


class TopsortCase(unittest.TestCase):
    
    def test_topsort(self):
        V = [1, 2, 3, 4, 5]
        E = [(1, 2), (1, 3), (2, 3), (3, 4), (4, 5), (3, 5), (1, 5)]
        order = topsort(V, E)
        exp_order = [1, 2, 3, 4, 5]
        self.assertEqual(order, exp_order)
        
        V = [1, 2, 3, 4, 5]
        E = [(1, 2), (2, 3), (3, 1), (4, 5)]
        order = topsort(V, E)
        self.assertEqual(order, None)
        cycle = get_cycle(V, E)
        self.assertCountEqual(cycle, {1, 2, 3})


if __name__ == '__main__':
    unittest.main()
