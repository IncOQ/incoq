###############################################################################
# test_setmatch.py                                                            #
# Author: Jon Brandvein                                                       #
###############################################################################

"""Unit tests for the auxmap module."""


import unittest

import invinc.incast as L
from invinc.central import CentralCase

from .mask import Mask

from .setmatch import *


class TestSetmatchMacros(CentralCase):
    
    def test_bindmatch_bb(self):
        code = make_bindmatch('R', Mask('bb'), ['x', 'y'], [], L.pc('pass'))
        
        exp_code = L.pc('''
            if ((x, y) in R):
                pass
            ''')
        
        self.assertEqual(code, exp_code)
    
    def test_bindmatch_uu(self):
        code = make_bindmatch('R', Mask('uu'), [], ['x', 'y'], L.pc('pass'))
        
        exp_code = L.pc('''
            for (x, y) in R:
                pass
            ''')
        
        self.assertEqual(code, exp_code)
    
    def test_bindmatch_b1(self):
        code = make_bindmatch('R', Mask('b1'), ['x'], [], L.pc('pass'))
        
        exp_code = L.pc('''
            for _ in setmatch(R, 'b1', x):
                pass
            ''')
        
        self.assertEqual(code, exp_code)
    
    def test_bindmatch_other(self):
        code = make_bindmatch('R', Mask('bu'), ['x'], ['y'], L.pc('pass'))
        
        exp_code = L.pc('''
            for y in setmatch(R, 'bu', x):
                pass
            ''')
        
        self.assertEqual(code, exp_code)
    
    def test_tuplematch_bb(self):
        code = make_tuplematch(L.pe('v'), Mask('bb'),
                               ['x', 'y'], [], L.pc('pass'))
        
        exp_code = L.pc('''
            if ((x, y) == v):
                pass
            ''')
        
        self.assertEqual(code, exp_code)
    
    def test_tuplematch_uu(self):
        code = make_tuplematch(L.pe('v'), Mask('uu'),
                               [], ['x', 'y'], L.pc('pass'))
        
        exp_code = L.pc('''
            (x, y) = v
            pass
            ''')
        
        self.assertEqual(code, exp_code)
    
    def test_tuplematch_other(self):
        code = make_tuplematch(L.pe('v'), Mask('bu'),
                               ['x'], ['y'], L.pc('pass'))
        
        exp_code = L.pc('''
            for y in setmatch({v}, 'bu', x):
                pass
            ''')
        
        self.assertEqual(code, exp_code)


if __name__ == '__main__':
    unittest.main()
