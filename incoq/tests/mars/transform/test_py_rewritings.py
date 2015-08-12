"""Unit tests for py_rewritings.py."""


import unittest

from incoq.mars.incast import P, L
from incoq.mars.transform.py_rewritings import *


class ExpressionPreprocessorCase(unittest.TestCase):
    
    def setUp(self):
        class check(P.ExtractMixin):
            """Check that the input code matches the expected
            output code.
            """
            @classmethod
            def action(cls, source, exp_source=None, *, mode=None):
                if exp_source is None:
                    exp_source = source
                tree = P.Parser.action(source, mode=mode)
                tree = ExpressionPreprocessor.run(tree)
                exp_tree = P.Parser.action(exp_source, mode=mode)
                self.assertEqual(tree, exp_tree)
        
        self.check = check
    
    def test_assignment(self):
        self.check.pc('a = b')
        self.check.pc('a, b = c')
        self.check.pc('a = b = c', 'b = c; a = b')
    
    def test_comparisons(self):
        self.check.pe('a < b')
        self.check.pe('a < b < c', 'a < b and b < c')


class PassPostprocessorCase(unittest.TestCase):
    
    def test_postprocess(self):
        # Make a tree by parsing syntactically valid code, then
        # scrubbing out all the occurrences of Pass. The processor
        # should add them back.
        class PassScrubber(P.NodeTransformer):
            def visit_Pass(self, node):
                return []
        
        orig_tree = P.Parser.p('''
            def f():
                pass
            while True:
                pass
            for x in S:
                pass
            if True:
                pass
            if False:
                x = 1
            ''')
        tree = PassScrubber.run(orig_tree)
        tree = PassPostprocessor.run(tree)
        self.assertEqual(tree, orig_tree)


class RuntimeImportCase(unittest.TestCase):
    
    def test_preprocess(self):
        tree = P.Parser.p('''
            import incoq.mars.runtime
            import incoq.mars.runtime as foo
            import incoq.mars.runtime as bar
            from incoq.mars.runtime import *
            import baz
            from baz import *
            Q = incoq.mars.runtime.Set()
            R = foo.Set()
            S = bar.Set()
            T = Set()
            ''')
        tree = RuntimeImportPreprocessor.run(tree)
        exp_tree = P.Parser.p('''
            import baz
            from baz import *
            Q = Set()
            R = Set()
            S = Set()
            T = Set()
            ''')
        self.assertEqual(tree, exp_tree)
    
    def test_postprocess(self):
        tree = P.Parser.p('''
            R = Set()
            ''')
        tree = RuntimeImportPostprocessor.run(tree)
        exp_tree = P.Parser.p('''
            from incoq.mars.runtime import *
            R = Set()
            ''')
        self.assertEqual(tree, exp_tree)


class MainCallCase(unittest.TestCase):
    
    def test_preprocess(self):
        tree = P.Parser.p('''
            x = 1
            if __name__ == '__main__':
                main()
            y = 2
            ''')
        tree = MainCallRemover.run(tree)
        exp_tree = P.Parser.p('''
            x = 1
            y = 2
            ''')
        self.assertEqual(tree, exp_tree)
    
    def test_postprocess(self):
        tree = P.Parser.p('''
            x = 1
            def main():
                pass
            ''')
        tree = MainCallAdder.run(tree)
        exp_tree = P.Parser.p('''
            x = 1
            def main():
                pass
            if __name__ == '__main__':
                main()
            ''')
        self.assertEqual(tree, exp_tree)
        
        tree = P.Parser.p('''
            x = 1
            ''')
        tree = MainCallAdder.run(tree)
        exp_tree = P.Parser.p('''
            x = 1
            ''')
        self.assertEqual(tree, exp_tree)


class VardeclCase(unittest.TestCase):
    
    def test_preprocess(self):
        tree = P.Parser.p('''
            R = Set()
            R = Set()
            S = Set()
            x = 1
            def main():
                T = Set()
            ''')
        tree, rels = preprocess_vardecls(tree)
        exp_tree = P.Parser.p('''
            x = 1
            def main():
                T = Set()
            ''')
        exp_rels = ['R', 'S']
        self.assertEqual(tree, exp_tree)
        self.assertSequenceEqual(rels, exp_rels)
    
    def test_postprocess(self):
        tree = P.Parser.p('''
            def main():
                print(S, T)
            ''')
        tree = postprocess_vardecls(tree, ['S', 'T'], ['S_bu'])
        exp_tree = P.Parser.p('''
            S = Set()
            T = Set()
            S_bu = Map()
            def main():
                print(S, T)
            ''')
        self.assertEqual(tree, exp_tree)
        
        tree = P.Parser.p('pass')
        tree = postprocess_vardecls(tree, [], [])
        exp_tree = P.Parser.p('pass')
        self.assertEqual(tree, exp_tree)


class SymbolInfoCase(unittest.TestCase):
    
    def test_preprocess(self):
        tree = P.Parser.p('''
            INFO(R, a=1)
            INFO(S)
            pass
            ''')
        tree, syminfo = SymbolInfoImporter.run(tree)
        exp_tree = P.Parser.p('''
            pass
            ''')
        exp_syminfo = {'R': {'a': 1}, 'S': {}}
        self.assertEqual(tree, exp_tree)
        self.assertEqual(syminfo, exp_syminfo)
        
        with self.assertRaises(L.ProgramError):
            tree = P.Parser.p('''
                INFO(R, a=1)
                INFO(R, a=2)
                ''')
            SymbolInfoImporter.run(tree)


if __name__ == '__main__':
    unittest.main()
