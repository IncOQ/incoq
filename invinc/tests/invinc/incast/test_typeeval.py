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
    
    
    def test(self):
        tree = self.p('''
            print(x)
            x, y = (1+2, True and False)
            (x, y)
            [1, 2, 'a']
            {x for x in S}
            ''')
        res = analyze_types(tree, {'S': SetType(strtype)})
        for t in res.items():
            print(t)


if __name__ == '__main__':
    unittest.main()
