"""Unit tests for test_trans.py."""


import unittest

from incoq.mars.incast import L
from incoq.mars.comp.join import CoreClauseTools
from incoq.mars.comp.trans import *


class JoinCase(unittest.TestCase):
    
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


if __name__ == '__main__':
    unittest.main()
