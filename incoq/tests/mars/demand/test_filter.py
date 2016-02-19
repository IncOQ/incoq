"""Unit tests for filter.py."""


import unittest

from incoq.mars.incast import L
from incoq.mars.comp import CoreClauseVisitor
from incoq.mars.obj import ObjClauseVisitor
from incoq.mars.demand.filter import *
from incoq.mars.demand.filter import Tag, Filter


class ClauseVisitor(CoreClauseVisitor, ObjClauseVisitor):
    pass


class FilterCase(unittest.TestCase):
    
    def setUp(self):
        self.visitor = ClauseVisitor()
    
    def test_generate_structures(self):
        comp = L.Parser.pe('''
            {(o_f,) for (s, t) in REL(U) for (s, o) in M()
                    for (t, o) in M () for (o, o_f) in F(f)}
            ''')
        structures = generate_structures(self.visitor, comp, 'Q')
        exp_structures = [
            Tag(0, 'Q_T_s', 's', L.RelMember(['s', 't'], 'U')),
            Tag(0, 'Q_T_t', 't', L.RelMember(['s', 't'], 'U')),
            Filter(1, 'Q_d_M_1', L.MMember('s', 'o'), ['Q_T_s']),
            Tag(1, 'Q_T_o_1', 'o', L.RelMember(['s', 'o'], 'Q_d_M_1')),
            Filter(2, 'Q_d_M_2', L.MMember('t', 'o'), ['Q_T_t']),
            Tag(2, 'Q_T_o_2', 'o', L.RelMember(['t', 'o'], 'Q_d_M_2')),
            Filter(3, 'Q_d_F_f', L.FMember('o', 'o_f', 'f'),
                   ['Q_T_o_1', 'Q_T_o_2']),
            Tag(3, 'Q_T_o_f', 'o_f', L.RelMember(['o', 'o_f'], 'Q_d_F_f')),
        ]
        self.assertEqual(structures, exp_structures)


if __name__ == '__main__':
    unittest.main()
