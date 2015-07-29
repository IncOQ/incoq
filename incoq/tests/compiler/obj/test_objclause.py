"""Unit tests for objclause.py"""


import unittest

import incoq.compiler.incast as L
from incoq.compiler.comp import Rate
from incoq.compiler.obj.objclause import *


class ObjClauseFactory(ObjClauseFactory_Mixin):
    typecheck = True

class ObjClauseFactory_NoTC(ObjClauseFactory):
    typecheck = False


class ObjClauseCase(unittest.TestCase):
    
    def test_mclause(self):
        cl = MClause('S', 'x')
        
        # Construct from expression.
        cl2 = MClause.from_expr(L.pe('(S, x) in _M'))
        self.assertEqual(cl2, cl)
        
        # AST round-trip.
        clast = cl.to_AST()
        exp_clast = L.Enumerator(L.tuplify(('S', 'x'), lval=True),
                                 L.ln('_M'))
        self.assertEqual(clast, exp_clast)
        cl2 = MClause.from_AST(exp_clast, ObjClauseFactory)
        self.assertEqual(cl2, cl)
        
        # Attributes.
        self.assertEqual(cl.enumlhs, ('S', 'x'))
        self.assertEqual(cl.pat_mask, (False, True))
        self.assertEqual(cl.enumvars_tagsin, ('S',))
        self.assertEqual(cl.enumvars_tagsout, ('x',))
        
        # Rate.
        rate = cl.rate([])
        self.assertEqual(rate, Rate.UNRUNNABLE)
        
        # Code.
        code = cl.get_code(['S'], L.pc('pass'))
        exp_code = L.pc('''
            if isinstance(S, Set):
                for x in S:
                    pass
            ''')
        self.assertEqual(code, exp_code)
        
        # Code, no type-checks.
        cl = MClause_NoTC('S', 'x')
        code = cl.get_code(['S'], L.pc('pass'))
        exp_code = L.pc('''
            for x in S:
                pass
            ''')
        self.assertEqual(code, exp_code)
    
    def test_fclause(self):
        cl = FClause('o', 'v', 'f')
        
        # Construct from expression.
        cl2 = FClause.from_expr(L.pe('(o, v) in _F_f'))
        self.assertEqual(cl2, cl)
        
        # AST round-trip.
        clast = cl.to_AST()
        exp_clast = L.Enumerator(L.tuplify(('o', 'v'), lval=True),
                                 L.ln('_F_f'))
        self.assertEqual(clast, exp_clast)
        cl2 = FClause.from_AST(exp_clast, ObjClauseFactory)
        self.assertEqual(cl2, cl)
        
        # Attributes.
        self.assertEqual(cl.enumlhs, ('o', 'v'))
        self.assertEqual(cl.pat_mask, (False, True))
        self.assertEqual(cl.enumvars_tagsin, ('o',))
        self.assertEqual(cl.enumvars_tagsout, ('v',))
        
        # Rate.
        rate = cl.rate([])
        self.assertEqual(rate, Rate.UNRUNNABLE)
        rate = cl.rate(['o'])
        self.assertEqual(rate, Rate.CONSTANT)
        
        # Code.
        code = cl.get_code(['o'], L.pc('pass'))
        exp_code = L.pc('''
            if hasattr(o, 'f'):
                v = o.f
                pass
            ''')
        self.assertEqual(code, exp_code)
        
        # Code, no type-checks.
        cl = FClause_NoTC('o', 'v', 'f')
        code = cl.get_code(['o'], L.pc('pass'))
        exp_code = L.pc('''
            v = o.f
            pass
            ''')
        self.assertEqual(code, exp_code)
    
    def test_mapclause(self):
        cl = MapClause('m', 'k', 'v')
        
        # Construct from expression.
        cl2 = MapClause.from_expr(L.pe('(m, k, v) in _MAP'))
        self.assertEqual(cl2, cl)
        
        # AST round-trip.
        clast = cl.to_AST()
        exp_clast = L.Enumerator(L.tuplify(('m', 'k', 'v'), lval=True),
                                 L.ln('_MAP'))
        self.assertEqual(clast, exp_clast)
        cl2 = MapClause.from_AST(exp_clast, ObjClauseFactory)
        self.assertEqual(cl2, cl)
        
        # Attributes.
        self.assertEqual(cl.enumlhs, ('m', 'k', 'v'))
        self.assertEqual(cl.pat_mask, (False, True, True))
        self.assertEqual(cl.enumvars_tagsin, ('m',))
        self.assertEqual(cl.enumvars_tagsout, ('k', 'v'))
        
        # Rate.
        rate = cl.rate([])
        self.assertEqual(rate, Rate.UNRUNNABLE)
        
        # Code.
        
        code = cl.get_code(['m'], L.pc('pass'))
        exp_code = L.pc('''
            if isinstance(m, Map):
                for k, v in m.items():
                    pass
            ''')
        self.assertEqual(code, exp_code)
        
        code = cl.get_code(['m', 'k'], L.pc('pass'))
        exp_code = L.pc('''
            if isinstance(m, Map):
                if k in m:
                    v = m[k]
                    pass
            ''')
        self.assertEqual(code, exp_code)
        
        # Code, no type-checks.
        cl = MapClause_NoTC('m', 'k', 'v')
        code = cl.get_code(['m'], L.pc('pass'))
        exp_code = L.pc('''
            for k, v in m.items():
                pass
            ''')
        self.assertEqual(code, exp_code)
    
    def test_objclausefactory(self):
        cl = MClause('S', 'x')
        clast = L.Enumerator(L.tuplify(['S', 'x'], lval=True),
                             L.pe('_M'))
        cl2 = ObjClauseFactory.from_AST(clast)
        self.assertEqual(cl2, cl)
        
        cl = FClause_NoTC('o', 'v', 'f')
        clast = L.Enumerator(L.tuplify(['o', 'v'], lval=True),
                             L.pe('_F_f'))
        cl2 = ObjClauseFactory_NoTC.from_AST(clast)
        self.assertEqual(cl2, cl)
        self.assertIsInstance(cl2, FClause_NoTC)


if __name__ == '__main__':
    unittest.main()
