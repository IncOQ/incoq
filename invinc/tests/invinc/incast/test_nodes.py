"""Unit tests for nodes.py."""


import unittest
import ast
import iast

from invinc.compiler.incast.nodes import *
from invinc.compiler.incast.nodes import incast_nodes_untyped


class Nodes(unittest.TestCase):
    
    def test_typed_nodes(self):
        Name('a', Load())
        BinOp(NameConstant(True), Add(), NameConstant(True, None))
    
    def test_type_adder(self):
        node = incast_nodes_untyped['Name']('x', Load())
        node = TypeAdder.run(node)
        exp_node = Name('x', Load())
        self.assertEqual(node, exp_node)


if __name__ == '__main__':
    unittest.main()
