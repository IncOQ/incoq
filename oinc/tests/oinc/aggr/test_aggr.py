"""Unit tests for aggr.py."""


import unittest

import oinc.incast as L
from oinc.set import Mask
from oinc.central import CentralCase

from oinc.aggr.aggr import *
from oinc.aggr.aggr import get_cg_class


class SpecCase(unittest.TestCase):
    
    def test_spec(self):
        # Aggregate of a relation.
        node = L.pe('count(R)')
        spec = AggrSpec.from_node(node)
        
        self.assertEqual(spec.aggrop, 'count')
        self.assertEqual(spec.rel, 'R')
        self.assertEqual(spec.relmask, Mask('u'))
        self.assertEqual(spec.params, ())
        self.assertEqual(spec.oper_demname, None)
        self.assertEqual(spec.oper_demparams, None)
        
        constrs = spec.get_domain_constraints('A')
        exp_constrs = []
        self.assertEqual(constrs, exp_constrs)
        
        # Aggregate of a setmatch, with demand.
        node = L.pe('count(DEMQUERY(foo, [c1], '
                            'setmatch(R, "bub", (c1, c2))))')
        spec = AggrSpec.from_node(node)
        
        self.assertEqual(spec.aggrop, 'count')
        self.assertEqual(spec.rel, 'R')
        self.assertEqual(spec.relmask, Mask('bub'))
        self.assertEqual(spec.params, ('c1', 'c2'))
        self.assertEqual(spec.oper_demname, 'foo')
        self.assertEqual(spec.oper_demparams, ('c1',))
        
        constrs = spec.get_domain_constraints('A')
        exp_constrs = [('A.1', 'R.1'),
                       ('A.2', 'R.3')]
        self.assertEqual(constrs, exp_constrs)

class DemCountParamDemCase(unittest.TestCase):
    
    """Demand-driven count query over an operand with parameters
    and demand.
    """
    
    def setUp(self):
        self.aggr = L.pe('count(DEMQUERY(R, [p1], setmatch(R, "bbu", (p1, p2))))')
        self.spec = AggrSpec.from_node(self.aggr)
        self.incaggr = IncAggr(self.aggr, self.spec, 'A', 'A', None, False)
        self.cg = get_cg_class(self.spec.aggrop)(self.incaggr)
    
    def test_addu(self):
        code = self.cg.make_addu_maint('_')
        exp_code = L.pc('''
            _val = 0
            for _elem in setmatch(R, 'bbu', (p1, p2)):
                _val = (_val + 1)
            (_1, _2) = (p1, p2)
            A.add((_1, _2, _val))
            demand_R(p1)
            ''')
        self.assertEqual(code, exp_code)
    
    def test_removeu(self):
        code = self.cg.make_removeu_maint('_')
        exp_code = L.pc('''
            undemand_R(p1)
            (_1, _2) = (p1, p2)
            _elem = A.smlookup('bbu', (p1, p2))
            A.remove((_1, _2, _elem))
            ''')
        self.assertEqual(code, exp_code)
    
    def test_oper_maint_add(self):
        code = self.cg.make_oper_maint('_', 'add', L.pe('e'))
        exp_code = L.pc('''
            (_v1, _v2, _v3) = e
            if ((_v1, _v2) in _U_A):
                _val = A.smlookup('bbu', (_v1, _v2))
                _val = (_val + 1)
                (_1, _2) = (_v1, _v2)
                _elem = A.smlookup('bbu', (_v1, _v2))
                A.remove((_1, _2, _elem))
                A.add((_1, _2, _val))
            ''')
        self.assertEqual(code, exp_code)
    
    def test_retrieval_code(self):
        code = self.cg.make_retrieval_code()
        exp_code = L.pe('''
            DEMQUERY(A, [p1, p2], A.smlookup('bbu', (p1, p2)))
            ''')
        self.assertEqual(code, exp_code)

