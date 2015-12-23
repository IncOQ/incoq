"""Unit tests for symtab.py."""


import unittest

from incoq.mars.incast import L
from incoq.mars.types import Set, Top
from incoq.mars.symtab import *


class NamingCase(unittest.TestCase):
    
    def test_fresh_name_generator(self):
        gen = N.fresh_name_generator('x{}')
        names = [next(gen) for _ in range(3)]
        exp_names = ['x1', 'x2', 'x3']
        self.assertEqual(names, exp_names)
    
    def test_subnames(self):
        names = N.get_subnames('x', 3)
        exp_names = ['x_v1', 'x_v2', 'x_v3']
        self.assertEqual(names, exp_names)
    
    def test_auxmap(self):
        name = N.get_auxmap_name('R', L.mask('bu'))
        exp_name = 'R_bu'
        self.assertEqual(name, exp_name)
    
    def test_maintfunc(self):
        name = N.get_maint_func_name('Q', 'R', 'add')
        exp_name = '_maint_Q_for_R_add'
        self.assertEqual(name, exp_name)


class SymbolCase(unittest.TestCase):
    
    def test_rel(self):
        r = RelationSymbol('R', type=Set(Top))
        s = str(r)
        exp_s = 'Relation R (type: {Top})'
        self.assertEqual(s, exp_s)
        
        s = r.decl_comment
        exp_s = 'R : {Top}'
        self.assertEqual(s, exp_s)
    
    def test_map(self):
        m = MapSymbol('M')
        s = str(m)
        exp_s = 'Map M (type: {Bottom: Bottom})'
        self.assertEqual(s, exp_s)
    
    def test_var(self):
        v = VarSymbol('v', type=Set(Top))
        s = str(v)
        exp_s = 'Var v (type: {Top})'
        self.assertEqual(s, exp_s)
    
    def test_query(self):
        q = QuerySymbol('Q', node=L.Num(5))
        s = str(q)
        exp_s = 'Query Q (5)'
        self.assertEqual(s, exp_s)


class SymbolTableCase(unittest.TestCase):
    
    def test_fresh_vars(self):
        symtab = SymbolTable()
        v = next(symtab.fresh_vars)
        exp_v = '_v1'
        self.assertEqual(v, exp_v)
        v = next(symtab.fresh_vars)
        exp_v = '_v2'
        self.assertEqual(v, exp_v)
    
    def test_symbols(self):
        symtab = SymbolTable()
        symtab.define_relation('R')
        symtab.define_relation('S')
        symtab.define_map('M')
        
        rels = list(symtab.get_relations().keys())
        exp_rels = ['R', 'S']
        self.assertSequenceEqual(rels, exp_rels)
    
    def test_dump(self):
        symtab = SymbolTable()
        symtab.define_relation('R')
        symtab.define_relation('S')
        symtab.define_map('M')
        
        s = symtab.dump_symbols()
        exp_s = L.trim('''
            Relation R (type: {Bottom})
            Relation S (type: {Bottom})
            Map M (type: {Bottom: Bottom})
            ''')
        self.assertEqual(s, exp_s)


