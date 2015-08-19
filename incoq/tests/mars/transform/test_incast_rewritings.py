"""Unit tests for incast_rewritings.py."""


import unittest

from incoq.mars.incast import L
from incoq.mars.transform.incast_rewritings import *


class RelUpdateCase(unittest.TestCase):
    
    def test_preprocess(self):
        orig_tree = L.Parser.p('''
            def main():
                S.add(1)
                T.add(2)
                (a + b).add(3)
            ''')
        tree = SetUpdateImporter.run(orig_tree, ['S'])
        exp_tree = L.Parser.p('''
            def main():
                S.reladd(1)
                T.add(2)
                (a + b).add(3)
            ''')
        self.assertEqual(tree, exp_tree)
        
        tree = RelUpdateExporter.run(tree)
        self.assertEqual(tree, orig_tree)


class RewritingsCase(unittest.TestCase):
    
    def test_disallow_attr(self):
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
