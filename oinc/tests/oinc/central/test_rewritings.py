"""Unit tests for rewritings.py."""


import unittest

import oinc.incast as L
from oinc.central.manager import CentralCase
from oinc.central.rewritings import *


class RewriterCase(CentralCase):
    
    def test_distalgo(self):
        tree = L.parse_structast('''
            len(set((a for a in S))) > 0
            ''')
        tree = DistalgoImporter.run(tree)
        exp_tree = L.parse_structast('''
            count({a for a in S}) > 0
            ''')
        self.assertEqual(tree, exp_tree)
    
    def test_relationfinder(self):
        tree = L.p('''
            R = runtimelib.Set()
            S = set()
            T = 5
            
            ''')
        res = RelationFinder.run(tree)
        exp_res = ['R', 'S']
        self.assertCountEqual(res, exp_res)
        
        tree = L.p('''
            R = Set()
            S = Set()
            T = Set()
            for x in R:
                S.add({(x, y) for y in R})
            print(T)
            ''')
        res = RelationFinder.run(tree)
        exp_res = ['R', 'S']
        self.assertCountEqual(res, exp_res)
    
    def test_macroupdaterewriter(self):
        tree = L.p('''
            A.update(B)
            A.intersection_update(B)
            A.difference_update(B)
            A.symmetric_difference_update(B)
            A.assign_update(B)
            A.clear()
            ''')
        tree = MacroSetUpdateRewriter.run(tree)
        
        exp_tree = L.p('''
            for _upelem in B:
                if (_upelem not in A):
                    A.add(_upelem)
            for _upelem in list(A):
                if (_upelem not in B):
                    A.remove(_upelem)
            for _upelem in list(B):
                if (_upelem in A):
                    A.remove(_upelem)
            for _upelem in list(B):
                if (_upelem in A):
                    A.remove(_upelem)
                else:
                    A.add(_upelem)
            if A is not B:
                while (len(A) > 0):
                    _upelem = next(iter(A))
                    A.remove(_upelem)
                for _upelem in B:
                    A.add(_upelem)
            while (len(A) > 0):
                _upelem = next(iter(A))
                A.remove(_upelem)
            ''')
        
        self.assertEqual(tree, exp_tree)
    
    def test_updaterewriter(self):
        tree = L.p('''
            R.add((x, y))
            S.remove((o.f, v))
            T.add(z)
            T.remove((3 + 5, 4))
            U.add(foo(x))
            ''')
        tree = UpdateRewriter.run(tree, self.manager.namegen)
        exp_tree = L.p('''
            R.add((x, y))
            v1 = (o.f, v)
            S.remove(v1)
            T.add(z)
            T.remove((3 + 5, 4))
            v2 = foo(x)
            U.add(v2)
            ''')
        self.assertEqual(tree, exp_tree)
    
    def test_minmax(self):
        tree = L.p('''
            max({1} | {x for x in R} | S)
            max({1} & {1, 2})
            ''')
        tree = MinMaxRewriter.run(tree)
        exp_tree = L.p('''
            max2(max2(1), max({x for x in R}), max(S))
            max({1} & {1, 2})
            ''')
        self.assertEqual(tree, exp_tree)
    
    def test_deadcode(self):
        tree = L.p('''
            A = Set()
            B = Set()
            C = Set()
            for x in A:
                B.add(y)
            C.add(z)
            print(C)
            ''')
        tree = eliminate_deadcode(tree, obj_domain_out=True)
        
        exp_tree = L.p('''
            A = Set()
            pass
            C = Set()
            for x in A:
                pass
            C.add(z)
            print(C)
            ''')
        
        self.assertEqual(tree, exp_tree)


if __name__ == '__main__':
    unittest.main()
