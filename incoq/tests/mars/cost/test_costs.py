"""Unit tests for costs.py."""


import unittest

from incoq.mars.cost.costs import *


class CostCase(unittest.TestCase):
    
    def test_eval_coststr(self):
        cost = eval_coststr('ProductCost([NameCost("A"), UnitCost()])')
        exp_cost = ProductCost([NameCost('A'), UnitCost()])
        self.assertEqual(cost, exp_cost)
    
    def test_costvisitor(self):
        names = []
        
        class Visitor(CostVisitor):
            def visit_NameCost(self, cost):
                names.append(cost.name)
        
        cost = ProductCost([NameCost('A'),
                           SumCost([UnitCost(), NameCost('B')])])
        Visitor.run(cost)
        exp_names = ['A', 'B']
        self.assertSequenceEqual(names, exp_names)
    
    def test_costtransformer(self):
        class Transformer(CostTransformer):
            def visit_NameCost(self, cost):
                return cost._replace(name=cost.name * 2)
        
        cost = ProductCost([NameCost('A'),
                           SumCost([UnitCost(), NameCost('B')])])
        cost = Transformer.run(cost)
        exp_cost = ProductCost([NameCost('AA'),
                                SumCost([UnitCost(), NameCost('BB')])])
        self.assertEqual(cost, exp_cost)
    
    def test_prettyprint(self):
        cost = SumCost((ProductCost((NameCost('a'), NameCost('b'),
                                     NameCost('a'), NameCost('b'),
                                     NameCost('b'), NameCost('c'),
                                     NameCost('a'))),
                        ProductCost((UnknownCost(), UnknownCost(),
                                     UnitCost()))))
        output = PrettyPrinter.run(cost)
        exp_output = '((a^3 * b^3 * c) + (1 * ?^2))'
        self.assertEqual(output, exp_output)


if __name__ == '__main__':
    unittest.main()
