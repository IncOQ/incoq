"""Unit tests for symtab.py."""


import unittest

from incoq.mars.incast import L
from incoq.mars.symtab import *


class NamingCase(unittest.TestCase):
    
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
        r = RelationSymbol('R')
        self.assertIs(r.arity, None)
        r.unify(arity=2)
        self.assertEqual(r.arity, 2)
        
        s = str(r)
        exp_s = 'Relation R (arity: 2)'
        self.assertEqual(s, exp_s)
        
        with self.assertRaises(L.ProgramError):
            r.unify(arity=3)
    
    def test_map(self):
        m = MapSymbol('M')
        s = str(m)
        exp_s = 'Map M'
        self.assertEqual(s, exp_s)


class SymbolTableCase(unittest.TestCase):
    
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
            Relation R
            Relation S
            Map M
            ''')
        self.assertEqual(s, exp_s)


if __name__ == '__main__':
    unittest.main()
