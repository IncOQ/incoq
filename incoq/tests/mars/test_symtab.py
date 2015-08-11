"""Unit tests for symtab.py."""


import unittest

from incoq.mars.incast import L
from incoq.mars.symtab import *


class NamingCase(unittest.TestCase):
    
    def test_subnames(self):
        names = N.get_subnames('x', 3)
        exp_names = ['x_v1', 'x_v2', 'x_v3']
        self.assertEqual(names, exp_names)
    
    def test_auxmap(self):
        name = N.get_auxmap_name('R', L.mask('bu'))
        exp_name = 'R_bu'
        self.assertEqual(name, exp_name)
    
    def test_maintfunc(self):
        name = N.get_maint_func_name('Q', 'R', 'add')
        exp_name = '_maint_Q_for_R_add'
        self.assertEqual(name, exp_name)


if __name__ == '__main__':
    unittest.main()
