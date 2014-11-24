"""Unit tests for tupclause.py"""


import unittest

import invinc.incast as L
from invinc.comp import Rate

from .tupclause import *


class TupClauseFactory(TupClauseFactory_Mixin):
    typecheck = True

class TupClauseFactory_NoTC(TupClauseFactory):
    typecheck = False


class TupClauseCase(unittest.TestCase):
    
    def test_tclause(self):
        cl = TClause('t', ['x', 'y'])
        
        # AST round-trip.
        clast = cl.to_AST()
        exp_clast = L.Enumerator(L.tuplify(('t', 'x', 'y'), lval=True),
                                 L.ln('_TUP2'))
        self.assertEqual(clast, exp_clast)
        cl2 = TClause.from_AST(exp_clast, TupClauseFactory)
        self.assertEqual(cl2, cl)
        
        # Attributes.
        self.assertEqual(cl.enumlhs, ('t', 'x', 'y'))
        self.assertEqual(cl.pat_mask, (True, True, True))
        self.assertEqual(cl.enumvars_tagsin, ('t',))
        self.assertEqual(cl.enumvars_tagsout, ('x', 'y'))
        
        self.assertCountEqual(cl.get_domain_constrs('_'),
                              [('_t', ('<T>', '_t.1', '_t.2')),
                               ('_t.1', '_x'),
                               ('_t.2', '_y')])
        
        # Rate.
        rate = cl.rate([])
        self.assertEqual(rate, Rate.UNRUNNABLE)
        rate = cl.rate(['t'])
        self.assertEqual(rate, Rate.CONSTANT)
        
        # Code.
        code = cl.get_code(['t'], L.pc('pass'))
        exp_code = L.pc('''
            if isinstance(t, tuple) and len(t) == 2:
                for x, y in setmatch({(t, t[0], t[1])}, 'buu', t):
                    pass
            ''')
        self.assertEqual(code, exp_code)
        
        # Code, no type-checks.
        cl = TClause_NoTC('t', ['x', 'y'])
        code = cl.get_code(['t'], L.pc('pass'))
        exp_code = L.pc('''
            for x, y in setmatch({(t, t[0], t[1])}, 'buu', t):
                pass
            ''')
        self.assertEqual(code, exp_code)
    
    def test_objclausefactory(self):
        cl = TClause('t', ['x', 'y'])
        clast = L.Enumerator(L.tuplify(['t', 'x', 'y'], lval=True),
                             L.pe('_TUP2'))
        cl2 = TupClauseFactory.from_AST(clast)
        self.assertEqual(cl2, cl)
        
        cl2 = TupClauseFactory_NoTC.from_AST(clast)
        self.assertEqual(cl2, cl)
        self.assertIsInstance(cl2, TClause_NoTC)


if __name__ == '__main__':
    unittest.main()
