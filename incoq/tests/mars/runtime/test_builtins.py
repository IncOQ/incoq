"""Unit tests for builtins.py."""


import unittest
import pickle

from incoq.mars.runtime.builtins import *


class BuiltinsCase(unittest.TestCase):
    
    def test_noops(self):
        CONFIG(1, 2, a=3)
        SYMCONFIG(1, a=2, b=3)
        QUERY(1, a=2, b=3)
        self.assertEqual(QUERY('Q', 5), 5)
    
    def test_aggregates(self):
        self.assertEqual(count(range(3)), 3)
        
        self.assertEqual(sum([1, 2, 3]), 6)
        self.assertEqual(sum([(1,), (2,), (3,)]), 6)
        
        self.assertEqual(min([2, 1, 3]), 1)
        self.assertEqual(max([2, 1, 3]), 3)
        self.assertEqual(min([]), None)
        self.assertEqual(max([]), None)
    
    def test_typechecks(self):
        self.assertTrue(isset({1}))
        self.assertTrue(isset(CSet([1])))
        self.assertFalse(isset(object()))
        
        class Obj: pass
        o = Obj()
        o.f = 1
        self.assertTrue(hasfield(o, 'f'))
        self.assertFalse(hasfield(o, 'g'))
        self.assertFalse(hasfield({1}, 'f'))
        
        self.assertTrue(ismap({1: 2}))
        self.assertTrue(ismap(Map({1: 2})))
        self.assertFalse(ismap({1}))
        
        self.assertTrue(hasarity((1, 2), 2))
        self.assertFalse(hasarity((1, 2), 3))
        self.assertFalse(hasarity(object(), 2))
    
    def test_set_identity(self):
        s1 = Set()
        s2 = Set()
        self.assertTrue(s1 == s1)
        self.assertFalse(s1 != s1)
        self.assertFalse(s1 == s2)
        self.assertTrue(s1 != s2)
    
    def test_set_repr(self):
        r = repr(Set())
        exp_r = 'Set({})'
        self.assertEqual(r, exp_r)
        
        r = repr(Set({5}))
        exp_r = 'Set({5})'
        self.assertEqual(r, exp_r)
        
        s = str(Set({5, 6}))
        exp_s = '{5, 6}'
        self.assertEqual(s, exp_s)
        
        v = Set()
        v.add(v)
        r = repr(v)
        exp_r = 'Set({...})'
        self.assertEqual(r, exp_r)
    
    def test_set_updates(self):
        # Add/remove.
        s1 = Set()
        s1.add(5)
        s1.add(6)
        s1.remove(5)
        s2 = Set({6})
        self.assertCountEqual(s1, s2)
        
        # Bulk updates.
        s = Set({0})
        s.copy_update({1, 2, 3})
        self.assertCountEqual(s, {1, 2, 3})
        s.update({4, 5})
        self.assertCountEqual(s, {1, 2, 3, 4, 5})
        s.difference_update({1, 2})
        self.assertCountEqual(s, {3, 4, 5})
        s.intersection_update(s, {4, 5, 6})
        self.assertCountEqual(s, {4, 5})
        s.symmetric_difference_update({5, 6})
        self.assertCountEqual(s, {4, 6})
        s.clear()
        self.assertCountEqual(s, set())
        
        # Check edge case.
        s = Set({1, 2})
        s.difference_update(s)
        self.assertCountEqual(s, set())
        s1 = Set({1, 2})
        s2 = Set(s1)
        s1.copy_update(s1)
        self.assertCountEqual(s1, s2)
    
    def test_set_pickle(self):
        s1 = Set({1, 2, 3})
        b = pickle.dumps(s1)
        s2 = pickle.loads(b)
        self.assertEqual(set(s1), set(s2))
    
    def test_set_imglookup(self):
        s = Set({(1, 2), (1, 3), (2, 3), (2, 4)})
        img = s.imglookup('bu', (1,))
        exp_img = {(2,), (3,)}
        self.assertCountEqual(img, exp_img)
        
        # Degenerate cases.
        s = Set(set())
        img = s.imglookup('', ())
        exp_img = {}
        self.assertCountEqual(img, exp_img)
        s = Set({()})
        img = s.imglookup('', ())
        exp_img = {()}
        self.assertCountEqual(img, exp_img)
    
    def test_set_unwrap(self):
        s = Set({(1,), (2,)})
        unwrapped = s.unwrap()
        exp_unwrapped = {1, 2}
        self.assertCountEqual(unwrapped, exp_unwrapped)
    
    def test_cset_repr(self):
        r = repr(CSet())
        exp_r = 'CSet({})'
        self.assertEqual(r, exp_r)
        
        r = repr(CSet({5}))
        exp_r = 'CSet({5: 1})'
        self.assertEqual(r, exp_r)
        
        s = str(CSet({5, 6}))
        exp_s = '{5, 6}'
        self.assertEqual(s, exp_s)
        
        v = CSet()
        v.add(v)
        r = repr(v)
        exp_r = 'CSet({...: 1})'
        self.assertEqual(r, exp_r)
    
    def test_cset_updates(self):
        s = CSet({'a': 1, 'b': 2})
        
        # inccount, deccount, getcount.
        s.inccount('a')
        s.deccount('b')
        self.assertCountEqual(dict(s), {'a': 2, 'b': 1})
        self.assertEqual(s.getcount('a'), 2)
        
        # add, remove.
        s.add('c')
        self.assertCountEqual(dict(s), {'a': 2, 'b': 1, 'c': 1})
        s.remove('c')
        self.assertCountEqual(dict(s), {'a': 2, 'b': 1})
        
        # clear, update.
        s.clear()
        self.assertCountEqual(dict(s), {})
        s.add('a')
        s.update({'a': 2})
        self.assertCountEqual(dict(s), {'a': 3})
        
        # Strictness.
        with self.assertRaises(AssertionError):
            s.add('a')
        with self.assertRaises(AssertionError):
            s.remove('b')
        # Remove at count 1 only.
        with self.assertRaises(AssertionError):
            s.remove('a')
    
    def test_cset_pickle(self):
        s1 = CSet({1, 2, 3})
        b = pickle.dumps(s1)
        s2 = pickle.loads(b)
        self.assertEqual(dict(s1), dict(s2))
    
    def test_cset_imglookup(self):
        # Throw in some reference counts for the heck of it.
        # No effect on result.
        s = CSet({(1, 2): 3, (1, 3): 2, (2, 3) : 2, (2, 4) :1})
        img = s.imglookup('bu', (1,))
        exp_img = {(2,), (3,)}
        self.assertCountEqual(img, exp_img)
    
    def test_map_repr(self):
        r = repr(Map())
        exp_r = 'Map({})'
        self.assertEqual(r, exp_r)
        
        r = repr(Map({'a': 1}))
        exp_r = "Map({'a': 1})"
        self.assertEqual(r, exp_r)
        
        s = str(Map({'a': 1}))
        exp_s = '{a: 1}'
        self.assertEqual(s, exp_s)
        
        v = Map()
        v[v] = v
        r = repr(v)
        exp_r = 'Map({...: ...})'
        self.assertEqual(r, exp_r)
    
    def test_map_pickle(self):
        m1 = Map({'a': 1, 'b': 2})
        b = pickle.dumps(m1)
        m2 = pickle.loads(b)
        self.assertEqual(dict(m1), dict(m2))
    
    def test_map_setfrommap(self):
        m = Map({('a',): 1, ('b',): 2})
        s = m.setfrommap('bu')
        exp_s = {('a', 1), ('b', 2)}
        self.assertCountEqual(s, exp_s)
        
        # Degenerate cases.
        m = Map({})
        s = m.setfrommap('u')
        exp_s = set()
        self.assertCountEqual(s, exp_s)
        m = Map({(): 1})
        s = m.setfrommap('u')
        exp_s = {(1,)}
        self.assertCountEqual(s, exp_s)
    
    def test_obj_repr(self):
        r = repr(Obj())
        exp_r = 'Obj()'
        self.assertEqual(r, exp_r)
        
        r = repr(Obj(f=5))
        exp_r = 'Obj(f=5)'
        self.assertEqual(r, exp_r)
        
        r = repr(Obj(f=5, g=6))
        exp_r = 'Obj(f=5, g=6)'
        self.assertEqual(r, exp_r)
        
        o = Obj()
        o.f = o
        r = repr(o)
        exp_r = 'Obj(f=...)'
        self.assertEqual(r, exp_r)
    
    def test_obj_asdict(self):
        d = Obj(f=5, g=6).asdict()
        exp_d = {'f': 5, 'g': 6}
        self.assertEqual(d, exp_d)
    
    def test_obj_pickle(self):
        o = Obj(f=5, g=6)
        b = pickle.dumps(o)
        o2 = pickle.loads(b)
        self.assertEqual(o.asdict(), o2.asdict())


if __name__ == '__main__':
    unittest.main()
