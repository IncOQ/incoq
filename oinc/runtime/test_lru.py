"""Unit tests for the lru module."""


import unittest

from .lru import *


class TestLRU(unittest.TestCase):
    
    def test_lru(self):
        s = LRUTracker()
        s.add(1)
        s.add(2)
        s.add(3)
        self.assertEqual(s.peek(), 1)
        s.remove(1)
        self.assertEqual(s.peek(), 2)
        v = s.pop()
        self.assertEqual(v, 2)
        s.add(4)
        s.ping(3)
        self.assertEqual(s.peek(), 4)


if __name__ == '__main__':
    unittest.main()
