"""Unit tests for util.py."""


import unittest

from simplestruct import Struct

from invinc.compiler.incast.newtypes import *
from invinc.compiler.incast.newtypes import (
        add_fresh_typevars, subst_typevars, apply_constraint, TypeAnalyzer)
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
        t6 = DictType(numbertype, numbertype)
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
    
    def test_constraint_applier(self):
        """Constraints:
            tuple<number, T3> <= T1
            T1 <= tuple<T2, bottom>
            T2 <= top
            tuple<top, bottom> <= T1
            top <= T3
        """
        c1 = (TupleType([numbertype, TypeVar('T3')]), TypeVar('T1'))
        c2 = (TypeVar('T1'), TupleType([TypeVar('T2'), bottomtype]))
        c3 = (TypeVar('T2'), toptype)
        c4 = (TupleType([toptype, bottomtype]), TypeVar('T1'))
        c5 = (toptype, TypeVar('T3'))
        store = {'T1': bottomtype, 'T2': bottomtype, 'T3': bottomtype}
        apply_constraint(store, *c1)
        apply_constraint(store, *c2)
        apply_constraint(store, *c3)
        apply_constraint(store, *c4)
        apply_constraint(store, *c5)
        apply_constraint(store, *c1)
        
        exp_store = {
            'T1': TupleType([toptype, toptype]),
            'T2': numbertype,
            'T3': toptype,
        }
        self.assertEqual(store, exp_store)
        
        c6 = (TypeVar('T1'), bottomtype)
        with self.assertRaises(TypeAnalysisFailure):
            apply_constraint(store, *c6)
    
    def test_analyze(self):
        # given that v is a tuple<number, top>
        # conclude that R is a set<top>
        tree = self.p('''
            (x, y) = v
            R.add(x)
            R.add('a')
            ''')
        tree = add_fresh_typevars(tree)
        store = {'_T' + str(i): bottomtype for i in range(1, 8+1)}
        store.update({k: bottomtype for k in ['x', 'y', 'v', 'R']})
        store['v'] = TupleType([numbertype, toptype])
        
        # Should converge within 10 goes.
        for _ in range(10):
            oldstore = store.copy()
            TypeAnalyzer.run(tree, store)
        self.assertEqual(oldstore, store)
        
        exp_store = {
            '_T1': numbertype,
            '_T2': toptype,
            '_T3': TupleType([numbertype, toptype]),
            '_T4': TupleType([numbertype, toptype]),
            '_T5': SetType(toptype),
            '_T6': numbertype,
            '_T7': SetType(toptype),
            '_T8': strtype,
            'R': SetType(toptype),
            'v': TupleType([numbertype, toptype]),
            'x': numbertype,
            'y': toptype,
        }
        self.assertEqual(store, exp_store)
        
        tree = subst_typevars(tree, store)
        self.assertEqual(tree.body[0].value.type,
                         TupleType([numbertype, toptype]))
        
        print(ts_typed(tree))
    
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
