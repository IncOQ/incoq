"""Unit tests for types.py."""


import unittest

from incoq.mars.types import *
from incoq.mars.types import TopClass, BottomClass


class TypeCase(unittest.TestCase):
    
    def test_str(self):
        self.assertEqual(str(Top), 'Top')
        self.assertEqual(str(Bottom), 'Bottom')
        
        self.assertEqual(str(Bool), 'bool')
        self.assertEqual(str(Number), 'Number')
        self.assertEqual(str(String), 'str')
        
        self.assertEqual(str(Union([Bool, String])), '(bool | str)')
        self.assertEqual(str(Tuple([Bool, String])), '(bool, str)')
        self.assertEqual(str(Set(Bool)), '{bool}')
    
    def test_singleton(self):
        obj = TopClass()
        self.assertIs(obj, Top)
        obj = BottomClass()
        self.assertIs(obj, Bottom)
    
    def test_order_trivial(self):
        ts = [Bottom, Bool, Set(String), Union([Bool, String]), Top]
        for t in ts:
            with self.subTest(t=t):
                self.assertTrue(Bottom.issubtype(t))
                self.assertTrue(t.issubtype(Top))
                self.assertTrue(Top.issupertype(t))
                self.assertTrue(t.issupertype(Bottom))
    
    def test_join_trivial(self):
        ts = [Bottom, Bool, Set(String), Union([Bool, String]), Top]
        for t in ts:
            with self.subTest(t=t):
                # Join.
                self.assertEqual(t.join(Bottom), t)
                self.assertEqual(Bottom.join(t), t)
                self.assertEqual(t.join(Top), Top)
                self.assertEqual(Top.join(t), Top)
                # Meet.
                self.assertEqual(t.meet(Bottom), Bottom)
                self.assertEqual(Bottom.meet(t), Bottom)
                self.assertEqual(t.meet(Top), t)
                self.assertEqual(Top.meet(t), t)
    
    def test_union(self):
        t = Union([Bool, String])
        self.assertTrue(Bool.issubtype(t))
        self.assertFalse(Number.issubtype(t))
        
        # These are true in reality but not produced by the
        # current implementation.
        self.assertFalse(Union([Bool]).issubtype(t))
        self.assertFalse(Union([]).issubtype(Bottom))
    
    def test_tuple(self):
        t = Tuple([Bool, String])
        self.assertTrue(Tuple([Bottom, String]).issubtype(t))
        self.assertTrue(Tuple([Top, String]).issupertype(t))
        self.assertFalse(Tuple([Bottom, Top]).issubtype(t))
        self.assertFalse(Tuple([Bottom, Top]).issupertype(t))
        
        t2 = Tuple([String, String])
        self.assertEqual(t.join(t2), Tuple([Top, String]))
        self.assertEqual(t.meet(t2), Tuple([Bottom, String]))
    
    def test_set(self):
        t = Set(String)
        self.assertTrue(Set(Bottom).issubtype(t))
        self.assertTrue(Set(Top).issupertype(t))
        self.assertFalse(Set(Bool).issubtype(t))
        self.assertFalse(Set(Bool).issupertype(t))
        
        t2 = Set(Bool)
        self.assertEqual(t.join(t2), Set(Top))
        self.assertEqual(t.meet(t2), Set(Bottom))


if __name__ == '__main__':
    unittest.main()
