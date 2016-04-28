"""Unit tests for util.py."""

import unittest

from incoq.mars.incast import nodes as L
from incoq.mars.incast.util import *
from incoq.mars.incast.pyconv import Parser


class UtilCase(unittest.TestCase):
    
    def test_uncounted_set_rel_update(self):
        # Set update.
        code = set_update(L.Name('S'), L.SetAdd(), L.Name('x'),
                          counted=False)
        exp_code = Parser.pc('S.add(x)')
        self.assertEqual(code, exp_code)
        code = set_update(L.Name('S'), L.SetRemove(), L.Name('x'),
                          counted=False)
        exp_code = Parser.pc('S.remove(x)')
        self.assertEqual(code, exp_code)
        
        # Rel update.
        code = rel_update('S', L.SetAdd(), 'x',
                          counted=False)
        exp_code = Parser.pc('S.reladd(x)')
        self.assertEqual(code, exp_code)
        code = rel_update('S', L.SetRemove(), 'x',
                          counted=False)
        exp_code = Parser.pc('S.relremove(x)')
        self.assertEqual(code, exp_code)
    
    def test_counted_set_rel_update(self):
        # Set update.
        code = set_update(L.Name('S'), L.SetAdd(), L.Name('x'),
                          counted=True)
        exp_code = Parser.pc('''
            if x not in S:
                S.add(x)
            else:
                S.inccount(x)
            ''')
        self.assertEqual(code, exp_code)
        code = set_update(L.Name('S'), L.SetRemove(), L.Name('x'),
                          counted=True)
        exp_code = Parser.pc('''
            if S.getcount(x) == 1:
                S.remove(x)
            else:
                S.deccount(x)
            ''')
        self.assertEqual(code, exp_code)
        
        # Rel update.
        code = rel_update('S', L.SetAdd(), 'x',
                          counted=True)
        exp_code = Parser.pc('''
            if x not in S:
                S.reladd(x)
            else:
                S.relinccount(x)
            ''')
        self.assertEqual(code, exp_code)
        code = rel_update('S', L.SetRemove(), 'x',
                          counted=True)
        exp_code = Parser.pc('''
            if S.getcount(x) == 1:
                S.relremove(x)
            else:
                S.reldeccount(x)
            ''')
        self.assertEqual(code, exp_code)
    
    def test_insert_rel_maint(self):
        update_code = Parser.pc('R.reladd(x)')
        maint_code = Parser.pc('pass')
        code = insert_rel_maint(update_code, maint_code, L.SetAdd())
        exp_code = Parser.pc('''
            R.reladd(x)
            pass
            ''')
        self.assertEqual(code, exp_code)
        
        update_code = Parser.pc('R.relremove(x)')
        maint_code = Parser.pc('pass')
        code = insert_rel_maint(update_code, maint_code, L.SetRemove())
        exp_code = Parser.pc('''
            pass
            R.relremove(x)
            ''')
        self.assertEqual(code, exp_code)
    
    def test_insert_rel_maint_call(self):
        update = Parser.ps('R.reladd(x)')
        code = insert_rel_maint_call(update, 'maint')
        exp_code = Parser.pc('''
            R.reladd(x)
            maint(x)
            ''')
        self.assertEqual(code, exp_code)
        
        update = Parser.ps('R.relremove(x)')
        code = insert_rel_maint_call(update, 'maint')
        exp_code = Parser.pc('''
            maint(x)
            R.relremove(x)
            ''')
        self.assertEqual(code, exp_code)
    
    def test_set_update_name(self):
        self.assertEqual(set_update_name(L.SetAdd()), 'add')
        self.assertEqual(set_update_name(L.SetRemove()), 'remove')
        self.assertEqual(set_update_name(L.IncCount()), 'inccount')
        self.assertEqual(set_update_name(L.DecCount()), 'deccount')
    
    def test_apply_renamer(self):
        tree = Parser.pc('a + b')
        tree = apply_renamer(tree, lambda x: '_' + x)
        exp_tree = Parser.pc('_a + _b')
        self.assertEqual(tree, exp_tree)
    
    def test_unwrapper(self):
        tree = Parser.p('''
            def main():
                print(QUERY('Q1', 1 + QUERY('Q2', 2)))
            ''')
        tree = Unwrapper.run(tree, ['Q2'])
        exp_tree = Parser.p('''
            def main():
                print(QUERY('Q1', 1 + unwrap(QUERY('Q2', 2))))
            ''')
        self.assertEqual(tree, exp_tree)
    
    def test_is_injective(self):
        tree = Parser.pe('(1, "a", True, None, (False, x))')
        self.assertTrue(is_injective(tree))
        
        tree = Parser.pe('(1 + 1)')
        self.assertFalse(is_injective(tree))
    
    def test_get_setunion(self):
        tree = Parser.pe('1 | 2 | (3 + 4)')
        parts = get_setunion(tree)
        exp_parts = [
            Parser.pe('1'),
            Parser.pe('2'),
            Parser.pe('3 + 4'),
        ]
        self.assertSequenceEqual(parts, exp_parts)


if __name__ == '__main__':
    unittest.main()
