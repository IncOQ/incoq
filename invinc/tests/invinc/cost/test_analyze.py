"""Unit tests for analyze.py."""


import unittest

import invinc.compiler.incast as L
from invinc.compiler.set import Mask
from invinc.compiler.central import CentralCase

from invinc.compiler.cost.cost import *
from invinc.compiler.cost.analyze import *
from invinc.compiler.cost.analyze import (CostAnalyzer, func_costs,
                                          type_to_cost, VarRewriter)


class AnalyzeCase(CentralCase):
    
    def test_intraproc_simple(self):
        tree = L.pc('''
            for x in S:
                for y in T:
                    foo
            for z in R:
                bar
            ''')
        cost = CostAnalyzer.run(tree, (), {}, {})
        exp_cost_str = '((S*T) + R)'
        self.assertEqual(str(cost), exp_cost_str)
        
        tree = L.pc('''
            if True:
                for x in S:
                    for y in T:
                        foo
                    baz
                    for w in T:
                        pass
            else:
                for q in A:
                    baz()
            for z in S:
                bar
            ''')
        cost = CostAnalyzer.run(tree, (), {}, {})
        exp_cost_str = '((S*T) + (A*UNKNOWN_baz))'
        self.assertEqual(str(cost), exp_cost_str)
        
        tree = L.pc('''
            while True:
                for x in T:
                    pass
            for z in S:
                bar
            ''')
        cost = CostAnalyzer.run(tree, (), {}, {})
        exp_cost_str = '((?*T) + S)'
        self.assertEqual(str(cost), exp_cost_str)
    
    def test_intraproc_setmatch(self):
        tree = L.pc('''
            result = set()
            for y in setmatch(R, 'bu', x):
                for z in setmatch(S, 'bu', y):
                    if (z not in result):
                        result.add(z)
            return result
            ''')
        cost = CostAnalyzer.run(tree, ('x'), {}, {})
        exp_cost_str = '(R_out[x]*S_out)'
        self.assertEqual(str(cost), exp_cost_str)
    
    def test_interproc_simple(self):
        tree = L.pc('''
            def f():
                for x in S:
                    for y in T:
                        foo
            def g():
                for z in R:
                    f()
            ''')
        costs = func_costs(tree)
        exp_cost_strs = {'f': '(S*T)',
                         'g': '(R*S*T)'}
        self.assertEqual({k: str(v) for k, v in costs.items()}, exp_cost_strs)
    
    def test_interproc_setmatch(self):
        tree = L.pc('''
            def f(x, y):
                for a in setmatch(R, 'bu', x):
                    for b in setmatch(S, 'bu', y):
                        for c in setmatch(T, 'bu', z):
                            foo
            def g(u):
                for v in Z:
                    f(u, v)
            ''')
        costs = func_costs(tree)
        exp_cost_strs = {'f': '(R_out[x]*S_out[y]*T_out)',
                         'g': '(Z*R_out[u]*S_out*T_out)'}
        self.assertEqual({k: str(v) for k, v in costs.items()}, exp_cost_strs)
    
    def test_costlabel(self):
        tree = L.pc('''
            def f(x):
                for y in setmatch(R, 'bu', x):
                    pass
            ''')
        costmap = func_costs(tree)
        tree = CostLabelAdder.run(tree, costmap)
        exp_tree = L.pc('''
            def f(x):
                Comment('Cost: O(R_out[x])')
                for y in setmatch(R, 'bu', x):
                    pass
            ''')
        self.assertEqual(tree, exp_tree)
    
    def test_typetocost(self):
        ST, TT, OT = L.SetType, L.TupleType, L.ObjType
        t = TT([OT('A'), OT('B'), TT([OT('C'), OT('D')])])
        cost = type_to_cost(t)
        exp_cost = ProductCost([NameCost('A'), NameCost('B'),
                                ProductCost([NameCost('C'), NameCost('D')])])
        self.assertEqual(cost, exp_cost)
        
        cost = type_to_cost(t, {(1,): UnitCost(), (2, 1): UnitCost()})
        exp_cost = ProductCost([NameCost('A'), UnitCost(),
                                ProductCost([NameCost('C'), UnitCost()])])
        self.assertEqual(cost, exp_cost)
    
    def test_VarRewriter(self):
        ST, TT, OT = L.SetType, L.TupleType, L.ObjType
        t = ST(TT([OT('A'), OT('B'), TT([OT('C'), OT('D')])]))
        self.manager.vartypes['R'] = t
        self.manager.domcosts = {'R': {(2, 0): UnitCost()}}
        
        cost = NameCost('R')
        cost = VarRewriter.run(cost, self.manager)
        exp_cost = ProductCost([NameCost('A'), NameCost('B'),
                                NameCost('D')])
        self.assertEqual(cost, exp_cost)
        
        cost = IndefImgsetCost('R', Mask('buu'))
        cost = VarRewriter.run(cost, self.manager)
        exp_cost = ProductCost([NameCost('B'), NameCost('D')])
        self.assertEqual(cost, exp_cost)


if __name__ == '__main__':
    unittest.main()
