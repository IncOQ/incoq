"""Unit tests for param_analysis.py."""


import unittest

from incoq.mars.incast import L
import incoq.mars.types as T
from incoq.mars.symtab import SymbolTable
from incoq.mars.comp import CoreClauseTools
from incoq.mars.transform.param_analysis import *


class ParamAnalysisCase(unittest.TestCase):
    
    def setUp(self):
        self.ct = CoreClauseTools()
    
    def test_make_demand_func(self):
        tree = make_demand_func('Q')
        exp_tree = L.Parser.ps('''
            def _demand_Q(_elem):
                if _elem not in _U_Q:
                    _U_Q.reladd(_elem)
            ''')
        self.assertEqual(tree, exp_tree)
    
    def test_determine_demand_params(self):
        comp = L.Parser.pe('{x for (x, y) in REL(R) if z > 5}')
        
        # Strat: all.
        symtab = SymbolTable()
        query = symtab.define_query('Q', node=comp, params=('x', 'z'),
                                    demand_param_strat='all')
        demand_params = determine_demand_params(self.ct, query)
        exp_demand_params = ['x', 'z']
        self.assertSequenceEqual(demand_params, exp_demand_params)
        
        # Strat: unconstrained.
        symtab = SymbolTable()
        query = symtab.define_query('Q', node=comp, params=('x', 'z'),
                                    demand_param_strat='unconstrained')
        demand_params = determine_demand_params(self.ct, query)
        exp_demand_params = ['z']
        self.assertSequenceEqual(demand_params, exp_demand_params)
        
        # Strat: explicit.
        symtab = SymbolTable()
        query = symtab.define_query('Q', node=comp, params=('x', 'z'),
                                    demand_param_strat='explicit',
                                    demand_params=['x'])
        demand_params = determine_demand_params(self.ct, query)
        exp_demand_params = ['x']
        self.assertSequenceEqual(demand_params, exp_demand_params)
        
        # explicit requires demand_params attribute.
        symtab = SymbolTable()
        query = symtab.define_query('Q', node=comp, params=('x', 'z'),
                                    demand_param_strat='explicit')
        with self.assertRaises(AssertionError):
            determine_demand_params(self.ct, query)
        
        # Non-explicit requires absence of demand_params attribute.
        symtab = SymbolTable()
        query = symtab.define_query('Q', node=comp, params=('x', 'z'),
                                    demand_params=('x',))
        with self.assertRaises(AssertionError):
            determine_demand_params(self.ct, query)
    
    def test_scope_builder(self):
        query = L.Parser.pe("QUERY('Q', {(x, y) for (x, y) in REL(R)})")
        tree = L.Parser.p('''
            def main():
                x = 1
                print(QUERY('Q', {(x, y) for (x, y) in REL(R)}))
                z = 2
            def test():
                print(QUERY('Q', {(x, y) for (x, y) in REL(R)}))
            ''')
        scope_info = ScopeBuilder.run(tree, bindenv=['a'])
        scopes = []
        for k, (node, scope) in scope_info.items():
            # Check that the query is listed twice and the ids of the
            # nodes match the key.
            self.assertEqual(k, id(node))
            self.assertEqual(node, query)
            scopes.append(scope)
        exp_scopes = [{'a', 'main', 'test', 'x', 'z'}, {'a', 'main', 'test'}]
        # Check the contents of the scopes.
        self.assertCountEqual(scopes, exp_scopes)
    
    def test_query_context_instantiator(self):
        ctxs = iter(['a', 'b', 'a', 'b'])
        class Inst(QueryContextInstantiator):
            def get_context(self, node):
                return next(ctxs)
            def apply_context(self, query, context):
                query.ctx = context
                query.node = L.BinOp(L.Str(context), L.Add(), L.Str(context))
        
        symtab = SymbolTable()
        symtab.define_query('Q', node=L.Parser.pe('1 + 1'))
        tree = L.Parser.p('''
            def main():
                print(QUERY('Q', 1 + 1))
                print(QUERY('Q', 1 + 1))
                print(QUERY('Q', 1 + 1))
                print(QUERY('Q', 1 + 1))
            ''')
        tree = Inst.run(tree, symtab)
        exp_tree = L.Parser.p('''
            def main():
                print(QUERY('Q', 'a' + 'a'))
                print(QUERY('Q_ctx2', 'b' + 'b'))
                print(QUERY('Q', 'a' + 'a'))
                print(QUERY('Q_ctx2', 'b' + 'b'))
            ''')
        self.assertEqual(tree, exp_tree)
        self.assertEqual(symtab.get_queries()['Q'].ctx, 'a')
        self.assertEqual(symtab.get_queries()['Q_ctx2'].ctx, 'b')
    
    def test_query_context_instantiator_nested(self):
        class Doubler(L.NodeTransformer):
            def visit_Num(self, node):
                return L.Num(node.n * 2)
            def visit_Query(self, node):
                return node
        
        class Inst(QueryContextInstantiator):
            def get_context(self, node):
                return None
            def apply_context(self, query, context):
                query.node = Doubler.run(query.node)
        
        symtab = SymbolTable()
        symtab.define_query('Q1', node=L.Parser.pe('1 + 1'))
        symtab.define_query('Q2', node=L.Parser.pe(
                "2 + QUERY('Q1', 1 + 1)"))
        tree = L.Parser.p('''
            def main():
                print(QUERY('Q2', 2 + QUERY('Q1', 1 + 1)))
            ''')
        tree = Inst.run(tree, symtab)
        exp_tree = L.Parser.p('''
            def main():
                print(QUERY('Q2', 4 + QUERY('Q1', 2 + 2)))
            ''')
        self.assertEqual(tree, exp_tree)
        # Check that outer query symbol was updated.
        query_sym2 = symtab.get_queries()['Q2']
        exp_q2 = L.Parser.pe(
                "4 + QUERY('Q1', 2 + 2)")
        self.assertEqual(query_sym2.node, exp_q2)
    
    def test_param_analyzer_basic(self):
        comp = L.Parser.pe('{(x, y) for (x, y) in REL(R)}')
        symtab = SymbolTable()
        query_sym = symtab.define_query('Q', node=comp)
        tree = L.Parser.p('''
            def main():
                x = 1
                print(QUERY('Q', {(x, y) for (x, y) in REL(R)}))
            ''')
        
        tree = ParamAnalyzer.run(tree, symtab)
        self.assertEqual(query_sym.params, ('x',))
    
    def test_param_analyzer_inst(self):
        comp = L.Parser.pe('{(x, y) for (x, y) in REL(R)}')
        symtab = SymbolTable()
        query_sym = symtab.define_query('Q', node=comp)
        tree = L.Parser.p('''
            def main():
                x = 1
                print(QUERY('Q', {(x, y) for (x, y) in REL(R)}))
            def test1():
                x = 1
                y = 2
                print(QUERY('Q', {(x, y) for (x, y) in REL(R)}))
            def test2():
                x = 1
                print(QUERY('Q', {(x, y) for (x, y) in REL(R)}))
            ''')
        
        tree = ParamAnalyzer.run(tree, symtab)
        exp_tree = L.Parser.p('''
            def main():
                x = 1
                print(QUERY('Q', {(x, y) for (x, y) in REL(R)}))
            def test1():
                x = 1
                y = 2
                print(QUERY('Q_ctx2', {(x, y) for (x, y) in REL(R)}))
            def test2():
                x = 1
                print(QUERY('Q', {(x, y) for (x, y) in REL(R)}))
            ''')
        self.assertEqual(tree, exp_tree)
        
        queries = symtab.get_queries()
        self.assertEqual(queries.keys(), {'Q', 'Q_ctx2'})
        self.assertEqual(query_sym.params, ('x',))
        inst_query_sym = queries['Q_ctx2']
        self.assertEqual(inst_query_sym.params, ('x', 'y'))
    
    def test_demand_analyzer(self):
        comp = L.Parser.pe('{(x, y) for (x, y) in REL(R)}')
        symtab = SymbolTable()
        symtab.clausetools = self.ct
        symtab.define_relation('R', type=T.Set(T.Tuple([T.Number, T.Number])))
        symtab.define_var('x', type=T.Number)
        symtab.define_var('y', type=T.Number)
        query_sym = symtab.define_query('Q', node=comp, impl='inc',
                                        demand_param_strat='explicit',
                                        demand_params=('x',))
        tree = L.Parser.p('''
            def main():
                x = 1
                print(QUERY('Q', {(x, y) for (x, y) in REL(R)}))
            ''')
        
        tree = DemandAnalyzer.run(tree, symtab)
        exp_tree = L.Parser.p('''
            def _demand_Q(_elem):
                if (_elem not in _U_Q):
                    _U_Q.reladd(_elem)
            
            def main():
                x = 1
                print(FIRSTTHEN(_demand_Q((x,)), QUERY('Q',
                    {(x, y) for (x,) in REL(_U_Q) for (x, y) in REL(R)})))
            ''')
        self.assertEqual(tree, exp_tree)
        
        self.assertEqual(query_sym.params, ('x',))
        self.assertEqual(query_sym.demand_params, ('x',))
        uset_sym = symtab.get_symbols()[query_sym.demand_set]
        self.assertEqual(uset_sym.type, T.Set(T.Tuple([T.Number])))
    
    def test_nested_demand_analyzer(self):
        comp1 = L.Parser.pe(
            '{(y,) for (x, y) in REL(R)}')
        comp2 = L.Parser.pe(
            "{z for (z,) in VARS(QUERY('Q1', {(y,) for (x, y) in REL(R)}))}")
        symtab = SymbolTable()
        symtab.clausetools = self.ct
        symtab.define_relation('R', type=T.Set(T.Tuple([T.Number, T.Number])))
        for v in ['x', 'y', 'z']:
            symtab.define_var(v, type=T.Number)
        query_sym1 = symtab.define_query('Q1', node=comp1, impl='inc',
                                        demand_param_strat='explicit',
                                        demand_params=('x',))
        query_sym2 = symtab.define_query('Q2', node=comp2, impl='inc')
        tree = L.Parser.p('''
            def main():
                x = 1
                print(QUERY('Q2', {z for (z,) in VARS(QUERY('Q1',
                    {(y,) for (x, y) in REL(R)}))}))
            ''')
        tree = NestedDemandAnalyzer.run(tree, symtab)
        exp_tree = L.Parser.p('''
            def _demand_Q2(_elem):
                if (_elem not in _U_Q2):
                    _U_Q2.reladd(_elem)
            
            def main():
                x = 1
                print(FIRSTTHEN(_demand_Q2((x,)), QUERY('Q2', {z for (x,) in REL(_U_Q2) for (z,) in VARS(QUERY('Q1', {(y,) for (x,) in VARS(QUERY('_QU_Q1', {(x,) for (x,) in REL(_U_Q2)})) for (x, y) in REL(R)}))})))
            ''')
        self.assertEqual(tree, exp_tree)
        
        self.assertEqual(query_sym1.demand_query, '_QU_Q1')
        self.assertEqual(query_sym2.demand_set, '_U_Q2')
        demquery_sym = symtab.get_symbols()['_QU_Q1']
        self.assertEqual(demquery_sym.type, T.Set(T.Tuple([T.Number])))


if __name__ == '__main__':
    unittest.main()
