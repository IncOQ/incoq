"""Unit tests for auxmap.py."""


import unittest

from incoq.mars.incast import L
from incoq.mars.type import T
from incoq.mars.symtab import N, SymbolTable
from incoq.mars.auxmap import *
from incoq.mars.auxmap import (make_imgadd, make_imgremove,
                               make_auxmap_maint_func)


class AuxmapCase(unittest.TestCase):
    
    def test_make_imgadd(self):
        code = make_imgadd(N.fresh_name_generator(), 'm', 'k', 'v')
        exp_code = L.Parser.pc('''
            if k not in m:
                _v1 = Set()
                m.mapassign(k, _v1)
            m[k].add(v)
            ''')
        self.assertEqual(code, exp_code)
    
    def test_make_imgremove(self):
        code = make_imgremove(N.fresh_name_generator(), 'm', 'k', 'v')
        exp_code = L.Parser.pc('''
            m[k].remove(v)
            if len(m[k]) == 0:
                m.mapdelete(k)
            ''')
        self.assertEqual(code, exp_code)
    
    def test_maint_add(self):
        auxmap = AuxmapInvariant('m', 'R', L.mask('bu'))
        func = make_auxmap_maint_func(N.fresh_name_generator(),
                                      auxmap, L.SetAdd())
        exp_func = L.Parser.ps('''
            def _maint_m_for_R_add(_elem):
                (_elem_v1, _elem_v2) = _elem
                _v1_key = (_elem_v1,)
                _v1_value = (_elem_v2,)
                if (_v1_key not in m):
                    _v2 = Set()
                    m.mapassign(_v1_key, _v2)
                m[_v1_key].add(_v1_value)
            ''')
        self.assertEqual(func, exp_func)
    
    def test_maint_remove(self):
        auxmap = AuxmapInvariant('m', 'R', L.mask('bu'))
        func = make_auxmap_maint_func(N.fresh_name_generator(),
                                      auxmap, L.SetRemove())
        exp_func = L.Parser.ps('''
            def _maint_m_for_R_remove(_elem):
                (_elem_v1, _elem_v2) = _elem
                _v1_key = (_elem_v1,)
                _v1_value = (_elem_v2,)
                m[_v1_key].remove(_v1_value)
                if (len(m[_v1_key]) == 0):
                    m.mapdelete(_v1_key)
            ''')
        self.assertEqual(func, exp_func)
    
    def test_imglookup_finder(self):
        tree = L.Parser.p('''
            def f():
                R.imglookup('bu', (x,))
                R.imglookup('bu', (x,))
                R.imglookup('ub', (y,))
                S.imglookup('bu', (x,))
            ''')
        auxmaps = AuxmapFinder.run(tree)
        exp_auxmaps = [
            AuxmapInvariant('R_bu', 'R', L.mask('bu')),
            AuxmapInvariant('R_ub', 'R', L.mask('ub')),
            AuxmapInvariant('S_bu', 'S', L.mask('bu')),
        ]
        self.assertEqual(auxmaps, exp_auxmaps)
    
    def test_auxmap_transformer(self):
        auxmaps = [
            AuxmapInvariant('R_bu', 'R', L.mask('bu')),
        ]
        tree = L.Parser.p('''
            def f():
                elem = (1, 2)
                R.reladd(elem)
                print(R.imglookup('bu', (x,)))
                S.reladd(elem)
                print(S.imglookup('bu', (x,)))
                R.relinccount(elem)
            ''')
        tree = AuxmapTransformer.run(tree, N.fresh_name_generator(), auxmaps)
        exp_tree = L.Parser.p('''
            def _maint_R_bu_for_R_add(_elem):
                (_elem_v1, _elem_v2) = _elem
                _v1_key = (_elem_v1,)
                _v1_value = (_elem_v2,)
                if (_v1_key not in R_bu):
                    _v2 = Set()
                    R_bu.mapassign(_v1_key, _v2)
                R_bu[_v1_key].add(_v1_value)
            
            def _maint_R_bu_for_R_remove(_elem):
                (_elem_v1, _elem_v2) = _elem
                _v3_key = (_elem_v1,)
                _v3_value = (_elem_v2,)
                R_bu[_v3_key].remove(_v3_value)
                if (len(R_bu[_v3_key]) == 0):
                    R_bu.mapdelete(_v3_key)
            
            def f():
                elem = (1, 2)
                R.reladd(elem)
                _maint_R_bu_for_R_add(elem)
                print(R_bu.get((x,), Set()))
                S.reladd(elem)
                print(S.imglookup('bu', (x,)))
                R.relinccount(elem)
            ''')
        self.assertEqual(tree, exp_tree)
    
    def test_make_auxmap_type(self):
        mask = L.mask('bbu')
        
        # Normal case.
        t_rel = T.Set(T.Tuple([T.Number, T.Top, T.String]))
        t = make_auxmap_type(mask, t_rel)
        exp_t = T.Map(T.Tuple([T.Number, T.Top]),
                      T.Set(T.Tuple([T.String])))
        self.assertEqual(t, exp_t)
        
        # Bottom case.
        t_rel = T.Set(T.Bottom)
        t = make_auxmap_type(mask, t_rel)
        exp_t = T.Map(T.Tuple([T.Bottom, T.Bottom]),
                      T.Set(T.Tuple([T.Bottom])))
        self.assertEqual(t, exp_t)
        
        # Other case, incorrect arity.
        t_rel = T.Set(T.Tuple([T.Number]))
        t = make_auxmap_type(mask, t_rel)
        exp_t = T.Map(T.Top, T.Top)
        self.assertEqual(t, exp_t)
    
    def test_define_map(self):
        symtab = SymbolTable()
        symtab.define_relation(
            'R', type=T.Set(T.Tuple([T.Number, T.Top, T.String])))
        symtab.define_relation('S')
        symtab.define_relation('T', type=T.Set(T.Top))
        R_auxmap = AuxmapInvariant('R_bbu', 'R', L.mask('bbu'))
        S_auxmap = AuxmapInvariant('S_bbu', 'S', L.mask('bbu'))
        T_auxmap = AuxmapInvariant('T_bbu', 'T', L.mask('bbu'))
        
        # Normal relation type.
        define_map(R_auxmap, symtab)
        mapsym = symtab.get_maps()['R_bbu']
        self.assertEqual(
            mapsym.type,
            T.Map(T.Tuple([T.Number, T.Top]),
                  T.Set(T.Tuple([T.String]))))
        
        # Bottom relation type.
        define_map(S_auxmap, symtab)
        mapsym = symtab.get_maps()['S_bbu']
        self.assertEqual(
            mapsym.type,
            T.Map(T.Tuple([T.Bottom, T.Bottom]),
                  T.Set(T.Tuple([T.Bottom]))))
        
        # Top relation type.
        define_map(T_auxmap, symtab)
        mapsym = symtab.get_maps()['T_bbu']
        self.assertEqual(
            mapsym.type,
            T.Map(T.Top, T.Top))


if __name__ == '__main__':
    unittest.main()
