"""Unit tests for algebra.py."""


import unittest

from incoq.util.misc import new_namespace
from incoq.mars.incast import L
import incoq.mars.cost.costs as costs
import incoq.mars.cost.algebra as algebra
from incoq.mars.cost.algebra import (
    TrivialSimplifier, build_factor_index,
    product_dominates, all_products_dominated,
    simplify_sum_of_products, simplify_min_of_sums,
    multiply_sums_of_products, Normalizer)

C = new_namespace(costs, algebra)


class AlgebraCase(unittest.TestCase):
    
    def test_imgkeysubstitutor(self):
        orig_cost = C.Product([C.DefImgset('R', L.mask('bbu'), ['A', 'B']),
                               C.DefImgset('S', L.mask('ubb'), ['B', 'C'])])
        cost = C.ImgkeySubstitutor.run(orig_cost, {'A': 'x', 'B': 'y'})
        exp_cost = C.Product([C.DefImgset('R', L.mask('bbu'), ['x', 'y']),
                              C.DefImgset('S', L.mask('ubb'), ['y', 'C'])])
        self.assertEqual(cost, exp_cost)
        
        cost = C.ImgkeySubstitutor.run(orig_cost, lambda x: x * 2)
        exp_cost = C.Product([C.DefImgset('R', L.mask('bbu'), ['AA', 'BB']),
                              C.DefImgset('S', L.mask('ubb'), ['BB', 'CC'])])
        self.assertEqual(cost, exp_cost)
    
    def test_trivialsimplifier(self):
        cost = C.Sum([C.Unit(), C.Name('A'), C.Name('A'),
                      C.Product([C.Name('A'), C.Unit(), C.Unit()]),
                      C.Min([C.Name('A'), C.Unit()])])
        cost = TrivialSimplifier.run(cost)
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
        right = [p([n('A'), n('A')]),
                 p([n('A'), n('B')])]
        # [a*a, a]
        left1 = [p([n('A'), n('A')]),
                 p([n('A')])]
        # [a, b, c]
        left2 = [p([n('A')]),
                 p([n('B')]),
                 p([n('C')])]
        
        self.assertTrue(all_products_dominated(left1, right))
        self.assertFalse(all_products_dominated(left2, right))
        self.assertTrue(all_products_dominated(right, right))
        
        # [1]
        left = [p([C.Unit()])]
        # [a]
        right = [p([n('A')])]
        self.assertTrue(all_products_dominated(left, right))
    
    def test_simplify_sum_of_products(self):
        s, p, n = C.Sum, C.Product, C.Name
        
        # a*a + a*a + a + a*b + 1 -> a*a + a*b
        cost = s([p([n('A'), n('A')]),
                  p([n('A'), n('A')]),
                  p([n('A')]),
                  p([n('A'), n('B')]),
                  p([C.Unit()])])
        cost = simplify_sum_of_products(cost)
        exp_cost = s([p([n('A'), n('A')]),
                      p([n('A'), n('B')])])
        self.assertEqual(cost, exp_cost)
        
        # a*b + b*a -> a*b
        cost = s([p([n('A'), n('B')]),
                  p([n('B'), n('A')])])
        cost = simplify_sum_of_products(cost)
        exp_cost = s([p([n('A'), n('B')])])
        self.assertEqual(cost, exp_cost)
    
    def test_simplify_min_of_sums(self):
        m, s, p, n = C.Min, C.Sum, C.Product, C.Name
        
        # min(a + b, a*a*a, b) -> min(a*a*a, b)
        cost = m([s([p([n('A')]), p([n('B')])]),
                  s([p([n('A'), n('A'), n('A')])]),
                  s([p([n('B')])])])
        cost = simplify_min_of_sums(cost)
        exp_cost = m([s([p([n('A'), n('A'), n('A')])]),
                      s([p([n('B')])])])
        self.assertEqual(cost, exp_cost)
    
    def test_multiply_sums_of_products(self):
        s, p, n = C.Sum, C.Product, C.Name
        
        # [(a + b), (c + d), (e + f)]
        costs = [s([p([n('A')]), p([n('B')])]),
                 s([p([n('C')]), p([n('D')])]),
                 s([p([n('E')]), p([n('F')])])]
        cost = multiply_sums_of_products(costs)
        # a*c*e + a*c*f + a*d*e + a*d*f +
        # b*c*e + b*c*f + b*d*e + b*d*f
        exp_cost = s([p([n('A'), n('C'), n('E')]),
                      p([n('A'), n('C'), n('F')]),
                      p([n('A'), n('D'), n('E')]),
                      p([n('A'), n('D'), n('F')]),
                      p([n('B'), n('C'), n('E')]),
                      p([n('B'), n('C'), n('F')]),
                      p([n('B'), n('D'), n('E')]),
                      p([n('B'), n('D'), n('F')])])
        self.assertEqual(cost, exp_cost)
    
    def test_normalize(self):
        m, s, p, n = C.Min, C.Sum, C.Product, C.Name
        
        # a * min(b, c * (d + min(e, f))) -->
        # min(a*b, a*c*d + a*c*e, a*c*d + a*c*f)
        orig_cost = p([n('A'), m([n('B'), p([n('C'),
                    s([n('D'), m([n('E'), n('F')])])])])])
        # Use Normalizer directly because we don't want to unwrap
        # anything.
        cost = Normalizer.run(orig_cost)
        exp_cost = m([s([p([n('A'), n('B')])]),
                      s([p([n('A'), n('C'), n('D')]),
                         p([n('A'), n('C'), n('E')])]),
                      s([p([n('A'), n('C'), n('D')]),
                         p([n('A'), n('C'), n('F')])])])
        self.assertEqual(cost, exp_cost)
        
        # Check that it unwraps.
        
        cost = n('A')
        cost = C.normalize(cost)
        exp_cost = n('A')
        self.assertEqual(cost, exp_cost)
        
        cost = C.normalize(orig_cost)
        exp_cost = m([p([n('A'), n('B')]),
                      s([p([n('A'), n('C'), n('D')]),
                         p([n('A'), n('C'), n('E')])]),
                      s([p([n('A'), n('C'), n('D')]),
                         p([n('A'), n('C'), n('F')])])])
        self.assertEqual(cost, exp_cost)
    
    def test_normalize_hard(self):
        # Regression test based on a bigger example.
        
        # ((1 + (S * ((1 + (T * ((1))))))) + (1 + (R * ((1)))))
        src = L.trim('''
            Sum(terms=(Sum(terms=(Unit(), Product(terms=(Name(name='S'),
            Sum(terms=(Sum(terms=(Unit(), Product(terms=(Name(name='T'),
            Sum(terms=(Sum(terms=(Unit(),)),)))))),)))))),
            Sum(terms=(Unit(), Product(terms=(Name(name='R'),
            Sum(terms=(Sum(terms=(Unit(),)),))))))))
            ''')
        # Should return (S * T) + R, but without simplifying products
        # it returns (S * T * 1) + (R * 1).
        cost = C.eval_coststr(src)
        cost = C.normalize(cost)
        exp_cost = C.Sum([C.Product([C.Name('S'), C.Name('T')]),
                          C.Name('R')])
        self.assertEqual(cost, exp_cost)


if __name__ == '__main__':
    unittest.main()
