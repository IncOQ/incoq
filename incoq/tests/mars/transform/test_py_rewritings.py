"""Unit tests for py_rewritings.py."""


import unittest

from incoq.mars.incast import P, L
from incoq.mars.types import Top, Set, Map
from incoq.mars.symtab import N, RelationSymbol, MapSymbol
from incoq.mars.transform.py_rewritings import *


class QueryDirectiveRewriterCase(unittest.TestCase):
    
    def test_preprocess(self):
        tree = P.Parser.p('''
            QUERY('1 + 2', a=3, b=4)
            ''')
        tree = QueryDirectiveRewriter.run(tree)
        exp_tree = P.Parser.p('''
            QUERY(1 + 2, a=3, b=4)
            ''')
        self.assertEqual(tree, exp_tree)


class ConstructPreprocessorCase(unittest.TestCase):
    
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
                tree = ConstructPreprocessor.run(tree)
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
        S_sym = RelationSymbol('S', type=Set(Top))
        T_sym = RelationSymbol('T')
        S_bu_sym = MapSymbol('S_bu', type=Map(Top, Top))
        
        tree = P.Parser.p('''
            def main():
                print(S, T)
            ''')
        tree = postprocess_vardecls(tree, [S_sym, T_sym], [S_bu_sym])
        exp_tree = P.Parser.p('''
            COMMENT('S : {Top}')
            S = Set()
            COMMENT('T : {Bottom}')
            T = Set()
            COMMENT('S_bu : {Top: Top}')
            S_bu = Map()
            def main():
                print(S, T)
            ''')
        self.assertEqual(tree, exp_tree)
        
        tree = P.Parser.p('pass')
        tree = postprocess_vardecls(tree, [], [])
        exp_tree = P.Parser.p('pass')
        self.assertEqual(tree, exp_tree)


class DirectiveCase(unittest.TestCase):
    
    def test_preprocess(self):
        tree = P.Parser.p('''
            CONFIG(a=1)
            CONFIG(a=1, b=2)
            SYMCONFIG(R, a=1)
            SYMCONFIG(S)
            QUERY(1 + 2, a=3, b=4)
            pass
            ''')
        tree, info = DirectiveImporter.run(tree)
        exp_tree = P.Parser.p('''
            pass
            ''')
        exp_config_info = [{'a': 1}, {'a': 1, 'b': 2}]
        exp_symconfig_info = [('R', {'a': 1}), ('S', {})]
        exp_query_info = [(P.Parser.pe('1 + 2'), {'a': 3, 'b': 4})]
        self.assertEqual(tree, exp_tree)
        self.assertEqual(info.config_info, exp_config_info)
        self.assertEqual(info.symconfig_info, exp_symconfig_info)
        self.assertEqual(info.query_info, exp_query_info)


if __name__ == '__main__':
    unittest.main()
