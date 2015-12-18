"""Unit tests for trans.py."""


import unittest

from incoq.mars.incast import L
from incoq.mars.symtab import N
from incoq.mars.comp.join import CoreClauseTools
from incoq.mars.comp.trans import *


class TransCase(unittest.TestCase):
    
    def setUp(self):
        self.ct = CoreClauseTools()
    
    def test_join_expander(self):
        Q1 = L.Parser.pe('''{(x, y, z) for (x, y) in REL(R)
                                       for (y, z) in REL(S)}''')
        Q2 = L.Parser.pe('{(x,) for (x,) in REL(R)}')
        Q3 = L.Parser.pe('{True for (x,) in REL(R)}')
        query_params = {'Q1': ('x',), 'Q2': (), 'Q3': ()}
        
        tree = L.Parser.p('''
            def main():
                for (x, y, z) in QUERY('Q1', _Q1):
                    pass
                for z in QUERY('Q2', _Q2):
                    pass
                for z in QUERY('Q3', _Q3):
                    pass
            ''', subst={'_Q1': Q1, '_Q2': Q2, '_Q3': Q3})
        
        tree = JoinExpander.run(tree, self.ct, ['Q1', 'Q2', 'Q3'],
                                query_params)
        exp_tree = L.Parser.p('''
            def main():
                for (y,) in R.imglookup('bu', (x,)):
                    for (z,) in S.imglookup('bu', (y,)):
                        pass
                for z in QUERY('Q2', {(x,) for (x,) in REL(R)}):
                    pass
                for z in QUERY('Q3', {True for (x,) in REL(R)}):
                    pass
            ''')
        self.assertEqual(tree, exp_tree)
    
    def test_make_comp_maint_func(self):
        comp = L.Parser.pe('''{x + z for (x, y) in REL(R)
                                     for (y, z) in REL(S)}''')
        func = make_comp_maint_func(self.ct, N.fresh_name_generator(),
                                    comp, 'Q', 'R', L.SetAdd(),
                                    counted=True)
        exp_func = L.Parser.ps('''
            def _maint_Q_for_R_add(_elem):
                for (_v1_x, _v1_y, _v1_z) in \
                        {(_v1_x, _v1_y, _v1_z)
                         for (_v1_x, _v1_y) in SING(_elem)
                         for (_v1_y, _v1_z) in REL(S)}:
                    _v1_result = (_v1_x + _v1_z)
                    if (_v1_result not in Q):
                        Q.reladd(_v1_result)
                    else:
                        Q.relinccount(_v1_result)
            ''')
        self.assertEqual(func, exp_func)
    
    def test_comp_transformer(self):
        comp = L.Parser.pe('''{x + y for (x, y) in REL(R)}''')
        tree = L.Parser.p('''
            def main():
                R.reladd(e)
            ''')
        tree = CompTransformer.run(tree, self.ct, N.fresh_name_generator(),
                                   comp, 'Q', counted=True)
        exp_tree = L.Parser.p('''
            def _maint_Q_for_R_add(_elem):
                for (_v1_x, _v1_y) in \
                        {(_v1_x, _v1_y) for (_v1_x, _v1_y) in SING(_elem)}:
                    _v1_result = (_v1_x + _v1_y)
                    if (_v1_result not in Q):
                        Q.reladd(_v1_result)
                    else:
                        Q.relinccount(_v1_result)
            
            def _maint_Q_for_R_remove(_elem):
                for (_v2_x, _v2_y) in \
                        {(_v2_x, _v2_y) for (_v2_x, _v2_y) in SING(_elem)}:
                    _v2_result = (_v2_x + _v2_y)
                    if (Q.getcount(_v2_result) == 1):
                        Q.relremove(_v2_result)
                    else:
                        Q.reldeccount(_v2_result)
            
            def main():
                R.reladd(e)
                _maint_Q_for_R_add(e)
            ''')
        self.assertEqual(tree, exp_tree)


if __name__ == '__main__':
    unittest.main()
