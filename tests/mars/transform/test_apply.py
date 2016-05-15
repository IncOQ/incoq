"""Unit tests for apply.py."""


import unittest

from incoq.mars.incast import L, P
from incoq.mars.transform.apply import *


class QueryNodeFinderCase(unittest.TestCase):
    
    @property
    def common_tree(self):
        return L.Parser.p('''
            def main():
                print(QUERY('Q2', 2 + QUERY('Q1', 1)))
                print(QUERY('Q1', 1))
                print(QUERY('Q3', 3))
            ''')
    
    def test_basic(self):
        queries = QueryNodeFinder.run(self.common_tree)
        exp_queries = [
            ('Q1', L.Parser.pe('1')),
            ('Q2', L.Parser.pe("2 + QUERY('Q1', 1)")),
            ('Q3', L.Parser.pe('3')),
        ]
        self.assertSequenceEqual(list(queries.items()), exp_queries)
    
    def test_first(self):
        result = QueryNodeFinder.run(self.common_tree, first=True)
        exp_result = ('Q1', L.Parser.pe('1'))
        self.assertEqual(result, exp_result)
        
        tree = L.Parser.p('''
            def main():
                pass
            ''')
        result = QueryNodeFinder.run(tree, first=True)
        self.assertIsNone(result)
    
    def test_ignore(self):
        queries = QueryNodeFinder.run(self.common_tree, ignore=['Q2'])
        exp_queries = [
            ('Q1', L.Parser.pe('1')),
            ('Q3', L.Parser.pe('3')),
        ]
        self.assertSequenceEqual(list(queries.items()), exp_queries)


class ApplyCase(unittest.TestCase):
    
    def test_transform_source(self):
        source = P.trim('''
            import incoq.mars.runtime as runtime
            S = runtime.Set()
            def main():
                a = b = c
            ''')
        source, _symtab = transform_source(source, options={'costs': 'false'})
        exp_source = P.trim('''
            from incoq.mars.runtime import *
            def main():
                b = c
                a = b
            
            if (__name__ == '__main__'):
                main()
            
            ''')
        self.assertEqual(source, exp_source)


if __name__ == '__main__':
    unittest.main()
