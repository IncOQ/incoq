"""Unit tests for tree.py."""


import unittest

from incoq.runtime.tree import *


class TreeCase(unittest.TestCase):
    
    def test_tree(self):
        t = Tree()
        t[1] = None
        t[2] = None
        t[3] = None
        self.assertEqual(t.__min__(), 1)
        self.assertEqual(t.__max__(), 3)
        self.assertEqual(len(t), 3)
        
        t = Tree()
        self.assertIsNone(t.__min__())
        self.assertIsNone(t.__max__())
        self.assertEqual(len(t), 0)


if __name__ == '__main__':
    unittest.main()
