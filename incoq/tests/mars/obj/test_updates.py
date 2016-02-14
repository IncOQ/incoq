"""Unit tests for updates.py."""


import unittest

from incoq.mars.incast import L
from incoq.mars.symbol import S, N
from incoq.mars.obj.comp import ObjRelations
from incoq.mars.obj.updates import *


class ClauseCase(unittest.TestCase):
    
    def test_pairdomainimporter(self):
        objrels = ObjRelations(True, ['f'], True, [2])
        fresh_vars = N.fresh_name_generator()
        tree = L.Parser.p('''
            def main():
                s.add(e)
                s.remove(e)
                R.reladd(e)
                R.relremove(e)
                R.relclear()
                d[k] = v
                del d[k]
                M.mapassign(k, v)
                M.mapdelete(k)
                M.mapclear()
                o.f = v
                del o.f
            ''')
        tree = PairDomainImporter.run(tree, fresh_vars, objrels)
        exp_tree = L.Parser.p('''
            def main():
                _v1 = (s, e)
                _M.reladd(_v1)
                _v2 = (s, e)
                _M.relremove(_v2)
                R.reladd(e)
                R.relremove(e)
                R.relclear()
                _v3 = (d, k, v)
                _MAP.reladd(_v3)
                _v4 = (d, k, d[k])
                _MAP.relremove(_v4)
                M.mapassign(k, v)
                M.mapdelete(k)
                M.mapclear()
                _v5 = (o, v)
                _F_f.reladd(_v5)
                _v6 = (o, o.f)
                _F_f.relremove(_v6)
            ''')
        self.assertEqual(tree, exp_tree)
        
        with self.assertRaises(L.TransformationError):
            tree = L.Parser.pc('s.update(t)')
            PairDomainImporter.run(tree, fresh_vars, objrels)
        with self.assertRaises(L.TransformationError):
            tree = L.Parser.pc('s.clear()')
            PairDomainImporter.run(tree, fresh_vars, objrels)
        with self.assertRaises(L.TransformationError):
            tree = L.Parser.pc('d.dictclear()')
            PairDomainImporter.run(tree, fresh_vars, objrels)


if __name__ == '__main__':
    unittest.main()
