"""Unit tests for symbols.py."""


import unittest

from incoq.mars.incast import L
from incoq.mars.type import T
from incoq.mars.symbol.symbols import *


class MetaSymbolCase(unittest.TestCase):
    
    def test_symbolattribute_default(self):
        class Sym:
            A = SymbolAttribute('A', 1, None)
        s = Sym()
        self.assertEqual(s.A, 1)
        Sym.default_A = 2
        self.assertEqual(s.A, 2)
        s.A = 3
        self.assertEqual(s.A, 3)
    
    def test_symbolattribute_allowed_values(self):
        class Sym:
            A = SymbolAttribute('A', None, None, allowed_values=[1, 2])
        s = Sym()
        s.A = 1
        s.A = 2
        with self.assertRaises(ValueError):
            s.A = 3
    
    def test_metasymbol_symbol_attrs(self):
        self.assertEqual(Symbol._symbol_attrs, ())
        
        class Sym(Symbol):
            A = SymbolAttribute('A', None, None)
            B = SymbolAttribute('B', None, None)
        self.assertEqual(Sym._symbol_attrs, (Sym.A, Sym.B))
    
    def test_metasymbol_name_consistency(self):
        with self.assertRaises(AssertionError):
            class Sym(Symbol):
                A = SymbolAttribute('B', None, None)
    
    def test_symbol_update(self):
        class Sym(Symbol):
            A = SymbolAttribute('A', None, None)
            B = SymbolAttribute('B', None, None, parser=lambda x: 5)
        s = Sym('s')
        s.update(A=1)
        self.assertEqual(s.A, 1)
        s.parse_and_update(B=2)
        self.assertEqual(s.B, 5)
    
    def test_symbol_clone_attrs(self):
        class Sym(Symbol):
            A = SymbolAttribute('A', None, None)
            B = SymbolAttribute('B', None, None)
        s = Sym('s', A=1)
        self.assertEqual(s.clone_attrs(), {'A': 1})


class SymbolCase(unittest.TestCase):
    
    def test_rel(self):
        r = RelationSymbol('R', type=T.Set(T.Top))
        s = str(r)
        exp_s = 'Relation R (type: {Top})'
        self.assertEqual(s, exp_s)
        
        s = r.decl_comment
        exp_s = 'R : {Top}'
        self.assertEqual(s, exp_s)
    
    def test_map(self):
        m = MapSymbol('M')
        s = str(m)
        exp_s = 'Map M (type: {Bottom: Bottom})'
        self.assertEqual(s, exp_s)
    
    def test_var(self):
        v = VarSymbol('v', type=T.Set(T.Top))
        s = str(v)
        exp_s = 'Var v (type: {Top})'
        self.assertEqual(s, exp_s)
    
    def test_query(self):
        q = QuerySymbol('Q', node=L.Num(5))
        s = str(q)
        exp_s = 'Query Q (5)'
        self.assertEqual(s, exp_s)


if __name__ == '__main__':
    unittest.main()
