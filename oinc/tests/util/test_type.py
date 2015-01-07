###############################################################################
# test_type.py                                                                #
# Author: Jon Brandvein                                                       #
###############################################################################

"""Unit tests for the type module."""


import unittest

from oinc.util.type import *


class TestTypeChecking(unittest.TestCase, TypeCase):
    
    def test_checktype(self):
        checktype('a', str)
        checktype(True, int)    # This is correct, bool subtypes int
        with self.assertRaisesRegex(
                TypeError, 'Expected int; got NoneType object'):
            checktype(None, int)
    
    def test_checktype_seq(self):
        checktype_seq([], str)
        checktype_seq([3, True], int)
        with self.assertRaisesRegex(
                TypeError, 'Expected sequence of bool; got sequence with '
                           'int object'):
            checktype_seq([3, True], bool)
        with self.assertRaisesRegex(
                TypeError, 'Expected sequence of bool; '
                           'got bool object instead of sequence'):
            checktype_seq(True, bool)
        with self.assertRaisesRegex(
                TypeError, 'Expected non-string sequence of str; '
                           'got string'):
            checktype_seq('abc', str)
        with self.assertRaisesRegex(
                TypeError, 'Expected sequence of int; '
                           'got generator object instead of sequence'):
            checktype_seq((i for i in range(3)), int)
    
    def test_checksubclass(self):
        checksubclass(str, object)
        checksubclass(str, str)
        with self.assertRaisesRegex(
                TypeError, 'Expected subclass of str; got int class'):
            checksubclass(int, str)
    
    def test_checksubclass_seq(self):
        checksubclass_seq([str, object], object)
        with self.assertRaisesRegex(
                TypeError, 'Expected sequence of subclasses of str; '
                           'got sequence with int class'):
            checksubclass_seq([str, int], str)
        with self.assertRaisesRegex(
                TypeError, 'Expected sequence of subclasses of str; '
                           'got sequence with int object'):
            checksubclass_seq([str, 3], str)
        
        with self.assertRaisesRegex(
                TypeError, 'Expected sequence of subclasses of str; '
                           'got bool class instead of sequence'):
            checksubclass_seq(bool, str)
        
    def test_TypeCase(self):
        # Here, assertTypeError is the object being tested,
        # not a tool for testing.
        
        with self.assertTypeError(int):
            checktype(object, int)
        
        with self.assertTypeError(int, sequence=True):
            checktype_seq(object, int)
        
        with self.assertTypeError(int, subclass=True):
            checksubclass(4, int)
        
        with self.assertTypeError(int, sequence=True, subclass=True):
            checksubclass_seq([int, bool, 4], int)
        
        with self.assertRaises(AssertionError):
            with self.assertTypeError(int):
                checktype(object, str)


if __name__ == '__main__':
    unittest.main()
