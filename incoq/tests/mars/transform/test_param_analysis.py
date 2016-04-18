"""Unit tests for param_analysis.py."""


import unittest

from incoq.mars.incast import L
from incoq.mars.type import T
from incoq.mars.symbol import S
from incoq.mars.comp import CoreClauseTools
from incoq.mars.transform.param_analysis import *


class ParamAnalysisCase(unittest.TestCase):
    
    def setUp(self):
        self.ct = CoreClauseTools()
    
    def test_find_nested_queries(self):
        tree = L.Parser.pe('''
            QUERY('Q1', QUERY('Q2', 1) + QUERY('Q3', 2))
            ''')
        queries = find_nested_queries(tree)
        exp_queries = [
            L.Parser.pe("QUERY('Q2', 1)"),
            L.Parser.pe("QUERY('Q3', 2)"),
        ]
        self.assertSequenceEqual(queries, exp_queries)
    
    def test_make_demand_func(self):
        tree = make_demand_func('Q')
        exp_tree = L.Parser.ps('''
            def _demand_Q(_elem):
                if _elem not in _U_Q:
                    _U_Q.reladd(_elem)
            ''')
        self.assertEqual(tree, exp_tree)
    
    def test_determine_comp_demand_params(self):
        comp = L.Parser.pe('{x for (x, y) in REL(R) if z > 5}')
        
        # Strat: All.
        demand_params = determine_comp_demand_params(
                            self.ct, comp, ('x', 'z'), None, S.All)
        exp_demand_params = ['x', 'z']
        self.assertSequenceEqual(demand_params, exp_demand_params)
        
        # Strat: Unconstrained.
        demand_params = determine_comp_demand_params(
                            self.ct, comp, ('x', 'z'), None, S.Unconstrained)
        exp_demand_params = ['z']
        self.assertSequenceEqual(demand_params, exp_demand_params)
        
        # Strat: Explicit.
        demand_params = determine_comp_demand_params(
                            self.ct, comp, ('x', 'z'), ('x',), S.Explicit)
        exp_demand_params = ['x']
        self.assertSequenceEqual(demand_params, exp_demand_params)
        
        # Explicit requires demand_params attribute.
        with self.assertRaises(AssertionError):
            determine_comp_demand_params(self.ct, comp,
                                         ('x', 'z'), None, S.Explicit)
        
        # Non-explicit requires absence of demand_params attribute.
        with self.assertRaises(AssertionError):
            determine_comp_demand_params(self.ct, comp,
                                         ('x', 'z'), ('x',), S.All)
    
    def test_make_demand_set(self):
        symtab = S.SymbolTable()
        comp = L.Parser.pe('{(x, y) for (x, y) in REL(R)}')
        symtab.define_var('x', type=T.String)
        query = symtab.define_query('Q', node=comp, demand_params=('x',))
        
        uset = make_demand_set(symtab, query)
        
        self.assertEqual(uset.name, '_U_Q')
        self.assertEqual(uset.type, T.Set(T.Tuple([T.String])))
        self.assertEqual(query.demand_set, '_U_Q')
    
    def test_make_demand_query(self):
        symtab = S.SymbolTable()
        symtab.clausetools = self.ct
        comp = L.Parser.pe('{(x, y) for (x, y) in REL(R)}')
        symtab.define_var('x', type=T.String)
        query = symtab.define_query('Q', node=comp, demand_params=('x',))
        left_clauses = L.Parser.pe('{None for (x,) in REL(S)}').clauses
        
        demquery = make_demand_query(symtab, query, left_clauses)
        
        self.assertEqual(demquery.name, '_QU_Q')
        self.assertEqual(demquery.type, T.Set(T.Tuple([T.String])))
        exp_demquery_node = L.Parser.pe('{(_v1x,) for (_v1x,) in REL(S)}')
        self.assertEqual(demquery.node, exp_demquery_node)
        self.assertEqual(query.demand_query, '_QU_Q')
    
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
        scope_info = ScopeBuilder.run(tree, self.ct, bindenv=['a'])
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
        
        # Nested case.
        query = L.Parser.pe("QUERY('Q1', {(x, y) for (x, y) in REL(S)})")
        tree = L.Parser.p('''
            def main():
                print(QUERY('Q2', {x for (x,) in REL(R) for (x,) in
                    VARS(QUERY('Q1', {(x, y) for (x, y) in REL(S)}))}))
            ''')
        scope_info = ScopeBuilder.run(tree, self.ct)
        for (node, scope) in scope_info.values():
            if node == query:
                break
        else:
            assert()
        exp_scope = {'main', 'x'}
        self.assertEqual(scope, exp_scope)
        
        # Nested case, outer comprehension unmarked.
        query = L.Parser.pe("QUERY('Q1', {(x, y) for (x, y) in REL(S)})")
        tree = L.Parser.p('''
            def main():
                print({x for (x,) in REL(R) for (x,) in
                    VARS(QUERY('Q1', {(x, y) for (x, y) in REL(S)}))})
            ''')
        scope_info = ScopeBuilder.run(tree, self.ct)
        for (node, scope) in scope_info.values():
            if node == query:
                break
        else:
            assert()
        exp_scope = {'main', 'x'}
        self.assertEqual(scope, exp_scope)
    
    def test_context_tracker(self):
        _self = self
        class Tracker(ContextTracker):
            def process(self, tree):
                orig_tree = tree
                self.result = []
                tree = super().process(tree)
                _self.assertEqual(tree, orig_tree)
                return self.result
            def visit_Name(self, node):
                if node.id == 'B':
                    self.result.append(self.get_left_clauses())
        
        inner_comp = L.Parser.pe('''
            {(x,) for (x,) in REL(R) if B}
            ''')
        aggr = L.Parser.pe('''
            count(QUERY('Q1', {(x,) for (x,) in REL(R) if B}))
            ''')
        outer_comp = L.Parser.pe('''
            {z for (z,) in REL(S) if B
               if z > QUERY('Q2', count(QUERY('Q1',
                                  {(x,) for (x,) in REL(R) if B})))
               if B}
            ''')
        other_comp = L.Parser.pe('''
            {a for (a,) in REL(S) if B}
            ''')
        symtab = S.SymbolTable()
        query_sym1 = symtab.define_query('Q1', node=inner_comp,
                                         impl=S.Inc)
        query_sym2 = symtab.define_query('Q2', node=aggr,
                                         impl=S.Inc)
        query_sym3 = symtab.define_query('Q3', node=outer_comp,
                                         impl=S.Inc)
        query_sym4 = symtab.define_query('Q4', node=outer_comp,
                                         impl=S.Normal)
        tree = L.Parser.p('''
            def main():
                print(QUERY('Q3',
                    {z for (z,) in REL(S) if B
                       if z > QUERY('Q2', count(QUERY('Q1',
                                          {(x,) for (x,) in REL(R) if B})))
                       if B}))
                print(QUERY('Q4', {a for (a,) in REL(S) if B}))
            ''')
        result = Tracker.run(tree, symtab)
        exp_result = [
            (L.RelMember(('z',), 'S'),),
            (L.RelMember(('x',), 'R'),),
            (L.RelMember(('z',), 'S'),
             L.Cond(L.Name('B')),
             L.Cond(L.Parser.pe('''
                z > QUERY('Q2', count(QUERY('Q1', {(x,) for (x,) in REL(R)
                                                        if B})))
                '''))),
            None
        ]
        self.assertEqual(result, exp_result)
    
    def test_context_tracker_aggr(self):
        _self = self
        class Tracker(ContextTracker):
            def process(self, tree):
                orig_tree = tree
                self.result = []
                tree = super().process(tree)
                _self.assertEqual(tree, orig_tree)
                return self.result
            def visit_Name(self, node):
                if node.id == 'B':
                    self.result.append(self.get_left_clauses())
        
        aggr = L.Parser.pe('''
            count(B)
            ''')
        symtab = S.SymbolTable()
        query_sym1 = symtab.define_query('Q1', node=aggr,
                                         impl=S.Inc)
        tree = L.Parser.p('''
            def main():
                print(QUERY('Q1', count(B, (x,), U)))
            ''')
        result = Tracker.run(tree, symtab)
        exp_result = [
            (L.VarsMember(('x',), L.Name('U')),),
        ]
        self.assertEqual(result, exp_result)
    
    def test_param_analyzer_basic(self):
        comp = L.Parser.pe('{(x,) for (x,) in REL(R) if x > y}')
        symtab = S.SymbolTable()
        symtab.clausetools = self.ct
        query_sym = symtab.define_query('Q', node=comp)
        tree = L.Parser.p('''
            def main():
                y = 1
                print(QUERY('Q', {(x,) for (x,) in REL(R) if x > y}))
            ''')
        scope_info = ScopeBuilder.run(tree, symtab.clausetools)
        tree = ParamAnalyzer.run(tree, symtab, scope_info)
        self.assertEqual(query_sym.params, ('y',))
        
        # Inconsistent case.
        comp = L.Parser.pe('{(x,) for (x,) in REL(R) if x > y}')
        symtab = S.SymbolTable()
        symtab.clausetools = self.ct
        query_sym = symtab.define_query('Q', node=comp)
        tree = L.Parser.p('''
            def f1():
                x = 1
                print(QUERY('Q', {(x,) for (x,) in REL(R) if x > y}))
            def f2():
                y = 1
                print(QUERY('Q', {(x,) for (x,) in REL(R) if x > y}))
            ''')
        scope_info = ScopeBuilder.run(tree, symtab.clausetools)
        with self.assertRaises(L.ProgramError):
            tree = ParamAnalyzer.run(tree, symtab, scope_info)
    
    def test_param_analyzer_nested(self):
        inner_comp = L.Parser.pe('{(x,) for (x,) in REL(R) if x > y}')
        aggr = L.Parser.pe('''
            count(QUERY('Q1', {(x,) for (x,) in REL(R) if x > y}))
            ''')
        outer_comp = L.Parser.pe('''
            {z for (z,) in REL(S) if z > QUERY('Q2',
            count(QUERY('Q1', {(x,) for (x,) in REL(R) if x > y})))}
            ''')
        symtab = S.SymbolTable()
        symtab.clausetools = self.ct
        query_sym1 = symtab.define_query('Q1', node=inner_comp)
        query_sym2 = symtab.define_query('Q2', node=aggr)
        query_sym3 = symtab.define_query('Q3', node=outer_comp)
        tree = L.Parser.p('''
            def main():
                y = 1
                z = 2
                print(QUERY('Q3', {z for (z,) in REL(S) if z > QUERY('Q2',
                    count(QUERY('Q1', {(x,) for (x,) in REL(R) if x > y})))}))
            ''')
        scope_info = ScopeBuilder.run(tree, symtab.clausetools)
        
        tree = ParamAnalyzer.run(tree, symtab, scope_info)
        self.assertEqual(query_sym1.params, ('y',))
        self.assertEqual(query_sym2.params, ('y',))
        self.assertEqual(query_sym3.params, ('z', 'y'))
    
    def test_demand_param_analyzer(self):
        inner_comp = L.Parser.pe('{(x,) for (x,) in REL(R) if x > y}')
        aggr = L.Parser.pe('''
            count(QUERY('Q1', {(x,) for (x,) in REL(R) if x > y}))
            ''')
        outer_comp = L.Parser.pe('''
            {z for (z,) in REL(S) if z > QUERY('Q2',
            count(QUERY('Q1', {(x,) for (x,) in REL(R) if x > y})))}
            ''')
        symtab = S.SymbolTable()
        symtab.clausetools = self.ct
        query_sym1 = symtab.define_query('Q1', node=inner_comp,
                                         params=('y',), impl=S.Inc)
        query_sym2 = symtab.define_query('Q2', node=aggr,
                                         params=('y',), impl=S.Inc)
        query_sym3 = symtab.define_query('Q3', node=outer_comp,
                                         params=('z', 'y'), impl=S.Inc)
        tree = L.Parser.p('''
            def main():
                y = 1
                z = 2
                print(QUERY('Q3', {z for (z,) in REL(S) if z > QUERY('Q2',
                    count(QUERY('Q1', {(x,) for (x,) in REL(R) if x > y})))}))
            ''')
        
        DemandParamAnalyzer.run(tree, symtab)
        self.assertTrue(query_sym1.uses_demand)
        self.assertTrue(query_sym2.uses_demand)
        self.assertTrue(query_sym3.uses_demand)
        self.assertEqual(query_sym1.demand_params, ('y',))
        self.assertEqual(query_sym2.demand_params, ('y',))
        self.assertEqual(query_sym3.demand_params, ('y',))
    
    def test_demand_param_analyzer_uses_demand(self):
        # Case where comp does not need demand.
        comp = L.Parser.pe('''
            {(x,) for (x,) in REL(S)}
            ''')
        symtab = S.SymbolTable()
        symtab.clausetools = self.ct
        query_sym = symtab.define_query('Q', node=comp,
                                         params=('x',), impl=S.Inc)
        tree = L.Parser.p('''
            def main():
                print(QUERY('Q', {(x,) for (x,) in REL(S)}))
            ''')
        DemandParamAnalyzer.run(tree, symtab)
        self.assertFalse(query_sym.uses_demand)
        self.assertEqual(query_sym.demand_params, ())
        
        # Case where aggregate does not need demand.
        comp = L.Parser.pe('''
            {(x,) for (x,) in REL(S)}
            ''')
        aggr = L.Parser.pe('''
            count(QUERY('Q1', {(x,) for (x,) in REL(S)}))
            ''')
        symtab = S.SymbolTable()
        symtab.clausetools = self.ct
        query_sym1 = symtab.define_query('Q1', node=comp,
                                         params=('x',), impl=S.Inc)
        query_sym2 = symtab.define_query('Q2', node=aggr,
                                         params=('x',), impl=S.Inc)
        tree = L.Parser.p('''
            def main():
                print(QUERY('Q2', count(
                      QUERY('Q1', {(x,) for (x,) in REL(S)}))))
            ''')
        DemandParamAnalyzer.run(tree, symtab)
        self.assertFalse(query_sym1.uses_demand)
        self.assertFalse(query_sym2.uses_demand)
        self.assertEqual(query_sym2.demand_params, ())
        
        # Case where it needs it because the operand uses demand.
        comp = L.Parser.pe('''
            {(x,) for (x,) in REL(S) if x > y}
            ''')
        aggr = L.Parser.pe('''
            count(QUERY('Q1', {(x,) for (x,) in REL(S) if x > y}))
            ''')
        symtab = S.SymbolTable()
        symtab.clausetools = self.ct
        query_sym1 = symtab.define_query('Q1', node=comp,
                                         params=('x', 'y'), impl=S.Inc)
        query_sym2 = symtab.define_query('Q2', node=aggr,
                                         params=('x', 'y'), impl=S.Inc)
        tree = L.Parser.p('''
            def main():
                print(QUERY('Q2', count(
                      QUERY('Q1', {(x,) for (x,) in REL(S) if x > y}))))
            ''')
        DemandParamAnalyzer.run(tree, symtab)
        self.assertTrue(query_sym1.uses_demand)
        self.assertTrue(query_sym2.uses_demand)
        self.assertEqual(query_sym2.demand_params, ('x', 'y'))
        
        # Case where it needs it because it appears in a comprehension.
        aggr = L.Parser.pe('''
            count(R)
            ''')
        comp = L.Parser.pe('''
            {(x,) for (x,) in REL(S) if x > QUERY('Q1', count(R))}
            ''')
        symtab = S.SymbolTable()
        symtab.clausetools = self.ct
        query_sym1 = symtab.define_query('Q1', node=aggr,
                                         params=(), impl=S.Inc)
        query_sym2 = symtab.define_query('Q2', node=comp,
                                         params=(), impl=S.Inc)
        tree = L.Parser.p('''
            def main():
                print(QUERY('Q2', {(x,) for (x,) in REL(S) if x >
                      QUERY('Q1', count(R))}))
            ''')
        DemandParamAnalyzer.run(tree, symtab)
        self.assertTrue(query_sym1.uses_demand)
        self.assertFalse(query_sym2.uses_demand)
        self.assertEqual(query_sym1.demand_params, ())
    
    def test_demand_transformer_basic(self):
        comp = L.Parser.pe('{(x,) for (x,) in REL(R) if x > y}')
        symtab = S.SymbolTable()
        symtab.clausetools = self.ct
        query_sym = symtab.define_query(
            'Q', node=comp, uses_demand=True,
            demand_params=('y',), impl=S.Inc)
        symtab.define_var('y', type=T.Number)
        tree = L.Parser.p('''
            def main():
                print(QUERY('Q', {(x,) for (x,) in REL(R) if x > y}))
            ''')
        tree = DemandTransformer.run(tree, symtab)
        exp_tree = L.Parser.p('''
            def _demand_Q(_elem):
                if (_elem not in _U_Q):
                    _U_Q.reladd(_elem)
            
            def main():
                print(FIRSTTHEN(_demand_Q((y,)),
                      QUERY('Q', {(x,) for (y,) in REL(_U_Q)
                                       for (x,) in REL(R) if (x > y)})))
            ''')
        self.assertEqual(tree, exp_tree)
        self.assertEqual(query_sym.node, L.Parser.pe('''
            {(x,) for (y,) in REL(_U_Q) for (x,) in REL(R) if (x > y)}
            '''))
        self.assertEqual(query_sym.demand_set, '_U_Q')
        uset_sym = symtab.get_relations()['_U_Q']
        self.assertEqual(uset_sym.type, T.Set(T.Tuple([T.Number])))
    
    def test_demand_transformer_nested(self):
        inner_comp = L.Parser.pe('{(x,) for (x,) in REL(R) if x > y}')
        aggr = L.Parser.pe('''
            count(QUERY('Q1', {(x,) for (x,) in REL(R) if x > y}))
            ''')
        outer_comp = L.Parser.pe('''
            {z for (z,) in REL(S) if z > QUERY('Q2',
            count(QUERY('Q1', {(x,) for (x,) in REL(R) if x > y})))}
            ''')
        symtab = S.SymbolTable()
        symtab.clausetools = self.ct
        query_sym1 = symtab.define_query(
            'Q1', node=inner_comp, uses_demand=True,
            demand_params=('y',), impl=S.Inc)
        query_sym2 = symtab.define_query(
            'Q2', node=aggr, uses_demand=True,
            demand_params=('y',), impl=S.Inc)
        query_sym3 = symtab.define_query(
            'Q3', node=outer_comp, uses_demand=True,
            demand_params=('y',), impl=S.Inc)
        symtab.define_var('x', type=T.Number)
        symtab.define_var('y', type=T.Number)
        symtab.define_var('z', type=T.Number)
        tree = L.Parser.p('''
            def main():
                y = 1
                z = 2
                print(QUERY('Q3', {z for (z,) in REL(S) if z > QUERY('Q2',
                    count(QUERY('Q1', {(x,) for (x,) in REL(R) if x > y})))}))
            ''')
        tree = DemandTransformer.run(tree, symtab)
        exp_tree = L.Parser.p('''
            def _demand_Q3(_elem):
                if (_elem not in _U_Q3):
                    _U_Q3.reladd(_elem)
            
            def main():
                y = 1
                z = 2
                print(FIRSTTHEN(_demand_Q3((y,)),
                      QUERY('Q3', {z for (y,) in REL(_U_Q3) for (z,) in REL(S)
                                     if (z > QUERY('Q2', count(QUERY('Q1',
                      {(x,) for (y,) in VARS(QUERY('_QU_Q1',
                          {(_v2y,) for (_v2y,) in VARS(QUERY('_QU_Q2',
                                       {(_v1y,) for (_v1y,) in REL(_U_Q3)
                                       for (_v1z,) in REL(S)}))}))
                            for (x,) in REL(R) if x > y}),
                      (y,),
                      QUERY('_QU_Q2', {(_v1y,) for (_v1y,) in REL(_U_Q3)
                                               for (_v1z,) in REL(S)}))))})))
            ''')
        self.assertEqual(tree, exp_tree)
        self.assertEqual(query_sym1.demand_query, '_QU_Q1')
        self.assertEqual(query_sym2.demand_query, '_QU_Q2')
        self.assertEqual(query_sym3.demand_set, '_U_Q3')
        self.assertEqual(symtab.get_queries()['_QU_Q1'].type,
                         T.Set(T.Tuple([T.Number])))
        self.assertEqual(symtab.get_queries()['_QU_Q2'].type,
                         T.Set(T.Tuple([T.Number])))
        self.assertEqual(symtab.get_relations()['_U_Q3'].type,
                         T.Set(T.Tuple([T.Number])))
    
    def test_demand_resetter(self):
        symtab = S.SymbolTable()
        query_sym1 = symtab.define_query(
            'Q1', demand_set='U1')
        query_sym2 = symtab.define_query(
            'Q2', demand_set='U2')
        tree = L.Parser.p('''
            def main():
                resetdemand()
                resetdemandfor(['Q1'])
            ''')
        tree = DemandResetter.run(tree, symtab)
        exp_tree = L.Parser.p('''
            def main():
                U1.relclear()
                U2.relclear()
                U1.relclear()
            ''')
        self.assertEqual(tree, exp_tree)


if __name__ == '__main__':
    unittest.main()
