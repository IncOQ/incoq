"""Unit tests for nodeconv.py."""


import unittest

from oinc.incast.nodes import *
from oinc.incast.structconv import parse_structast
from oinc.incast.nodeconv import *
from oinc.incast.nodeconv import value_to_ast


class NodeconvCase(unittest.TestCase):
    
    def p(self, source, mode=None):
        return parse_structast(source, mode=mode)
    
    def pc(self, source):
        return self.p(source, mode='code')
    
    def ps(self, source):
        return self.p(source, mode='stmt')
    
    def pe(self, source):
        return self.p(source, mode='expr')
    
    def test_valuetoast(self):
        val = {1: 'a', 2: [{3: False}, ({4}, 5, None)]}
        tree = value_to_ast(val)
        exp_tree = self.pe('{1: "a", 2: [{3: False}, ({4}, 5, None)]}')
        self.assertEqual(tree, exp_tree)
    
    def test_import_SetUpdate(self):
        tree = self.ps('S.add(x)')
        tree = IncLangImporter.run(tree)
        exp_tree = SetUpdate(Name('S', Load()), 'add', Name('x', Load()))
        self.assertEqual(tree, exp_tree)
    
    def test_import_OPTIONS(self):
        tree = self.ps('OPTIONS(a = "b")')
        tree = IncLangImporter.run(tree)
        exp_tree = NOptions({'a': 'b'})
        self.assertEqual(tree, exp_tree)
    
    def test_import_MAINT(self):
        tree = self.pc('''
            with MAINT(Q, 'after', 'S.add(x)'):
                S.add(x)
                pass
            ''')
        tree = IncLangImporter.run(tree)
        update_node = SetUpdate(Name('S', Load()), 'add', Name('x', Load()))
        exp_tree = (Maintenance('Q', 'S.add(x)',
                                (), (update_node,), (Pass(),)),)
        self.assertEqual(tree, exp_tree)
    
    def test_import_COMP(self):
        tree = self.pe('COMP({x for x in S}, [S], {"a": "b"})')
        tree = IncLangImporter.run(tree)
        exp_tree = Comp(
            Name('x', Load()),
            (Enumerator(Name('x', Store()), Name('S', Load())),),
            ('S',), {'a': 'b'})
        self.assertEqual(tree, exp_tree)
        
        # Make sure omitting params/options works.
        
        tree1 = self.pe('COMP({x for x in S})')
        tree1 = IncLangImporter.run(tree1)
        tree2 = self.pe('COMP({x for x in S}, None, None)')
        tree2 = IncLangImporter.run(tree2)
        exp_tree = Comp(
            Name('x', Load()),
            (Enumerator(Name('x', Store()), Name('S', Load())),),
            None, None)
        self.assertEqual(tree1, exp_tree)
        self.assertEqual(tree2, exp_tree)
    
    def test_export(self):
        orig_tree = self.p('''
            OPTIONS(u = 'v')
            S.add(x)
            setmatch(R, 'bu', x)
            COMP({x for x in S if x in T}, [S], {'a': 'b'})
            sum(R)
            ''')
        tree = IncLangImporter.run(orig_tree)
        tree = IncLangExporter.run(tree)
        exp_tree = self.p('''
            OPTIONS(...)
            S.add(x)
            setmatch(R, 'bu', x)
            COMP({x for x in S if x in T}, [S], {'a': 'b'})
            sum(R, None)
            ''')
        self.assertEqual(tree, exp_tree)


if __name__ == '__main__':
    unittest.main()
