"""Unit tests for param_analysis.py."""


import unittest

from incoq.mars.incast import L
from incoq.mars.transform.param_analysis import *


class ParamAnalysisCase(unittest.TestCase):
    
    def test_scope_builder(self):
        query = L.Parser.pe("QUERY('Q', {(x, y) for (x, y) in R})")
        tree = L.Parser.p('''
            def main():
                x = 1
                print(QUERY('Q', {(x, y) for (x, y) in R}))
                z = 2
            def test():
                print(QUERY('Q', {(x, y) for (x, y) in R}))
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


if __name__ == '__main__':
    unittest.main()
