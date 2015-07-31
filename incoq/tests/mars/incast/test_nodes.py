"""Unit tests for nodes.py."""


import unittest

import incoq.mars.incast.nodes as L


class NodesCase(unittest.TestCase):
    
    def test_basic(self):
        # Check basic node construction.
        node = L.Name('foo', L.Read())
        source = L.dump(node)
        exp_source = L.trim('''
            Name(id = 'foo',
                 ctx = Read())
            ''')
        self.assertEqual(source, exp_source)
        
        with self.assertRaises(TypeError):
            L.Name(123, L.Read())


if __name__ == '__main__':
    unittest.main()
