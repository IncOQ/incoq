"""Unit tests for macros.py."""


import unittest

from invinc.compiler.incast.nodes import *
from invinc.compiler.incast.structconv import parse_structast
from invinc.compiler.incast.macros import *


class MacroCase(unittest.TestCase):
    
    def p(self, source, mode=None, subst=None):
        tree = parse_structast(source, mode=mode, subst=subst)
        return IncMacroProcessor.run(tree)
    
    def pe(self, source):
        return self.p(source, mode='expr')
    
    def test_IncMacro(self):
        tree = self.p('S.nsadd(x)')
        update_node = SetUpdate(self.pe('S'), 'add', self.pe('x'))
        exp_tree = self.p('''
            if x not in S:
                UPDATE
            ''', subst={'<c>UPDATE': update_node})
        self.assertEqual(tree, exp_tree)
    
    def test_setmap(self):
        tree = self.p('S.smassignkey("bbu", k, v, "_")')
        exp_tree = self.p('''
            (_1, _2) = k
            S.add((_1, _2, v))
            ''')
        self.assertEqual(tree, exp_tree)
        
        tree = self.p('S.smdelkey("bbu", k, "_")')
        exp_tree = self.p('''
            (_1, _2) = k
            _elem = S.smlookup("bbu", k)
            S.remove((_1, _2, _elem))
            ''')
        self.assertEqual(tree, exp_tree)
        
        tree = self.p('S.smnsassignkey("bbu", k, v, "_")')
        exp_tree = self.p('''
            (_1, _2) = k
            if not setmatch(S, "bbu", k).isempty():
                _elem = S.smlookup("bbu", k)
                S.remove((_1, _2, _elem))
            S.add((_1, _2, v))
            ''')
        self.assertEqual(tree, exp_tree)
        
        tree = self.p('S.smnsdelkey("bbu", k, "_")')
        exp_tree = self.p('''
            if not setmatch(S, "bbu", k).isempty():
                (_1, _2) = k
                _elem = S.smlookup("bbu", k)
                S.remove((_1, _2, _elem))
            ''')
        self.assertEqual(tree, exp_tree)
        
        tree = self.p('S.smreassignkey("bbu", k, v, "_")')
        exp_tree = self.p('''
            (_1, _2) = k
            _elem = S.smlookup("bbu", k)
            S.remove((_1, _2, _elem))
            S.add((_1, _2, v))
            ''')
        self.assertEqual(tree, exp_tree)
    
    def test_fields(self):
        tree = self.p('''
            o.nsassignfield(f, v)
            o.nsdelfield(g)
            ''')
        exp_tree = self.p('''
            if hasattr(o, 'f'):
                del o.f
            o.f = v
            if hasattr(o, 'g'):
                del o.g
            ''')
        self.assertEqual(tree, exp_tree)


if __name__ == '__main__':
    unittest.main()

