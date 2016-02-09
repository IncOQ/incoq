"""Unit tests for comp.py."""


import unittest

from incoq.mars.incast import L
from incoq.mars.symbol import S, N
from incoq.mars.auxmap import SetFromMapInvariant
from incoq.mars.aggr.comp import *


class CompCase(unittest.TestCase):
    
    def test_aggrmapreplacer(self):
        replacer = AggrMapReplacer(N.fresh_name_generator())
        
        result = replacer.process(L.Parser.pe('M[(i,)] + N[(j, k)]'))
        exp_result = (
            L.Parser.pe('_v1 + _v2'),
            [L.SetFromMapMember(['i', '_v1'], 'SM', 'M', L.mask('bu')),
             L.SetFromMapMember(['j', 'k', '_v2'], 'SN', 'N', L.mask('bbu'))],
        )
        self.assertEqual(result, exp_result)
        
        result = replacer.process(L.Parser.pe('M[(i,)] + O[(k,)]'))
        exp_result = (
            L.Parser.pe('_v1 + _v3'),
            [L.SetFromMapMember(['k', '_v3'], 'SO', 'O', L.mask('bu'))],
        )
        self.assertEqual(result, exp_result)
        
        exp_sfm_invs = [
            SetFromMapInvariant('SM', 'M', L.mask('bu')),
            SetFromMapInvariant('SN', 'N', L.mask('bbu')),
            SetFromMapInvariant('SO', 'O', L.mask('bu')),
        ]
        self.assertSequenceEqual(list(replacer.sfm_invs), exp_sfm_invs)
    
    def test_aggrmapcomprewriter(self):
        symtab = S.SymbolTable()
        comp = L.Parser.pe('{x for (x,) in REL(R) if M[(x,)] > 5}')
        symtab.define_query('Q', node=comp)
        tree = L.Parser.p('''
            def main():
                print(QUERY('Q', {x for (x,) in REL(R) if M[(x,)] > 5}))
            ''')
        tree, sfm_invs = AggrMapCompRewriter.run(tree, symtab)
        exp_tree = L.Parser.p('''
            def main():
                print(QUERY('Q', {x for (x,) in REL(R)
                                    for (x, _v1) in SETFROMMAP(SM, M, 'bu')
                                    if (_v1 > 5)}))
            ''')
        exp_sfm_invs = [
            SetFromMapInvariant('SM', 'M', L.mask('bu')),
        ]
        self.assertEqual(tree, exp_tree)
        self.assertSequenceEqual(list(sfm_invs), exp_sfm_invs)
    
    def test_transform_comps_with_maps(self):
        symtab = S.SymbolTable()
        comp = L.Parser.pe('{x for (x,) in REL(R) if M[(x,)] > 5}')
        symtab.define_map('M')
        symtab.define_query('Q', node=comp)
        tree = L.Parser.p('''
            def main():
                M.mapassign(k, v)
                print(QUERY('Q', {x for (x,) in REL(R) if M[(x,)] > 5}))
            ''')
        tree = transform_comps_with_maps(tree, symtab)
        exp_tree = L.Parser.p('''
            def _maint_SM_for_M_assign(_key, _val):
                (_key_v1,) = _key
                _v2_elem = (_key_v1, _val)
                SM.reladd(_v2_elem)
            
            def _maint_SM_for_M_delete(_key):
                _val = M[_key]
                (_key_v1,) = _key
                _v3_elem = (_key_v1, _val)
                SM.relremove(_v3_elem)
            
            def main():
                M.mapassign(k, v)
                _maint_SM_for_M_assign(k, v)
                print(QUERY('Q', {x for (x,) in REL(R)
                    for (x, _v1) in SETFROMMAP(SM, M, 'bu') if (_v1 > 5)}))
            ''')
        self.assertEqual(tree, exp_tree)


if __name__ == '__main__':
    unittest.main()
