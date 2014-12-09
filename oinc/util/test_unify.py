"""Unit tests for unify.py."""


import unittest

from .unify import *


class UnifyCase(unittest.TestCase):
    
    def test_unify(self):
        # f(g(x), y) = f(g(h(z)), y)
        eqs = [(('f', ('g', 'x'), 'y'), ('f', ('g', ('h', 'z')), 'y'))]
        subst = unify(eqs)
        exp_subst = {'x': ('h', 'z')}
        self.assertEqual(subst, exp_subst)
        
        # f(x, x) = f(a, a)
        eqs = [(('f', 'x', 'x'), ('f', ('a',), ('a',)))]
        subst = unify(eqs)
        exp_subst = {'x': ('a',)}
        self.assertEqual(subst, exp_subst)
        
        # f(x, g(x)) = f(a, g(b))
        eqs = [(('f', 'x', ('g', 'x')), ('f', ('a',), ('g', ('b',))))]
        subst = unify(eqs)
        exp_subst = None
        self.assertEqual(subst, exp_subst)
        
        # f(x, y) = f(_, z)
        eqs = [(('f', 'x', 'y'), ('f', '_', 'z')),
               (('f', 'x', 'y'), '_')]
        subst = unify(eqs)
        exp_subst = {'y': 'z'}
        self.assertEqual(subst, exp_subst)


if __name__ == '__main__':
    unittest.main()
