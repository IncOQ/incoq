"""Unit tests for costs.py."""


import unittest

from incoq.util.misc import new_namespace
from incoq.mars.incast import L
import incoq.mars.cost.costs as costs
import incoq.mars.cost.algebra as algebra
from incoq.mars.cost.algebra import (
    build_factor_index, product_dominates, all_products_dominated,
    simplify_sum_of_products, simplify_min_of_sums, multiply_sums_of_products)

C = new_namespace(costs, algebra)


class AlgebraCase(unittest.TestCase):
    
    def test_imgkeysubstitutor(self):
        cost = C.Product([C.DefImgset('R', L.mask('bbu'), ['a', 'b']),
                          C.DefImgset('S', L.mask('ubb'), ['b', 'c'])])
        cost = C.ImgkeySubstitutor.run(cost, {'a': 'x', 'b': 'y'})
        exp_cost = C.Product([C.DefImgset('R', L.mask('bbu'), ['x', 'y']),
                              C.DefImgset('S', L.mask('ubb'), ['y', 'c'])])
        self.assertEqual(cost, exp_cost)
    
    def test_trivialsimplifier(self):
        cost = C.Sum([C.Unit(), C.Name('A'), C.Name('A'),
                      C.Product([C.Name('A'), C.Unit(), C.Unit()]),
                      C.Min([C.Name('A'), C.Unit()])])
        cost = C.TrivialSimplifier.run(cost)
        exp_cost = C.Sum([C.Name('A'),
                          C.Product([C.Name('A')]),
                          C.Min([C.Name('A'), C.Unit()])])
        self.assertEqual(cost, exp_cost)
    
    def test_build_factor_index(self):
        p1 = C.Product([C.Name('A'), C.Name('A'), C.Name('B')])
        p2 = C.Product([C.Name('B'), C.Unit()])
        factor_index = build_factor_index([p1, p2])
        exp_factor_index = {
            p1: {C.Name('A'): 2, C.Name('B'): 1},
            p2: {C.Name('B'): 1, C.Unit(): 1}
        }
        self.assertDictEqual(factor_index, exp_factor_index)
    
    def test_product_dominates(self):
        # a * a * c
        p1 = C.Product([C.Name('A'), C.Name('A'), C.Name('C')])
        # a * c * 1
        p2 = C.Product([C.Name('A'), C.Name('C'), C.Unit()])
        # a * b * c
        p3 = C.Product([C.Name('A'), C.Name('B'), C.Name('C')])
        
        self.assertTrue(product_dominates(p1, p2))
        self.assertFalse(product_dominates(p1, p3))
        self.assertTrue(product_dominates(p1, p1))
    
    def test_all_products_dominated(self):
        p, n = C.Product, C.Name
        # [a*a, a*b]
        right = [p([n('a'), n('a')]),
                 p([n('a'), n('b')])]
        # [a*a, a]
        left1 = [p([n('a'), n('a')]),
                 p([n('a')])]
        # [a, b, c]
        left2 = [p([n('a')]),
                 p([n('b')]),
                 p([n('c')])]
        
        self.assertTrue(all_products_dominated(left1, right))
        self.assertFalse(all_products_dominated(left2, right))
        self.assertTrue(all_products_dominated(right, right))
        
        # [1]
        left = [p([C.Unit()])]
        # [a]
        right = [p([n('a')])]
        self.assertTrue(all_products_dominated(left, right))
    
    def test_simplify_sum_of_products(self):
        s, p, n = C.Sum, C.Product, C.Name
        
        # a*a + a*a + a + a*b -> a*a + a*b
        cost = s([p([n('a'), n('a')]),
                  p([n('a'), n('a')]),
                  p([n('a')]),
                  p([n('a'), n('b')])])
        cost = simplify_sum_of_products(cost)
        exp_cost = s([p([n('a'), n('a')]),
                      p([n('a'), n('b')])])
        self.assertEqual(cost, exp_cost)
        
        # a*b + b*a -> a*b
        cost = s([p([n('a'), n('b')]),
                  p([n('b'), n('a')])])
        cost = simplify_sum_of_products(cost)
        exp_cost = s([p([n('a'), n('b')])])
        self.assertEqual(cost, exp_cost)
    
    def test_simplify_min_of_sums(self):
        m, s, p, n = C.Min, C.Sum, C.Product, C.Name
        
        # min(a + b, a*a*a, b) -> min(a*a*a, b)
        cost = m([s([p([n('a')]), p([n('b')])]),
                  s([p([n('a'), n('a'), n('a')])]),
                  s([p([n('b')])])])
        cost = simplify_min_of_sums(cost)
        exp_cost = m([s([p([n('a'), n('a'), n('a')])]),
                      s([p([n('b')])])])
        self.assertEqual(cost, exp_cost)
    
    def test_multiply_sums_of_products(self):
        s, p, n = C.Sum, C.Product, C.Name
        
        # [(a + b), (c + d), (e + f)]
        costs = [s([p([n('a')]), p([n('b')])]),
                 s([p([n('c')]), p([n('d')])]),
                 s([p([n('e')]), p([n('f')])])]
        cost = multiply_sums_of_products(costs)
        # a*c*e + a*c*f + a*d*e + a*d*f +
        # b*c*e + b*c*f + b*d*e + b*d*f
        exp_cost = s([p([n('a'), n('c'), n('e')]),
                      p([n('a'), n('c'), n('f')]),
                      p([n('a'), n('d'), n('e')]),
                      p([n('a'), n('d'), n('f')]),
                      p([n('b'), n('c'), n('e')]),
                      p([n('b'), n('c'), n('f')]),
                      p([n('b'), n('d'), n('e')]),
                      p([n('b'), n('d'), n('f')])])
        self.assertEqual(cost, exp_cost)


if __name__ == '__main__':
    unittest.main()
