"""Unit tests for error.py."""


import unittest
import sys

from incoq.compiler.incast.structconv import *
from incoq.compiler.incast.error import *


# Use a derived class that doesn't rely on external unparsing logic.
class ProgramError(ProgramError):
    @classmethod
    def ts(cls, tree):
        return unparse_structast(tree)


class StructconvCase(unittest.TestCase):
    
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
