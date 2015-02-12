"""Unit tests for util.py."""


import unittest

from simplestruct import Struct

from invinc.compiler.incast.types import *
from invinc.compiler.incast.structconv import parse_structast
from invinc.compiler.incast.nodeconv import IncLangImporter
from invinc.compiler.incast import ts, ts_typed, trim


class TypeCase(unittest.TestCase):
    
    def p(self, source, subst=None, mode=None):
        return IncLangImporter.run(
                    parse_structast(source, mode=mode, subst=subst))
    
    def test_frozendict_field(self):
        class A(Struct):
            f = FrozenDictField(int)
        a = A({1: 'a', 2: 'b'})
        
        class A(Struct):
            f = FrozenDictField(int, int)
        with self.assertRaises(TypeError):
            a = A({1: 1, 2: 'b'})
    
    def test_unify_types(self):
        t1 = SetType(numbertype)
        t2 = SetType(toptype)
        t3 = ListType(numbertype)
        self.assertEqual(t1.unify(t2), t1)
        self.assertEqual(t2.unify(t3), bottomtype)
    
    def test_eval_typestr(self):
        t = eval_typestr('SetType(numbertype)')
        exp_t = SetType(numbertype)
        self.assertEqual(t, exp_t)
    
    def test_annotator(self):
        tree = self.p('''
            x = d['a']
            y = ('a', 1)
            z = {'b': 2, x: y[1]}
            print({o.f for o in S if o.f > 0})
            ''')
        ann = {'d': DictType(strtype, strtype),
               'S': SetType(ObjType('O'))}
        objtypes = {'O': {'f': numbertype}}
        tree = TypeAnnotator.run(tree, ann, objtypes)
        source = ts_typed(tree)
        exp_source = trim('''
            (x : str) = ((d : {str: str})[('a' : str)] : str)
            (y : (str, Number)) = ((('a' : str), (1 : Number)) : (str, Number))
            (z : {str: Number}) = ({('b' : str): (2 : Number), (x : str): ((y : (str, Number))[(1 : Number)] : Number)} : {str: Number})
            ((print : Top)((COMP({((o : O).f : Number) for (o : O) in (S : {O}) if ((((o : O).f : Number) > (0 : Number)) : bool)}, None, None) : Number)) : Top)
        ''')


if __name__ == '__main__':
    unittest.main()
