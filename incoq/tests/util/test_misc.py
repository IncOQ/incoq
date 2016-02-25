"""Unit tests for misc.py."""


import unittest

from incoq.util.misc import *
from incoq.util.collections import frozendict


class MiscCase(unittest.TestCase):
    
    def test_union_namespace(self):
        ns1 = {'a': 1, '_z': 4}
        ns2 = {'__all__': ['b'], 'b': 2, 'c': 3}
        ns = {'__all__': []}
        flood_namespace(ns, ns1, ns2)
        exp_ns = {'__all__': ['a', 'b'], 'a': 1, 'b': 2}
        self.assertEqual(ns, exp_ns)
    
    def test_freeze(self):
        v = freeze(True)
        self.assertEqual(v, True)
        
        v = freeze([1, [2, 3]])
        self.assertEqual(v, (1, (2, 3)))
        
        v = freeze({'a': {1, (2, 3)}, 'b': [4, 5]})
        exp_v = frozendict({'a': frozenset({1, (2, 3)}),
                            'b': (4, 5)})
        self.assertEqual(v, exp_v)


if __name__ == '__main__':
    unittest.main()
