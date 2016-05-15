"""Unit tests for py_rewritings.py."""


import unittest

from incoq.mars.incast import P, L
from incoq.mars.type import T
from incoq.mars.symbol import N
from incoq.mars.transform.py_rewritings import *


class QueryDirectiveCase(unittest.TestCase):
    
    def test_preprocess(self):
        tree = P.Parser.p('''
            QUERY('1 + 2', a=3, b=4)
            ''')
        tree = preprocess_query_directives(tree)
        exp_tree = P.Parser.p('''
            QUERY(1 + 2, a=3, b=4)
            ''')
        self.assertEqual(tree, exp_tree)


class ConstructCase(unittest.TestCase):
    
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
                tree = preprocess_constructs(tree)
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


class HeaderCase(unittest.TestCase):
    
    def test_postprocess(self):
        tree = P.Parser.p('pass')
        tree = postprocess_header(tree, ['a', 'b'])
        exp_tree = P.Parser.p('''
            COMMENT('a')
            COMMENT('b')
            pass
            ''')
        self.assertEqual(tree, exp_tree)


class PassCase(unittest.TestCase):
    
    def test_postprocess(self):
        # Make a tree by parsing syntactically valid code, then
        # scrubbing out all the occurrences of Pass. The postprocessor
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
        tree = postprocess_pass(tree)
        self.assertEqual(tree, orig_tree)


class RuntimeImportCase(unittest.TestCase):
    
    def test_preprocess(self):
        tree = P.Parser.p('''
            import incoq.mars.runtime
            import incoq.mars.runtime as foo
            import incoq.mars.runtime as bar
            from incoq.mars.runtime import *
            import baz
            from baz import Set
            from baz import *
            Q = incoq.mars.runtime.Set()
            R = foo.Set()
            S = bar.Set()
            T = Set()
            U = baz.Set()
            ''')
        tree = preprocess_runtime_import(tree)
        exp_tree = P.Parser.p('''
            import baz
            from baz import Set
            from baz import *
            Q = Set()
            R = Set()
            S = Set()
            T = Set()
            U = baz.Set()
            ''')
        self.assertEqual(tree, exp_tree)
    
    def test_postprocess(self):
        tree = P.Parser.p('''
            R = Set()
            ''')
        tree = postprocess_runtime_import(tree)
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
        tree = preprocess_main_call(tree)
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
        tree = postprocess_main_call(tree)
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
        tree = postprocess_main_call(tree)
        exp_tree = P.Parser.p('''
            x = 1
            ''')
        self.assertEqual(tree, exp_tree)


class VarDeclCase(unittest.TestCase):
    
    def test_preprocess(self):
        tree = P.Parser.p('''
            R = Set()
            R = Set()
            M = Map()
            S = Set()
            x = 1
            def main():
                T = Set()
            ''')
        tree, decls = preprocess_var_decls(tree)
        exp_tree = P.Parser.p('''
            x = 1
            def main():
                T = Set()
            ''')
        exp_decls = [('R', 'Set'), ('M', 'Map'), ('S', 'Set')]
        self.assertEqual(tree, exp_tree)
        self.assertSequenceEqual(decls, exp_decls)
    
    def test_postprocess(self):
        decls = [
            ('S', 'Set', 'S : {Top}'),
            ('T', 'Set', 'T : {Bottom}'),
            ('S_bu', 'Map', 'S_bu : {Top: Top}')]
        tree = P.Parser.p('''
            def main():
                print(S, T)
            ''')
        tree = postprocess_var_decls(tree, decls)
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
        tree = postprocess_var_decls(tree, [])
        exp_tree = P.Parser.p('pass')
        self.assertEqual(tree, exp_tree)


class DirectiveCase(unittest.TestCase):
    
    def test_preprocess(self):
        tree = P.Parser.p('''
            CONFIG(a=1)
            CONFIG(a=1, b=2)
            SYMCONFIG('R', a=1)
            SYMCONFIG('S')
            QUERY(1 + 2, a=3, b=4)
            pass
            ''')
        tree, info = preprocess_directives(tree)
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
