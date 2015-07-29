"""Unit tests for nodes.py."""


import unittest
import ast
import iast

from incoq.compiler.incast.nodes_untyped import *


class NodesCast(unittest.TestCase):
    
    def test_native_namespace(self):
        Pass = native_nodes['Pass']
        self.assertIs(Pass, ast.Pass)
        Comment = native_nodes['Comment']
        self.assertTrue(issubclass(Comment, ast.AST))
    
    def test_incast_namespace(self):
        _Pass = incast_nodes['Pass']
        self.assertTrue(issubclass(_Pass, iast.AST))
        # IncAST nodes are also exported in the module's global namespace.
        self.assertIs(Pass, _Pass)
    
    # TODO: Can have unit tests for nodes with special __new__()
    # methods that do coercion.


if __name__ == '__main__':
    unittest.main()
