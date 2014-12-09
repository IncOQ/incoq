"""Unit tests for tags.py."""


import unittest
from itertools import chain

import oinc.incast as L
from oinc.comp import AsymptoticOrderer, Join, DeltaInfo
from oinc.obj import ObjClauseFactory_Mixin

from .demclause import DemClauseFactory_Mixin

from .tags import *
from .tags import Tag, Filter, USet


#def format_structs(structs):
#    return [s.__dict__ for s in structs]


class CF(DemClauseFactory_Mixin, ObjClauseFactory_Mixin):
    pass


class TestTags(unittest.TestCase):
    
    def make_join(self, source, delta=None):
        join = Join.from_comp(L.pe(
                    'COMP({{... {}}}, [], {{}})'.format(source)),
                    CF)
        join = join._replace(delta=delta)
        return join
    
    def setUp(self):
        self.sample_join = self.make_join(
            'for (x, y) in R for (y, z) in R '
            'for (z, w) in DEMQUERY(foo, [z], T) for a in S')
        
        self.sample_exp_structs = [
            Tag(i=0, name='Q_Tx', var='x',
                lhs=('x', 'y'), rel='R'),
            Tag(i=0, name='Q_Ty1', var='y',
                lhs=('x', 'y'), rel='R'),
            Filter(i=1, name='Q_dR2',
                   lhs=('y', 'z'), rel='R',
                   preds=('Q_Ty1',)),
            Tag(i=1, name='Q_Ty2', var='y',
                lhs=('y', 'z'), rel='Q_dR2'),
            Tag(i=1, name='Q_Tz', var='z',
                lhs=('y', 'z'), rel='Q_dR2'),
            USet(i=2, name='foo', vars=('z',),
                 preds=('Q_Tz',), pred_clauses=None),
            Tag(i=2, name='Q_Tw', var='w',
                lhs=('z', 'w'), rel='T'),
            Tag(i=3, name='Q_Ta', var='a',
                lhs=('a',), rel='S'),
        ]
        
        self.subdem_nontag_uset = USet(
                i=2, name='foo', vars=('z',),
                preds=None, pred_clauses=self.sample_join.clauses[:2])
    
    def test_make_structures(self):
        ds = make_structures(self.sample_join.clauses, 'Q',
                             singletag=False, subdem_tags=True)
        structs = chain(ds.tags, ds.filters, ds.usets)
        self.assertCountEqual(structs, self.sample_exp_structs)
        
        ds = make_structures(self.sample_join.clauses, 'Q',
                             singletag=False, subdem_tags=False)
        self.assertIn(self.subdem_nontag_uset, ds.usets)
    
    def test_prune_structures(self):
        ds = make_structures(self.sample_join.clauses, 'Q',
                             singletag=False, subdem_tags=True)
        prune_structures(ds, [], subdem_tags=True)
        structs = chain(ds.tags, ds.filters, ds.usets)
        
        exp_names = ['Q_Ty1', 'Q_Tz', 'Q_dR2', 'foo']
        exp_structs = [s for s in self.sample_exp_structs
                         if s.name in exp_names]
        self.assertCountEqual(structs, exp_structs)
    
    def test_used_filters(self):
        join = self.make_join(
            'for (a, b) in U for (a, x) in _M '
            'for (b, x) in _M for (x, y) in _M')
        
        ds = make_structures(join.clauses, 'Q',
                             singletag=False, subdem_tags=True)
        
        join2 = self.make_join(
            'for (a, b) in U for (a, x) in _M '
            'for (b, x) in _M for (x, y) in {e}',
            DeltaInfo('_M', L.pe('e'), ('x', 'y'), 'add'))
        ordering = AsymptoticOrderer().get_order(
                                            enumerate(join2.clauses), [])
        
        used_indices = get_used_filters(ds, ordering, True)
        
        exp_used_indices = [1, 3]
        
        self.assertCountEqual(used_indices, exp_used_indices)
    
    def test_structures_to_comps(self):
        join = self.make_join(
            'for (x, y) in R for (y, z) in R for a in S')
        
        ds = make_structures(join.clauses, 'Q',
                             singletag=False, subdem_tags=True)
        prune_structures(ds, [1], subdem_tags=True)
        res = structures_to_comps(ds, CF)
        
        exp_res = [
            ('Q_Ty1', L.pe('COMP({y for (x, y) in R}, [], {})')),
            ('Q_dR2', L.pe('COMP({(y, z) for y in Q_Ty1 '
                                        'for (y, z) in R}, [], {})')),
        ]
        
        self.assertEqual(res, exp_res)
    
    def test_uset_to_comp(self):
        ds = make_structures(self.sample_join.clauses, 'Q',
                             singletag=False, subdem_tags=True)
        uset = ds.usets[0]
        comp = uset_to_comp(ds, uset, CF, self.sample_join.clauses[0])
        
        exp_comp = L.pe('COMP({z for z in Q_Tz}, [], {})')
        
        self.assertEqual(comp, exp_comp)
        
        ds = make_structures(self.sample_join.clauses, 'Q',
                             singletag=False, subdem_tags=False)
        uset = ds.usets[0]
        comp = uset_to_comp(ds, uset, CF, self.sample_join.clauses[0])
        
        exp_comp = L.pe('COMP({z for (x, y) in R for (y, z) in R}, [], {})')
        
        self.assertEqual(comp, exp_comp)
    
    def test_filter_comps(self):
        join = self.make_join(
            'for (a, b) in R for (b, c) in S for (c, d) in _M')
        comp1 = L.pe(
            'COMP({(a, b, c, d) for (a, b) in deltamatch(S, "bb", e, 1) for (b, c) in S for (c, d) in _M}, '
                 '[], {})')
        comp2 = L.pe(
            'COMP({(a, b, c, d) for (a, b) in R for (b, c) in S for (c, d) in deltamatch(_M, "bb", e, 1)}, '
                 '[], {})')
        
        tree = L.p('''
            print(COMP1)
            print(COMP2)
            ''', subst={'COMP1': comp1, 'COMP2': comp2})
        
        ds = make_structures(join.clauses, 'Q',
                             singletag=False, subdem_tags=True)
        tree, ds = filter_comps(tree, CF, ds,
                                [comp1, comp2],
                                True, augmented=False, subdem_tags=True)
        struct_names = [s.name for s in ds.tags + ds.filters + ds.usets]
        
        exp_tree = L.p('''
            print(COMP({(a, b, c, d) for (a, b) in deltamatch(S, 'bb', e, 1) for (b, c) in Q_dS for (c, d) in _M}, [], {}))
            print(COMP({(a, b, c, d) for (a, b) in R for (b, c) in Q_dS for (c, d) in deltamatch(Q_d_M, 'bb', e, 1) for (c, d) in Q_d_M}, [], {}))
            ''')
        exp_struct_names = ['Q_Tb1', 'Q_dS', 'Q_Tc', 'Q_d_M']
        
        self.assertEqual(tree, exp_tree)
        self.assertCountEqual(struct_names, exp_struct_names)


if __name__ == '__main__':
    unittest.main()
