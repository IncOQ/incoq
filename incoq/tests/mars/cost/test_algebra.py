"""Unit tests for costs.py."""


import unittest

from incoq.util.misc import new_namespace
from incoq.mars.incast import L
import incoq.mars.cost.costs as costs
import incoq.mars.cost.algebra as algebra

C = new_namespace(costs, algebra)


class AlgebraCase(unittest.TestCase):
    
    def test_imgkeysubstitutor(self):
        cost = C.Product([C.DefImgset('R', L.mask('bbu'), ['a', 'b']),
                          C.DefImgset('S', L.mask('ubb'), ['b', 'c'])])
        cost = C.ImgkeySubstitutor.run(cost, {'a': 'x', 'b': 'y'})
        exp_cost = C.Product([C.DefImgset('R', L.mask('bbu'), ['x', 'y']),
                              C.DefImgset('S', L.mask('ubb'), ['y', 'c'])])
        self.assertEqual(cost, exp_cost)


if __name__ == '__main__':
    unittest.main()
