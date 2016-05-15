"""Unit tests for types.py."""


import unittest

from incoq.mars.type.types import *
from incoq.mars.type.types import TopClass, BottomClass


class TypeCase(unittest.TestCase):
    
    @property
    def sample_types(self):
        return [Bottom, Bool, Top, Tuple([Number]),
                Set(String), Map(String, Bool),
                Refine('name', String), Enum('color')]
    
    @property
    def sample_types_simple(self):
        return [Bottom, Bool, Top]
    
    def test_str(self):
        self.assertEqual(str(Top), 'Top')
        self.assertEqual(str(Bottom), 'Bottom')
        
        self.assertEqual(str(Bool), 'bool')
        self.assertEqual(str(Number), 'Number')
        self.assertEqual(str(String), 'str')
        
        self.assertEqual(str(Tuple([Bool, String])), '(bool, str)')
        self.assertEqual(str(Set(Bool)), '{bool}')
        
        self.assertEqual(str(Refine('name', String)), 'name:str')
        
        self.assertEqual(str(Enum('color')), 'color')
    
    def test_singleton(self):
        obj = TopClass()
        self.assertIs(obj, Top)
        obj = BottomClass()
        self.assertIs(obj, Bottom)
    
    def test_order_trivial(self):
        for t in self.sample_types:
            with self.subTest(t=t):
                self.assertTrue(Bottom.issmaller(t))
                self.assertTrue(t.issmaller(Top))
                self.assertTrue(Top.isbigger(t))
                self.assertTrue(t.isbigger(Bottom))
    
    def test_join_trivial(self):
        for t in self.sample_types:
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
                # None.
                self.assertEqual(t.join(None), t)
                self.assertEqual(t.meet(None), t)
    
    def test_widen_trivial(self):
        ts = self.sample_types_simple
        for t in ts:
            with self.subTest(t=t):
                self.assertEqual(t.widen(0), Top)
                self.assertEqual(t.widen(1), t)
    
    def test_tuple(self):
        t = Tuple([Bool, String])
        self.assertTrue(Tuple([Bottom, String]).issmaller(t))
        self.assertTrue(Tuple([Top, String]).isbigger(t))
        self.assertFalse(Tuple([Bottom, Top]).issmaller(t))
        self.assertFalse(Tuple([Bottom, Top]).isbigger(t))
        
        t2 = Tuple([String, String])
        self.assertEqual(t.join(t2), Tuple([Top, String]))
        self.assertEqual(t.meet(t2), Tuple([Bottom, String]))
        
        t = Tuple([Tuple([Bool, String]), String])
        self.assertEqual(t.widen(3), t)
        self.assertEqual(t.widen(2), Tuple([Tuple([Top, Top]), String]))
        self.assertEqual(t.widen(1), Tuple([Top, Top])),
        self.assertEqual(t.widen(0), Top)
    
    def test_sequence_covariance(self):
        # Test covariant sequences, using Set.
        
        t = Set(String)
        self.assertTrue(Set(Bottom).issmaller(t))
        self.assertTrue(Set(Top).isbigger(t))
        self.assertFalse(Set(Bool).issmaller(t))
        self.assertFalse(Set(Bool).isbigger(t))
        
        t2 = Set(Bool)
        self.assertEqual(t.join(t2), Set(Top))
        self.assertEqual(t.meet(t2), Set(Bottom))
    
    def test_sequence_subtype(self):
        # Test mixing different kinds of sequences.
        t1 = Set(String)
        t2 = List(Bool)
        
        self.assertTrue(Sequence(String).isbigger(t1))
        self.assertFalse(Sequence(String).isbigger(t2))
        
        self.assertEqual(t1.join(t2), Sequence(Top))
        self.assertEqual(t1.meet(t2), Bottom)
    
    def test_map(self):
        t = Map(String, Bool)
        self.assertTrue(Map(Top, Bool).isbigger(t))
        self.assertTrue(Map(Bottom, Bottom).issmaller(t))
        self.assertFalse(Map(Top, Bottom).isbigger(t))
        self.assertFalse(Map(Bottom, Top).isbigger(t))
        
        t2 = Map(Bool, Bool)
        self.assertEqual(t.join(t2), Map(Top, Bool))
        self.assertEqual(t.meet(t2), Map(Bottom, Bool))
        
        t = Map(String, Map(String, Bool))
        self.assertEqual(t.widen(3), t)
        self.assertEqual(t.widen(2), Map(String, Map(Top, Top)))
        self.assertEqual(t.widen(1), Map(Top, Top))
        self.assertEqual(t.widen(0), Top)
    
    def test_refine(self):
        t1 = Refine('name', String)
        t2 = Refine('firstname', t1)
        t3 = Refine('address', String)
        self.assertTrue(String.isbigger(t1))
        self.assertTrue(t2.issmaller(t1))
        self.assertFalse(t1.isbigger(t3))
        
        self.assertEqual(t1.join(t2), t1)
        self.assertEqual(t1.meet(t2), t2)
        self.assertEqual(t2.join(t3), String)
        self.assertEqual(t2.meet(t3), Bottom)
        
        self.assertEqual(t2.widen(3), t2)
        self.assertEqual(t2.widen(2), t1)
        self.assertEqual(t2.widen(1), String)
    
    def test_eval(self):
        t = eval_typestr('Set(Tuple([Bool, Number]))')
        exp_t = Set(Tuple([Bool, Number]))
        self.assertEqual(t, exp_t)


if __name__ == '__main__':
    unittest.main()
