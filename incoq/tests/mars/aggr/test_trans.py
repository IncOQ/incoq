"""Unit tests for trans.py."""


import unittest

from incoq.mars.incast import L
from incoq.mars.symbol import N
from incoq.mars.aggr.trans import *
from incoq.mars.aggr.trans import make_aggr_maint_func


class TransCase(unittest.TestCase):
    
    def test_aggr_maint_func_add(self):
        aggrinv = AggrInvariant('A', L.Count(), 'R', L.mask('bu'), ['x'])
        func = make_aggr_maint_func(N.fresh_name_generator(),
                                    aggrinv, L.SetAdd())
        exp_func = L.Parser.ps('''
            def _maint_A_for_R_add(_elem):
                (_elem_v1, _elem_v2) = _elem
                _v1_key = (_elem_v1,)
                _v1_value = (_elem_v2,)
                _v1_state = A.get(_v1_key, 0)
                _v1_state = (_v1_state + 1)
                if (_v1_key in A):
                    A.mapdelete(_v1_key)
                A.mapassign(_v1_key, _v1_state)
            ''')
        self.assertEqual(func, exp_func)
    
    def test_aggr_maint_func_remove(self):
        aggrinv = AggrInvariant('A', L.Count(), 'R', L.mask('bu'), ['x'])
        func = make_aggr_maint_func(N.fresh_name_generator(),
                                    aggrinv, L.SetRemove())
        exp_func = L.Parser.ps('''
            def _maint_A_for_R_remove(_elem):
                (_elem_v1, _elem_v2) = _elem
                _v1_key = (_elem_v1,)
                _v1_value = (_elem_v2,)
                _v1_state = A[_v1_key]
                _v1_state = (_v1_state - 1)
                A.mapdelete(_v1_key)
                if (not (_v1_state == 0)):
                    A.mapassign(_v1_key, _v1_state)
            ''')
        self.assertEqual(func, exp_func)


if __name__ == '__main__':
    unittest.main()
