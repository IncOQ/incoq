"""Unit tests for rewritings.py."""


import unittest

from incoq.mars.incast import P
from incoq.mars.transform.rewritings import *


class ImportPreprocessorCase(unittest.TestCase):
    
    def setUp(self):
        class check(P.ExtractMixin):
            """Check that the input code matches the expected
            output code.
            """
            @classmethod
            def action(cls, source, exp_source=None, *, mode=None):
                if exp_source is None:
                    exp_source = source
                tree = P.Parser.action(source, mode=mode)
                tree = ImportPreprocessor.run(tree)
                exp_tree = P.Parser.action(exp_source, mode=mode)
                self.assertEqual(tree, exp_tree)
        
        self.check = check
    
    def test_assignment(self):
        self.check.pc('a = b')
        self.check.pc('a, b = c')
        self.check.pc('a = b = c', 'b = c; a = b')
    
    def test_comparisons(self):
        self.check.pe('a < b')
        self.check.pe('a < b < c', 'a < b and b < c')


if __name__ == '__main__':
    unittest.main()
