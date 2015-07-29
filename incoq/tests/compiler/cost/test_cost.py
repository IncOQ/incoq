"""Unit tests for cost.py."""


import unittest

from incoq.compiler.set import Mask
from incoq.compiler.cost.cost import *
from incoq.compiler.cost.cost import (
        without_duplicates, all_products_dominated,
        all_sums_of_products_dominate,
        simplify_sum_of_products, simplify_min_of_sums,
        multiply_sums_of_products)


class CostCase(unittest.TestCase):
    
    def test_cost(self):
        cost = SumCost.from_sums([SumCost((NameCost('a'), NameCost('b'))),
                                  SumCost((NameCost('c'),))])
        exp_cost = SumCost((NameCost('a'), NameCost('b'), NameCost('c')))
        self.assertEqual(cost, exp_cost)
    
    def test_visitor(self):
        class Foo(CostTransformer):
            def visit_NameCost(self, cost):
                return NameCost('z')
        
        cost = SumCost((NameCost('a'), NameCost('b')))
        cost = Foo.run(cost)
        exp_cost = SumCost((NameCost('z'), NameCost('z')))
        self.assertEqual(cost, exp_cost)
    
    def test_substitute(self):
        cost = SumCost((NameCost('a'), DefImgsetCost('R', Mask.OUT, ('b',))))
        subst = {NameCost('a'): NameCost('x'),
                 IndefImgsetCost('R', Mask.OUT): NameCost('y')}
        
        cost = CostSubstitutor.run(cost, subst, subsume_maps=False)
        exp_cost = SumCost((NameCost('x'),
                            DefImgsetCost('R', Mask.OUT, ('b',))))
        self.assertEqual(cost, exp_cost)
        
        cost = CostSubstitutor.run(cost, subst, subsume_maps=True)
        exp_cost = SumCost((NameCost('x'), NameCost('y')))
        self.assertEqual(cost, exp_cost)
    
    def test_prettyprint(self):
        cost = SumCost((ProductCost((NameCost('a'), NameCost('b'),
                                     NameCost('a'), NameCost('b'),
                                     NameCost('b'), NameCost('c'),
                                     NameCost('a'))),
                        ProductCost((UnknownCost(), UnitCost()))))
        output = PrettyPrinter.run(cost)
        exp_output = '((a^3*b^3*c) + (1*?))'
        self.assertEqual(output, exp_output)
    
    def test_simplifier(self):
        cost = SumCost((UnitCost(), NameCost('a'), NameCost('a')))
        cost = Simplifier.run(cost)
        exp_cost = NameCost('a')
        self.assertEqual(cost, exp_cost)
    
    def test_elim_duplicate(self):
        # a + a + b -> a + b
        cost = SumCost((NameCost('a'), NameCost('a'), NameCost('b')))
        cost = without_duplicates(cost)
        exp_cost = SumCost((NameCost('a'), NameCost('b')))
        self.assertEqual(cost, exp_cost)
    
    def test_products_dominated(self):
        pc, nc = ProductCost, NameCost
        # [a*a, a*b]
        right = [pc((nc('a'), nc('a'))),
                 pc((nc('a'), nc('b')))]
        # [a*a, a]
        left1 = [pc((nc('a'), nc('a'))),
                 pc((nc('a'),))]
        # [a, b, c]
        left2 = [pc((nc('a'),)),
                 pc((nc('b'),)),
                 pc((nc('c'),))]
        
        self.assertTrue(all_products_dominated(left1, right))
        self.assertFalse(all_products_dominated(left2, right))
        
        self.assertTrue(all_products_dominated(
                        [pc((UnitCost(),))], [pc((NameCost('a'),))]))
    
    def test_sums_dominate(self):
        sc, pc, nc = SumCost, ProductCost, NameCost
        # [a*a*a*b + a*b*b, a*b*b*b*b]
        left = [sc((pc((nc('a'), nc('a'), nc('a'), nc('b'))),
                    pc((nc('a'), nc('b'), nc('b'))))),
                sc((pc((nc('a'), nc('b'), nc('b'), nc('b'), nc('b'))),))]
        # [a*a*b + a*b*b, a*b*b*b + 1]
        right = [sc((pc((nc('a'), nc('a'), nc('b'))),
                     pc((nc('a'), nc('b'), nc('b'))))),
                 sc((pc((nc('a'), nc('b'), nc('b'), nc('b'))),
                     pc((UnitCost(),))))]
        
        self.assertTrue(all_sums_of_products_dominate(left, right))
        self.assertFalse(all_sums_of_products_dominate(right, left))
    
    def test_simplify_sum_of_products(self):
        # a*a + a*a + a + a*b -> a*a + a*b
        cost = SumCost((ProductCost((NameCost('a'), NameCost('a'))),
                        ProductCost((NameCost('a'), NameCost('a'))),
                        ProductCost((NameCost('a'),)),
                        ProductCost((NameCost('a'), NameCost('b')))))
        cost = simplify_sum_of_products(cost)
        exp_cost = SumCost((ProductCost((NameCost('a'), NameCost('a'))),
                            ProductCost((NameCost('a'), NameCost('b')))))
        self.assertEqual(cost, exp_cost)
        
        # a*b + b*a -> a*b
        cost = SumCost((ProductCost((NameCost('a'), NameCost('b'))),
                        ProductCost((NameCost('b'), NameCost('a')))))
        cost = simplify_sum_of_products(cost)
        exp_cost = SumCost((ProductCost((NameCost('a'), NameCost('b'))),))
        self.assertEqual(cost, exp_cost)
    
    def test_simplify_min_of_sums(self):
        # min(a + b, a*a*a, b)
        cost = MinCost((SumCost((ProductCost((NameCost('a'),)),
                                 ProductCost((NameCost('b'),)))),
                        SumCost((ProductCost((NameCost('a'), NameCost('a'),
                                              NameCost('a'))),)),
                        SumCost((ProductCost((NameCost('b'),)),))))
        cost = simplify_min_of_sums(cost)
        exp_cost_str = 'min(((a*a*a)), ((b)))'
        self.assertEqual(str(cost), exp_cost_str)
    
    def test_multiply_sums_of_products(self):
        # [(a + b), (c + d), (e + f)]
        costs = [SumCost((ProductCost((NameCost('a'),)),
                          ProductCost((NameCost('b'),)))),
                 SumCost((ProductCost((NameCost('c'),)),
                          ProductCost((NameCost('d'),)))),
                 SumCost((ProductCost((NameCost('e'),)),
                          ProductCost((NameCost('f'),))))]
        cost = multiply_sums_of_products(costs)
        exp_cost_str = ('((a*c*e) + (a*c*f) + (a*d*e) + (a*d*f) + '
                        '(b*c*e) + (b*c*f) + (b*d*e) + (b*d*f))')
        self.assertEqual(str(cost), exp_cost_str)
    
    def test_normalize(self):
        cost = ProductCost((SumCost((NameCost('a'), NameCost('b'))),
                            SumCost((NameCost('c'), NameCost('d'))),
                            SumCost((NameCost('e'), NameCost('f')))))
        cost = normalize(cost)
        exp_cost_str = ('((a*c*e) + (a*c*f) + (a*d*e) + (a*d*f) + '
                         '(b*c*e) + (b*c*f) + (b*d*e) + (b*d*f))')
        self.assertEqual(str(cost), exp_cost_str)
    
    def test_lteq(self):
        sc, pc, nc = SumCost, ProductCost, NameCost
        # min(a*a*b + a*b*b, a*b*b*b + 1)
        left = [sc((pc((nc('a'), nc('a'), nc('b'))),
                    pc((nc('a'), nc('b'), nc('b'))))),
                sc((pc((nc('a'), nc('b'), nc('b'), nc('b'))),
                    pc((UnitCost(),))))]
        left = MinCost(left)
        # min(a*a*a*b + a*b*b, a*b*b*b*b)
        right = [sc((pc((nc('a'), nc('a'), nc('a'), nc('b'))),
                     pc((nc('a'), nc('b'), nc('b'))))),
                 sc((pc((nc('a'), nc('b'), nc('b'), nc('b'), nc('b'))),))]
        right = MinCost(right)
        
        self.assertTrue(lteq(left, right))
        self.assertFalse(lteq(right, left))


if __name__ == '__main__':
    unittest.main()
