"""Unit tests for analyze.py."""


import unittest

from incoq.util.misc import new_namespace
from incoq.mars.incast import L
import incoq.mars.cost.costs as costs
import incoq.mars.cost.algebra as algebra
import incoq.mars.cost.analyze as analyze
from incoq.mars.cost.analyze import (
    TrivialCostAnalyzer, SizeAnalyzer, LoopCostAnalyzer)

C = new_namespace(costs, algebra, analyze)


class AnalyzeCase(unittest.TestCase):
    
    def test_trivialcostanalyzer(self):
        # This case isn't very interesting because without loops and
        # function calls we can only produce Unit and Unknown costs.
        tree = L.Parser.pc('''
            if True:
                a = 1 + 1
            ''')
        cost = TrivialCostAnalyzer.run(tree)
        exp_cost = C.Unit()
        self.assertEqual(cost, exp_cost)
    
    def test_sizeanalyzer(self):
        expr = L.Parser.pe('1 + 1')
        cost = SizeAnalyzer.run(expr)
        exp_cost = C.Unit()
        self.assertEqual(cost, exp_cost)
        
        expr = L.Parser.pe('S if b else T')
        cost = SizeAnalyzer.run(expr)
        exp_cost = C.Sum([C.Name('S'), C.Name('T')])
        self.assertEqual(cost, exp_cost)
    
    def test_loopcostanalyzer(self):
        tree = L.Parser.pc('''
            for x in S:
                for y in T:
                    A
            for z in R:
                B
            ''')
        cost = LoopCostAnalyzer.run(tree)
        exp_cost = C.Sum([C.Product([C.Name('S'), C.Name('T')]),
                          C.Name('R')])
        self.assertEqual(cost, exp_cost)
        
        tree = L.Parser.pc('''
            while True:
                for x in R:
                    pass
            ''')
        cost = LoopCostAnalyzer.run(tree)
        exp_cost = C.Product([C.Unknown(), C.Name('R')])
        self.assertEqual(cost, exp_cost)


if __name__ == '__main__':
    unittest.main()
