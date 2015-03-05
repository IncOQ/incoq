"""Unit tests for util.py."""


import unittest
from simplestruct import Struct

from invinc.compiler.incast.types import *


class TypeCase(unittest.TestCase):
    
    def test_frozendict_field(self):
        class A(Struct):
            f = FrozenDictField(int)
        a = A({1: 'a', 2: 'b'})
        
        class A(Struct):
            f = FrozenDictField(int, int)
        with self.assertRaises(TypeError):
            a = A({1: 1, 2: 'b'})
    
    def test_subtypeof_matches(self):
        t1 = SetType(numbertype)
        t2 = SetType(toptype)
        self.assertTrue(t1.issubtype(toptype))
        self.assertTrue(bottomtype.issubtype(t1))
        self.assertTrue(t1.issubtype(t2))
        
        self.assertTrue(t1.matches(t2))
        t3 = TupleType([t1, t2])
        t4 = TupleType([toptype, toptype])
        self.assertTrue(t3.matches(t4))
        self.assertFalse(bottomtype.matches(toptype))
        
        constrs = t3.match_against(t4)
        exp_constrs = [(t1, toptype), (t2, toptype)]
        self.assertEqual(constrs, exp_constrs)
    
    def test_join_types(self):
        t1 = SetType(numbertype)
        t2 = SetType(toptype)
        t3 = ListType(numbertype)
        self.assertEqual(t1.join(t2), t2)
        self.assertEqual(t1.join(t2, inverted=True), t1)
        self.assertEqual(t2.join(t3), toptype)
        
        t4 = DictType(toptype, numbertype)
        t5 = DictType(numbertype, bottomtype)
        t6 = DictType(toptype, numbertype)
        self.assertEqual(t4.join(t5), t6)
    
    def test_expand_types(self):
        t = DictType(SetType(TypeVar('T')),
                     TupleType([numbertype, TypeVar('U')]))
        t = t.expand({'T': strtype, 'U': toptype})
        exp_t = DictType(SetType(strtype),
                         TupleType([numbertype, toptype]))
        self.assertEqual(t, exp_t)
    
    def test_widen(self):
        t = DictType(SetType(numbertype),
                     TupleType([toptype, SetType(toptype)]))
        t1 = t.widen(0)
        self.assertEqual(t1, toptype)
        t2 = t.widen(1)
        self.assertEqual(t2, DictType(toptype, toptype))
        t3 = t.widen(2)
        self.assertEqual(t3, DictType(SetType(toptype),
                                      TupleType([toptype, toptype])))
        t4 = t.widen(3)
        self.assertEqual(t4, t)
    
    def test_refine(self):
        t1 = RefineType('foo', numbertype)
        self.assertTrue(t1.issubtype(numbertype))
        self.assertEqual(t1.join(numbertype), numbertype)
        t2 = RefineType('bar', numbertype)
        self.assertTrue(t1.join(t2), numbertype)
        self.assertEqual(t1.meet(t2), bottomtype)
        
        t3 = RefineType('baz', SetType(numbertype))
        self.assertEqual(t3.widen(2), SetType(numbertype))
    
    def test_eval_typestr(self):
        t = eval_typestr('SetType(numbertype)')
        exp_t = SetType(numbertype)
        self.assertEqual(t, exp_t)


if __name__ == '__main__':
    unittest.main()
