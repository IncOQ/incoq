"""Unit tests for error.py."""

import unittest
import sys

from incoq.mars.incast.pyconv import Parser
from incoq.mars.incast.error import *


class ErrorCase(unittest.TestCase):
    
    def test_format(self):
        node1 = Parser.pe('a + b')
        node2 = Parser.pc('pass; pass')
        try:
            raise ProgramError('test', node=node1)
        except ProgramError as e:
            lines1 = format_exception(*sys.exc_info())
            lines2 = format_exception(*sys.exc_info(), ast_context=node2)
        exp_lines1 = [
            'incoq.mars.incast.error.ProgramError: test\n',
            'AST context: (a + b)\n',
        ]
        exp_lines2 = [
            'incoq.mars.incast.error.ProgramError: test\n',
            'AST context:\n',
            '    pass\n',
            '    pass\n',
        ]
        self.assertEqual(lines1[-2:], exp_lines1)
        self.assertEqual(lines2[-4:], exp_lines2)


if __name__ == '__main__':
    unittest.main()
