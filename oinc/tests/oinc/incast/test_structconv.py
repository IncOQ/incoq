"""Unit tests for structconv.py."""


import unittest
import ast
import sys

from oinc.incast.nodes import *
from oinc.incast.structconv import *


# Use a derived class that doesn't rely on external unparsing logic.
class ProgramError(ProgramError):
    @classmethod
    def ts(cls, tree):
        return unparse_structast(tree)


class StructconvCase(unittest.TestCase):
    
    def test_convert(self):
        struct_tree = Module((Pass(),))
        
        # Import.
        tree = ast.parse('pass')
        tree = import_structast(tree)
        self.assertEqual(tree, struct_tree)
        
        # Parse.
        tree = parse_structast('pass')
        self.assertEqual(tree, struct_tree)
        
        # Unparse.
        source = unparse_structast(struct_tree)
        exp_source = 'pass'
        self.assertEqual(source, exp_source)
        
        # Export.
        tree = export_structast(struct_tree)
        self.assertTrue(isinstance(tree, ast.Module) and
                        len(tree.body) == 1 and
                        isinstance(tree.body[0], ast.Pass))
    
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
    
    def test_programerror(self):
        tree = parse_structast('x; pass')
        exc = ProgramError('foo', node=tree.body[0],
                           ast_context=[tree, tree.body[0]])
        s = exc.format_ast_context(exc.ast_context)
        exp_s = trim('''
            AST context (most local node last):
            ==== Module ====
            x
            pass
            ==== Expr ====
            x
            
            ''')
        self.assertEqual(s, exp_s)
        
        try:
            raise exc
        except ProgramError:
            exc_info = sys.exc_info()
        s = ''.join(exc.format_self(*exc_info))
        pat_s = trim('''
            Traceback \(most recent call last\):
              File .*
                raise exc
            .*ProgramError: foo
            
            AST context \(most local node last\):
            ==== Module ====
            x
            pass
            ==== Expr ====
            x
            
            ''')
        self.assertRegex(s, pat_s)
        del exc_info


if __name__ == '__main__':
    unittest.main()
