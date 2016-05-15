"""Unit tests for trans.py."""


import unittest

from incoq.compiler.incast import L
from incoq.compiler.type import T
from incoq.compiler.symbol import S, N
from incoq.compiler.auxmap.trans import *
from incoq.compiler.auxmap.trans import (make_imgadd, make_imgremove,
                                     make_auxmap_maint_func,
                                     make_setfrommap_maint_func,
                                     make_wrap_maint_func)


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
    
    def test_auxmap_maint_add(self):
        auxmap = AuxmapInvariant('m', 'R', L.mask('bu'), False, False)
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
    
    def test_auxmap_maint_remove(self):
        auxmap = AuxmapInvariant('m', 'R', L.mask('bu'), False, False)
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
    
    def test_auxmap_maint_add_unwrap(self):
        auxmap = AuxmapInvariant('m', 'R', L.mask('bu'), True, True)
        func = make_auxmap_maint_func(N.fresh_name_generator(),
                                      auxmap, L.SetAdd())
        exp_func = L.Parser.ps('''
            def _maint_m_for_R_add(_elem):
                (_elem_v1, _elem_v2) = _elem
                _v1_key = _elem_v1
                _v1_value = _elem_v2
                if (_v1_key not in m):
                    _v2 = Set()
                    m.mapassign(_v1_key, _v2)
                m[_v1_key].add(_v1_value)
            ''')
        self.assertEqual(func, exp_func)
    
    def test_setfrommap_maint_assign(self):
        setfrommap = SetFromMapInvariant('R', 'M', L.mask('bu'))
        func = make_setfrommap_maint_func(N.fresh_name_generator(),
                                          setfrommap, 'assign')
        exp_func = L.Parser.ps('''
            def _maint_R_for_M_assign(_key, _val):
                (_key_v1,) = _key
                _v1_elem = (_key_v1, _val)
                R.reladd(_v1_elem)
            ''')
        self.assertEqual(func, exp_func)
    
    def test_setfrommap_maint_delete(self):
        setfrommap = SetFromMapInvariant('R', 'M', L.mask('bu'))
        func = make_setfrommap_maint_func(N.fresh_name_generator(),
                                          setfrommap, 'delete')
        exp_func = L.Parser.ps('''
            def _maint_R_for_M_delete(_key):
                _val = M[_key]
                (_key_v1,) = _key
                _v1_elem = (_key_v1, _val)
                R.relremove(_v1_elem)
            ''')
        self.assertEqual(func, exp_func)
    
    def test_wrap_maint(self):
        # Wrap.
        wrapinv = WrapInvariant('Q', 'R', False)
        func = make_wrap_maint_func(N.fresh_name_generator(),
                                    wrapinv, L.SetAdd())
        exp_func = L.Parser.ps('''
            def _maint_Q_for_R_add(_elem):
                _v1_v = (_elem,)
                Q.reladd(_v1_v)
            ''')
        self.assertEqual(func, exp_func)
        
        # Unwrap.
        wrapinv = WrapInvariant('Q', 'R', True)
        func = make_wrap_maint_func(N.fresh_name_generator(),
                                    wrapinv, L.SetAdd())
        exp_func = L.Parser.ps('''
            def _maint_Q_for_R_add(_elem):
                _v1_v = index(_elem, 0)
                Q.reladd(_v1_v)
            ''')
        self.assertEqual(func, exp_func)
    
    def test_invariant_finder(self):
        tree = L.Parser.p('''
            def f():
                R.imglookup('bu', (x,))
                R.imglookup('bu', (y,))
                M.setfrommap('bu')
                R.imglookup('ubb', (y, z))
                S.imglookup('bu', (x,))
                unwrap(R.imglookup('ubb', (y, z)))
                unwrap(S)
                wrap(R)
            ''')
        auxmaps, setfrommaps, wraps = InvariantFinder.run(tree)
        exp_auxmaps = [
            AuxmapInvariant('R_bu', 'R', L.mask('bu'), True, False),
            AuxmapInvariant('R_ubb', 'R', L.mask('ubb'), False, False),
            AuxmapInvariant('S_bu', 'S', L.mask('bu'), True, False),
            AuxmapInvariant('R_ubb', 'R', L.mask('ubb'), False, True),
        ]
        exp_setfrommaps = [
            SetFromMapInvariant('SM', 'M', L.mask('bu')),
        ]
        exp_wraps = [
            WrapInvariant('S_unwrapped', 'S', True),
            WrapInvariant('R_wrapped', 'R', False),
        ]
        self.assertSequenceEqual(list(auxmaps), exp_auxmaps)
        self.assertSequenceEqual(list(setfrommaps), exp_setfrommaps)
        self.assertSequenceEqual(list(wraps), exp_wraps)
    
    def test_invariant_transformer(self):
        auxmaps = [
            AuxmapInvariant('R_bu', 'R', L.mask('bu'), True, False),
            AuxmapInvariant('R_bu_2', 'R', L.mask('bu'), False, True),
        ]
        setfrommaps = [
            SetFromMapInvariant('S', 'M', L.mask('bu')),
        ]
        wraps = [
            WrapInvariant('Q1', 'R', False),
            WrapInvariant('Q2', 'R', True),
        ]
        tree = L.Parser.p('''
            def f():
                elem = (1, 2)
                R.reladd(elem)
                print(R.imglookup('bu', (x,)))
                S.reladd(elem)
                print(S.imglookup('bu', (x,)))
                R.relinccount(elem)
                R.relclear()
                M.mapassign(k, v)
                M.mapdelete(k)
                M.mapclear()
                print(M.setfrommap('bu'))
                print(unwrap(R.imglookup('bu', (x,))))
                for x in unwrap(R.imglookup('bu', (x,))):
                    pass
            ''')
        trans = InvariantTransformer(N.fresh_name_generator(),
                                     auxmaps, setfrommaps, wraps)
        tree = trans.process(tree)
        exp_maint_funcs = [
            '_maint_R_bu_for_R_add',
            '_maint_R_bu_for_R_remove',
            '_maint_R_bu_2_for_R_add',
            '_maint_R_bu_2_for_R_remove',
            '_maint_S_for_M_assign',
            '_maint_S_for_M_delete',
            '_maint_Q1_for_R_add',
            '_maint_Q1_for_R_remove',
            '_maint_Q2_for_R_add',
            '_maint_Q2_for_R_remove',
        ]
        exp_tree = L.Parser.p('''
            def _maint_R_bu_for_R_add(_elem):
                (_elem_v1, _elem_v2) = _elem
                _v1_key = _elem_v1
                _v1_value = (_elem_v2,)
                if (_v1_key not in R_bu):
                    _v2 = Set()
                    R_bu.mapassign(_v1_key, _v2)
                R_bu[_v1_key].add(_v1_value)
            
            def _maint_R_bu_for_R_remove(_elem):
                (_elem_v1, _elem_v2) = _elem
                _v3_key = _elem_v1
                _v3_value = (_elem_v2,)
                R_bu[_v3_key].remove(_v3_value)
                if (len(R_bu[_v3_key]) == 0):
                    R_bu.mapdelete(_v3_key)
            
            def _maint_R_bu_2_for_R_add(_elem):
                (_elem_v1, _elem_v2) = _elem
                _v4_key = (_elem_v1,)
                _v4_value = _elem_v2
                if (_v4_key not in R_bu_2):
                    _v5 = Set()
                    R_bu_2.mapassign(_v4_key, _v5)
                R_bu_2[_v4_key].add(_v4_value)
            
            def _maint_R_bu_2_for_R_remove(_elem):
                (_elem_v1, _elem_v2) = _elem
                _v6_key = (_elem_v1,)
                _v6_value = _elem_v2
                R_bu_2[_v6_key].remove(_v6_value)
                if (len(R_bu_2[_v6_key]) == 0):
                    R_bu_2.mapdelete(_v6_key)
            
            def _maint_S_for_M_assign(_key, _val):
                (_key_v1,) = _key
                _v7_elem = (_key_v1, _val)
                S.reladd(_v7_elem)
            
            def _maint_S_for_M_delete(_key):
                _val = M[_key]
                (_key_v1,) = _key
                _v8_elem = (_key_v1, _val)
                S.relremove(_v8_elem)
            
            def _maint_Q1_for_R_add(_elem):
                _v9_v = (_elem,)
                Q1.reladd(_v9_v)
            
            def _maint_Q1_for_R_remove(_elem):
                _v10_v = (_elem,)
                Q1.relremove(_v10_v)
            
            def _maint_Q2_for_R_add(_elem):
                _v11_v = index(_elem, 0)
                Q2.reladd(_v11_v)
            
            def _maint_Q2_for_R_remove(_elem):
                _v12_v = index(_elem, 0)
                Q2.relremove(_v12_v)
            
            def f():
                elem = (1, 2)
                R.reladd(elem)
                _maint_R_bu_for_R_add(elem)
                _maint_R_bu_2_for_R_add(elem)
                _maint_Q1_for_R_add(elem)
                _maint_Q2_for_R_add(elem)
                print(R_bu[x] if x in R_bu else Set())
                S.reladd(elem)
                print(S.imglookup('bu', (x,)))
                R.relinccount(elem)
                Q2.relclear()
                Q1.relclear()
                R_bu_2.mapclear()
                R_bu.mapclear()
                R.relclear()
                M.mapassign(k, v)
                _maint_S_for_M_assign(k, v)
                _maint_S_for_M_delete(k)
                M.mapdelete(k)
                S.relclear()
                M.mapclear()
                print(S)
                print(R_bu_2[(x,)] if (x,) in R_bu_2 else Set())
                for x in R_bu_2[(x,)] if (x,) in R_bu_2 else ():
                    pass
            ''')
        self.assertSequenceEqual(list(trans.maint_funcs), exp_maint_funcs)
        self.assertEqual(tree, exp_tree)
    
    def test_make_auxmap_type(self):
        auxmapinv = AuxmapInvariant('M', 'R', L.mask('bbu'), False, True)
        
        # Normal case.
        t_rel = T.Set(T.Tuple([T.Number, T.Top, T.String]))
        t = make_auxmap_type(auxmapinv, t_rel)
        exp_t = T.Map(T.Tuple([T.Number, T.Top]),
                      T.Set(T.String))
        self.assertEqual(t, exp_t)
        
        # Bottom case.
        t_rel = T.Set(T.Bottom)
        t = make_auxmap_type(auxmapinv, t_rel)
        exp_t = T.Map(T.Tuple([T.Bottom, T.Bottom]),
                      T.Set(T.Bottom))
        self.assertEqual(t, exp_t)
        
        # Other case, incorrect arity.
        t_rel = T.Set(T.Tuple([T.Number]))
        t = make_auxmap_type(auxmapinv, t_rel)
        exp_t = T.Map(T.Top, T.Top)
        self.assertEqual(t, exp_t)
    
    def test_make_setfrommap_type(self):
        mask = L.mask('bub')
        
        # Normal case.
        t_map = T.Map(T.Tuple([T.Number, T.Top]), T.String)
        t = make_setfrommap_type(mask, t_map)
        exp_t = T.Set(T.Tuple([T.Number, T.String, T.Top]))
        self.assertEqual(t, exp_t)
        
        # Bottom case.
        t_map = T.Map(T.Bottom, T.Bottom)
        t = make_setfrommap_type(mask, t_map)
        exp_t = T.Set(T.Tuple([T.Bottom, T.Bottom, T.Bottom]))
        self.assertEqual(t, exp_t)
        
        # Other case, incorrect arity.
        t_map = T.Map(T.Tuple([T.Number]), T.Tuple([]))
        t = make_setfrommap_type(mask, t_map)
        exp_t = T.Set(T.Top)
        self.assertEqual(t, exp_t)
    
    def test_make_wrap_type(self):
        wrapinv1 = WrapInvariant('Q1', 'R', False)
        wrapinv2 = WrapInvariant('Q2', 'R', True)
        
        # Normal case.
        
        t_oper = T.Set(T.Number)
        t = make_wrap_type(wrapinv1, t_oper)
        exp_t = T.Set(T.Tuple([T.Number]))
        self.assertEqual(t, exp_t)
        
        t_oper = T.Set(T.Tuple([T.Number]))
        t = make_wrap_type(wrapinv2, t_oper)
        exp_t = T.Set(T.Number)
        self.assertEqual(t, exp_t)
    
    def test_define_map(self):
        symtab = S.SymbolTable()
        symtab.define_relation(
            'R', type=T.Set(T.Tuple([T.Number, T.Top, T.String])))
        symtab.define_relation('S')
        symtab.define_relation('T', type=T.Set(T.Top))
        R_auxmap = AuxmapInvariant('R_bbu', 'R', L.mask('bbu'), False, False)
        S_auxmap = AuxmapInvariant('S_bbu', 'S', L.mask('bbu'), False, False)
        T_auxmap = AuxmapInvariant('T_bbu', 'T', L.mask('bbu'), False, False)
        
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
    
    def test_define_set(self):
        symtab = S.SymbolTable()
        symtab.define_map(
            'M', type=T.Map(T.Tuple([T.Number, T.Top]), T.String))
        inv = SetFromMapInvariant('S', 'M', L.mask('bbu'))
        
        define_set(inv, symtab)
        relsym = symtab.get_relations()['S']
        self.assertEqual(
            relsym.type,
            T.Set(T.Tuple([T.Number, T.Top, T.String])))


if __name__ == '__main__':
    unittest.main()
