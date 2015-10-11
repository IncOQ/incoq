"""Unit tests for optimized.py."""


import unittest

from incoq.mars.incast import L
import incoq.mars.types as T
from incoq.mars.symtab import SymbolTable
from incoq.mars.transform.optimize import *
from incoq.mars.transform.optimize import SingletonUnwrapper


class UnwrapSingletonsCase(unittest.TestCase):
    
    def test_unwrapper_updates(self):
        symtab = SymbolTable()
        tree = L.Parser.p('''
            def main():
                v = (1,)
                S.reladd(v)
                v = 2
                T.reladd(v)
            ''')
        tree = SingletonUnwrapper.run(tree, symtab.fresh_vars, ['S'])
        exp_tree = L.Parser.p('''
            def main():
                v = (1,)
                _v1 = v[0]
                S.reladd(_v1)
                v = 2
                T.reladd(v)
            ''')
        self.assertEqual(tree, exp_tree)
    
    def test_unwrapper_loops(self):
        symtab = SymbolTable()
        tree = L.Parser.p('''
            def main():
                for x in S:
                    (y,) = x
                    print(y)
                for z in T:
                    print(z)
                for (x2,) in S:
                    pass
                for (z2,) in T:
                    pass
            ''')
        tree = SingletonUnwrapper.run(tree, symtab.fresh_vars, ['S'])
        exp_tree = L.Parser.p('''
            def main():
                for _v1 in S:
                    x = (_v1,)
                    (y,) = x
                    print(y)
                for z in T:
                    print(z)
                for x2 in S:
                    pass
                for (z2,) in T:
                    pass
            ''')
        self.assertEqual(tree, exp_tree)
    
    def test_unwrap(self):
        symtab = SymbolTable()
        symtab.define_relation('S', type=T.Set(T.Tuple([T.Number])))
        symtab.define_relation('T', type=T.Set(T.Tuple([T.Number, T.Number])))
        tree = L.Parser.p('''
            def main():
                v = (1,)
                S.reladd(v)
                v = (2, 3)
                T.reladd(v)
                for x in S:
                    (y,) = x
                    print(y)
                for x2 in T:
                    print(x2)
            ''')
        tree, rel_names = unwrap_singletons(tree, symtab)
        exp_tree = L.Parser.p('''
            def main():
                v = (1,)
                _v1 = v[0]
                S.reladd(_v1)
                v = (2, 3)
                T.reladd(v)
                for _v3 in S:
                    x = (_v3,)
                    (y,) = x
                    print(y)
                for x2 in T:
                    print(x2)
            ''')
        self.assertEqual(tree, exp_tree)
        exp_rel_names = {'S'}
        self.assertEqual(rel_names, exp_rel_names)
        exp_S_type = T.Set(T.Number)
        exp_T_type = T.Set(T.Tuple([T.Number, T.Number]))
        self.assertEqual(symtab.get_relations()['S'].type, exp_S_type)
        self.assertEqual(symtab.get_relations()['T'].type, exp_T_type)


if __name__ == '__main__':
    unittest.main()
