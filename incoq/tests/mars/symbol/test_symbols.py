"""Unit tests for symbols.py."""


import unittest

from incoq.mars.incast import L
from incoq.mars.type import T
from incoq.mars.symbol.symbols import *


class SymbolCase(unittest.TestCase):
    
    def test_metasymbol(self):
        self.assertEqual(Symbol._symbol_attrs, (Symbol.name,))
        
        TS = TypedSymbolMixin
        self.assertEqual(TS._symbol_attrs,
                         (Symbol.name, TS.type, TS.min_type, TS.max_type))
    
    def test_symbol(self):
        r = RelationSymbol('R', type=T.Set(T.Top))
        self.assertEqual(r.clone_attrs(), {'type': T.Set(T.Top)})
    
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
