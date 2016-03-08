"""Unit tests for relation_rewritings.py."""


import unittest

from incoq.mars.incast import L
from incoq.mars.symbol import S, N
from incoq.mars.transform.relation_rewritings import *


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


if __name__ == '__main__':
    unittest.main()
