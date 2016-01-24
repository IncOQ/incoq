"""Unit tests for trans.py."""


import unittest

from incoq.mars.incast import L
from incoq.mars.type import T
from incoq.mars.symbol import S, N
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
        
        tree = L.Parser.p('''
            def main():
                for (x, y, z) in QUERY('Q1', _Q1):
                    pass
                for z in QUERY('Q2', _Q2):
                    pass
                for z in QUERY('Q3', _Q3):
                    pass
            ''', subst={'_Q1': Q1, '_Q2': Q2, '_Q3': Q3})
        
        tree = JoinExpander.run(tree, self.ct, ['Q1', 'Q2', 'Q3'])
        exp_tree = L.Parser.p('''
            def main():
                for (x, y) in R:
                    for (z,) in S.imglookup('bu', (y,)):
                        pass
                for z in QUERY('Q2', {(x,) for (x,) in REL(R)}):
                    pass
                for z in QUERY('Q3', {True for (x,) in REL(R)}):
                    pass
            ''')
        self.assertEqual(tree, exp_tree)
    
    def test_convert_subquery_clause(self):
        cl = L.VarsMember(['x', 'y'], L.Name('R'))
        cl = convert_subquery_clause(cl)
        exp_cl = L.RelMember(['x', 'y'], 'R')
        self.assertEqual(cl, exp_cl)
        
        cl = L.VarsMember(['x', 'y'],
                          L.Parser.pe("R.imglookup('buu', (a,))"))
        cl = convert_subquery_clause(cl)
        exp_cl = L.RelMember(['a', 'x', 'y'], 'R')
        self.assertEqual(cl, exp_cl)
    
    def test_convert_subquery_clauses(self):
        comp = L.Parser.pe('''
            {x for (x, y) in WITHOUT(VARS(R.imglookup('buu', (a,))), e)
               if y > 5}''')
        comp = convert_subquery_clauses(comp)
        exp_comp = L.Parser.pe('''
            {x for (a, x, y) in WITHOUT(REL(R), e)
               if y > 5}''')
        self.assertEqual(comp, exp_comp)
    
    def test_make_comp_maint_func(self):
        comp = L.Parser.pe('''{x + z for (x, y) in REL(R)
                                     for (y, z) in REL(S)}''')
        func = make_comp_maint_func(self.ct, N.fresh_name_generator(),
                                    iter(['J']),
                                    comp, 'Q', 'R', L.SetAdd(),
                                    counted=True)
        exp_func = L.Parser.ps('''
            def _maint_Q_for_R_add(_elem):
                for (_v1_x, _v1_y, _v1_z) in QUERY('J',
                        {(_v1_x, _v1_y, _v1_z)
                         for (_v1_x, _v1_y) in SING(_elem)
                         for (_v1_y, _v1_z) in REL(S)}):
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
                S.reladd(e)
                R.relclear()
                S.relclear()
            ''')
        tree = CompMaintainer.run(tree, self.ct, N.fresh_name_generator(),
                                  iter(['J1', 'J2']),
                                  comp, 'RQ', counted=True)
        exp_tree = L.Parser.p('''
            def _maint_RQ_for_R_add(_elem):
                for (_v1_x, _v1_y) in QUERY('J1',
                        {(_v1_x, _v1_y) for (_v1_x, _v1_y) in SING(_elem)}):
                    _v1_result = (_v1_x + _v1_y)
                    if (_v1_result not in RQ):
                        RQ.reladd(_v1_result)
                    else:
                        RQ.relinccount(_v1_result)
            
            def _maint_RQ_for_R_remove(_elem):
                for (_v2_x, _v2_y) in QUERY('J2',
                        {(_v2_x, _v2_y) for (_v2_x, _v2_y) in SING(_elem)}):
                    _v2_result = (_v2_x + _v2_y)
                    if (RQ.getcount(_v2_result) == 1):
                        RQ.relremove(_v2_result)
                    else:
                        RQ.reldeccount(_v2_result)
            
            def main():
                R.reladd(e)
                _maint_RQ_for_R_add(e)
                S.reladd(e)
                RQ.relclear()
                R.relclear()
                S.relclear()
            ''')
        self.assertEqual(tree, exp_tree)
    
    def test_incrementalize_comp(self):
        comp = L.Parser.pe('{(x,) for (x,) in REL(R)}')
        symtab = S.SymbolTable()
        symtab.clausetools = CoreClauseTools()
        query = symtab.define_query('Q', node=comp,
                                    type=T.Set(T.Tuple([T.Number])))
        
        tree = L.Parser.p('''
            def main():
                R.reladd(e)
                print(QUERY('Q', {(x,) for (x,) in REL(R)}))
            ''')
        tree = incrementalize_comp(tree, symtab, query, 'R_Q')
        for decl in tree.decls:
            if decl.name == 'main':
                func = decl
                break
        exp_func = L.Parser.ps('''
            def main():
                R.reladd(e)
                _maint_R_Q_for_R_add(e)
                print(R_Q)
            ''')
        self.assertEqual(func, exp_func)
    
    def test_incrementalize_comp_with_params(self):
        comp = L.Parser.pe('{(2 * y,) for (x, y) in REL(R)}')
        symtab = S.SymbolTable()
        symtab.clausetools = CoreClauseTools()
        symtab.define_var('x', type=T.Number)
        symtab.define_var('y', type=T.Number)
        symtab.define_relation('R', type=T.Set(T.Tuple([T.Number, T.Number])))
        query = symtab.define_query('Q', node=comp, params=('x',),
                                    type=T.Set(T.Tuple([T.Number])))
        
        tree = L.Parser.p('''
            def main():
                R.reladd(e)
                print(QUERY('Q', {(2 * y,) for (x, y) in REL(R)}))
            ''')
        tree = incrementalize_comp(tree, symtab, query, 'R_Q')
        for decl in tree.decls:
            if decl.name == 'main':
                func = decl
                break
        exp_func = L.Parser.ps('''
            def main():
                R.reladd(e)
                _maint_R_Q_for_R_add(e)
                print(R_Q.imglookup('bu', (x,)))
            ''')
        self.assertEqual(func, exp_func)
        self.assertEqual(query.type, T.Set(T.Tuple([T.Number, T.Number])))
    
    def test_expand_maintjoins(self):
        comp = L.Parser.pe('{x for (x,) in REL(R)}')
        maint_comp = L.Parser.pe('{(x,) for (x,) in SING(e)}')
        symtab = S.SymbolTable()
        symtab.clausetools = CoreClauseTools()
        query = symtab.define_query('Q', node=comp)
        join = symtab.define_query('J', node=maint_comp)
        query.maint_joins = [join]
        
        tree = L.Parser.p('''
            def main():
                for (x,) in QUERY('J', _MAINT_COMP):
                    pass
            ''', subst={'_MAINT_COMP': maint_comp})
        tree = expand_maintjoins(tree, symtab, query)
        exp_tree = L.Parser.p('''
            def main():
                (x,) = e
                pass
            ''')
        self.assertEqual(tree, exp_tree)


if __name__ == '__main__':
    unittest.main()
