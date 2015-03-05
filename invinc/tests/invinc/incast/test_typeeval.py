"""Unit tests for typeeval.py."""


import unittest

from invinc.compiler.incast.structconv import parse_structast
from invinc.compiler.incast.nodeconv import IncLangImporter
from invinc.compiler.incast.types import *
from invinc.compiler.incast.types import add_fresh_typevars, subst_typevars
from invinc.compiler.incast import ts_typed, trim

from invinc.compiler.incast.typeeval import *


class ConstraintCase(unittest.TestCase):
    
    def p(self, source, subst=None, mode=None):
        return IncLangImporter.run(
                    parse_structast(source, mode=mode, subst=subst))
    
    def test_program1(self):
        tree = self.p('''
            x, y = (1+2, True and False)
            (x, y)
            [1, 2, 'a']
            {x for x in S}
            ''')
        tree, store = analyze_types(tree, {'S': SetType(bottomtype)})
        source = ts_typed(tree)
        exp_source = trim('''
            (((x : Number), (y : bool)) : (Number, bool)) = (((((1 : Number) + (2 : Number)) : Number), (((True : bool) and (False : bool)) : bool)) : (Number, bool))
            (((x : Number), (y : bool)) : (Number, bool))
            ([(1 : Number), (2 : Number), ('a' : str)] : [Top])
            (COMP({(x : Number) for (x : Number) in (S : {Bottom})}, None, None) : {Number})
            ''')
        self.assertEqual(source, exp_source)
        self.assertEqual(store['x'], numbertype)
    
    def test_program2(self):
        tree = self.p('''
            S.add(x)
            ''')
        tree, store = analyze_types(tree, {'x': numbertype})
        self.assertEqual(store['S'], SetType(numbertype))
    
    def test_program3(self):
        tree = self.p('''
            S.add(T)
            T.add(S)
            ''')
        tree, store = analyze_types(tree)
        s = str(store['S'])
        exp_s = '{{{{{Top}}}}}'
        self.assertEqual(s, exp_s)


if __name__ == '__main__':
    unittest.main()
