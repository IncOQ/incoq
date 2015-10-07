"""Unit tests for optimized.py."""


import unittest

from incoq.mars.incast import L
import incoq.mars.types as T
from incoq.mars.symtab import SymbolTable
from incoq.mars.transform.optimize import *
from incoq.mars.transform.optimize import SingletonUnwrapper


class FlattenSingletonsCase(unittest.TestCase):
    
    def test_unwrapper(self):
        symtab = SymbolTable()
        tree = L.Parser.p('''
            def main():
                S.reladd((1,))
                T.reladd(2)
                for x in S:
                    (y,) = x
                    print(y)
                for z in T:
                    print(z)
            ''')
        tree = SingletonUnwrapper.run(tree, symtab.fresh_vars, ['S'])
        exp_tree = L.Parser.p('''
            def main():
                S.reladd((1,)[0])
                T.reladd(2)
                for _v1 in S:
                    x = (_v1,)
                    (y,) = x
                    print(y)
                for z in T:
                    print(z)
            ''')
        self.assertEqual(tree, exp_tree)
    
    def test_flatten(self):
        symtab = SymbolTable()
        symtab.define_relation('S', type=T.Set(T.Tuple([T.Number])))
        symtab.define_relation('T', type=T.Set(T.Tuple([T.Number, T.Number])))
        tree = L.Parser.p('''
            def main():
                S.reladd((1,))
                T.reladd((2, 3))
                for x in S:
                    (y,) = x
                    print(y)
                for x2 in T:
                    print(x2)
            ''')
        tree = flatten_singletons(tree, symtab)
        exp_tree = L.Parser.p('''
            def main():
                S.reladd((1,)[0])
                T.reladd((2, 3))
                for _v1 in S:
                    x = (_v1,)
                    (y,) = x
                    print(y)
                for x2 in T:
                    print(x2)
            ''')
        self.assertEqual(tree, exp_tree)
        exp_S_type = T.Set(T.Number)
        exp_T_type = T.Set(T.Tuple([T.Number, T.Number]))
        self.assertEqual(symtab.get_relations()['S'].type, exp_S_type)
        self.assertEqual(symtab.get_relations()['T'].type, exp_T_type)


if __name__ == '__main__':
    unittest.main()
