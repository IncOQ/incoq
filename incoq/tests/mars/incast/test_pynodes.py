"""Unit tests for pynodes.py."""


import unittest

import incoq.mars.incast.nodes as L
import incoq.mars.incast.pynodes as P


class PynodesCase(unittest.TestCase):
    
    def test_parse(self):
        tree = P.Parser.ps('a = _b', patterns=True)
        exp_tree = P.Assign(targets = (P.Name(id = 'a',
                                              ctx = P.Store()),),
                            value = L.PatVar(id = '_b'))
        self.assertEqual(tree, exp_tree)
    
    def test_unparse(self):
        tree = P.Parser.ps('a = b')
        source = P.Parser.ts(tree)
        exp_source = 'a = b'
        self.assertEqual(source, exp_source)


if __name__ == '__main__':
    unittest.main()
