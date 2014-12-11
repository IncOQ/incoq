"""Unit tests for objcomp.py."""


import unittest

from util.collections import OrderedSet
from oinc.comp import CompSpec
import oinc.incast as L

from .objclause import ObjClauseFactory_Mixin as CF
from .objcomp import *
from .objcomp import (RetrievalReplacer, RetrievalExpander,
                      flatten_retrievals, unflatten_retrievals,
                      flatten_sets, unflatten_sets)


class ObjcompCase(unittest.TestCase):
    
    def test_retrieval_replacer(self):
        field_namer = lambda lhs, rhs: 'f_' + lhs + '_' + rhs
        map_namer = lambda lhs, rhs: 'm_' + lhs + '_' + rhs
        
        tree = L.pe('a.b[c.d].e + a[b[c]]')
        replacer = RetrievalReplacer(field_namer, map_namer)
        tree = replacer.process(tree)
        field_repls = replacer.field_repls
        map_repls = replacer.map_repls
        
        exp_tree = L.pe('f_m_f_a_b_f_c_d_e + m_a_m_b_c')
        exp_field_repls = [
            ('a', 'b', 'f_a_b'),
            ('c', 'd', 'f_c_d'),
            ('m_f_a_b_f_c_d', 'e', 'f_m_f_a_b_f_c_d_e'),
        ]
        exp_map_repls = [
            ('f_a_b', 'f_c_d', 'm_f_a_b_f_c_d'),
            ('b', 'c', 'm_b_c'),
            ('a', 'm_b_c', 'm_a_m_b_c'),
        ]
        
        self.assertEqual(tree, exp_tree)
        self.assertSequenceEqual(field_repls, exp_field_repls)
        self.assertSequenceEqual(map_repls, exp_map_repls)
    
    def test_retrieval_expander(self):
        tree = L.pe('f_f_m_a_b_c_d + foo')
        field_exps = {'f_f_m_a_b_c_d': ('f_m_a_b_c', 'd'),
                      'f_m_a_b_c': ('m_a_b', 'c')}
        map_exps = {'m_a_b': ('a', 'b')}
        tree = RetrievalExpander.run(tree, field_exps, map_exps)
        
        exp_tree = L.pe('a[b].c.d + foo')
        
        self.assertEqual(tree, exp_tree)
    
    def test_flatten_retrievals(self):
        comp = L.pe('COMP({x.a for x in S.b[c] if x.a > 5}, [S])')
        
        comp, seen_fields, seen_map = flatten_retrievals(comp)
        
        exp_comp = L.pe('''
            COMP({x_a for (S, S_b) in _F_b for (S_b, c, m_S_b_k_c) in _MAP
                      for x in m_S_b_k_c for (x, x_a) in _F_a
                      if x_a > 5}, [S])
            ''')
        exp_seen_fields = ['b', 'a']
        exp_seen_map = True
        
        self.assertEqual(comp, exp_comp)
        self.assertEqual(seen_fields, exp_seen_fields)
        self.assertEqual(seen_map, exp_seen_map)
    
    def test_unflatten_retrievals(self):
        comp = L.pe('''
            COMP({x_a for (S, S_b) in _F_b for (S_b, c, m_S_b_k_c) in _MAP
                      for x in m_S_b_k_c for (x, x_a) in _F_a
                      if x_a > 5}, [S])
            ''')
        comp = unflatten_retrievals(comp)
        
        exp_comp = L.pe('COMP({x.a for x in S.b[c] if x.a > 5}, [S])')
        
        self.assertEqual(comp, exp_comp) 
    
    def test_flatten_unflatten_sets(self):
        comp = L.pe(
            'COMP({x for (o, o_s) in _F_s for (o, o_t) in _F_t '
                    'for x in o_s if x in o_t if x in T}, [S, T])')
        
        flatcomp, use_mset = flatten_sets(comp, ['T'])
        
        exp_flatcomp = L.pe(
            'COMP({x for (o, o_s) in _F_s for (o, o_t) in _F_t '
                    'for (o_s, x) in _M if (o_t, x) in _M if x in T}, '
                 '[S, T])')
        
        self.assertEqual(flatcomp, exp_flatcomp)
        self.assertTrue(use_mset)
        
        unflatcomp = unflatten_sets(flatcomp)
        self.assertEqual(unflatcomp, comp)
    
    def test_pattern_unflatten(self):
        # Test that patternizing/depatternizing interacts well with
        # object clauses.
        
        comp = L.pe(
            'COMP({x for x in S if x in T for y in S '
                    'for y2 in x if y == y2}, '
                 '[S, T], {})')
        comp, _use_mset, _fields, _use_map = flatten_comp(comp, [])
        
        spec = CompSpec.from_comp(comp, CF)
        spec = spec.to_pattern()
        spec = spec.to_nonpattern()
        comp = spec.to_comp({})
        comp = unflatten_comp(comp)
        
        exp_comp = L.pe(
            'COMP({x for x in S if x in T for y in S if y in x}, '
                 '[S, T], {})')
        
        self.assertEqual(comp, exp_comp)
    
    def test_unflatten_subclause(self):
        # Make sure we don't do anything foolish when presented with
        # a subtractive enum.
        comp = L.pe(
            'COMP({z for (x, y) in _M for (y, z) in _M - {e}}, [])')
        comp = unflatten_comp(comp)
        exp_comp = L.pe(
            'COMP({z for y in x for (y, z) in _M - {e}}, [])')
        self.assertEqual(comp, exp_comp)


if __name__ == '__main__':
    unittest.main()
