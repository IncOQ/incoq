"""Unit tests for costs.py."""


import unittest

from incoq.util.misc import new_namespace
from incoq.mars.incast import L
import incoq.mars.cost.costs as costs
import incoq.mars.cost.algebra as algebra
from incoq.mars.cost.algebra import (
    build_factor_index, product_dominates, all_products_dominated)

C = new_namespace(costs, algebra)


class AlgebraCase(unittest.TestCase):
    
    def test_imgkeysubstitutor(self):
        cost = C.Product([C.DefImgset('R', L.mask('bbu'), ['a', 'b']),
                          C.DefImgset('S', L.mask('ubb'), ['b', 'c'])])
        cost = C.ImgkeySubstitutor.run(cost, {'a': 'x', 'b': 'y'})
        exp_cost = C.Product([C.DefImgset('R', L.mask('bbu'), ['x', 'y']),
                              C.DefImgset('S', L.mask('ubb'), ['y', 'c'])])
        self.assertEqual(cost, exp_cost)
    
    def test_basicsimplifier(self):
        cost = C.Sum([C.Unit(), C.Name('A'), C.Name('A'),
                      C.Product([C.Name('A'), C.Unit(), C.Unit()]),
                      C.Min([C.Name('A'), C.Unit()])])
        cost = C.BasicSimplifier.run(cost)
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


if __name__ == '__main__':
    unittest.main()