class DemMinParamNoDemCase(unittest.TestCase):
    
    """Demand-driven min query over an operand with parameters but
    no demand.
    """
    
    def setUp(self):
        self.aggr = L.pe('min(setmatch(R, "bbu", (p1, p2)))')
        self.spec = AggrSpec.from_node(self.aggr)
        self.incaggr = IncAggr(self.aggr, self.spec, 'A', 'A', None, False)
        self.cg = get_cg_class(self.spec.aggrop)(self.incaggr)
    
    def test_addu(self):
        code = self.cg.make_addu_maint('_')
        exp_code = L.pc('''
            _val = (Tree(), None)
            for _elem in setmatch(R, 'bbu', (p1, p2)):
                (_tree, _) = _val
                _tree[_elem] = None
                _val = (_tree, _tree.__min__())
            (_1, _2) = (p1, p2)
            A.add((_1, _2, _val))
            ''')
        self.assertEqual(code, exp_code)
    
    def test_removeu(self):
        code = self.cg.make_removeu_maint('_')
        exp_code = L.pc('''
            (_1, _2) = (p1, p2)
            _elem = A.smlookup('bbu', (p1, p2))
            A.remove((_1, _2, _elem))
            ''')
        self.assertEqual(code, exp_code)
    
    def test_oper_maint_remove(self):
        code = self.cg.make_oper_maint('_', 'remove', L.pe('e'))
        exp_code = L.pc('''
            (_v1, _v2, _v3) = e
            if ((_v1, _v2) in _U_A):
                _val = A.smlookup('bbu', (_v1, _v2))
                (_tree, _) = _val
                del _tree[_v3]
                _val = (_tree, _tree.__min__())
                (_1, _2) = (_v1, _v2)
                _elem = A.smlookup('bbu', (_v1, _v2))
                A.remove((_1, _2, _elem))
                A.add((_1, _2, _val))
            ''')
        self.assertEqual(code, exp_code)

class DemSumNoParamCase(unittest.TestCase):
    
    """Demand-driven sum query over an operand with no parameters and
    no demand.
    """
    
    def setUp(self):
        self.aggr = L.pe('sum(R)')
        self.spec = AggrSpec.from_node(self.aggr)
        self.incaggr = IncAggr(self.aggr, self.spec, 'A', 'A', None, False)
        self.cg = get_cg_class(self.spec.aggrop)(self.incaggr)
    
    def test_addu(self):
        code = self.cg.make_addu_maint('_')
        exp_code = L.pc('''
            _val = 0
            for _elem in setmatch(R, 'u', ()):
                _val = (_val + _elem)
            _ = ()
            A.add(_val)
            ''')
        self.assertEqual(code, exp_code)
    
    def test_removeu(self):
        code = self.cg.make_removeu_maint('_')
        exp_code = L.pc('''
            _ = ()
            _elem = A.smlookup('u', ())
            A.remove(_elem)
            ''')
        self.assertEqual(code, exp_code)
    
    def test_oper_maint_add(self):
        code = self.cg.make_oper_maint('_', 'add', L.pe('e'))
        exp_code = L.pc('''
            _v1 = e
            if (() in _U_A):
                _val = A.smlookup('u', ())
                _val = (_val + _v1)
                _ = ()
                _elem = A.smlookup('u', ())
                A.remove(_elem)
                A.add(_val)
            ''')
        self.assertEqual(code, exp_code)

class NoDemCountParamNoDemCase(unittest.TestCase):
    
    """Count query over an operand with parameters, but no demand for
    aggregate nor operand.
    """
    
    def setUp(self):
        self.aggr = L.pe('count(setmatch(R, "bbu", (p1, p2)))')
        self.spec = AggrSpec.from_node(self.aggr)
        self.incaggr = IncAggr(self.aggr, self.spec, 'A', None, None, False)
        self.cg = get_cg_class(self.spec.aggrop)(self.incaggr)
    
    def test_oper_maint_add(self):
        code = self.cg.make_oper_maint('_', 'add', L.pe('e'))
        exp_code = L.pc('''
            (_v1, _v2, _v3) = e
            _val = A.smdeflookup('bbu', (_v1, _v2), (0, 0))
            (_state, _count) = _val
            _state = (_state + 1)
            _val = (_state, (_count + 1))
            (_1, _2) = (_v1, _v2)
            if (not setmatch(A, 'bbu', (_v1, _v2)).isempty()):
                _elem = A.smlookup('bbu', (_v1, _v2))
                A.remove((_1, _2, _elem))
            A.add((_1, _2, _val))
            ''')
        self.assertEqual(code, exp_code)
    
    def test_retrieval_code(self):
        code = self.cg.make_retrieval_code()
        exp_code = L.pe('''
            A.smdeflookup('bbu', (p1, p2), (0, 0))[0]
            ''')
        self.assertEqual(code, exp_code)

