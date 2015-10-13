"""Unit tests for test_join.py."""


import unittest

from incoq.mars.incast import L
from incoq.mars.comp.clause import *
from incoq.mars.comp.join import *


class JoinCase(unittest.TestCase):
    
    def setUp(self):
        self.factory = CompInfoFactory()
        self.comp = L.Parser.pe('''{z for (x, y) in REL(R)
                                      for (y, z) in REL(S)}''')
        self.comp_info = self.factory.make_comp_info(self.comp, ['x'])
    
    def test_construction(self):
        # Construct manually.
        cl_info1 = RelMemberInfo(L.RelMember(['x', 'y'], 'R'))
        cl_info2 = RelMemberInfo(L.RelMember(['y', 'z'], 'S'))
        resexp = L.Parser.pe('z')
        clauses = [cl_info1, cl_info2]
        comp_info = CompInfo(self.factory, clauses, ['x'], resexp)
        
        # Check fields.
        self.assertSequenceEqual(comp_info.clauses, clauses)
        self.assertSequenceEqual(comp_info.boundvars, ['x'])
        self.assertEqual(comp_info.resexp, resexp)
        
        # Compare with construction via factory.
        self.assertEqual(comp_info, self.comp_info)
    
    def test_get_code(self):
        code = self.comp_info.get_code([L.Pass()])
        exp_code = L.Parser.pc('''
            for (y,) in R.imglookup('bu', (x,)):
                for (z,) in S.imglookup('bu', (y,)):
                    pass
            ''')
        self.assertEqual(code, exp_code)


if __name__ == '__main__':
    unittest.main()
