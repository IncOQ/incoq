"""Unit tests for incast_rewritings.py."""


import unittest

from incoq.mars.incast import L
from incoq.mars.symtab import N
from incoq.mars.transform.incast_rewritings import *


class SetMapCase(unittest.TestCase):
    
    def test_preprocess(self):
        orig_tree = L.Parser.p('''
            def main():
                S.add(x)
                S.add(x + y)
                T.add(x)
                (a + b).add(x)
                M[k] = v
                del M[k]
                N[k] = v
                {x for (x, y) in S}
            ''')
        tree = SetMapImporter.run(orig_tree, N.fresh_var_generator(),
                                  ['S'], ['M'])
        exp_tree = L.Parser.p('''
            def main():
                S.reladd(x)
                _v1 = (x + y)
                S.reladd(_v1)
                T.add(x)
                (a + b).add(x)
                M.mapassign(k, v)
                M.mapdelete(k)
                N[k] = v
                {x for (x, y) in REL(S)}
            ''')
        self.assertEqual(tree, exp_tree)
        
        tree = SetMapExporter.run(tree)
        exp_tree = L.Parser.p('''
            def main():
                S.add(x)
                _v1 = (x + y)
                S.add(_v1)
                T.add(x)
                (a + b).add(x)
                M[k] = v
                del M[k]
                N[k] = v
                {x for (x, y) in S}
            ''')
        self.assertEqual(tree, exp_tree)


class DisallowerCase(unittest.TestCase):
    
    def test_disallower_attr(self):
        with self.assertRaises(TypeError):
            AttributeDisallower.run(L.Parser.pc('o.f'))
    
    def test_disallower_generalcall(self):
        # Call nodes good.
        GeneralCallDisallower.run(L.Parser.pc('f(a)'))
        # GeneralCall nodes bad.
        with self.assertRaises(TypeError):
            GeneralCallDisallower.run(L.Parser.pc('o.f(a)'))


if __name__ == '__main__':
    unittest.main()
