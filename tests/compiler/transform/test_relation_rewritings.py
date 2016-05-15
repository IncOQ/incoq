"""Unit tests for relation_rewritings.py."""


import unittest

from incoq.compiler.incast import L
from incoq.compiler.type import T
from incoq.compiler.symbol import S, N
from incoq.compiler.transform.relation_rewritings import *
from incoq.compiler.transform.relation_rewritings import (
    rewrite_with_unwraps, rewrite_with_wraps)


class UpdateRewritingsCase(unittest.TestCase):
    
    def test_rewrite_memberconds(self):
        comp = L.Parser.pe('{a for x in s if x in t if (x, y) in o.f}')
        symtab = S.SymbolTable()
        symtab.define_query('Q', node=comp)
        tree = L.Parser.p('''
            def main():
                print(QUERY('Q', _COMP))
            ''', subst={'_COMP': comp})
        
        tree = rewrite_memberconds(tree, symtab)
        exp_tree = L.Parser.p('''
            def main():
                print(QUERY('Q', {a for x in s for x in t
                                    for (x, y) in o.f}))
            ''')
        self.assertEqual(tree, exp_tree)
    
    def test_expand_bulkupdates(self):
        symtab = S.SymbolTable()
        tree = L.Parser.p('''
            def main():
                S.update(T)
                S.intersection_update(T)
                S.difference_update(T)
                S.symmetric_difference_update(T)
                S.copy_update(T)
                D.dictcopy_update(E)
            ''')
        tree = expand_bulkupdates(tree, symtab)
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
                if (D is not E):
                    for _v6 in list(D):
                        del D[_v6]
                    for _v6 in E:
                        D[_v6] = E[_v6]
            ''')
        self.assertEqual(tree, exp_tree)
    
    def test_specialization(self):
        symtab = S.SymbolTable()
        symtab.define_relation('S')
        symtab.define_map('M')
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
        tree = specialize_rels_and_maps(orig_tree, symtab)
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
        
        tree = unspecialize_rels_and_maps(tree, symtab)
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
    
    def test_expand_clear(self):
        symtab = S.SymbolTable()
        tree = L.Parser.p('''
            def main():
                S.clear()
                M.dictclear()
            ''')
        tree = expand_clear(tree, symtab)
        exp_tree = L.Parser.p('''
            def main():
                for _v1 in list(S):
                    S.remove(_v1)
                for _v2 in list(M):
                    del M[_v2]
            ''')
        self.assertEqual(tree, exp_tree)
    
    def test_rewrite_with_unwraps(self):
        comp1 = L.Parser.pe('''
            {2 * x for x in R}
            ''')
        comp2 = L.Parser.pe('''
            {(2 * x,) for x in R}
            ''')
        comp3 = L.Parser.pe('''
            {2 * y for (y,) in VARS(QUERY('Q1', {2 * x for x in R}))
                   for (y,) in VARS(QUERY('Q2', {(2 * x,) for x in R}))}
            ''')
        symtab = S.SymbolTable()
        symtab.define_query('Q1', node=comp1, type=T.Set(T.Number))
        symtab.define_query('Q2', node=comp2)
        symtab.define_query('Q3', node=comp3)
        tree = L.Parser.p('''
            def main():
                print(QUERY('Q3', _COMP))
            ''', subst={'_COMP': comp3})
        
        tree = rewrite_with_unwraps(tree, symtab)
        exp_tree = L.Parser.p('''
            def main():
                print(unwrap(QUERY('Q3',
                {((2 * y),) for (y,) in VARS(unwrap(QUERY('Q1',
                                {((2 * x),) for x in R})))
                            for (y,) in VARS(QUERY('Q2',
                                {((2 * x),) for x in R}))})))
            ''')
        self.assertEqual(tree, exp_tree)
        t = symtab.get_queries()['Q1'].type
        exp_t = T.Set(T.Tuple([T.Number]))
        self.assertEqual(t, exp_t)
    
    def test_rewrite_with_wraps(self):
        comp = L.Parser.pe('''
            {2 * x for x in R for y in unwrap(R) for (z,) in R}
            ''')
        symtab = S.SymbolTable()
        symtab.define_query('Q', node=comp)
        tree = L.Parser.p('''
            def main():
                print(QUERY('Q', _COMP))
            ''', subst={'_COMP': comp})
        
        tree = rewrite_with_wraps(tree, symtab)
        exp_tree = L.Parser.p('''
            def main():
                print(QUERY('Q', {(2 * x) for (x,) in VARS(wrap(R))
                                          for (y,) in VARS(R)
                                          for (z,) in R}))
            ''')
        self.assertEqual(tree, exp_tree)
    
    def test_relationalize_clauses(self):
        comp = L.Parser.pe('{x for (x,) in R for y in S for z in t}')
        symtab = S.SymbolTable()
        symtab.define_query('Q', node=comp)
        symtab.define_relation('R')
        symtab.define_relation('S')
        tree = L.Parser.p('''
            def main():
                print(QUERY('Q', {x for (x,) in R for y in S for z in t}))
            ''')
        tree = relationalize_clauses(tree, symtab)
        exp_tree = L.Parser.p('''
            def main():
                print(QUERY('Q',
                    {x for (x,) in REL(R) for (y,) in VARS(wrap(S))
                       for z in t}))
            ''')
        self.assertEqual(tree, exp_tree)
    
    def test_eliminate_dead_relations(self):
        symtab = S.SymbolTable()
        symtab.define_relation('R')
        symtab.define_relation('S')
        tree = L.Parser.p('''
            def main():
                R.reladd(x)
                S.reladd(y)
                t.add(z)
                print(S)
            ''')
        tree = eliminate_dead_relations(tree, symtab)
        exp_tree = L.Parser.p('''
            def main():
                S.reladd(y)
                t.add(z)
                print(S)
            ''')
        self.assertEqual(tree, exp_tree)
        rels = symtab.get_relations().keys()
        exp_rels = ['S']
        self.assertCountEqual(rels, exp_rels)


if __name__ == '__main__':
    unittest.main()
