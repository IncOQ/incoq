"""Unit tests for tags.py."""


import unittest

import oinc.compiler.incast as L
from oinc.compiler.central import CentralCase
from oinc.compiler.demand.demtrans import *


class TransCase(CentralCase):
    
    def test_deminc(self):
        comp = L.pe('COMP({x for (x, y) in S for (y, z) in T}, [z], '
                    '{"uset_force": False})')
        tree = L.p('''
            S.add(e)
            print(COMP)
            ''', subst={'COMP': comp})
        
        tree = deminc_relcomp(tree, self.manager, comp, 'Q')
        tree = L.elim_deadfuncs(tree, lambda n: n.startswith('_maint_'))
        
        exp_tree = L.p('''
            Q_dT = RCSet()
            def _maint_Q_dT_Q_Ty1_add(_e):
                for (v7_y, v7_z) in COMP({(v7_y, v7_z)
                        for v7_y in deltamatch(Q_Ty1, 'b', _e, 1)
                        for (v7_y, v7_z) in T},
                        [], {'_deltaelem': '_e',
                             '_deltalhs': 'v7_y',
                             '_deltaop': 'add',
                             '_deltarel': 'Q_Ty1',
                             'impl': 'auxonly'}):
                    Q_dT.add((v7_y, v7_z))
            
            def _maint_Q_dT_Q_Ty1_remove(_e):
                for (v8_y, v8_z) in COMP({(v8_y, v8_z)
                        for v8_y in deltamatch(Q_Ty1, 'b', _e, 1)
                        for (v8_y, v8_z) in T},
                        [], {'_deltaelem': '_e',
                             '_deltalhs': 'v8_y',
                             '_deltaop': 'remove',
                             '_deltarel': 'Q_Ty1',
                             'impl': 'auxonly'}):
                    Q_dT.remove((v8_y, v8_z))
            
            Q_Ty1 = RCSet()
            def _maint_Q_Ty1_S_add(_e):
                for (v5_x, v5_y) in COMP({(v5_x, v5_y)
                        for (v5_x, v5_y) in deltamatch(S, 'bb', _e, 1)},
                        [], {'_deltaelem': '_e',
                             '_deltalhs': '(v5_x, v5_y)',
                             '_deltaop': 'add',
                             '_deltarel': 'S',
                             'impl': 'auxonly'}):
                    if (v5_y not in Q_Ty1):
                        with MAINT(Q_dT, 'after', 'Q_Ty1.add(v5_y)'):
                            Q_Ty1.add(v5_y)
                            _maint_Q_dT_Q_Ty1_add(v5_y)
                    else:
                        Q_Ty1.incref(v5_y)
            
            Q = RCSet()
            def _maint_Q_S_add(_e):
                for (v1_x, v1_y, v1_z) in COMP({(v1_x, v1_y, v1_z)
                        for (v1_x, v1_y) in deltamatch(S, 'bb', _e, 1)
                        for (v1_y, v1_z) in Q_dT},
                        [], {'_deltaelem': '_e',
                             '_deltalhs': '(v1_x, v1_y)',
                             '_deltaop': 'add',
                             '_deltarel': 'S',
                             'impl': 'auxonly'}):
                    if ((v1_z, v1_x) not in Q):
                        Q.add((v1_z, v1_x))
                    else:
                        Q.incref((v1_z, v1_x))
            
            with MAINT(Q, 'after', 'S.add(e)'):
                with MAINT(Q_Ty1, 'after', 'S.add(e)'):
                    S.add(e)
                    _maint_Q_Ty1_S_add(e)
                _maint_Q_S_add(e)
            print(setmatch(Q, 'bu', z))
            ''')
        
        self.assertEqual(tree, exp_tree)
    
    def test_deminc_nested(self):
        comp = L.pe(
            'COMP({(x, y, z) for (x, y) in R '
                         'for (y, z) in DEMQUERY(foo, [y], A)}, '
                 '[], '
                 '{"uset_force": False})')
        tree = L.p('''
            R.add(e)
            print(COMP)
            ''', subst={'COMP': comp})
        tree = deminc_relcomp(tree, self.manager, comp, 'Q')
        tree = L.elim_deadfuncs(tree, lambda n: n.startswith('_maint_'))
        
        exp_tree = L.p('''
            foo_delta = RCSet()
            def _maint_foo_delta_Q_Ty_add(_e):
                for v7_y in COMP({v7_y
                        for v7_y in deltamatch(Q_Ty, 'b', _e, 1)},
                        [], {'_deltaelem': '_e',
                             '_deltalhs': 'v7_y',
                             '_deltaop': 'add',
                             '_deltarel': 'Q_Ty',
                             'impl': 'auxonly'}):
                    foo_delta.add(v7_y)
            
            Q_Ty = RCSet()
            def _maint_Q_Ty_R_add(_e):
                for (v5_x, v5_y) in COMP({(v5_x, v5_y)
                        for (v5_x, v5_y) in deltamatch(R, 'bb', _e, 1)},
                        [], {'_deltaelem': '_e',
                             '_deltalhs': '(v5_x, v5_y)',
                             '_deltaop': 'add',
                             '_deltarel': 'R',
                             'impl': 'auxonly'}):
                    if (v5_y not in Q_Ty):
                        with MAINT(foo_delta, 'after', 'Q_Ty.add(v5_y)'):
                            Q_Ty.add(v5_y)
                            _maint_foo_delta_Q_Ty_add(v5_y)
                    else:
                        Q_Ty.incref(v5_y)
            
            Q = RCSet()
            def _maint_Q_R_add(_e):
                for (v1_x, v1_y, v1_z) in COMP({(v1_x, v1_y, v1_z)
                        for (v1_x, v1_y) in deltamatch(R, 'bb', _e, 1)
                        for (v1_y, v1_z) in A},
                        [], {'_deltaelem': '_e',
                             '_deltalhs': '(v1_x, v1_y)',
                             '_deltaop': 'add',
                             '_deltarel': 'R',
                             'impl': 'auxonly'}):
                    Q.add((v1_x, v1_y, v1_z))
            
            with MAINT(demand_foo, 'after', 'R.add(e)'):
                with MAINT(Q, 'after', 'R.add(e)'):
                    with MAINT(Q_Ty, 'after', 'R.add(e)'):
                        R.add(e)
                        _maint_Q_Ty_R_add(e)
                    _maint_Q_R_add(e)
                for v9_y in foo_delta.elements():
                    demand_foo(v9_y)
                foo_delta.clear()
            print(Q)
            ''')
        
        self.assertEqual(tree, exp_tree)


if __name__ == '__main__':
    unittest.main()
