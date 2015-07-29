"""Unit tests for pairrel.py."""


import unittest

import incoq.compiler.incast as L
from incoq.compiler.obj.pairrel import *


class PairrelCase(unittest.TestCase):
    
    def test_basic(self):
        self.assertTrue(is_mrel('_M'))
        self.assertTrue(is_frel('_F_f'))
        self.assertFalse(is_frel('R'))
        self.assertEqual(get_frel_field('_F_f'), 'f')
        self.assertEqual(make_frel('f'), '_F_f')
        self.assertTrue(is_maprel('_MAP'))
    
    def test_parseclause(self):
        comp = L.pe('''
            COMP({... for (a, b) in _M for (c, d) in _F_e
                      for (f, g, h) in _MAP if x > 5}, [], {})
            ''')
        
        res1 = get_menum(comp.clauses[0])
        exp_res1 = (L.sn('a'), L.sn('b'))
        res2 = get_fenum(comp.clauses[1])
        exp_res2 = (L.sn('c'), L.sn('d'), 'e')
        res3 = get_mapenum(comp.clauses[2])
        exp_res3 = (L.sn('f'), L.sn('g'), L.sn('h'))
        
        self.assertEqual(res1, exp_res1)
        self.assertEqual(res2, exp_res2)
        self.assertEqual(res3, exp_res3)


if __name__ == '__main__':
    unittest.main()
