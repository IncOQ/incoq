"""Unit tests for util.py."""


import unittest

from incoq.util.collections import OrderedSet
from incoq.compiler.incast.nodes import *
from incoq.compiler.incast.structconv import parse_structast, NodeTransformer
from incoq.compiler.incast.nodeconv import IncLangImporter
from incoq.compiler.incast.util import *
from incoq.compiler.incast.util import FuncDefLister
from incoq.compiler.incast import ts


class UtilCase(unittest.TestCase):
    
    def p(self, source, subst=None, mode=None):
        return IncLangImporter.run(
                    parse_structast(source, mode=mode, subst=subst))
    
    def pc(self, source, **kargs):
        return self.p(source, mode='code', **kargs)
    
    def ps(self, source, **kargs):
        return self.p(source, mode='stmt', **kargs)
    
    def pe(self, source, **kargs):
        return self.p(source, mode='expr', **kargs)
    
    def test_usedvars(self):
        tree = self.p('''
            a = b
            b = c
            d = e + f
            R.add(1)
            {() for a in b}
            ''')
        vars = VarsFinder.run(tree)
        exp_vars = ['a', 'b', 'c', 'd', 'e', 'f', 'R']
        self.assertSequenceEqual(vars, exp_vars)
        
        # Ignore store.
        vars = VarsFinder.run(tree, ignore_store=True)
        self.assertSequenceEqual(vars, ['a', 'b', 'c', 'e', 'f'])
        
        # Ignore functions.
        tree = self.p('''
            def f(a, b):
                c
            if f(d):
                pass
            ''')
        names = VarsFinder.run(tree, ignore_functions=False)
        vars = VarsFinder.run(tree, ignore_functions=True)
        self.assertCountEqual(names, ['c', 'd', 'f'])
        self.assertCountEqual(vars, ['c', 'd'])
        
        # Ignore relations.
        tree = self.p('''
            COMP({x for x in S if sum(R) > 0
                    if sum(setmatch(T, 'bu', 1)) > 0
                    if y in Z},
                [], {})
            ''')
        names1 = VarsFinder.run(tree, ignore_rels=False)
        names2 = VarsFinder.run(tree, ignore_rels=True)
        self.assertCountEqual(names1, ['x', 'S', 'R', 'T', 'y', 'Z'])
        self.assertCountEqual(names2, ['x', 'y'])
    
    def test_varrenamer(self):
        tree = self.p('''
            (a, b, c) = (a, b, c)
            ''')
        nameit = iter(['b1', 'b2'])
        subst = {'a': 'a1', 'b': lambda n: next(nameit)}
        tree = VarRenamer.run(tree, subst)
        exp_tree = self.p('''
            (a1, b1, c) = (a1, b2, c)
            ''')
        self.assertEqual(tree, exp_tree)
    
    def test_scope(self):
        os = OrderedSet
        
        # Ensure that scope stack info is returned correctly.
        
        class FooScoper(ScopeVisitor):
            def process(self, tree):
                self.res = []
                super().process(tree)
                return self.res
            def visit_Name(self, node):
                super().visit_Name(node)
                if node.id == 'X':
                    self.res.append(list(self._scope_stack))
        
        tree = self.p('''
            def f(p):
                X
            for R in f(1):
                if R:
                    X
                    {a for a in R if len({X for a in a}) > 0}
            ''')
        res = FooScoper.run(tree)
        res_flat = [ScopeVisitor.bvars_from_scopestack(sc)
                    for sc in res]
        
        exp_res = [
            [os(['f', 'R']), os(['p'])],
            [os(['f', 'R'])],
            [os(['f', 'R']), os(['a']), os(['a'])],
        ]
        exp_res_flat = [
            os(['f', 'R', 'p']),
            os(['f', 'R']),
            os(['f', 'R', 'a']),
        ]
        
        self.assertEqual(res, exp_res)
        self.assertEqual(res_flat, exp_res_flat)
        
        # Ensure the order of traversal is correct.
        
        class FooScoper(ScopeVisitor):
            def process(self, tree):
                self.res = {}
                super().process(tree)
                return self.res
            def visit_Name(self, node):
                if isinstance(node.ctx, Store):
                    self.res[node.id] = self.current_bvars()
                super().visit_Name(node)
        
        tree = self.p('''
            a = 1
            for d in {c2 for c1 in R for c2 in {b for b in a}}:
                e = 2
            ''')
        res = FooScoper.run(tree)
        
        exp_res = {
            'a': os([]),
            'c1': os(['a']),
            'b': os(['a', 'c1']),
            'c2': os(['a', 'c1']),
            'd': os(['a']),
            'e': os(['a', 'd']),
        }
        
        self.assertEqual(res, exp_res)
    
    def test_prefix_names(self):
        tree = self.p('a = b + c')
        tree = prefix_names(tree, ['a', 'b'], 'p')
        
        exp_tree = self.p('pa = pb + c')
        
        self.assertEqual(tree, exp_tree)
    
    def test_name_counter(self):
        namegen = NameGenerator(fmt='a{}', counter=100)
        self.assertEqual(namegen.peek(), 'a100')
        self.assertEqual(namegen.peek(), 'a100')
        self.assertEqual(namegen.next(), 'a100')
        self.assertEqual(namegen.next_prefix(), 'a101_')
        self.assertEqual(next(namegen), 'a102')
        
        tree = self.p('a = b + c')
        tree = namegen.prefix_names(tree, {'a', 'b'})
        
        exp_tree = self.p('a103_a = a103_b + c')
        
        self.assertEqual(tree, exp_tree)
    
    def test_injective(self):
        tree = self.pe('a')
        self.assertTrue(is_injective(tree))
        tree = self.pe('a + b')
        self.assertFalse(is_injective(tree))
        tree = self.pe('(a, (b, c))')
        self.assertTrue(is_injective(tree))
        tree = self.pe('(a, (b, (c + d)))')
        self.assertFalse(is_injective(tree))
    
    def test_query_replacer(self):
        q1 = Aggregate(self.pe('a'), 'count', {})
        q2 = Aggregate(self.pe('a'), 'sum', {})
        
        tree = Expr(q1)
        tree = QueryReplacer.run(tree, q1, q2)
        exp_tree = Expr(q2)
        self.assertEqual(tree, exp_tree)
    
    def test_query_mapper(self):
        q1 = Aggregate(self.p('a'), 'count', {})
        q2 = Aggregate(self.p('a'), 'sum', {})
        
        class Foo(QueryMapper):
            def map_Aggregate(self, query):
                return query._replace(op='sum')
        
        tree = Expr(q1)
        tree = Foo.run(tree)
        exp_tree = Expr(q2)
        self.assertEqual(tree, exp_tree)
    
    def test_StmtTransformer(self):
        _self = self
        
        class Foo(StmtTransformer):
            def visit_arg(self, node):
                new_code = _self.pc('print(x)', subst={'x': node.arg})
                self.pre_stmts.extend(new_code)
            def visit_Name(self, node):
                new_code = _self.pc('print(x)', subst={'x': node.id})
                self.pre_stmts.extend(new_code)
        
        tree = self.p('''
            def f(x):
                g(x)
            ''')
        tree = Foo.run(tree)
        
        exp_tree = self.p('''
            print(x)
            def f(x):
                print(g)
                print(x)
                g(x)
            ''')
        
        self.assertEqual(tree, exp_tree)
    
    def test_OuterMaintTransformer(self):
        _self = self
        
        class Foo(OuterMaintTransformer):
            def visit_SetUpdate(self, node):
                id = node.target.id
                name = 'Q_' + id
                desc = ts(node)
                precode = _self.pc('print(N)', subst={'N': id + '_pre'})
                postcode = _self.pc('print(N)', subst={'N': id + '_post'})
                return self.with_outer_maint(node, name, desc,
                                             precode, postcode)
        
        in_tree = self.p('''
            with MAINT(T, 'after', 'S.add(1)'):
                with MAINT(P, 'after', 'S.add(1)'):
                    S.add(1)
                    R.add(2)
            ''')
        tree = Foo.run(in_tree, ['P', 'T'])
        
        exp_tree = Module(
            (Maintenance(
                'Q_S', 'S.add(1)',
                self.pc('print(S_pre)'),
                (Maintenance(
                    'T', 'S.add(1)',
                    (),
                    (Maintenance(
                        'P', 'S.add(1)',
                        (),
                        self.pc('S.add(1)'),
                        (Maintenance(
                            'Q_R', 'R.add(2)',
                            self.pc('print(R_pre)'),
                            self.pc('R.add(2)'),
                            self.pc('print(R_post)')
                        ),)
                    ),),
                    ()
                ),),
                self.pc('print(S_post)'),
            ),))
        
        self.assertEqual(tree, exp_tree)
        
        tree = Foo.run(in_tree, ['P'])
        
        exp_tree = Module(
            (Maintenance(
                'T', 'S.add(1)',
                (),
                (Maintenance(
                    'Q_S', 'S.add(1)',
                    self.pc('print(S_pre)'),
                    (Maintenance(
                        'P', 'S.add(1)',
                        (),
                        self.pc('S.add(1)'),
                        (Maintenance(
                            'Q_R', 'R.add(2)',
                            self.pc('print(R_pre)'),
                            self.pc('R.add(2)'),
                            self.pc('print(R_post)')
                        ),)
                    ),),
                    self.pc('print(S_post)'),
                ),),
                ()
            ),))
        
        self.assertEqual(tree, exp_tree)
    
    def test_rewrite_compclauses(self):
        class FooRewriter(NodeTransformer):
            def process(self, tree):
                self.new_clauses = []
                tree = super().process(tree)
                return tree, self.new_clauses
            
            def visit_Name(self, node):
                if node.id in ['x', 'y', 'z']:
                    newcl = Enumerator(Name('_' + node.id, Store()),
                                       Name('R', Load()))
                    self.new_clauses.append(newcl)
                    return node._replace(id='_' + node.id)
        
        orig_comp = self.pe('COMP({x + z for x in S if y > 1}, [])')
        
        comp = rewrite_compclauses(orig_comp, FooRewriter.run)
        exp_comp = self.pe(
            'COMP({_x + _z for _x in R for _x in S '
                          'for _y in R if _y > 1 '
                          'for _x in R for _z in R},'
                 '[])')
        self.assertEqual(comp, exp_comp)
        
        comp = rewrite_compclauses(orig_comp, FooRewriter.run, after=True)
        exp_comp = self.pe(
            'COMP({_x + _z for _x in S for _x in R '
                          'if _y > 1 for _y in R '
                          'for _x in R for _z in R},'
                 '[])')
        self.assertEqual(comp, exp_comp)
        
        comp = rewrite_compclauses(orig_comp, FooRewriter.run, enum_only=True)
        exp_comp = self.pe(
            'COMP({x + z for _x in R for _x in S '
                        'if y > 1},'
                 '[])')
        self.assertEqual(comp, exp_comp)
    
    def test_rewrite_compclauses_recursive(self):
        class FooRewriter(NodeTransformer):
            def process(self, tree):
                self.new_clauses = []
                tree = super().process(tree)
                return tree, self.new_clauses
            
            def visit_Name(self, node):
                if node.id not in ['x', 'y']:
                    return node
                newid = {'x': 'y', 'y': 'z'}[node.id]
                newcl = Enumerator(Name(newid, Store()),
                                   Name('R', Load()))
                self.new_clauses.append(newcl)
                return node._replace(id=(node.id + node.id))
        
        orig_comp = self.pe('COMP({x for x in S}, [])')
        
        comp = rewrite_compclauses(orig_comp, FooRewriter.run,
                                   enum_only=True, recursive=True)
        exp_comp = self.pe(
            'COMP({x for z in R for yy in R for xx in S},'
                 '[])')
        self.assertEqual(comp, exp_comp)
    
    def test_skeletonize(self):
        tree = self.p('''
            with MAINT(Q, 'after', 'S.add(1)'):
                S.add(1)
                a = 1
                for x in R:
                    with MAINT(Q, 'before', 'T.add(2)'):
                        c = 3
                        T.add(2)
                b = 2
            ''')
        tree = maint_skeleton(tree)
        exp_tree = self.p('''
            with MAINT(Q, 'after', 'S.add(1)'):
                S.add(1)
                with MAINT(Q, 'before', 'T.add(2)'):
                    pass
                    T.add(2)
            ''')
        self.assertEqual(tree, exp_tree)
    
    def test_funcdeffinderlister(self):
        tree = self.p('''
            def f(a, b):
                print((a, b))
            def g(c):
                pass
            def g(d):
                pass
            ''')
        with self.assertRaises(AssertionError):
            FuncDefLister.run(tree, lambda n: True)
        
        f = FuncDefLister.run(tree, lambda n: n in ['f'])['f']
        exp_f = self.ps('def f(a, b): print((a, b))')
        self.assertEqual(f, exp_f)
    
    def test_demfuncmaker(self):
        maker = DemfuncMaker('Q', 'Qdesc', ('x', 'y'), None)
        
        code = maker.make_usetvars()
        exp_code = self.pc('''
            _U_Q = RCSet()
            _UEXT_Q = Set()
            ''')
        self.assertEqual(code, exp_code)
        
        code = maker.make_demfunc()
        exp_code = self.pc('''
            def demand_Q(x, y):
                'Qdesc'
                if ((x, y) not in _U_Q):
                    _U_Q.add((x, y))
                else:
                    _U_Q.incref((x, y))
            ''')
        self.assertEqual(code, exp_code)
        
        code = maker.make_undemfunc()
        exp_code = self.pc('''
            def undemand_Q(x, y):
                'Qdesc'
                if (_U_Q.getref((x, y)) == 1):
                    _U_Q.remove((x, y))
                else:
                    _U_Q.decref((x, y))
            ''')
        self.assertEqual(code, exp_code)
        
        code = maker.make_queryfunc()
        exp_code = self.pc('''
            def query_Q(x, y):
                'Qdesc'
                if ((x, y) not in _UEXT_Q):
                    _UEXT_Q.add((x, y))
                    demand_Q(x, y)
                return True
            ''')
        self.assertEqual(code, exp_code)
        
        maker = DemfuncMaker('Q', 'Qdesc', ('x', 'y'), 100)
        
        code = maker.make_usetvars()
        exp_code = self.pc('''
            _U_Q = RCSet()
            _UEXT_Q = LRUSet()
            ''')
        self.assertEqual(code, exp_code)
        
        code = maker.make_queryfunc()
        exp_code = self.pc('''
            def query_Q(x, y):
                'Qdesc'
                if ((x, y) not in _UEXT_Q):
                    while (len(_UEXT_Q) >= 100):
                        _top_v1, _top_v2 = _top = _UEXT_Q.peek()
                        undemand_Q(_top_v1, _top_v2)
                        _UEXT_Q.remove(_top)
                    _UEXT_Q.add((x, y))
                    demand_Q(x, y)
                else:
                    _UEXT_Q.ping((x, y))
                return True
            ''')
        self.assertEqual(code, exp_code)


if __name__ == '__main__':
    unittest.main()
