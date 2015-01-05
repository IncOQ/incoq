"""Unit tests for auxmap.py."""


import unittest

import oinc.incast as L
from oinc.set import Mask, AuxmapSpec
from oinc.central import CentralCase
from oinc.set.auxmap import *
from oinc.set.auxmap import make_auxmap_maint_code


class TestAuxmap(CentralCase):
    
    def mainttest_helper(self, maskstr):
        spec = AuxmapSpec('R', Mask(maskstr))
        
        # Make the prefix '_' so it's easier to read/type.
        self.manager.namegen.next_prefix = lambda: '_'
        
        code = make_auxmap_maint_code(self.manager, spec, L.ln('e'), 'add')
        
        return code
    
    def test_auxmap_inv_maint(self):
        tree = self.mainttest_helper('bubuu')
        
        exp_tree = L.pc('''
            (_1, _2, _3, _4, _5) = e
            if ((_1, _3) not in _m_R_bubuu):
                _m_R_bubuu.assignkey((_1, _3), set())
            _m_R_bubuu[(_1, _3)].add((_2, _4, _5))
            ''')
        
        self.assertEqual(tree, exp_tree)
    
    def test_auxmap_inv_maint_fancy(self):
        tree = self.mainttest_helper('u1b3ww')
        
        exp_tree = L.pc('''
            (_1, _2, _3, _4, _5, _6) = e
            if ((_1 == _2) and (_3 == _4)):
                if (_3 not in _m_R_u1b3ww):
                    _m_R_u1b3ww.assignkey(_3, RCSet())
                if (_1 not in _m_R_u1b3ww[_3]):
                    _m_R_u1b3ww[_3].add(_1)
                else:
                    _m_R_u1b3ww[_3].incref(_1)
            ''')
        
        self.assertEqual(tree, exp_tree)
    
    def test_auxmap_inv_maint_allbound(self):
        tree = self.mainttest_helper('bb')
        
        exp_tree = L.pc('''
            (_1, _2) = e
            if ((_1, _2) not in _m_R_bb):
                _m_R_bb.assignkey((_1, _2), set())
            _m_R_bb[(_1, _2)].add(())
            ''')
        
        self.assertEqual(tree, exp_tree)
    
    def test_transform_degenerate_allunbound(self):
        tree = self.mainttest_helper('uu')
        
        exp_tree = L.pc('''
            (_1, _2) = e
            if (() not in _m_R_uu):
                _m_R_uu.assignkey((), set())
            _m_R_uu[()].add((_1, _2))
            ''')
        
        self.assertEqual(tree, exp_tree)
    
    def test_inc_relmatch(self):
        spec = AuxmapSpec('R', Mask('bu'))
        
        tree = L.p('''
            R.add((1, 2))
            print(setmatch(R, 'bu', 1))
            ''')
        
        tree = inc_relmatch(tree, self.manager, spec)
        
        exp_tree = L.p('''
            _m_R_out = Map()
            def _maint__m_R_out_add(_e):
                (v1_1, v1_2) = _e
                if (v1_1 not in _m_R_out):
                    _m_R_out.assignkey(v1_1, set())
                _m_R_out[v1_1].add(v1_2)
            
            def _maint__m_R_out_remove(_e):
                (v2_1, v2_2) = _e
                _m_R_out[v2_1].remove(v2_2)
                if _m_R_out[v2_1].isempty():
                    _m_R_out.delkey(v2_1)
            
            with MAINT(_m_R_out, 'after', 'R.add((1, 2))'):
                R.add((1, 2))
                _maint__m_R_out_add((1, 2))
            print(_m_R_out.imglookup(1))
            ''')
        
        self.assertEqual(tree, exp_tree)
    
    def test_queryfinder(self):
        code = L.p('''
            print(setmatch(R, 'bu', a))
            print(setmatch(R, 'ub', a))
            print(setmatch(R, 'bu', b))
            print(setmatch({(1, 2)}, 'bu', 1))
            S.add((3, 4, 5))
            print(S.smlookup('bbu', (3, 4)))
            ''')
        auxmap_specs = RelmatchQueryFinder.run(code)
        
        exp_specs = {AuxmapSpec('R', Mask('bu')),
                     AuxmapSpec('R', Mask('ub')),
                     AuxmapSpec('S', Mask('bbu'))}
        
        self.assertCountEqual(auxmap_specs, exp_specs)
    
    def test_deltamatch(self):
        code = L.p('deltamatch(R, "bbw", e, 1)')
        code = DeltaMatchRewriter.run(code)
        exp_code = L.p('''
            ({e} if (setmatch(R, 'bbw', (e[0], e[1])).getref(()) == 1)
                 else {})
            ''')
        self.assertEqual(code, exp_code)
    
    def test_transform(self):
        tree = L.p('''
            R.add((1, 2))
            R.remove((1, 2))
            print(setmatch(R, 'bu', a))
            print(setmatch(R, 'ub', a))
            print(setmatch(R, 'bu', b))
            print(setmatch({(1, 2)}, 'bu', 1))
            S.add((3, 4, 5))
            print(S.smlookup('bbu', (3, 4)))
            ''')
        
        tree = inc_all_relmatch(tree, self.manager)
        
        exp_tree = L.p('''
            _m_S_bbu = Map()
            def _maint__m_S_bbu_add(_e):
                (v5_1, v5_2, v5_3) = _e
                if ((v5_1, v5_2) not in _m_S_bbu):
                    _m_S_bbu.assignkey((v5_1, v5_2), set())
                _m_S_bbu[(v5_1, v5_2)].add(v5_3)
            
            def _maint__m_S_bbu_remove(_e):
                (v6_1, v6_2, v6_3) = _e
                _m_S_bbu[(v6_1, v6_2)].remove(v6_3)
                if _m_S_bbu[(v6_1, v6_2)].isempty():
                    _m_S_bbu.delkey((v6_1, v6_2))
            
            _m_R_in = Map()
            def _maint__m_R_in_add(_e):
                (v3_1, v3_2) = _e
                if (v3_2 not in _m_R_in):
                    _m_R_in.assignkey(v3_2, set())
                _m_R_in[v3_2].add(v3_1)
            
            def _maint__m_R_in_remove(_e):
                (v4_1, v4_2) = _e
                _m_R_in[v4_2].remove(v4_1)
                if _m_R_in[v4_2].isempty():
                    _m_R_in.delkey(v4_2)
            
            _m_R_out = Map()
            def _maint__m_R_out_add(_e):
                (v1_1, v1_2) = _e
                if (v1_1 not in _m_R_out):
                    _m_R_out.assignkey(v1_1, set())
                _m_R_out[v1_1].add(v1_2)
            
            def _maint__m_R_out_remove(_e):
                (v2_1, v2_2) = _e
                _m_R_out[v2_1].remove(v2_2)
                if _m_R_out[v2_1].isempty():
                    _m_R_out.delkey(v2_1)
            with MAINT(_m_R_out, 'after', 'R.add((1, 2))'):
                with MAINT(_m_R_in, 'after', 'R.add((1, 2))'):
                    R.add((1, 2))
                    _maint__m_R_in_add((1, 2))
                _maint__m_R_out_add((1, 2))
            with MAINT(_m_R_out, 'before', 'R.remove((1, 2))'):
                _maint__m_R_out_remove((1, 2))
                with MAINT(_m_R_in, 'before', 'R.remove((1, 2))'):
                    _maint__m_R_in_remove((1, 2))
                    R.remove((1, 2))
            print(_m_R_out.imglookup(a))
            print(_m_R_in.imglookup(a))
            print(_m_R_out.imglookup(b))
            print(setmatch({(1, 2)}, 'bu', 1))
            with MAINT(_m_S_bbu, 'after', 'S.add((3, 4, 5))'):
                S.add((3, 4, 5))
                _maint__m_S_bbu_add((3, 4, 5))
            print(_m_S_bbu.singlelookup((3, 4)))
            ''')
        
        self.assertEqual(tree, exp_tree)


if __name__ == '__main__':
    unittest.main()
