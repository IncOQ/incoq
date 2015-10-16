"""Unit tests for symtab.py."""


import unittest

from incoq.mars.incast import L
from incoq.mars.types import Set, Top
from incoq.mars.symtab import *


class NamingCase(unittest.TestCase):
    
    def test_fresh_name_generator(self):
        gen = N.fresh_name_generator('x{}')
        names = [next(gen) for _ in range(3)]
        exp_names = ['x1', 'x2', 'x3']
        self.assertEqual(names, exp_names)
    
    def test_subnames(self):
        names = N.get_subnames('x', 3)
        exp_names = ['x_v1', 'x_v2', 'x_v3']
        self.assertEqual(names, exp_names)
    
    def test_auxmap(self):
        name = N.get_auxmap_name('R', L.mask('bu'))
        exp_name = 'R_bu'
        self.assertEqual(name, exp_name)
    
    def test_maintfunc(self):
        name = N.get_maint_func_name('Q', 'R', 'add')
        exp_name = '_maint_Q_for_R_add'
        self.assertEqual(name, exp_name)


class SymbolCase(unittest.TestCase):
    
    def test_rel(self):
        r = RelationSymbol('R', type=Set(Top))
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
        v = VarSymbol('v', type=Set(Top))
        s = str(v)
        exp_s = 'Var v (type: {Top})'
        self.assertEqual(s, exp_s)
    
    def test_query(self):
        q = QuerySymbol('Q', node=L.Num(5))
        s = str(q)
        exp_s = 'Query Q (5)'
        self.assertEqual(s, exp_s)


class SymbolTableCase(unittest.TestCase):
    
    def test_fresh_vars(self):
        symtab = SymbolTable()
        v = next(symtab.fresh_vars)
        exp_v = '_v1'
        self.assertEqual(v, exp_v)
        v = next(symtab.fresh_vars)
        exp_v = '_v2'
        self.assertEqual(v, exp_v)
    
    def test_symbols(self):
        symtab = SymbolTable()
        symtab.define_relation('R')
        symtab.define_relation('S')
        symtab.define_map('M')
        
        rels = list(symtab.get_relations().keys())
        exp_rels = ['R', 'S']
        self.assertSequenceEqual(rels, exp_rels)
    
    def test_dump(self):
        symtab = SymbolTable()
        symtab.define_relation('R')
        symtab.define_relation('S')
        symtab.define_map('M')
        
        s = symtab.dump_symbols()
        exp_s = L.trim('''
            Relation R (type: {Bottom})
            Relation S (type: {Bottom})
            Map M (type: {Bottom: Bottom})
            ''')
        self.assertEqual(s, exp_s)


if __name__ == '__main__':
    unittest.main()
