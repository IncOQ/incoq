"""Unit tests for order.py."""


import unittest

from incoq.compiler.incast import L
from incoq.compiler.comp.clause import CoreClauseVisitor
from incoq.compiler.comp.order import *


class OrderCase(unittest.TestCase):
    
    def setUp(self):
        self.ct = CoreClauseVisitor()
    
    def test_order_clauses(self):
        comp = L.Parser.pe('''{None for (a, b) in REL(R) for (a, c) in REL(R)
                                    for (c,) in SING(e) if c > 5}''')
        clauses = comp.clauses
        exp_clauses = [clauses[i] for i in [2, 3, 1, 0]]
        clauses = order_clauses(self.ct, clauses)
        self.assertEqual(clauses, exp_clauses)


if __name__ == '__main__':
    unittest.main()
