"""Unit tests for pynodes.py."""


import unittest

import incoq.compiler.incast.nodes as L
import incoq.compiler.incast.pynodes as P


class PynodesCase(unittest.TestCase):
    
    def trip(self, source, exp_source=None):
        if exp_source is None:
            exp_source = source
        tree = P.Parser.p(source)
        source = P.Parser.ts(tree)
        self.assertEqual(source, exp_source)
    
    def test_parse(self):
        tree = P.Parser.ps('a = _b', patterns=True,
                           subst={'a': P.Name('c', P.Store())})
        exp_tree = P.Assign(targets = (P.Name(id = 'c',
                                              ctx = P.Store()),),
                            value = L.PatVar(id = '_b'))
        self.assertEqual(tree, exp_tree)
    
    def test_unparse(self):
        self.trip('a = b')

        self.trip(P.trim('''
            if a:
                pass
            elif b:
                pass
            else:
                pass
            '''))
    
    def test_unparse_comment(self):
        self.trip("COMMENT('Test')", '# Test')
        
        self.trip(P.trim('''
            for x in S:
                COMMENT('Test')
                pass
            '''), P.trim('''
            for x in S:
                # Test
                pass
            '''))


if __name__ == '__main__':
    unittest.main()
