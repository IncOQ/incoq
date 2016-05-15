"""Unit tests for incast_rewritings.py."""


import unittest

from incoq.compiler.incast import L
from incoq.compiler.symbol import N
from incoq.compiler.transform.incast_rewritings import *
from incoq.compiler.transform.incast_rewritings import QueryMarker


class QueryMarkerCase(unittest.TestCase):
    
    def test_basic(self):
        tree = L.Parser.p('''
            def main():
                print(1 + 2)
                print(QUERY('A', 3 + 4))
                print(3 + 4)
            ''')
        query_name_map = {L.Parser.pe('1 + 2'): 'Q1',
                          L.Parser.pe('3 + 4'): 'Q2'}
        tree = QueryMarker.run(tree, query_name_map)
        exp_tree = L.Parser.p('''
            def main():
                print(QUERY('Q1', 1 + 2))
                print(QUERY('A', 3 + 4))
                print(QUERY('Q2', 3 + 4))
            ''')
        self.assertEqual(tree, exp_tree)
    
    def test_notfound(self):
        tree = L.Parser.p('''
            def main():
                print(QUERY('A', 3 + 4))
            ''')
        with self.assertRaises(L.ProgramError):
            QueryMarker.run(tree, {L.Parser.pe('1 + 2'): 'Q'},
                                strict=True)
        with self.assertRaises(L.ProgramError):
            QueryMarker.run(tree, {L.Parser.pe('3 + 4'): 'Q'},
                                strict=True)
    
    def test_nested(self):
        tree = L.Parser.p('''
            def main():
                print(1 + (2 + 3))
            ''')
        query_name_map = {L.Parser.pe('(2 + 3)'): 'Q1',
                          L.Parser.pe('1 + (2 + 3)'): 'Q2'}
        tree = preprocess_query_markings(tree, query_name_map)
        exp_tree = L.Parser.p('''
            def main():
                print(QUERY('Q2', (1 + QUERY('Q1', (2 + 3)))))
            ''')
        self.assertEqual(tree, exp_tree)


class FirstThenCase(unittest.TestCase):
    
    def test_postprocess(self):
        tree = L.Parser.p('''
            def main():
                print(FIRSTTHEN(a, b))
            ''')
        tree = postprocess_firstthen(tree)
        exp_tree = L.Parser.p('''
            def main():
                print((a or True) and b)
            ''')
        self.assertEqual(tree, exp_tree)


class ClauseCase(unittest.TestCase):
    
    def test_preprocess_postprocess(self):
        orig_tree = L.Parser.p('''
            def main():
                {x for (x, y) in S for (x, y) in REL(R)
                   for (x, y) in {e} for (x, y) in R - {e}
                   for (x, y) in QUERY('Q', 1 + 1)}
            ''')
        tree = preprocess_clauses(orig_tree)
        exp_tree = L.Parser.p('''
            def main():
                {x for (x, y) in S for (x, y) in REL(R)
                   for (x, y) in SING(e) for (x, y) in WITHOUT(R, e)
                   for (x, y) in QUERY('Q', 1 + 1)}
            ''')
        self.assertEqual(tree, exp_tree)
        
        tree = postprocess_clauses(tree)
        self.assertEqual(tree, orig_tree)


class DisallowCase(unittest.TestCase):
    
    def test_disallower_generalcall(self):
        # Call nodes good.
        disallow_features(L.Parser.pc('f(a)'))
        # GeneralCall nodes bad.
        with self.assertRaises(TypeError):
            disallow_features(L.Parser.pc('o.f(a)'))


class AnnotationCase(unittest.TestCase):
    
    def test_annotation(self):
        check_annotations(L.Parser.pe("QUERY('Q', 1, {'nodemand': 2})"))
        
        with self.assertRaises(L.ProgramError):
            check_annotations(L.Parser.pe("QUERY('Q', 1, 2)"))
        
        with self.assertRaises(L.ProgramError):
            check_annotations(L.Parser.pe("QUERY('Q', 1, {'foo': 2})"))


if __name__ == '__main__':
    unittest.main()
