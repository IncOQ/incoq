"""Unit tests for aggrcomp.py."""


import unittest

import incoq.compiler.incast as L
from incoq.compiler.central import CentralCase
from incoq.compiler.aggr.aggrcomp import *
from incoq.compiler.aggr.aggrcomp import LookupReplacer


class AggrcompCase(CentralCase):
    
    def test_replacer(self):
        look = L.pe('R.smlookup("bu", x)')
        dem1 = L.pe('DEMQUERY(foo, [y], R.smlookup("bu", y))')
        dem2 = L.pe('DEMQUERY(bar, [z], R.smlookup("bu", z))')
        
        tree = L.pe('x + LOOK + DEM1 + DEM1 + DEM2',
                    subst={'LOOK': look, 'DEM1': dem1, 'DEM2': dem2})
        namer = L.NameGenerator()
        replacer = LookupReplacer(namer)
        tree, clauses = replacer.process(tree)
        repls = replacer.repls
        
        exp_tree = L.pe('x + v1 + v2 + v2 + v3')
        exp_clauses = [
            L.Enumerator(L.sn('v1'),
                         L.pe('{R.smlookup("bu", x)}')),
            L.Enumerator(L.sn('v2'),
                         L.pe('DEMQUERY(foo, [y], {R.smlookup("bu", y)})')),
            L.Enumerator(L.sn('v3'),
                         L.pe('DEMQUERY(bar, [z], {R.smlookup("bu", z)})')),
        ]
        exp_repls = {
            look: 'v1',
            dem1: 'v2',
            dem2: 'v3',
        }
        
        self.assertEqual(tree, exp_tree)
        self.assertEqual(clauses, exp_clauses)
        self.assertEqual(repls, exp_repls)
    
    def test_flatten_smlookups_nodem(self):
        comp = L.pe(
            'COMP({x for x in S '
                    'if Aggr1.smlookup("u", ()) > 5}, '
                 '[], {})')
        comp = flatten_smlookups(comp)
        # Ensure idempotence. We don't want to mess up an enumerator
        # in a maintenance comprehension.
        comp = flatten_smlookups(comp)
        
        exp_comp = L.pe(
            'COMP({x for x in S '
                    'for _av1 in {Aggr1.smlookup("u", ())} '
                    'if (_av1 > 5)}, '
                 '[], {})')
        
        self.assertEqual(comp, exp_comp)
    
    def test_flatten_smlookups_dem(self):
        comp = L.pe(
            'COMP({x for x in S '
                    'if DEMQUERY(foo, [u], Aggr1.smlookup("u", ())) > 5}, '
                 '[], {})')
        comp = flatten_smlookups(comp)
        comp = flatten_smlookups(comp)
        
        exp_comp = L.pe(
            'COMP({x for x in S '
                    'for _av1 in DEMQUERY(foo, [u], '
                                   '{Aggr1.smlookup("u", ())}) '
                    'if (_av1 > 5)}, '
                 '[], {})')
        
        self.assertEqual(comp, exp_comp)


if __name__ == '__main__':
    unittest.main()
