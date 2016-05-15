"""Unit tests for analyze.py."""


import unittest

from incoq.util.misc import new_namespace
from incoq.compiler.incast import L
from incoq.compiler.type import T
from incoq.compiler.symbol import S
import incoq.compiler.cost.costs as costs
import incoq.compiler.cost.algebra as algebra
import incoq.compiler.cost.analyze as analyze
from incoq.compiler.cost.analyze import (
    TrivialCostAnalyzer, SizeAnalyzer,
    LoopCostAnalyzer, CallCostAnalyzer,
    type_to_cost, rewrite_cost_using_types)
from incoq.compiler.comp import CoreClauseTools

C = new_namespace(costs, algebra, analyze)


class AnalyzeCase(unittest.TestCase):
    
    def test_trivialcostanalyzer(self):
        # This case isn't very interesting because without loops and
        # function calls we can only produce Unit and Unknown costs.
        tree = L.Parser.pc('''
            if True:
                a = 1 + 1
            ''')
        cost = TrivialCostAnalyzer.run(tree)
        exp_cost = C.Unit()
        self.assertEqual(cost, exp_cost)
    
    def test_sizeanalyzer(self):
        expr = L.Parser.pe('1 + 1')
        cost = SizeAnalyzer.run(expr)
        exp_cost = C.Unit()
        self.assertEqual(cost, exp_cost)
        
        expr = L.Parser.pe('S if b else T')
        cost = SizeAnalyzer.run(expr)
        exp_cost = C.Sum([C.Name('S'), C.Name('T')])
        self.assertEqual(cost, exp_cost)
    
    def test_loopcostanalyzer(self):
        tree = L.Parser.pc('''
            for x in S:
                for y in T:
                    A
            for z in R:
                B
            ''')
        cost = LoopCostAnalyzer.run(tree)
        exp_cost = C.Sum([C.Product([C.Name('S'), C.Name('T')]),
                          C.Name('R')])
        self.assertEqual(cost, exp_cost)
        
        tree = L.Parser.pc('''
            while True:
                for x in R:
                    pass
            ''')
        cost = LoopCostAnalyzer.run(tree)
        exp_cost = C.Product([C.Unknown(), C.Name('R')])
        self.assertEqual(cost, exp_cost)
        
        tree = L.Parser.pc('''
            for y in R.imglookup('bu', (x,)):
                for z in S.imglookup('bu', (y,)):
                    pass
            ''')
        cost = LoopCostAnalyzer.run(tree)
        exp_cost = C.Product([C.DefImgset('R', L.mask('bu'), ['x']),
                              C.DefImgset('S', L.mask('bu'), ['y'])])
        self.assertEqual(cost, exp_cost)
    
    def test_callcostanalyzer(self):
        func_params = {
            'f': ['w', 'x'],
            'g': ['y', 'z'],
            'h': ['u'],
        }
        func_costs = {
            'f': C.DefImgset('R', L.mask('bbu'), ['w', 'x']),
            'g': C.Sum([C.DefImgset('S', L.mask('bu'), ['y']),
                        C.DefImgset('S', L.mask('ub'), ['z'])]),
            'h': C.Name('T'),
        }
        tree = L.Parser.pc('''
            n = f(a, b)
            n = n + f(c, d)
            n = n + g(e, h(e))
            ''')
        cost = CallCostAnalyzer.run(tree, func_params, func_costs)
        exp_cost = C.Sum([C.DefImgset('R', L.mask('bbu'), ['a', 'b']),
                          C.DefImgset('R', L.mask('bbu'), ['c', 'd']),
                          C.Name('T'),
                          C.DefImgset('S', L.mask('bu'), ['e']),
                          C.IndefImgset('S', L.mask('ub'))])
        self.assertEqual(cost, exp_cost)
    
    def test_analyze_costs_simple(self):
        tree = L.Parser.pc('''
            def f():
                for x in S:
                    for y in T:
                        foo
            def g():
                for z in R:
                    f()
            ''')
        func_costs = C.analyze_costs(tree)
        exp_func_costs = {
            'f': C.Product([C.Name('S'), C.Name('T')]),
            'g': C.Product([C.Name('R'), C.Name('S'), C.Name('T')]),
        }
        self.assertEqual(func_costs, exp_func_costs)
        
        tree = L.Parser.pc('''
            def f():
                pass
            def g():
                g()
            ''')
        func_costs = C.analyze_costs(tree)
        exp_func_costs = {
            'f': C.Unit(),
        }
        self.assertEqual(func_costs, exp_func_costs)
    
    def test_interproc_setmatch(self):
        tree = L.Parser.pc('''
            def f(x, y):
                for a in R.imglookup('bu', (x,)):
                    for b in S.imglookup('bu', (y,)):
                        for c in T.imglookup('bu', (z,)):
                            foo
            def g(u):
                for v in Z:
                    f(u, v)
            ''')
        func_costs = C.analyze_costs(tree)
        exp_func_costs = {
            'f': C.Product([C.DefImgset('R', L.mask('bu'), ['x']),
                            C.DefImgset('S', L.mask('bu'), ['y']),
                            C.IndefImgset('T', L.mask('bu'))]),
            'g': C.Product([C.Name('Z'),
                            C.DefImgset('R', L.mask('bu'), ['u']),
                            C.IndefImgset('S', L.mask('bu')),
                            C.IndefImgset('T', L.mask('bu'))]),
        }
        self.assertEqual(func_costs, exp_func_costs)
    
    def test_type_to_cost(self):
        # Unknown type.
        cost = type_to_cost(T.Top)
        exp_cost = C.Unknown()
        self.assertEqual(cost, exp_cost)
        cost = type_to_cost(T.Bottom)
        exp_cost = C.Unknown()
        self.assertEqual(cost, exp_cost)
        
        # Atomic types.
        cost = type_to_cost(T.Number)
        exp_cost = C.Name('Number')
        self.assertEqual(cost, exp_cost)
        cost = type_to_cost(T.Refine('address', T.String))
        exp_cost = C.Name('address')
        self.assertEqual(cost, exp_cost)
        
        # Set of tuples.
        cost = type_to_cost(T.Tuple([T.Number, T.String]))
        exp_cost = C.Product([C.Name('Number'), C.Name('str')])
        self.assertEqual(cost, exp_cost)
        cost = type_to_cost(T.Tuple([T.Number, T.Tuple([T.String, T.Bool])]))
        exp_cost = C.Product([C.Name('Number'),
                              C.Product([C.Name('str'), C.Unit()])])
        self.assertEqual(cost, exp_cost)
    
    def test_rewrite_cost_using_types(self):
        symtab = S.SymbolTable()
        symtab.clausetools = CoreClauseTools()
        symtab.define_relation('R', type=T.Set(T.Number))
        symtab.define_relation('S', type=T.Set(T.Tuple(
                               [T.Bool, T.String, T.Bool, T.Enum('color')])))
        
        cost = C.Sum([C.Name('R'), C.IndefImgset('S', L.mask('buuu'))])
        cost = rewrite_cost_using_types(cost, symtab)
        exp_cost = C.Sum([C.Name('Number'), C.Name('str')])
        self.assertEqual(cost, exp_cost)
    
    def test_annotate_costs(self):
        symtab = S.SymbolTable()
        symtab.clausetools = CoreClauseTools()
        symtab.maint_funcs = ['f']
        tree = L.Parser.p('''
            def f(x):
                for y in R:
                    pass
            ''')
        tree = C.annotate_costs(tree, symtab)
        exp_tree = L.Parser.p('''
            def f(x):
                COMMENT('Cost: O(R)')
                COMMENT('      O(R)')
                for y in R:
                    pass
            ''')
        self.assertEqual(tree, exp_tree)
        exp_func_costs = {
            'f': C.Name('R'),
        }
        self.assertEqual(symtab.func_costs, exp_func_costs)


if __name__ == '__main__':
    unittest.main()
