"""Unit tests for incast_rewritings.py."""


import unittest

from incoq.mars.incast import L
from incoq.mars.symbol import N
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
                   for (x, y) in VARS(QUERY('Q', 1 + 1))}
            ''')
        self.assertEqual(tree, exp_tree)
        
        tree = postprocess_clauses(tree)
        self.assertEqual(tree, orig_tree)


class BulkUpdatesCase(unittest.TestCase):
    
    def test_preprocess(self):
        tree = L.Parser.p('''
            def main():
                S.update(T)
                S.intersection_update(T)
                S.difference_update(T)
                S.symmetric_difference_update(T)
                S.copy_update(T)
            ''')
        tree = preprocess_bulkupdates(tree, N.fresh_name_generator())
        exp_tree = L.Parser.p('''
            def main():
                for _v1 in T:
                    if (_v1 not in S):
                        S.add(_v1)
                for _v2 in list(S):
                    if (_v2 not in T):
                        S.remove(_v2)
                for _v3 in list(T):
                    if (_v3 in S):
                        S.remove(_v3)
                for _v4 in list(T):
                    if (_v4 in S):
                        S.remove(_v4)
                    else:
                        S.add(_v4)
                for _v5 in list(S):
                    if (_v5 not in T):
                        S.remove(_v5)
                for _v5 in list(T):
                    if (_v5 not in S):
                        S.add(_v5)
            ''')
        self.assertEqual(tree, exp_tree)
        
        # Arbitrary expressions are allowed at this point.
        tree = L.Parser.p('''
            def main():
                S.update(1+1)
            ''')
        tree = preprocess_bulkupdates(tree, N.fresh_name_generator())
        exp_tree = L.Parser.p('''
            def main():
                for _v1 in 1+1:
                    if _v1 not in S:
                        S.add(_v1)
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
                S.clear()
                (a + b).clear()
                M[k] = v
                del M[k]
                M.dictclear()
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
                S.relclear()
                (a + b).clear()
                M.mapassign(k, v)
                M.mapdelete(k)
                M.mapclear()
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
                S.clear()
                (a + b).clear()
                M[k] = v
                del M[k]
                M.dictclear()
                N[k] = v
                {x for (x, y) in S}
            ''')
        self.assertEqual(tree, exp_tree)


class SetClearCase(unittest.TestCase):
    
    def test_preprocess(self):
        tree = L.Parser.p('''
            def main():
                S.clear()
            ''')
        tree = preprocess_setclear(tree, N.fresh_name_generator())
        exp_tree = L.Parser.p('''
            def main():
                for _v1 in list(S):
                    S.remove(_v1)
            ''')
        self.assertEqual(tree, exp_tree)
        
        # Arbitrary expression case.
        tree = L.Parser.p('''
            def main():
                (1+1).clear()
            ''')
        tree = preprocess_setclear(tree, N.fresh_name_generator())
        exp_tree = L.Parser.p('''
            def main():
                for _v1 in list(1+1):
                    (1+1).remove(_v1)
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
