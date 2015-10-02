"""Unit tests for type_analysis.py."""


import unittest

from incoq.mars.incast import L
from incoq.mars.types import *
from incoq.mars.type_analysis import *


class AnalyzerCase(unittest.TestCase):
    
    def check(self, source, store, exp_store, type_error):
        """Confirm that the analyzer produces the expected modification
        to the type store, and the expected well-typedness result.
        """
        tree = L.Parser.p(source)
        analyzer = TypeAnalyzer(store)
        store = analyzer.process(tree)
        self.assertEqual(store, exp_store)
        assertfunc = self.assertTrue if type_error else self.assertFalse
        assertfunc(len(analyzer.errors) != 0)
    
    def test_for(self):
        source = '''
            def main():
                for x in S:
                    pass
            '''
        # Normal case, iter is Set.
        self.check(source,
            {'S': Set(String), 'x': Bottom},
            {'S': Set(String), 'x': String},
            False)
        # Iter is Top.
        self.check(source,
            {'S': Top, 'x': Bottom},
            {'S': Top, 'x': Top},
            True)
        # Iter is Bottom.
        self.check(source,
            {'S': Bottom, 'x': Bottom},
            {'S': Bottom, 'x': Bottom},
            False)
    
    def test_while(self):
        # Booleans in While tests are fine; other types are not.
        source = '''
            def main():
                while a:
                    pass
            '''
        self.check(source, {'a': Bool}, {'a': Bool}, False)
        self.check(source, {'a': Number}, {'a': Number}, True)
    
    def test_if(self):
        # Booleans in If tests are fine; other types are not.
        source = '''
            def main():
                if a:
                    pass
                else:
                    pass
            '''
        self.check(source, {'a': Bool}, {'a': Bool}, False)
        self.check(source, {'a': Number}, {'a': Number}, True)
    
    def test_assign(self):
        self.check('''
            def main():
                x = y
            ''',
            {'x': Number, 'y': String},
            {'x': Top, 'y': String},
            False)
    
    def test_decompassign(self):
        source = '''
            def main():
                x, y = v
            '''
        # Value is Tuple of correct arity.
        self.check(source,
                   {'x': String, 'y': Bottom, 'v': Tuple([Number, Bool])},
                   {'x': Top, 'y': Bool, 'v': Tuple([Number, Bool])},
                   False)
        # Value is Tuple of incorrect arity.
        self.check(source,
                   {'x': Bottom, 'y': Bottom,
                    'v': Tuple([Bottom, Bottom, Bottom])},
                   {'x': Top, 'y': Top,
                    'v': Tuple([Bottom, Bottom, Bottom])},
                   True)
        # Value is Top.
        self.check(source,
                   {'x': Bottom, 'y': Bottom, 'v': Top},
                   {'x': Top, 'y': Top, 'v': Top},
                   True)
        # Value is Bottom.
        self.check(source,
                   {'x': String, 'y': Bottom, 'v': Bottom},
                   {'x': String, 'y': Bottom, 'v': Bottom},
                   False)
    
    def test_setupdate(self):
        source = '''
            def main():
                S.add(v)
            '''
        # Normal case.
        self.check(source,
                   {'S': Set(String), 'v': Number},
                   {'S': Set(Top), 'v': Number},
                   False)
        # target is not a set.
        self.check(source,
                   {'S': Top, 'v': Number},
                   {'S': Top, 'v': Number},
                   True)
    
    def test_relupdate(self):
        source = '''
            def main():
                S.reladd(v)
            '''
        # Normal case.
        self.check(source,
                   {'S': Set(String), 'v': Number},
                   {'S': Set(Top), 'v': Number},
                   False)
        # target is not a set.
        self.check(source,
                   {'S': Top, 'v': Number},
                   {'S': Top, 'v': Number},
                   True)
    
    def test_readonly(self):
        # Disallow write context for UnaryOp.
        source = '''
            def main():
                (-a).add(b)
            '''
        self.check(source,
                   {'a': Set(Bottom), 'b': Number},
                   {'a': Set(Bottom), 'b': Number},
                   True)
    
    def test_unaryop(self):
        # Not requires Bool.
        source = '''
            def main():
                a = not b
            '''
        self.check(source,
                   {'a': Bottom, 'b': Bool},
                   {'a': Bool, 'b': Bool},
                   False)
        self.check(source,
                   {'a': Bottom, 'b': Number},
                   {'a': Bool, 'b': Number},
                   True)
        
        # Other ops require Number.
        source = '''
            def main():
                a = -b
            '''
        self.check(source,
                   {'a': Bottom, 'b': Bool},
                   {'a': Number, 'b': Bool},
                   True)
        self.check(source,
                   {'a': Bottom, 'b': Number},
                   {'a': Number, 'b': Number},
                   False)
    
    def test_boolop(self):
        # Both operands must be Bool.
        source = '''
            def main():
                a = b and c
            '''
        self.check(source,
                   {'a': Bottom, 'b': Bool, 'c': Bottom},
                   {'a': Bool, 'b': Bool, 'c': Bottom},
                   False)
        self.check(source,
                   {'a': Bottom, 'b': Bool, 'c': Top},
                   {'a': Bool, 'b': Bool, 'c': Top},
                   True)
    
    def test_binop(self):
        self.check('''
            def main():
                a = b + c
            ''',
           {'a': Bottom, 'b': Bool, 'c': Number},
           {'a': Top, 'b': Bool, 'c': Number},
           False)
    
    def test_compare(self):
        self.check('''
            def main():
                a = b < c
            ''',
           {'a': Bottom, 'b': Bool, 'c': Number},
           {'a': Bool, 'b': Bool, 'c': Number},
           False)
    
    def test_ifexp(self):
        # Test must be Bool.
        source = '''
            def main():
                a = b if c else d
            '''
        self.check(source,
           {'a': Bottom, 'b': Number, 'c': Bool, 'd': String},
           {'a': Top, 'b': Number, 'c': Bool, 'd': String},
           False)
        self.check(source,
           {'a': Bottom, 'b': Number, 'c': String, 'd': String},
           {'a': Top, 'b': Number, 'c': String, 'd': String},
           True)
    
    def test_num(self):
        self.check('''
            def main():
                a = 5
            ''',
            {'a': Bottom},
            {'a': Number},
            False)
    
    def test_str(self):
        self.check('''
            def main():
                a = 'dog'
            ''',
            {'a': Bottom},
            {'a': String},
            False)
    
    def test_nameconstant(self):
        self.check('''
            def main():
                a = True
            ''',
            {'a': Bottom},
            {'a': Bool},
            False)
        
        self.check('''
            def main():
                a = None
            ''',
            {'a': Bottom},
            {'a': Top},
            False)
    
    # Name should be sufficiently tested by all the other cases.
    
    def test_tuple(self):
        self.check('''
            def main():
                a = (b, c)
            ''',
            {'a': Bottom, 'b': Number, 'c': String},
            {'a': Tuple([Number, String]), 'b': Number, 'c': String},
            False)


if __name__ == '__main__':
    unittest.main()