class QueryRewriterCase(unittest.TestCase):
    
    class DoublerRewriter(QueryRewriter):
        
        class Doubler(L.NodeTransformer):
            def visit_Num(self, node):
                return node._replace(n=node.n * 2)
            def visit_Query(self, node):
                # Don't double-process nested queries.
                return
        
        def rewrite(self, symbol, name, expr):
            if isinstance(expr, L.Num) and expr.n == 0:
                return None
            else:
                return self.Doubler.run(expr)
    
    def test_basic(self):
        symtab = SymbolTable()
        symtab.define_query('Q1', node=L.Parser.pe('1 + 2'))
        symtab.define_query('Q2', node=L.Parser.pe('3 + 4'))
        symtab.define_query('Q3', node=L.Parser.pe('0'))
        tree = L.Parser.p('''
            def main():
                print(QUERY('Q1', 1 + 2))
                print(QUERY('Q1', 1 + 2))
                print(QUERY('Q2', 3 + 4))
                print(QUERY('Q3', 0))
            ''')
        tree = self.DoublerRewriter.run(tree, symtab)
        
        exp_tree = L.Parser.p('''
            def main():
                print(QUERY('Q1', 2 + 4))
                print(QUERY('Q1', 2 + 4))
                print(QUERY('Q2', 6 + 8))
                print(QUERY('Q3', 0))
            ''')
        self.assertEqual(tree, exp_tree)
        self.assertEqual(symtab.get_symbols()['Q1'].node,
                         L.Parser.pe('2 + 4'))
        self.assertEqual(symtab.get_symbols()['Q2'].node,
                         L.Parser.pe('6 + 8'))
        self.assertEqual(symtab.get_symbols()['Q3'].node,
                         L.Parser.pe('0'))
    
    def test_called_once(self):
        # rewrite() shouldn't be called multiple times for multiple
        # occurrences.
        
        class Counter(QueryRewriter):
            def process(self, tree):
                self.called = {}
                return super().process(tree)
            def rewrite(self, symbol, name, expr):
                self.called.setdefault(name, 0)
                self.called[name] += 1
                return expr
        
        symtab = SymbolTable()
        symtab.define_query('Q1', node=L.Parser.pe('1 + 2'))
        symtab.define_query('Q2', node=L.Parser.pe('3 + 4'))
        tree = L.Parser.p('''
            def main():
                print(QUERY('Q1', 1 + 2))
                print(QUERY('Q1', 1 + 2))
                print(QUERY('Q2', 3 + 4))
            ''')
        counter = Counter(symtab)
        counter.process(tree)
        self.assertEqual(counter.called['Q1'], 1)
        self.assertEqual(counter.called['Q2'], 1)
    
    def test_inconsistent(self):
        # No symbol.
        symtab = SymbolTable()
        tree = L.Parser.p('''
            def main():
                print(QUERY('Q1', 1 + 2))
            ''')
        with self.assertRaises(L.TransformationError):
            QueryRewriter.run(tree, symtab)
        
        # Symbol / occurrence mismatch.
        symtab = SymbolTable()
        symtab.define_query('Q1', node=L.Parser.pe('1 + 2'))
        tree = L.Parser.p('''
            def main():
                print(QUERY('Q1', 3 + 4))
            ''')
        with self.assertRaises(L.TransformationError):
            QueryRewriter.run(tree, symtab)
        
        # Multiple symbol mismatch.
        symtab = SymbolTable()
        symtab.define_query('Q1', node=L.Parser.pe('1 + 2'))
        tree = L.Parser.p('''
            def main():
                print(QUERY('Q1', 1 + 2))
                print(QUERY('Q1', 3 + 4))
            ''')
        with self.assertRaises(L.TransformationError):
            QueryRewriter.run(tree, symtab)
    
    def test_nonrecursive(self):
        class Rewriter(QueryRewriter):
            def rewrite(self, symbol, name, expr):
                if name == 'Q1':
                    return L.Query('Q2', L.Parser.pe('2'))
        
        symtab = SymbolTable()
        symtab.define_query('Q1', node=L.Parser.pe('1'))
        symtab.define_query('Q2', node=L.Parser.pe('2'))
        tree = L.Parser.p('''
            def main():
                print(QUERY('Q1', 1))
                print(QUERY('Q2', 2))
            ''')
        tree = Rewriter.run(tree, symtab)
        
        exp_tree = L.Parser.p('''
            def main():
                print(QUERY('Q1', QUERY('Q2', 2)))
                print(QUERY('Q2', 2))
            ''')
        self.assertEqual(tree, exp_tree)
        self.assertEqual(symtab.get_symbols()['Q1'].node,
                         L.Parser.pe("QUERY('Q2', 2)"))
    
    def test_nested(self):
        symtab = SymbolTable()
        # Define in reverse order to test proper ordering of
        # symbol processing.
        symtab.define_query('Q3', node=L.Parser.pe(
                                  "4 + QUERY('Q2', 3 + QUERY('Q1', 1 + 2))"))
        symtab.define_query('Q2', node=L.Parser.pe("3 + QUERY('Q1', 1 + 2)"))
        symtab.define_query('Q1', node=L.Parser.pe('1 + 2'))
        tree = L.Parser.p('''
            def main():
                print(QUERY('Q1', 1 + 2))
                print(QUERY('Q2', 3 + QUERY('Q1', 1 + 2)))
                print(QUERY('Q3', 4 + QUERY('Q2', 3 + QUERY('Q1', 1 + 2))))
            ''')
        tree = self.DoublerRewriter.run(tree, symtab)
        
        exp_tree = L.Parser.p('''
            def main():
                print(QUERY('Q1', 2 + 4))
                print(QUERY('Q2', 6 + QUERY('Q1', 2 + 4)))
                print(QUERY('Q3', 8 + QUERY('Q2', 6 + QUERY('Q1', 2 + 4))))
            ''')
        self.assertEqual(tree, exp_tree)
        self.assertEqual(symtab.get_symbols()['Q1'].node,
                         L.Parser.pe('2 + 4'))
        self.assertEqual(symtab.get_symbols()['Q2'].node,
                         L.Parser.pe("6 + QUERY('Q1', 2 + 4)"))
        self.assertEqual(symtab.get_symbols()['Q3'].node,
                         L.Parser.pe("8 + QUERY('Q2', 6 + "
                                     "QUERY('Q1', 2 + 4))"))


if __name__ == '__main__':
    unittest.main()
