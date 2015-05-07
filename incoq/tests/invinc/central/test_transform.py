###############################################################################
# test_transform.py                                                           #
# Author: Jon Brandvein                                                       #
###############################################################################

"""Unit tests for the transform module."""


import unittest

import incoq.compiler.incast as L
from incoq.compiler.central import CentralCase
from incoq.compiler.central.transform import *
from incoq.compiler.central.transform import transform_all_queries


class TestTransform(CentralCase):
    
    def test_transform(self):
        comp = L.pe('COMP({z for (x, y) in R for (y, z) in S}, [x], '
                       '{"impl": "inc"})')
        tree = L.p('''
            R.add(1)
            print(COMP)
            ''', subst={'COMP': comp})
        
        tree = transform_all_queries(tree, self.manager)
        tree = L.elim_deadfuncs(tree, lambda n: n.startswith('_maint_'))
        
        exp_tree = L.p('''
            Comp1 = RCSet()
            def _maint_Comp1_R_add(_e):
                Comment("Iterate {(v1_x, v1_y, v1_z) : (v1_x, v1_y) in deltamatch(R, 'bb', _e, 1), (v1_y, v1_z) in S}")
                (v1_x, v1_y) = _e
                for v1_z in setmatch(S, 'bu', v1_y):
                    if ((v1_x, v1_z) not in Comp1):
                        Comp1.add((v1_x, v1_z))
                    else:
                        Comp1.incref((v1_x, v1_z))
            
            with MAINT(Comp1, 'after', 'R.add(1)'):
                R.add(1)
                _maint_Comp1_R_add(1)
            print(setmatch(Comp1, 'bu', x))
            ''')
        
        self.assertEqual(tree, exp_tree)
    
    def test_preprocess(self):
        tree = L.p('''
            x = 1
            {y for (x, y) in R}
            COMP({y for (x, y) in R}, [y], {'impl': 'auxonly'})
            ''')
        given_opts = ({'obj_domain': False},
                      {'{y for (x, y) in R}': {'impl': 'inc'}})
        tree, opman = preprocess_tree(
                    self.manager, tree, given_opts)
        
        exp_tree = L.p('''
            x = 1
            COMP({y for (x, y) in R}, [x], {'impl': 'inc'})
            COMP({y for (x, y) in R}, [y], {'impl': 'auxonly'})
            ''')
        exp_nopts = {'obj_domain': False}
        
        self.assertEqual(tree, exp_tree)
        self.assertEqual(opman.nopts, exp_nopts)


if __name__ == '__main__':
    unittest.main()
