"""Unit tests for structconv.py."""


import unittest
import ast
from iast import PatVar

from invinc.compiler.incast.nodes import *
from invinc.compiler.incast.structconv import *


class StructconvCase(unittest.TestCase):
    
    def test_convert(self):
        struct_tree = Module((Return(Num(5)),))
        
        # Import.
        tree = ast.parse('return 5')
        tree = import_structast(tree)
        self.assertEqual(tree, struct_tree)
        
        # Parse.
        tree = parse_structast('return 5')
        self.assertEqual(tree, struct_tree)
        
        # Unparse.
        source = unparse_structast(struct_tree)
        exp_source = 'return 5'
        self.assertEqual(source, exp_source)
        
        # Export.
        tree = export_structast(struct_tree)
        self.assertTrue(isinstance(tree, ast.Module) and
                        len(tree.body) == 1 and
                        isinstance(tree.body[0], ast.Return))
    
    def test_parse(self):
        tree = parse_structast('_X + B', mode='expr',
                               subst={'B': 'b'},
                               patterns=True)
        exp_tree = BinOp(PatVar('_X'), Add(), Name('b', Load()))
        self.assertEqual(tree, exp_tree)
    
    def test_unparse(self):
        tree = parse_structast('pass')
        tree = tree._replace(body=(Comment('test'),) + tree.body)
        source = unparse_structast(tree)
        exp_source = trim('''
            # test
            pass
            ''')
        self.assertEqual(source, exp_source)


if __name__ == '__main__':
    unittest.main()
