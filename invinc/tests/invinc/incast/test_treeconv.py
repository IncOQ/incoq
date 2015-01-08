"""Unit tests for treeconv.py."""


import unittest

from invinc.compiler.incast.nodes import *
from invinc.compiler.incast.structconv import parse_structast
from invinc.compiler.incast.error import ProgramError
from invinc.compiler.incast.macros import IncMacroProcessor
from invinc.compiler.incast.treeconv import *


class TreeconvCase(unittest.TestCase):
    
    def p(self, source, mode=None):
        tree = parse_structast(source, mode=mode)
        tree = IncMacroProcessor.run(tree)
        return tree
    
    def pc(self, source):
        return self.p(source, mode='code')
    
    def pe(self, source):
        return self.p(source, mode='expr')
    
    def test_runtimelib(self):
        tree = self.p('''
            pass
            from invinc.runtime import *
            from foo import *
            from invinc.runtime import *
            ''')
        tree = remove_runtimelib(tree)
        exp_tree = self.p('''
            pass
            from foo import *
            ''')
        self.assertEqual(tree, exp_tree)
        
        tree = add_runtimelib(exp_tree)
        exp_tree = self.p('''
            from invinc.runtime import *
            pass
            from foo import *
            ''')
        self.assertEqual(tree, exp_tree)
    
    def test_options_reader(self):
        tree = self.p('''
            OPTIONS(a = 1, b = 2)
            OPTIONS(c = 3)
            foo
            QUERYOPTIONS('1 + 1', a = 1, b = 2)
            QUERYOPTIONS('2 + 2')
            ''')
        opts = ({'z': 5}, {self.pe('3 + 3'): {'z': 10}})
        tree, (nopts, qopts) = OptionsParser.run(tree, opts)
        
        exp_tree = self.p('foo')
        exp_nopts = {'a': 1, 'b': 2, 'c': 3, 'z': 5}
        exp_qopts = {self.pe('1 + 1'): {'a': 1, 'b': 2},
                     self.pe('2 + 2'): {},
                     self.pe('3 + 3'): {'z': 10}}
        
        self.assertEqual(tree, exp_tree)
        self.assertEqual(nopts, exp_nopts)
        self.assertEqual(qopts, exp_qopts)
        
        # Make sure we raise errors on redundant options.
        
        tree = self.p('''
            OPTIONS(a = 1)
            OPTIONS(a = 2)
            ''')
        with self.assertRaises(ProgramError):
            OptionsParser.run(tree)
        
        tree = self.p('''
            QUERYOPTIONS('1 + 1', a = 1)
            QUERYOPTIONS('(1 + 1)', b = 2)
            ''')
        with self.assertRaises(ProgramError):
            OptionsParser.run(tree)
    
    def test_infer_params(self):
        tree = self.p('''
            {y for (x, y) in R}
            x = 1
            {y for (x, y) in R}
            {y for (x, y) in {y for (x, y) in R}}
            COMP({y for (x, y) in R}, [y])
            ''')
        tree = infer_params(tree, obj_domain=False)
        
        exp_tree = self.p('''
            COMP({y for (x, y) in R}, [])
            x = 1
            COMP({y for (x, y) in R}, [x], None)
            COMP({y for (x, y) in
                     COMP({y for (x, y) in R}, [x], None)},
                 [x], None)
            COMP({y for (x, y) in R}, [y], None)
            ''')
        
        self.assertEqual(tree, exp_tree)
    
    def test_attach_qopts(self):
        q1 = '{x for (x, y) in R}'
        q2 = '{y for (x, y) in R if sum({x for (x, y) in R}) > 5}'
        q3 = 'sum({x for (x, y) in R})'
        tree = self.p(q2)
        opts = ({}, {self.pe(q1): {'a': 'b', 'params': ['c']},
                     self.pe(q2): {'d': 'e'},
                     self.pe(q3): {'f': 'g'},
                     self.pe('foo'): {}})
        tree, unused = attach_qopts_info(tree, opts)
        
        exp_tree = self.p('''
            COMP({y for (x, y) in R if sum(
                    COMP({x for (x, y) in R}, [c], {'a': 'b'}),
                    {'f': 'g'}) > 5},
                 None, {'d': 'e'})
            ''')
        exp_unused = {self.pe('foo')}
        
        self.assertEqual(tree, exp_tree)
        self.assertEqual(unused, exp_unused)
    
    def test_expand_maint(self):
        maint_node = Maintenance('Q', 'pass',
                                 self.pc('print(1)'),
                                 self.pc('pass'),
                                 self.pc('print(2)'))
        tree = Module((maint_node,))
        tree = MaintExpander.run(tree)
        
        exp_tree = self.p('''
        Comment('Begin maint Q before "pass"')
        print(1)
        Comment('End maint Q before "pass"')
        pass
        Comment('Begin maint Q after "pass"')
        print(2)
        Comment('End maint Q after "pass"')
        ''')
        
        self.assertEqual(tree, exp_tree)
    
    def test_export(self):
        tree = self.p('''
            OPTIONS(v = 'u')
            print(COMP({sum(x, {'c': 'd'}) for x in S}, [S], {'a': 'b'}))
            ''')
        tree = export_program(tree)
        exp_tree = parse_structast('''
            print({sum(x) for x in S})
            ''')
        self.assertEqual(tree, exp_tree)


if __name__ == '__main__':
    unittest.main()
