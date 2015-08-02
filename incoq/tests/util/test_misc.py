"""Unit tests for misc.py."""


import unittest
from types import SimpleNamespace

from incoq.util.misc import *


class MiscCase(unittest.TestCase):
    
    def test_union_namespace(self):
        ns1 = {'a': 1, '_z': 4}
        ns2 = {'__all__': ['b'], 'b': 2, 'c': 3}
        ns = {'__all__': []}
        flood_namespace(ns, ns1, ns2)
        exp_ns = {'__all__': ['a', 'b'], 'a': 1, 'b': 2}
        self.assertEqual(ns, exp_ns)


if __name__ == '__main__':
    unittest.main()
