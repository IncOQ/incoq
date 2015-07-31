"""Unit tests for rewritings.py."""


import unittest

from incoq.mars.incast import P
from incoq.mars.transform.rewritings import *


class ImportPreprocessorCase(unittest.TestCase):
    
    def setUp(self):
        class trip:
            @classmethod
            def p(cls, source, exp_source=None, *, mode=None):
                if exp_source is None:
                    exp_source = source
                tree = P.Parser.p(source, mode=mode)
                tree = ImportPreprocessor.run(tree)
                exp_tree = P.Parser.p(exp_source, mode=mode)
                self.assertEqual(tree, exp_tree)
            @classmethod
            def pc(cls, *args, **kargs):
                return cls.p(*args, mode='code', **kargs)
            @classmethod
            def pe(cls, *args, **kargs):
                return cls.p(*args, mode='expr', **kargs)
        
        self.trip = trip
    
    def test_assignment(self):
        self.trip.pc('a = b')
        self.trip.pc('a, b = c')
        self.trip.pc('a = b = c', 'b = c; a = b')
    
    def test_comparisons(self):
        self.trip.pe('a < b')
        self.trip.pe('a < b < c', 'a < b and b < c')


if __name__ == '__main__':
    unittest.main()
