"""Unit tests for match.py."""


import unittest

import oinc.incast as L
from oinc.set import Mask

from .match import *


class BindmatchCase(unittest.TestCase):
    
    def test_mset(self):
        code = mset_bindmatch(Mask.BB, ['x', 'y'], [], L.pc('pass'),
                              typecheck=True)
        exp_code = L.pc('''
            if isinstance(x, Set):
                if (y in x):
                    pass
            ''')
        self.assertEqual(code, exp_code)
        
        code = mset_bindmatch(Mask.BB, ['x', 'y'], [], L.pc('pass'),
                              typecheck=False)
        exp_code = L.pc('''
        if (y in x):
            pass
        ''')
        self.assertEqual(code, exp_code)
        
        code = mset_bindmatch(Mask.OUT, ['x'], ['y'], L.pc('pass'),
                              typecheck=False)
        exp_code = L.pc('''
            for y in x:
                pass
            ''')
        self.assertEqual(code, exp_code)
        
        code = mset_bindmatch(Mask.B1, ['x'], [], L.pc('pass'),
                              typecheck=False)
        exp_code = L.pc('''
            if x in x:
                pass
            ''')
        self.assertEqual(code, exp_code)
        
        code = mset_bindmatch(Mask.BW, ['x'], [], L.pc('pass'),
                              typecheck=False)
        exp_code = L.pc('''
            if not x.isempty():
                pass
            ''')
        self.assertEqual(code, exp_code)
        
        code = mset_bindmatch(Mask.IN, ['y'], ['x'], L.pc('pass'),
                              typecheck=True)
        exp_code = L.pc('''
            for x in setmatch(_M, 'ub', y):
                pass
            ''')
        self.assertEqual(code, exp_code)
        
        with self.assertRaises(AssertionError):
            mset_bindmatch(Mask.UU, [], ['x', 'y'], L.pc('pass'),
                           typecheck=True)
    
    def test_fset(self):
        code = fset_bindmatch('f', Mask.BB, ['x', 'y'], [], L.pc('pass'),
                              typecheck=True)
        exp_code = L.pc('''
            if hasattr(x, 'f'):
                if x.f == y:
                    pass
            ''')
        self.assertEqual(code, exp_code)
        
        code = fset_bindmatch('f', Mask.BB, ['x', 'y'], [], L.pc('pass'),
                              typecheck=False)
        exp_code = L.pc('''
            if (x.f == y):
                pass
            ''')
        self.assertEqual(code, exp_code)
                
        code = fset_bindmatch('f', Mask.OUT, ['x'], ['y'], L.pc('pass'),
                              typecheck=False)
        exp_code = L.pc('''
            y = x.f
            pass
            ''')
        self.assertEqual(code, exp_code)
        
        code = fset_bindmatch('f', Mask.B1, ['x'], [], L.pc('pass'),
                              typecheck=False)
        exp_code = L.pc('''
            if x == x.f:
                pass
            ''')
        self.assertEqual(code, exp_code)
        
        code = fset_bindmatch('f', Mask.BW, ['x'], [], L.pc('pass'),
                              typecheck=False)
        exp_code = L.pc('''
            if hasattr(x, 'f'):
                pass
            ''')
        self.assertEqual(code, exp_code)
        
        code = fset_bindmatch('f', Mask.IN, ['y'], ['x'], L.pc('pass'),
                              typecheck=True)
        exp_code = L.pc('''
            for x in setmatch(_F_f, 'ub', y):
                pass
            ''')
        self.assertEqual(code, exp_code)
        
        with self.assertRaises(AssertionError):
            fset_bindmatch('f', Mask.UU, [], ['x', 'y'], L.pc('pass'),
                           typecheck=True)
    
    def test_mapset(self):
        code = mapset_bindmatch(Mask('bbb'), ['x', 'y', 'z'], [],
                                L.pc('pass'), typecheck=True)
        exp_code = L.pc('''
            if isinstance(x, Map):
                if y in x and x[y] == z:
                    pass
            ''')
        self.assertEqual(code, exp_code)
        
        code = mapset_bindmatch(Mask('bbu'), ['x', 'y'], ['z'],
                                L.pc('pass'), typecheck=False)
        exp_code = L.pc('''
            if y in x:
                z = x[y]
                pass
        ''')
        self.assertEqual(code, exp_code)
        
        code = mapset_bindmatch(Mask('buu'), ['x'], ['y', 'z'],
                                L.pc('pass'), typecheck=False)
        exp_code = L.pc('''
            for y, z in x.items():
                pass
        ''')
        self.assertEqual(code, exp_code)
        
        with self.assertRaises(AssertionError):
            mapset_bindmatch(Mask('uuu'), [], ['x', 'y', 'z'],
                             L.pc('pass'), typecheck=True)
        
        code = mapset_bindmatch(Mask('ubb'), ['y', 'z'], ['x'],
                                L.pc('pass'), typecheck=True)
        exp_code = L.pc('''
            for x in setmatch(_MAP, 'ubb', (y, z)):
                pass
            ''')
        self.assertEqual(code, exp_code)


if __name__ == '__main__':
    unittest.main()
