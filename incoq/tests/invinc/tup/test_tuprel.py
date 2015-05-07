"""Unit tests for tupletrans.py."""


import unittest

import incoq.compiler.incast as L
from incoq.compiler.set import Mask
from incoq.compiler.tup.tuprel import *


class TuprelCase(unittest.TestCase):
    
    def test_trel_helpers(self):
        trel = make_trel(2)
        
        self.assertTrue(is_trel(trel))
        self.assertFalse(is_trel('_M'))
        
        arity = get_trel(trel)
        self.assertEqual(arity, 2)
    
    def test_trel_bindmatch(self):
        code = trel_bindmatch('_TUP2', Mask('bbu'), ['t', 'x', 'y'],
                              L.pc('pass'), typecheck=True)
        exp_code = L.pc('''
            if (isinstance(t, tuple) and (len(t) == 2)):
                if (t[1] == x):
                    for y in setmatch({(t, t[0], t[1])}, 'bbu', (t, x)):
                        pass
            ''')
        self.assertEqual(code, exp_code)
        
        code = trel_bindmatch('_TUP2', Mask('bbu'), ['t', 'x', 'y'],
                              L.pc('pass'), typecheck=False)
        exp_code = L.pc('''
            if (t[1] == x):
                for y in setmatch({(t, t[0], t[1])}, 'bbu', (t, x)):
                    pass
            ''')
        self.assertEqual(code, exp_code)
        
        code = trel_bindmatch('_TUP2', Mask('ubw'), ['t', 'x', 'y'],
                              L.pc('pass'), typecheck=True)
        exp_code = L.pc('''
            for t in setmatch(_TUP2, 'ubw', x):
                pass
            ''')
        self.assertEqual(code, exp_code)
    
    def test_checkbad(self):
        tree = L.pc('''
            for t in setmatch(_TUP2, 'ubw', x):
                pass
            ''')
        with self.assertRaises(AssertionError):
            check_bad_setmatches(tree)


if __name__ == '__main__':
    unittest.main()

