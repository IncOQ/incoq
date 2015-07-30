"""Unit tests for pynodes.py."""


import unittest

import incoq.mars.incast.nodes as L
import incoq.mars.incast.pynodes as P


class PynodesCase(unittest.TestCase):
    
    def test(self):
        node = P.Parser.p('a = _b', mode='stmt', patterns=True)
        exp_node = P.Assign(targets = (P.Name(id = 'a',
                                              ctx = P.Store()),),
                            value = L.PatVar(id = '_b'))
        self.assertEqual(node, exp_node)


if __name__ == '__main__':
    unittest.main()
