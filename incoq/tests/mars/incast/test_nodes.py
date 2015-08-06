"""Unit tests for nodes.py."""


import unittest

import incoq.mars.incast.nodes as L


class NodesCase(unittest.TestCase):
    
    def test_basic(self):
        # Check basic node construction.
        node = L.Name('foo')
        source = L.dump(node)
        exp_source = "Name(id = 'foo')"
        self.assertEqual(source, exp_source)
        
        with self.assertRaises(TypeError):
            L.Name(123)
    
    def test_patchwork(self):
        L.mask('bu')
        with self.assertRaises(ValueError):
            L.mask('abc')


if __name__ == '__main__':
    unittest.main()
