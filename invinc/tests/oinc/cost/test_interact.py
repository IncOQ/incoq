"""Unit tests for interact.py."""


import unittest
from types import SimpleNamespace

from invinc.util.unify import unify
import invinc.compiler.incast as L
from invinc.compiler.set import Mask
from invinc.compiler.comp import CompSpec
from invinc.compiler.central import CentralCase
from invinc.compiler.cost.cost import *
from invinc.compiler.cost.interact import *
from invinc.compiler.cost.interact import (make_dompath_eqs, split_resexp_vars,
                                         get_nondet_info, CostReinterpreter)


class DomainCase(CentralCase):
    
    def setUp(self):
        super().setUp()
        
        self.initsubst = {'R': ('<T>', ('<T>', 'x1', ('foo',)), 'y'),
                          'x': ('<T>', 'x1', ('foo',))}
        self.subst = add_domain_names(self.initsubst, {})
        self.domain_sizes = {'foo': NameCost('C')}
        self.cost_rules = {'R.1.1': NameCost('A'),
                           'R.2': NameCost('B')}
        self.trans = CostReinterpreter({}, self.subst, self.domain_sizes,
                                       self.cost_rules)
    
    def test_add_dompath_eqs(self):
        eqs = make_dompath_eqs(self.initsubst, ['R'])
        exp_eqs = [
            ('R', ('<T>', 'R.1', 'R.2')),
            ('R.1', ('<T>', 'R.1.1', 'R.1.2')),
            ('R.1.1', 'x1'),
            ('R.1.2', ('foo',)),
            ('R.2', 'y'),
        ]
        self.assertCountEqual(eqs, exp_eqs)
    
    def test_dompath_to_size(self):
        cost = self.trans.dompath_to_size('R')
        exp_cost_str = '((A*C)*B)'
        self.assertEqual(str(cost), exp_cost_str)
    
    def test_dompaths_for_mask(self):
        dompaths = self.trans.dompaths_for_mask('R', Mask.IN)
        exp_dompaths = ('R.1',)
        self.assertEqual(dompaths, exp_dompaths)
        
        dompaths = self.trans.dompaths_for_mask('R', Mask.UU)
        exp_dompaths = ('R.1', 'R.2')
        self.assertEqual(dompaths, exp_dompaths)
        
        dompaths = self.trans.dompaths_for_mask('R.2', Mask.U)
        exp_dompaths = ('R.2',)
        self.assertEqual(dompaths, exp_dompaths)
        
        dompaths = self.trans.dompaths_for_mask('R.2', Mask('b'))
        exp_dompaths = ()
        self.assertEqual(dompaths, exp_dompaths)
        
        dompaths = self.trans.dompaths_for_mask('S', Mask.IN)
        exp_dompaths = None
        self.assertEqual(dompaths, exp_dompaths)
    
    def test_reinterpreter_basic(self):
        # R + R_in
        cost = SumCost((NameCost('R'), IndefImgsetCost('R', Mask.IN)))
        cost = CostReinterpreter.run(cost, {}, self.subst, self.domain_sizes,
                                     self.cost_rules)
        exp_cost_str = '(((A*C)*B) + (A*C))'
        self.assertEqual(str(cost), exp_cost_str)

class CompCase(CentralCase):
    
    def test_resexp_vars(self):
        resexp = L.pe('(a + b, (c, d), (a, c, e, f))')
        bounds, unbounds = split_resexp_vars(resexp, Mask('bbu'))
        exp_bounds = {'c', 'd'}
        exp_unbounds = {'a', 'e', 'f'}
        self.assertEqual(bounds, exp_bounds)
        self.assertEqual(unbounds, exp_unbounds)
    
    def test_nondet_vars(self):
        comp = L.pe('COMP({(a, c, d) for (a, b) in R '
                                    'for (b, c) in _F_ '
                                    'for (c, b) in S '
                                    'for (c, d) in T '
                                    'for (d, e) in U}, [], {})')
        spec = CompSpec.from_comp(comp, self.manager.factory)
        result = get_nondet_info(spec, ['a'])
        exp_result = [
            ('R', Mask.OUT, {'b'}),
            ('_F_', Mask.BW, set()),
            ('S', Mask.BB, set()),
            ('T', Mask.OUT, {'d'}),
        ]
        self.assertEqual(result, exp_result)
    
    def test_reinterpreter_comp(self):
        comp1 = L.pe('COMP({(x, y, (x, z)) for (x, y) in S '
                                          'for (y, z) in T}, [], {})')
        comp2 = L.pe('COMP({(x, x) for (x, y) in U}, [], {})')
        spec1 = CompSpec.from_comp(comp1, self.manager.factory)
        spec2 = CompSpec.from_comp(comp2, self.manager.factory)
        
        # Dummy wrapper for what would be IncComp.
        Dummy1 = SimpleNamespace()
        Dummy1.spec = spec1
        Dummy2 = SimpleNamespace()
        Dummy2.spec = spec2
        invs = {'Q': Dummy1, 'S': Dummy2}
        # Boilerplate domain information regarding the comprehension.
        constrs = []
        constrs.extend(spec1.get_domain_constraints('Q'))
        constrs.extend(spec2.get_domain_constraints('S'))
        domain_subst = unify(constrs)
        domain_subst = add_domain_names(domain_subst, {})
        
        trans = CostReinterpreter(invs, domain_subst, {}, {})
        
        cost = NameCost('Q')
        cost = trans.process(cost)
        cost = normalize(cost)
        exp_cost_str = '(Q_x*Q_z)'
        self.assertEqual(str(cost), exp_cost_str)


if __name__ == '__main__':
    unittest.main()
