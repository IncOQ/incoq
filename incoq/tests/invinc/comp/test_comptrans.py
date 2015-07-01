"""Unit tests for comptrans.py."""


import unittest

import incoq.compiler.incast as L
from incoq.compiler.central import CentralCase
from incoq.compiler.comp.compspec import CompSpec
from incoq.compiler.comp.comptrans import *
from incoq.compiler.comp.comptrans import (
        IncComp, RelcompMaintainer,
        SubqueryArityFinder, get_subquery_demnames)


class TestComp(CentralCase):
    
    def test_change_tracker(self):
        comp = L.pe('COMP({(x, y, z) for (x, y) in S '
                                    'for (y, z) in T}, [], {})')
        spec = CompSpec.from_comp(comp, self.manager.factory)
        inccomp = IncComp(comp, spec, 'Q', False, None, None,
                          'no', 'das', 'auxonly', [], None)
        inccomp.change_tracker = True
        tree = L.p('''
            S.add(e)
            ''')
        tree, comps = RelcompMaintainer.run(tree, self.manager, inccomp)
        
        exp_tree = L.p('''
            Q = RCSet()
            def _maint_Q_S_add(_e):
                for (v1_x, v1_y, v1_z) in COMP({(v1_x, v1_y, v1_z)
                        for (v1_x, v1_y) in deltamatch(S, 'bb', _e, 1)
                        for (v1_y, v1_z) in T},
                        [], {'_deltaelem': '_e',
                             '_deltalhs': '(v1_x, v1_y)',
                             '_deltaop': 'add',
                             '_deltarel': 'S',
                             'impl': 'auxonly'}):
                    Q.add((v1_x, v1_y, v1_z))
            
            def _maint_Q_S_remove(_e):
                for (v2_x, v2_y, v2_z) in COMP({(v2_x, v2_y, v2_z)
                        for (v2_x, v2_y) in deltamatch(S, 'bb', _e, 1)
                        for (v2_y, v2_z) in T},
                        [], {'_deltaelem': '_e',
                             '_deltalhs': '(v2_x, v2_y)',
                             '_deltaop': 'remove',
                             '_deltarel': 'S',
                             'impl': 'auxonly'}):
                    Q.remove((v2_x, v2_y, v2_z))
            
            def _maint_Q_T_add(_e):
                for (v3_x, v3_y, v3_z) in COMP({(v3_x, v3_y, v3_z)
                        for (v3_x, v3_y) in S
                        for (v3_y, v3_z) in deltamatch(T, 'bb', _e, 1)},
                        [], {'_deltaelem': '_e',
                             '_deltalhs': '(v3_y, v3_z)',
                             '_deltaop': 'add',
                             '_deltarel': 'T',
                             'impl': 'auxonly'}):
                    Q.add((v3_x, v3_y, v3_z))
            
            def _maint_Q_T_remove(_e):
                for (v4_x, v4_y, v4_z) in COMP({(v4_x, v4_y, v4_z)
                        for (v4_x, v4_y) in S
                        for (v4_y, v4_z) in deltamatch(T, 'bb', _e, 1)},
                        [], {'_deltaelem': '_e',
                             '_deltalhs': '(v4_y, v4_z)',
                             '_deltaop': 'remove',
                             '_deltarel': 'T',
                             'impl': 'auxonly'}):
                    Q.remove((v4_x, v4_y, v4_z))
            
            with MAINT(Q, 'after', 'S.add(e)'):
                S.add(e)
                _maint_Q_S_add(e)
            ''')
        
        self.assertEqual(tree, exp_tree)
    
    def test_arityfinder(self):
        comp1 = L.pe('COMP({x for x in S}, [], {})')
        comp2 = L.pe('COMP({y for y in C1}, [], {})',
                     subst={'C1': comp1})
        tree = L.p('''
            print(C2)
            ''', subst={'C2': comp2})
        arity = SubqueryArityFinder.run(tree, comp1)
        self.assertEqual(arity, 1)
        
        comp3 = L.pe('COMP({(x, x) for x in S}, [], {})')
        comp4 = L.pe('COMP({z for (z, z) in C3}, [], {})',
                     subst={'C3': comp3})
        tree = L.p('''
            print(C4, C4)
            ''', subst={'C4': comp4})
        arity = SubqueryArityFinder.run(tree, comp3)
        self.assertEqual(arity, 2)
        
        comp5 = L.pe('COMP({z for (z, z) in C1}, [], {})',
                     subst={'C1': comp1})
        tree = L.p('''
            print(C5)
            ''', subst={'C5': comp5})
        arity = SubqueryArityFinder.run(tree, comp1)
        self.assertEqual(arity, False)
        
        tree = L.p('''
            print(C2, C1)
            ''', subst={'C2': comp2,
                        'C1': comp1})
        arity = SubqueryArityFinder.run(tree, comp1)
        self.assertEqual(arity, False)
    
    def test_inc_relcomp_basic(self):
        comp = L.pe('COMP({(x, y) for (x, y) in S}, [x], {})')
        tree = L.p('''
            S.add((1, 2))
            print(COMP)
            ''', subst={'COMP': comp})
        tree = inc_relcomp(tree, self.manager, comp, 'Q')
        
        exp_tree = L.p('''
            Q = RCSet()
            def _maint_Q_S_add(_e):
                for (v1_x, v1_y) in COMP({(v1_x, v1_y)
                        for (v1_x, v1_y) in deltamatch(S, 'bb', _e, 1)},
                        [], {'_deltaelem': '_e',
                             '_deltalhs': '(v1_x, v1_y)',
                             '_deltaop': 'add',
                             '_deltarel': 'S',
                             'impl': 'auxonly'}):
                    Q.add((v1_x, (v1_x, v1_y)))
            
            def _maint_Q_S_remove(_e):
                for (v2_x, v2_y) in COMP({(v2_x, v2_y)
                        for (v2_x, v2_y) in deltamatch(S, 'bb', _e, 1)},
                        [], {'_deltaelem': '_e',
                             '_deltalhs': '(v2_x, v2_y)',
                             '_deltaop': 'remove',
                             '_deltarel': 'S',
                             'impl': 'auxonly'}):
                    Q.remove((v2_x, (v2_x, v2_y)))
            
            with MAINT(Q, 'after', 'S.add((1, 2))'):
                S.add((1, 2))
                _maint_Q_S_add((1, 2))
            print(setmatch(Q, 'bu', x))
            ''')
        
        self.assertEqual(tree, exp_tree)
    
    def test_inc_relcomp_noparams(self):
        comp = L.pe('COMP({(x, y) for (x, y) in S}, [], {})')
        tree = L.p('''
            S.add((1, 2))
            print(COMP)
            ''', subst={'COMP': comp})
        tree = inc_relcomp(tree, self.manager, comp, 'Q')
        
        exp_tree = L.p('''
            Q = RCSet()
            def _maint_Q_S_add(_e):
                for (v1_x, v1_y) in COMP({(v1_x, v1_y)
                        for (v1_x, v1_y) in deltamatch(S, 'bb', _e, 1)},
                        [], {'_deltaelem': '_e',
                             '_deltalhs': '(v1_x, v1_y)',
                             '_deltaop': 'add',
                             '_deltarel': 'S',
                             'impl': 'auxonly'}):
                    Q.add((v1_x, v1_y))
            
            def _maint_Q_S_remove(_e):
                for (v2_x, v2_y) in COMP({(v2_x, v2_y)
                        for (v2_x, v2_y) in deltamatch(S, 'bb', _e, 1)},
                        [], {'_deltaelem': '_e',
                             '_deltalhs': '(v2_x, v2_y)',
                             '_deltaop': 'remove',
                             '_deltarel': 'S',
                             'impl': 'auxonly'}):
                    Q.remove((v2_x, v2_y))
            
            with MAINT(Q, 'after', 'S.add((1, 2))'):
                S.add((1, 2))
                _maint_Q_S_add((1, 2))
            print(Q)
            ''')
        
        self.assertEqual(tree, exp_tree)
    
    def test_inc_relcomp_maintcomps(self):
        comp = L.pe('COMP({z for (x, y) in R for (y, z) in S}, [x], {})')
        tree = L.p('''
            R.add((1, 2))
            print(COMP)
            ''', subst={'COMP': comp})
        inccomp = make_inccomp(tree, self.manager, comp, 'Q')
        tree, maintcomps = inc_relcomp_helper(tree, self.manager, inccomp)
        
        exp_tree = L.p('''
            Q = RCSet()
            def _maint_Q_R_add(_e):
                for (v1_x, v1_y, v1_z) in COMP({(v1_x, v1_y, v1_z)
                        for (v1_x, v1_y) in deltamatch(R, 'bb', _e, 1)
                        for (v1_y, v1_z) in S},
                        [], {'_deltaelem': '_e',
                             '_deltalhs': '(v1_x, v1_y)',
                             '_deltaop': 'add',
                             '_deltarel': 'R',
                             'impl': 'auxonly'}):
                    if ((v1_x, v1_z) not in Q):
                        Q.add((v1_x, v1_z))
                    else:
                        Q.incref((v1_x, v1_z))
            
            def _maint_Q_R_remove(_e):
                for (v2_x, v2_y, v2_z) in COMP({(v2_x, v2_y, v2_z)
                        for (v2_x, v2_y) in deltamatch(R, 'bb', _e, 1)
                        for (v2_y, v2_z) in S},
                        [], {'_deltaelem': '_e',
                             '_deltalhs': '(v2_x, v2_y)',
                             '_deltaop': 'remove',
                             '_deltarel': 'R',
                             'impl': 'auxonly'}):
                    if (Q.getref((v2_x, v2_z)) == 1):
                        Q.remove((v2_x, v2_z))
                    else:
                        Q.decref((v2_x, v2_z))
            
            def _maint_Q_S_add(_e):
                for (v3_x, v3_y, v3_z) in COMP({(v3_x, v3_y, v3_z)
                        for (v3_x, v3_y) in R
                        for (v3_y, v3_z) in deltamatch(S, 'bb', _e, 1)},
                        [], {'_deltaelem': '_e',
                             '_deltalhs': '(v3_y, v3_z)',
                             '_deltaop': 'add',
                             '_deltarel': 'S',
                             'impl': 'auxonly'}):
                    if ((v3_x, v3_z) not in Q):
                        Q.add((v3_x, v3_z))
                    else:
                        Q.incref((v3_x, v3_z))
            
            def _maint_Q_S_remove(_e):
                for (v4_x, v4_y, v4_z) in COMP({(v4_x, v4_y, v4_z)
                        for (v4_x, v4_y) in R
                        for (v4_y, v4_z) in deltamatch(S, 'bb', _e, 1)},
                        [], {'_deltaelem': '_e',
                             '_deltalhs': '(v4_y, v4_z)',
                             '_deltaop': 'remove',
                             '_deltarel': 'S',
                             'impl': 'auxonly'}):
                    if (Q.getref((v4_x, v4_z)) == 1):
                        Q.remove((v4_x, v4_z))
                    else:
                        Q.decref((v4_x, v4_z))
            
            with MAINT(Q, 'after', 'R.add((1, 2))'):
                R.add((1, 2))
                _maint_Q_R_add((1, 2))
            print(setmatch(Q, 'bu', x))
            ''')
        exp_maintcomps = [
            L.pe('''COMP({(v1_x, v1_y, v1_z)
                    for (v1_x, v1_y) in deltamatch(R, 'bb', _e, 1)
                    for (v1_y, v1_z) in S},
                    [], {'_deltaelem': '_e',
                         '_deltalhs': '(v1_x, v1_y)',
                         '_deltaop': 'add',
                         '_deltarel': 'R',
                         'impl': 'auxonly'})'''),
            L.pe('''COMP({(v2_x, v2_y, v2_z)
                    for (v2_x, v2_y) in deltamatch(R, 'bb', _e, 1)
                    for (v2_y, v2_z) in S},
                    [], {'_deltaelem': '_e',
                         '_deltalhs': '(v2_x, v2_y)',
                         '_deltaop': 'remove',
                         '_deltarel': 'R',
                         'impl': 'auxonly'})'''),
            L.pe('''COMP({(v3_x, v3_y, v3_z)
                    for (v3_x, v3_y) in R
                    for (v3_y, v3_z) in deltamatch(S, 'bb', _e, 1)},
                    [], {'_deltaelem': '_e',
                         '_deltalhs': '(v3_y, v3_z)',
                         '_deltaop': 'add',
                         '_deltarel': 'S',
                         'impl': 'auxonly'})'''),
            L.pe('''COMP({(v4_x, v4_y, v4_z)
                    for (v4_x, v4_y) in R
                    for (v4_y, v4_z) in deltamatch(S, 'bb', _e, 1)},
                    [], {'_deltaelem': '_e',
                         '_deltalhs': '(v4_y, v4_z)',
                         '_deltaop': 'remove',
                         '_deltarel': 'S',
                         'impl': 'auxonly'})'''),
        ]
        
        self.assertEqual(tree, exp_tree)
        self.assertEqual(maintcomps, exp_maintcomps)
        
        self.assertEqual(exp_maintcomps[0].options['impl'], 'auxonly')
    
    def test_inc_relcomp_uset(self):
        comp = L.pe('COMP({z for (x, y) in R for (y, z) in S}, [x], '
                            '{"uset_mode": "all"})')
        tree = L.p('''
            T.add(e)
            print(COMP)
            ''', subst={'COMP': comp})
        tree = inc_relcomp(tree, self.manager, comp, 'Q')
        
        exp_tree = L.p('''
            Q = RCSet()
            def _maint_Q__U_Q_add(_e):
                for (v1_x, v1_y, v1_z) in COMP({(v1_x, v1_y, v1_z)
                        for v1_x in deltamatch(_U_Q, 'b', _e, 1)
                        for (v1_x, v1_y) in R for (v1_y, v1_z) in S},
                        [], {'_deltaelem': '_e',
                             '_deltalhs': 'v1_x',
                             '_deltaop': 'add',
                             '_deltarel': '_U_Q',
                             'impl': 'auxonly'}):
                    if ((v1_x, v1_z) not in Q):
                        Q.add((v1_x, v1_z))
                    else:
                        Q.incref((v1_x, v1_z))
            
            def _maint_Q__U_Q_remove(_e):
                for (v2_x, v2_y, v2_z) in COMP({(v2_x, v2_y, v2_z)
                        for v2_x in deltamatch(_U_Q, 'b', _e, 1)
                        for (v2_x, v2_y) in R
                        for (v2_y, v2_z) in S},
                        [], {'_deltaelem': '_e',
                             '_deltalhs': 'v2_x',
                             '_deltaop': 'remove',
                             '_deltarel': '_U_Q',
                             'impl': 'auxonly'}):
                    if (Q.getref((v2_x, v2_z)) == 1):
                        Q.remove((v2_x, v2_z))
                    else:
                        Q.decref((v2_x, v2_z))
            
            def _maint_Q_R_add(_e):
                for (v3_x, v3_y, v3_z) in COMP({(v3_x, v3_y, v3_z)
                        for v3_x in _U_Q
                        for (v3_x, v3_y) in deltamatch(R, 'bb', _e, 1)
                        for (v3_y, v3_z) in S},
                        [], {'_deltaelem': '_e',
                             '_deltalhs': '(v3_x, v3_y)',
                             '_deltaop': 'add',
                             '_deltarel': 'R',
                             'impl': 'auxonly'}):
                    if ((v3_x, v3_z) not in Q):
                        Q.add((v3_x, v3_z))
                    else:
                        Q.incref((v3_x, v3_z))
            
            def _maint_Q_R_remove(_e):
                for (v4_x, v4_y, v4_z) in COMP({(v4_x, v4_y, v4_z)
                        for v4_x in _U_Q
                        for (v4_x, v4_y) in deltamatch(R, 'bb', _e, 1)
                        for (v4_y, v4_z) in S},
                        [], {'_deltaelem': '_e',
                             '_deltalhs': '(v4_x, v4_y)',
                             '_deltaop': 'remove',
                             '_deltarel': 'R',
                             'impl': 'auxonly'}):
                    if (Q.getref((v4_x, v4_z)) == 1):
                        Q.remove((v4_x, v4_z))
                    else:
                        Q.decref((v4_x, v4_z))
            
            def _maint_Q_S_add(_e):
                for (v5_x, v5_y, v5_z) in COMP({(v5_x, v5_y, v5_z)
                        for v5_x in _U_Q
                        for (v5_x, v5_y) in R
                        for (v5_y, v5_z) in deltamatch(S, 'bb', _e, 1)},
                        [], {'_deltaelem': '_e',
                             '_deltalhs': '(v5_y, v5_z)',
                             '_deltaop': 'add',
                             '_deltarel': 'S',
                             'impl': 'auxonly'}):
                    if ((v5_x, v5_z) not in Q):
                        Q.add((v5_x, v5_z))
                    else:
                        Q.incref((v5_x, v5_z))
            
            def _maint_Q_S_remove(_e):
                for (v6_x, v6_y, v6_z) in COMP({(v6_x, v6_y, v6_z)
                        for v6_x in _U_Q
                        for (v6_x, v6_y) in R
                        for (v6_y, v6_z) in deltamatch(S, 'bb', _e, 1)},
                        [], {'_deltaelem': '_e',
                             '_deltalhs': '(v6_y, v6_z)',
                             '_deltaop': 'remove',
                             '_deltarel': 'S',
                             'impl': 'auxonly'}):
                    if (Q.getref((v6_x, v6_z)) == 1):
                        Q.remove((v6_x, v6_z))
                    else:
                        Q.decref((v6_x, v6_z))
            
            _U_Q = RCSet()
            _UEXT_Q = Set()
            def demand_Q(x):
                '{(x, z) : x in _U_Q, (x, y) in R, (y, z) in S}'
                if (x not in _U_Q):
                    with MAINT(Q, 'after', '_U_Q.add(x)'):
                        _U_Q.add(x)
                        _maint_Q__U_Q_add(x)
                else:
                    _U_Q.incref(x)
            
            def undemand_Q(x):
                '{(x, z) : x in _U_Q, (x, y) in R, (y, z) in S}'
                if (_U_Q.getref(x) == 1):
                    with MAINT(Q, 'before', '_U_Q.remove(x)'):
                        _maint_Q__U_Q_remove(x)
                        _U_Q.remove(x)
                else:
                    _U_Q.decref(x)
            
            def query_Q(x):
                '{(x, z) : x in _U_Q, (x, y) in R, (y, z) in S}'
                if (x not in _UEXT_Q):
                    _UEXT_Q.add(x)
                    demand_Q(x)
                return True
            
            T.add(e)
            print(DEMQUERY(Q, [x], setmatch(Q, 'bu', x)))
            ''')
        
        self.assertEqual(tree, exp_tree)
    
    def test_auxonly_relcomp(self):
        comp1 = L.pe(
            'COMP({(y, z) for (x, y) in R for (y, z) in S}, [x], {})')
        comp2 = L.pe(
            'COMP({z for (x, y) in R for (y, z) in S}, [x], {})')
        tree = L.p('''
            R.add((1, 2))
            for (y, z) in COMP1:
                pass
            for z in COMP2:
                pass
            ''', subst={'COMP1': comp1,
                        'COMP2': comp2})
        tree = impl_auxonly_relcomp(tree, self.manager, comp1, 'Q1')
        tree = impl_auxonly_relcomp(tree, self.manager, comp2, 'Q2')
        
        exp_tree = L.p('''
            def query_Q2(x):
                'x -> {z : (x, y) in R, (y, z) in S}'
                result = set()
                for y in setmatch(R, 'bu', x):
                    for z in setmatch(S, 'bu', y):
                        if (z not in result):
                            result.add(z)
                return result
            
            R.add((1, 2))
            Comment('Iterate x -> {(y, z) : (x, y) in R, (y, z) in S}')
            for y in setmatch(R, 'bu', x):
                for z in setmatch(S, 'bu', y):
                    pass
            for z in query_Q2(x):
                pass
            ''')
        
        self.assertEqual(tree, exp_tree)
    
    def test_patternize_depatternize(self):
        orig_comp = L.pe('COMP({z for (x_2, y) in R if x == x_2 for (y_2, z) in S if y == y_2}, [x], {})')
        exp_comp = L.pe('COMP({z for (x, y) in R for (y, z) in S}, [x], {})')
        
        comp = patternize_comp(orig_comp, self.manager.factory)
        self.assertEqual(comp, exp_comp)
        comp = depatternize_comp(comp, self.manager.factory)
        self.assertEqual(comp, orig_comp)
    
    def test_get_subquery_demnames(self):
        comp = L.pe('''
            COMP({(x, y, v) for (x, y) in U for (y, z) in S
                   for w in DEMQUERY(query1, [x, z], Q1)
                   for v in DEMQUERY(query2, [y, w], Q2)}, [], {})
            ''')
        spec = CompSpec.from_comp(comp, self.manager.factory)
        res = get_subquery_demnames(spec)
        
        exp_spec1 = CompSpec.from_comp(L.pe('''
            COMP({(x, z) for (x, y) in U for (y, z) in S}, [], {})
            '''), self.manager.factory)
        exp_spec2 = CompSpec.from_comp(L.pe('''
            COMP({(y, w) for (x, y) in U for (y, z) in S for w in Q1}, [], {})
            '''), self.manager.factory)
        exp_res = [
            ('query1', exp_spec1),
            ('query2', exp_spec2),
        ]
        
        self.assertEqual(res, exp_res)
    
    def test_split_eqwild_clauses(self):
        comp = L.pe('''
            COMP({x for x in S for (x, x, _) in E}, [], {})
            ''')
        comp = split_eqwild_clauses(self.manager, comp)
        exp_comp = L.pe('''
            COMP({x for x in S for x in
                COMP({v1_x for (v1_x, v1_x, v1_w1) in E}, [], {})},
            [], {})
            ''')
        self.assertEqual(comp, exp_comp)


if __name__ == '__main__':
    unittest.main()
