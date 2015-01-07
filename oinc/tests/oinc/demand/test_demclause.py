"""Unit tests for demclause.py."""


import unittest

import oinc.compiler.incast as L
from oinc.compiler.comp import EnumClause, LookupClause, Rate
from oinc.compiler.demand.demclause import *


class DemClauseFactory(DemClauseFactory_Mixin):
    typecheck = True

class DemClauseFactory_NoTC(DemClauseFactory):
    typecheck = False


class DemclauseCase(unittest.TestCase):
    
    def test(self):
        cl = DemClause(EnumClause(['x', 'y'], 'R'), 'f', ['x'])
        
        # AST round-trip.
        clast = cl.to_AST()
        exp_clast = \
            L.Enumerator(L.tuplify(['x', 'y'], lval=True),
                         L.DemQuery('f', (L.ln('x'),), L.ln('R')))
        self.assertEqual(clast, exp_clast)
        cl2 = DemClause.from_AST(exp_clast, DemClauseFactory)
        self.assertEqual(cl2, cl)
        
        # Attributes.
        self.assertEqual(cl.pat_mask, (True, True))
        self.assertEqual(cl.enumvars_tagsin, ('x',))
        self.assertEqual(cl.enumvars_tagsout, ('y',))
        
        # Rewriting.
        cl2 = cl.rewrite_subst({'x': 'z'}, DemClauseFactory)
        exp_cl = DemClause(EnumClause(['z', 'y'], 'R'), 'f', ['z'])
        self.assertEqual(cl2, exp_cl)
        
        # Fancy rewriting, uses LookupClause.
        cl2 = DemClause(LookupClause(['x', 'y'], 'R'), 'f', ['x'])
        cl2 = cl2.rewrite_subst({'x': 'z'}, DemClauseFactory)
        exp_cl = DemClause(LookupClause(['z', 'y'], 'R'), 'f', ['z'])
        self.assertEqual(cl2, exp_cl)
        
        # Rating.
        rate = cl.rate(['x'])
        self.assertEqual(rate, Rate.NORMAL)
        rate = cl.rate([])
        self.assertEqual(rate, Rate.UNRUNNABLE)
        
        # Code generation.
        code = cl.get_code(['x'], L.pc('pass'))
        exp_code = L.pc('''
            DEMQUERY(f, [x], None)
            for y in setmatch(R, 'bu', x):
                pass
            ''')
        self.assertEqual(code, exp_code)


if __name__ == '__main__':
    unittest.main()
