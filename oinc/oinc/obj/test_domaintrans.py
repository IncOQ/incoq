"""Unit tests for domaintrans.py."""


import unittest

import oinc.incast as L
from oinc.central import CentralCase

from .domaintrans import *
from .domaintrans import (UpdateToPairTransformer, UpdateToObjTransformer,
                          flatten_all_comps, unflatten_all_comps,
                          AggregatePreprocessor)


class TestDomaintrans(CentralCase):
    
    def test_update_topair(self):
        tree = L.p('''
            x.add(y)
            T.add(x)
            o.foo = 4
            print(o.foo)
            del o.foo
            o.bar = 5
            m[k] = v
            del m[k]
            ''')
        tree, use_mset, fields, use_maprel = UpdateToPairTransformer.run(
                                                tree, False, set(), False,
                                                ['T'])
        
        exp_use_mset = True
        exp_fields = {'foo', 'bar'}
        exp_use_maprel = True
        exp_tree = L.p('''
            _M = MSet()
            _F_foo = FSet()
            _F_bar = FSet()
            _MAP = MAPSet()
            _M.add((x, y))
            T.add(x)
            _F_foo.add((o, 4))
            print(o.foo)
            _F_foo.remove((o, o.foo))
            _F_bar.add((o, 5))
            _MAP.add((m, k, v))
            _MAP.remove((m, k, m[k]))
            ''')
        
        self.assertEqual(tree, exp_tree)
        self.assertEqual(use_mset, exp_use_mset)
        self.assertEqual(fields, exp_fields)
        self.assertEqual(use_maprel, exp_use_maprel)
    
    def test_update_toobj(self):
        tree = L.p('''
            _M = MSet()
            _F_foo = FSet()
            _M.add((x, y))
            _F_foo.remove((o, o.foo))
            _M.add(w)
            _F_foo.add(w)
            _MAP.add((m, k, v))
            _MAP.remove(z)
            ''')
        tree = UpdateToObjTransformer.run(tree, self.manager.namegen)
        exp_tree = L.p('''
            x.add(y)
            del o.foo
            v1_cont, v1_item = w
            v1_cont.add(v1_item)
            v2_cont, v2_item = w
            v2_cont.foo = v2_item
            m[k] = v
            v3_map, v3_key, v3_value = z
            del v3_map[v3_key]
            ''')
        self.assertEqual(tree, exp_tree)
    
    def test_aggr(self):
        tree = L.p('''
            print(sum(x, {}))
            print(sum(o.f, {}))
            print(sum(o[a.b].f, {}))
            ''')
        tree = AggregatePreprocessor.run(tree)
        
        exp_tree = L.p('''
            print(sum(COMP({_e for _e in x}, [x], {}), {}))
            print(sum(COMP({_e for _e in o.f}, [o], {}), {}))
            print(sum(COMP({_e for _e in o[a.b].f}, [o, a], {}), {}))
            ''')
        
        self.assertEqual(tree, exp_tree)
    
    def test_pairdomain(self):
        tree = L.p('''
            S.add(o)
            T.add(o)
            o.a = 5
            print(COMP({x.a.b[c] for x in S if x in T}, [S, T], {}))
            ''')
        tree = to_pairdomain(tree, self.manager, ['T'])
        
        exp_tree = L.p('''
            _M = MSet()
            _F_a = FSet()
            _F_b = FSet()
            _MAP = MAPSet()
            _M.add((S, o))
            T.add(o)
            _F_a.add((o, 5))
            print(COMP({m_x_a_b_k_c for (S, x) in _M if x in T
                                    for (x, x_a) in _F_a
                                    for (x_a, x_a_b) in _F_b
                                    for (x_a_b, c, m_x_a_b_k_c) in _MAP},
                       [S, T], {}))
            ''')
        
        self.assertEqual(tree, exp_tree)
        
        tree = to_objdomain(tree, self.manager)
        
        exp_tree = L.p('''
            S.add(o)
            T.add(o)
            o.a = 5
            print(COMP({x.a.b[c] for x in S if x in T}, [S, T], {}))
            ''')
        
        self.assertEqual(tree, exp_tree)


if __name__ == '__main__':
    unittest.main()
