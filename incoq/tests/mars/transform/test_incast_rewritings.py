"""Unit tests for incast_rewritings.py."""


import unittest
import string

from incoq.mars.incast import L
from incoq.mars.transform.incast_rewritings import *


class SetMapCase(unittest.TestCase):
    
    def test_preprocess(self):
        orig_tree = L.Parser.p('''
            def main():
                S.add(1)
                T.add(2)
                (a + b).add(3)
                M[k] = v
                del M[k]
                print(M.get(k, d))
                N[k] = v
            ''')
        tree = SetMapImporter.run(orig_tree, ['S'], ['M'])
        exp_tree = L.Parser.p('''
            def main():
                S.reladd(1)
                T.add(2)
                (a + b).add(3)
                M.mapassign(k, v)
                M.mapdelete(k)
                print(M.mapget(k, d))
                N[k] = v
            ''')
        self.assertEqual(tree, exp_tree)
        
        tree = SetMapExporter.run(tree)
        self.assertEqual(tree, orig_tree)


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


class VarsFinderCase(unittest.TestCase):
    
    def test_varsfinder(self):
        # Exclude function name main and iterated relation R.
        tree = L.Parser.p('''
            def main():
                a = b
                c, d = e
                for f, g in h:
                    {i for j in R}
            ''')
        vars = sorted(VarsFinder.run(tree))
        exp_vars = list(string.ascii_lowercase)[:10]
        self.assertEqual(vars, exp_vars)


if __name__ == '__main__':
    unittest.main()