class HalfDemSumParamNoDemCase(unittest.TestCase):
    
    """Half-demand sum query over an operand with parameters but
    no demand.
    """
    
    def setUp(self):
        self.aggr = L.pe('sum(setmatch(R, "bbu", (p1, p2)))')
        self.spec = AggrSpec.from_node(self.aggr)
        self.incaggr = IncAggr(self.aggr, self.spec, 'A', 'A', None, True)
        self.cg = get_cg_class(self.spec.aggrop)(self.incaggr)
    
    def test_addu(self):
        code = self.cg.make_addu_maint('_')
        exp_code = L.pc('''
            _val = A.smdeflookup('bbu', (p1, p2), None)
            if (_val is None):
                (_1, _2) = (p1, p2)
                A.add((_1, _2, (0, 0)))
            ''')
        self.assertEqual(code, exp_code)
    
    def test_removeu(self):
        code = self.cg.make_removeu_maint('_')
        exp_code = L.pc('''
            _val = A.smlookup('bbu', (p1, p2))
            if (_val[1] == 0):
                (_1, _2) = (p1, p2)
                _elem = A.smlookup('bbu', (p1, p2))
                A.remove((_1, _2, _elem))
            ''')
        self.assertEqual(code, exp_code)
    
    def test_oper_maint_remove(self):
        code = self.cg.make_oper_maint('_', 'remove', L.pe('e'))
        exp_code = L.pc('''
            (_v1, _v2, _v3) = e
            _val = A.smlookup('bbu', (_v1, _v2))
            if ((_val[1] == 1) and ((_v1, _v2) not in _U_A)):
                (_1, _2) = (_v1, _v2)
                _elem = A.smlookup('bbu', (_v1, _v2))
                A.remove((_1, _2, _elem))
            else:
                (_state, _count) = _val
                _state = (_state - _v3)
                _val = (_state, (_count - 1))
                (_1, _2) = (_v1, _v2)
                _elem = A.smlookup('bbu', (_v1, _v2))
                A.remove((_1, _2, _elem))
                A.add((_1, _2, _val))
            ''')
        self.assertEqual(code, exp_code)

class TransformCase(CentralCase):
    
    def test_transform_noparams_nodem(self):
        aggr_node = L.pe('sum(R, {})')
        tree = L.p('''
            R.add(5)
            print(AGGR)
            ''', subst={'AGGR': aggr_node})
        tree = inc_aggr(tree, self.manager, aggr_node, 'A',
                        demand=True, half_demand=False)
        
        exp_tree = L.p('''
            A = Set()
            def _maint_A_add(_e):
                v1_v1 = _e
                if (() in _U_A):
                    v1_val = A.smlookup('u', ())
                    v1_val = (v1_val + v1_v1)
                    _ = ()
                    v1_elem = A.smlookup('u', ())
                    A.remove(v1_elem)
                    A.add(v1_val)
            
            def _maint_A_remove(_e):
                v2_v1 = _e
                if (() in _U_A):
                    v2_val = A.smlookup('u', ())
                    v2_val = (v2_val - v2_v1)
                    _ = ()
                    v2_elem = A.smlookup('u', ())
                    A.remove(v2_elem)
                    A.add(v2_val)
            
            _U_A = RCSet()
            _UEXT_A = Set()
            def demand_A():
                'sum(R, None)'
                if (() not in _U_A):
                    with MAINT(A, 'after', '_U_A.add(())'):
                        _U_A.add(())
                        v3_val = 0
                        for v3_elem in setmatch(R, 'u', ()):
                            v3_val = (v3_val + v3_elem)
                        _ = ()
                        A.add(v3_val)
                else:
                    _U_A.incref(())
            
            def undemand_A():
                'sum(R, None)'
                if (_U_A.getref(()) == 1):
                    with MAINT(A, 'before', '_U_A.remove(())'):
                        _ = ()
                        v4_elem = A.smlookup('u', ())
                        A.remove(v4_elem)
                        _U_A.remove(())
                else:
                    _U_A.decref(())
            
            def query_A():
                'sum(R, None)'
                if (() not in _UEXT_A):
                    _UEXT_A.add(())
                    demand_A()
                return True
            
            with MAINT(A, 'after', 'R.add(5)'):
                R.add(5)
                _maint_A_add(5)
            print(DEMQUERY(A, [], A.smlookup('u', (),)))
            ''')
        
        self.assertEqual(tree, exp_tree)


if __name__ == '__main__':
    unittest.main()
