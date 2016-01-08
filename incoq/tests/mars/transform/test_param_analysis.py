"""Unit tests for param_analysis.py."""


import unittest

from incoq.mars.incast import L
from incoq.mars.symtab import SymbolTable
from incoq.mars.transform.param_analysis import *


class ParamAnalysisCase(unittest.TestCase):
    
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
        scope_info = ScopeBuilder.run(tree)
        scopes = []
        for k, (node, scope) in scope_info.items():
            # Check that the query is listed twice and the ids of the
            # nodes match the key.
            self.assertEqual(k, id(node))
            self.assertEqual(node, query)
            scopes.append(scope)
        exp_scopes = [{'main', 'test', 'x', 'z'}, {'main', 'test'}]
        # Check the contents of the scopes.
        self.assertCountEqual(scopes, exp_scopes)
    
    def test_param_analyzer_basic(self):
        comp = L.Parser.pe('{(x, y) for (x, y) in REL(R)}')
        symtab = SymbolTable()
        query_sym = symtab.define_query('Q', node=comp)
        tree = L.Parser.p('''
            def main():
                x = 1
                print(QUERY('Q', {(x, y) for (x, y) in REL(R)}))
            ''')
        scope_info = ScopeBuilder.run(tree)
        
        tree = ParamAnalyzer.run(tree, symtab, scope_info)
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
        scope_info = ScopeBuilder.run(tree)
        
        tree = ParamAnalyzer.run(tree, symtab, scope_info)
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


if __name__ == '__main__':
    unittest.main()
