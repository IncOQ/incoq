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
    
    def test_eval_typestr(self):
        t = eval_typestr('SetType(numbertype)')
        exp_t = SetType(numbertype)
        self.assertEqual(t, exp_t)
    
    
#    def test_annotator(self):
#        tree = self.p('''
#            x = d['a']
#            y = ('a', 1)
#            z = {'b': 2, x: y[1]}
#            print({o.f for o in S if o.f > 0})
#            ''')
#        ann = {'d': DictType(strtype, strtype),
#               'S': SetType(ObjType('O'))}
#        objtypes = {'O': {'f': numbertype}}
#        tree = TypeAnnotator.run(tree, ann, objtypes)
#        source = ts_typed(tree)
#        exp_source = trim('''
#            (x : str) = ((d : {str: str})[('a' : str)] : str)
#            (y : (str, Number)) = ((('a' : str), (1 : Number)) : (str, Number))
#            (z : {str: Number}) = ({('b' : str): (2 : Number), (x : str): ((y : (str, Number))[(1 : Number)] : Number)} : {str: Number})
#            ((print : Top)((COMP({((o : O).f : Number) for (o : O) in (S : {O}) if ((((o : O).f : Number) > (0 : Number)) : bool)}, None, None) : Number)) : Top)
#        ''')


if __name__ == '__main__':
    unittest.main()
