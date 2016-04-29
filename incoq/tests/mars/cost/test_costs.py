"""Unit tests for costs.py."""


import unittest

import incoq.mars.cost.costs as C


class CostCase(unittest.TestCase):
    
    def test_eval_coststr(self):
        cost = C.eval_coststr('Product([Name("A"), Unit()])')
        exp_cost = C.Product([C.Name('A'), C.Unit()])
        self.assertEqual(cost, exp_cost)
    
    def test_costvisitor(self):
        names = []
        
        class Visitor(C.CostVisitor):
            def visit_Name(self, cost):
                names.append(cost.name)
        
        cost = C.Product([C.Name('A'), C.Sum([C.Unit(), C.Name('B')])])
        Visitor.run(cost)
        exp_names = ['A', 'B']
        self.assertSequenceEqual(names, exp_names)
    
    def test_costtransformer(self):
        class Transformer(C.CostTransformer):
            def visit_Name(self, cost):
                return cost._replace(name=cost.name * 2)
        
        cost = C.Product([C.Name('A'), C.Sum([C.Unit(), C.Name('B')])])
        cost = Transformer.run(cost)
        exp_cost = C.Product([C.Name('AA'), C.Sum([C.Unit(), C.Name('BB')])])
        self.assertEqual(cost, exp_cost)
    
    def test_prettyprint(self):
        cost = C.Sum((C.Product((C.Name('a'), C.Name('b'),
                                 C.Name('a'), C.Name('b'),
                                 C.Name('b'), C.Name('c'),
                                 C.Name('a'))),
                      C.Product((C.Unknown(), C.Unknown(), C.Unit()))))
        output = C.PrettyPrinter.run(cost)
        exp_output = '((a^3 * b^3 * c) + (1 * ?^2))'
        self.assertEqual(output, exp_output)


if __name__ == '__main__':
    unittest.main()
