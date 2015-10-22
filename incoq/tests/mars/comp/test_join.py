"""Unit tests for test_join.py."""


import unittest

from incoq.mars.incast import L
from incoq.mars.comp.clause import *
from incoq.mars.comp.join import *


class JoinCase(unittest.TestCase):
    
    def setUp(self):
        self.factory = CompInfoFactory()
    
    def make_comp_info(self, source, params):
        comp = L.Parser.pe(source)
        return self.factory.make_comp_info(comp, params)
    
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
        comp_info2 = self.make_comp_info('''{z for (x, y) in REL(R)
                                               for (y, z) in REL(S)}''',
                                         ['x'])
        self.assertEqual(comp_info, comp_info2)
    
    def test_make_join(self):
        cl_info1 = RelMemberInfo(L.RelMember(['x', 'y'], 'R'))
        cl_info2 = RelMemberInfo(L.RelMember(['y', 'z'], 'S'))
        comp_info = self.factory.make_join([cl_info1, cl_info2])
        exp_comp_info = self.make_comp_info(
            '{(x, y, z) for (x, y) in REL(R) for (y, z) in REL(S)}', [])
        self.assertEqual(comp_info, exp_comp_info)
    
    def test_lhs_vars(self):
        comp_info = self.make_comp_info('''{z for (x, y) in REL(R)
                                               for (y, z) in REL(S)}''',
                                        ['x'])
        self.assertSequenceEqual(comp_info.lhs_vars, ['x', 'y', 'z'])
    
    def test_is_join(self):
        # Is a join.
        comp = L.Parser.pe('''{(x, y, z) for (x, y) in REL(R)
                                         for (y, z) in REL(S)}''')
        comp_info = self.factory.make_comp_info(comp, [])
        self.assertTrue(comp_info.is_join)
        
        # Not a join because of bound variable.
        comp = L.Parser.pe('''{(x, y, z) for (x, y) in REL(R)
                                         for (y, z) in REL(S)}''')
        comp_info = self.factory.make_comp_info(comp, ['x'])
        self.assertFalse(comp_info.is_join)
        
        # Not a join because of result expression.
        comp = L.Parser.pe('''{x for (x, y) in REL(R)
                                 for (y, z) in REL(S)}''')
        comp_info = self.factory.make_comp_info(comp, [])
        self.assertFalse(comp_info.is_join)
        
        # Not a join because some variables are missing.
        comp = L.Parser.pe('''{(x, y) for (x, y) in REL(R)
                                      for (y, z) in REL(S)}''')
        comp_info = self.factory.make_comp_info(comp, [])
        self.assertFalse(comp_info.is_join)
    
    def test_get_clause_code(self):
        comp_info = self.make_comp_info('''{z for (x, y) in REL(R)
                                              for (y, z) in REL(S)}''',
                                        ['x'])
        code = comp_info.get_clause_code([L.Pass()])
        exp_code = L.Parser.pc('''
            for (y,) in R.imglookup('bu', (x,)):
                for (z,) in S.imglookup('bu', (y,)):
                    pass
            ''')
        self.assertEqual(code, exp_code)


if __name__ == '__main__':
    unittest.main()
