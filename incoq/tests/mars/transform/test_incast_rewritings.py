"""Unit tests for incast_rewritings.py."""


import unittest

from incoq.mars.incast import L
from incoq.mars.symtab import N
from incoq.mars.transform.incast_rewritings import *
from incoq.mars.transform.incast_rewritings import QueryMarker


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


class RelMapCase(unittest.TestCase):
    
    def test_preprocess_postprocess(self):
        orig_tree = L.Parser.p('''
            def main():
                S.add(x)
                S.add(x + y)
                T.add(x)
                (a + b).add(x)
                M[k] = v
                del M[k]
                N[k] = v
                {x for (x, y) in S}
            ''')
        tree = preprocess_rels_and_maps(orig_tree, N.fresh_name_generator(),
                                        ['S'], ['M'])
        exp_tree = L.Parser.p('''
            def main():
                S.reladd(x)
                _v1 = (x + y)
                S.reladd(_v1)
                T.add(x)
                (a + b).add(x)
                M.mapassign(k, v)
                M.mapdelete(k)
                N[k] = v
                {x for (x, y) in REL(S)}
            ''')
        self.assertEqual(tree, exp_tree)
        
        tree = postprocess_rels_and_maps(tree)
        exp_tree = L.Parser.p('''
            def main():
                S.add(x)
                _v1 = (x + y)
                S.add(_v1)
                T.add(x)
                (a + b).add(x)
                M[k] = v
                del M[k]
                N[k] = v
                {x for (x, y) in S}
            ''')
        self.assertEqual(tree, exp_tree)


class DisallowCase(unittest.TestCase):
    
    def test_disallower_attr(self):
        with self.assertRaises(TypeError):
            disallow_features(L.Parser.pc('o.f'))
    
    def test_disallower_generalcall(self):
        # Call nodes good.
        disallow_features(L.Parser.pc('f(a)'))
        # GeneralCall nodes bad.
        with self.assertRaises(TypeError):
            disallow_features(L.Parser.pc('o.f(a)'))


if __name__ == '__main__':
    unittest.main()
