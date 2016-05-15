"""Unit tests for updates.py."""


import unittest

from incoq.mars.incast import L
from incoq.mars.symbol import S, N
from incoq.mars.obj.comp import ObjRelations
from incoq.mars.obj.updates import *


class ClauseCase(unittest.TestCase):
    
    def test_pairdomainimporter_normal(self):
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
    
    def test_pairdomainimporter_noobjrels(self):
        objrels = ObjRelations(False, [], False, [])
        fresh_vars = N.fresh_name_generator()
        
        orig_tree = L.Parser.p('''
            def main():
                s.add(e)
                s.remove(e)
                d[k] = v
                del d[k]
                o.f = v
                del o.f
            ''')
        tree = PairDomainImporter.run(orig_tree, fresh_vars, objrels)
        self.assertEqual(tree, orig_tree)
    
    def test_pairdomainimporter_badnodes(self):
        objrels = ObjRelations(True, ['f'], True, [2])
        fresh_vars = N.fresh_name_generator()
        
        with self.assertRaises(L.TransformationError):
            tree = L.Parser.pc('s.update(t)')
            PairDomainImporter.run(tree, fresh_vars, objrels)
        with self.assertRaises(L.TransformationError):
            tree = L.Parser.pc('s.clear()')
            PairDomainImporter.run(tree, fresh_vars, objrels)
        with self.assertRaises(L.TransformationError):
            tree = L.Parser.pc('d.dictclear()')
            PairDomainImporter.run(tree, fresh_vars, objrels)
    
    def test_pairdomainexporter(self):
        objrels = ObjRelations(True, ['f'], True, [2])
        tree = L.Parser.p('''
            def main():
                R.reladd(a)
                _M.reladd(_v1)
                _M.relremove(_v2)
                _MAP.reladd(_v3)
                _MAP.relremove(_v4)
                _F_f.reladd(_v5)
                _F_f.relremove(_v6)
            ''')
        tree = PairDomainExporter.run(tree)
        exp_tree = L.Parser.p('''
            def main():
                R.reladd(a)
                index(_v1, 0).add(index(_v1, 1))
                index(_v2, 0).remove(index(_v2, 1))
                index(_v3, 0)[index(_v3, 1)] = index(_v3, 2)
                del index(_v4, 0)[index(_v4, 1)]
                index(_v5, 0).f = index(_v5, 1)
                del index(_v6, 0).f
            ''')
        self.assertEqual(tree, exp_tree)


if __name__ == '__main__':
    unittest.main()
