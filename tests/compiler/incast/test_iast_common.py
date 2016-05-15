"""Unit tests for iast_common.py."""


import unittest

from incoq.compiler.incast.iast_common import *


class IASTCommonCase(unittest.TestCase):
    
    def test_extractmixin(self):
        class A(ExtractMixin):
            @classmethod
            def action(cls, s, *, mode=None):
                return s + ' ' + str(mode)
        
        self.assertEqual(A.ps('a'), 'a stmt')


if __name__ == '__main__':
    unittest.main()
