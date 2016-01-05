"""Unit tests for param_analysis.py."""


import unittest

from incoq.mars.incast import L
from incoq.mars.symtab import SymbolTable
from incoq.mars.transform.param_analysis import *


class ParamAnalysisCase(unittest.TestCase):
    
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
        


if __name__ == '__main__':
    unittest.main()
