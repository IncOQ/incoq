###############################################################################
# test_str.py                                                                 #
# Author: Jon Brandvein                                                       #
###############################################################################

"""Unit tests for the str module."""


import unittest

from oinc.util.str import *


class TestStrings(unittest.TestCase):
    
    def test_brace_items(self):
        text1 = brace_items(['a', 'b'], '<', '>')
        text2 = '<a>, <b>'
        self.assertEqual(text1, text2)
    
    def test_quote_items(self):
        text1 = quote_items(['a', 'b'])
        text2 = '"a", "b"'
        self.assertEqual(text1, text2)
    
    def test_tuple_str(self):
        text1 = tuple_str(['a', 'b'])
        text2 = '(a, b)'
        self.assertEqual(text1, text2)
        
        text3 = tuple_str(['a'])
        text4 = 'a'
        self.assertEqual(text3, text4)
    
    def test_from_tuple_str(self):
        names1 = from_tuple_str('a')
        names2 = ['a']
        self.assertEqual(names1, names2)
        
        names3 = from_tuple_str('(a,)')
        names4 = ['a']
        self.assertEqual(names3, names4)
        
        names5 = from_tuple_str('(a, b, c)')
        names6 = ['a', 'b', 'c']
        self.assertEqual(names5, names6)
    
    def test_dedent_trim(self):
        text1 = dedent_trim(
            """
            for x in foo:
                print(x)
            """)
        exp_text1 = """for x in foo:\n    print(x)"""
        
        self.assertEqual(text1, exp_text1)
        
        text2 = dedent_trim('')
        exp_text2 = ''
        
        self.assertEqual(text2, exp_text2)
    
    def test_join_lines(self):
        text1 = join_lines(['abc', 'def'], prefix='# ')
        text2 = dedent_trim(
            """
            # abc
            # def
            
            """)
        self.assertEqual(text1, text2)
    
    def test_indent_lines(self):
        lines1 = indent_lines(['abc', 'def'], prefix='z')
        lines2 = ['zabc', 'zdef']
        self.assertEqual(lines1, lines2)
        
        lines1 = indent_lines(['abc', 'def'], prefix=2)
        lines2 = ['  abc', '  def']
        self.assertEqual(lines1, lines2)
    
    def test_side_by_side(self):
        text1 = dedent_trim(
            """
            a b c
            d e
            
            """)
        text2 = dedent_trim(
            """
            
            
            u v
            w x y z
            """)
        exp_output = dedent_trim(
            """
            .-------.---------.
            | a b c |         | <<<
            | d e   |         |
            |       | u v     |
            |       | w x y z |
            ^-------^---------^
            """)
        
        self.assertEqual(side_by_side(text1, text2, cmp=True), exp_output)


if __name__ == '__main__':
    unittest.main()
