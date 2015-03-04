"""Type analysis based on abstract interpretation."""


__all__ = [
    'TypeAnalysisFailure',
    'TypeAnalyzer',
    'analyze_types',
]


from invinc.util.seq import pairs

from .nodes import (Load, Store, Not, Eq, NotEq, Lt, LtE, Gt, GtE,
                    Is, IsNot, In, NotIn, Enumerator, expr)
from .structconv import NodeTransformer, AdvNodeVisitor
from .error import ProgramError
from .util import VarsFinder
from .types import *


class TypeAnalysisFailure(ProgramError):
    
    def __init__(self, msg=None, node=None, store=None):
        super().__init__(node=node)
        self.msg = msg
        self.node = node
        self.store = store
    
    def __str__(self):
        s = ''
        if self.msg is not None:
            s += str(self.msg)
        if self.store is not None:
            if self.msg is not None:
                s += '\n'
            s += 'Store: ' + str(self.store)
        return s


class TypeAnalyzer(AdvNodeVisitor):
    
    """Abstract interpreter for type analysis.
    
    The flow of type information mirrors the dataflow of the concrete
    interpretation. Nodes exchange data (types) with their children
    via visit() calls. Sending data to a child is done by passing an
    extra input argument to visit(). Receiving data is done by visit()
    returning a non-None value.
    
    Expression nodes have different behavior depending on whether they
    are in Load or Store context.
    
    There is a separate store mapping variables to their type
    information.
    """
    
    def __init__(self, store=None):
        super().__init__()
        if store is None:
            store = {}
        self.store = store
    
    def top_helper(self, node, input=None):
        # Result: top
        self.generic_visit(node)
        return toptype
    
    # Statements.
    
    def visit_Delete(self, node):
        # Don't bother descending into children.
        pass
    
    def visit_Assign(self, node):
        # Action: target <- value for each target
        t_value = self.visit(node.value)
        for t in node.targets:
            self.visit(t, t_value)
    
    def visit_For(self, node):
        # Trigger: iter = set<T> for some T
        #   Action: target <- T
        t_iter = self.visit(node.iter)
        if isinstance(t_iter, SetType):
            self.visit(node.target, t_iter.et)
        self.visit(node.body)
        self.visit(node.orelse)
    
    # Expressions.
    
    def visit_BoolOp(self, node):
        # Result: bool
        # Cond: v <= bool for each value v
        t_values = [self.visit(v) for v in node.values]
        if not all(t_v.issubtype(booltype) for t_v in t_values):
            raise TypeAnalysisFailure('BoolOp has non-bool arg',
                                      node, self.store)
        return booltype
    
    def visit_BinOp(self, node):
        # Result: number
        # Cond: left <= number, right <= number
        t_left = self.visit(node.left)
        t_right = self.visit(node.right)
        if not (t_left.issubtype(numbertype) and
                t_right.issubtype(numbertype)):
            raise TypeAnalysisFailure('BinOp has non-number arg',
                                      node, self.store)
        return numbertype
    
    def visit_UnaryOp(self, node):
        # If op is "not":
        #     Result: bool
        #     Cond: operand <= bool
        # Otherwise:
        #     Result: number
        #     Cond: operand <= number
        t_operand = self.visit(node.operand)
        resulttype = (booltype if isinstance(node.op, Not)
                      else numbertype)
        t = resulttype.join(t_operand)
        if not t.issubtype(resulttype):
            raise TypeAnalysisFailure('UnaryOp requires ' + str(resulttype),
                                      node, self.store)
        return t
    
    visit_Lambda = top_helper
    
    def visit_IfExp(self, node):
        # Result: join(body, orelse)
        # Cond: test <= bool
        t_test = self.visit(node.test)
        t_body = self.visit(node.body)
        t_orelse = self.visit(node.orelse)
        t = t_body.join(t_orelse)
        if not t_test.issubtype(booltype):
            raise TypeAnalysisFailure('IfExp requires bool condition',
                                      node, self.store)
        return t
    
    def visit_Dict(self, node):
        # Result: dict<join(keys), join(values)>
        t_keys = [self.visit(k) for k in node.keys]
        t_values = [self.visit(v) for v in node.values]
        return DictType(bottomtype.join(*t_keys), bottomtype.join(*t_values))
    
    def visit_Set(self, node):
        # Result: set<join(elts)>
        t_elts = [self.visit(e) for e in node.elts]
        return SetType(bottomtype.join(*t_elts))
    
    def visit_ListComp(self, node):
        # Result: list<elt>
        for gen in node.generators:
            self.visit(gen)
        t_elt = self.visit(node.elt)
        return ListType(t_elt)
    
    def visit_SetComp(self, node):
        # Result: set<elt>
        for gen in node.generators:
            self.visit(gen)
        t_elt = self.visit(node.elt)
        return SetType(t_elt)
    
    def visit_DictComp(self, node):
        # Result: dict<key, value>
        for gen in node.generators:
            self.visit(gen)
        t_key = self.visit(node.key)
        t_value = self.visit(node.value)
        return DictType(t_key, t_value)
    
    visit_GeneratorExp = top_helper
    visit_Yield = top_helper
    visit_YieldFrom = top_helper
    
    def compare_helper(self, node, op, t_left, t_right):
        # If op is ordering:
        #     Cond: left and right are bottom, numbertype, or any tuple
        # If op is equality/identity or their negations:
        #     No action
        # If op is membership or its negation:
        #     Cond: right <= set<top>
        def allowed(t):
            return (t is bottomtype or
                    t is numbertype or
                    isinstance(t, TupleType))
        
        if isinstance(op, (Lt, LtE, Gt, GtE)):
            if not (allowed(t_left) and allowed(t_right)):
                raise TypeAnalysisFailure('Order comparison requires '
                                          'number or tuple operands',
                                          node, self.store)
        elif isinstance(op, (Eq, NotEq, Is, IsNot)):
            # We don't check to see that the two operands are
            # of the same type. Even though this is hopefully
            # true in the final analysis results, it's not
            # necessarily true at an arbitrary intermediate
            # stage. We don't propagate type information against
            # the dataflow, so there's nothing to do.
            pass
        elif isinstance(op, (In, NotIn)):
            # Same issue as above. We don't compare the types against
            # each other, but at least we can say the RHS must be a set.
            if not t_right.issubtype(SetType(toptype)):
                raise TypeAnalysisFailure('Membership comparison requires '
                                          'set on right-hand side',
                                          node, self.store)
    
    def visit_Compare(self, node):
        # Result: bool
        # Cond: compare_helper(left, op, right) for each pair
        values = (node.left,) + node.comparators
        t_values = [self.visit(v) for v in values]
        print(values)
        for (t_left, t_right), op in zip(pairs(t_values), node.ops):
            self.compare_helper(node, op, t_left, t_right)
        return booltype
    
    def visit_Call(self, node):
        ### TODO
        # ???
        self.generic_visit(node)
        return bottomtype
    
    def visit_Num(self, node):
        # Result: number
        return numbertype
    
    def visit_Str(self, node):
        # Result: str
        return strtype
    
    visit_Bytes = top_helper
    
    def visit_NameConstant(self, node):
        # If True/False:
        #     Result: bool
        # If None:
        #     Result: top
        if node.value in [True, False]:
            return booltype
        else:
            return toptype
    
    visit_Ellipsis = top_helper
    
    # Context-dependent expressions.
    #
    # These nodes may appear in Load or Store context. These cases
    # are handled separately, since the dataflow goes in opposite
    # directions. Del context is ignored.
    
    def visit_Attribute(self, node, input=None):
        ### TODO
        return bottomtype
    
    def visit_Subscript(self, node, input=None):
        ### TODO
        return bottomtype
    
    visit_Starred = top_helper
    
    def visit_Name(self, node, input=None):
        # In load context:
        #     Result: store[id]
        # In store context:
        #     Action: store[id] <- input
        if isinstance(node.ctx, Load):
            assert input is None
            return self.store[node.id]
        elif isinstance(node.ctx, Store):
            assert input is not None
            self.store[node.id] = self.store[node.id].join(input)
    
    def visit_List(self, node, input=None):
        # In load context:
        #     Result: list<join(elts)>
        # In store context:
        #     Cond: input = list<T> for some T
        #     Action: elt_i <- T for each i
        if isinstance(node.ctx, Load):
            assert input is None
            t_elts = [self.visit(e) for e in node.elts]
            return ListType(bottomtype.join(*t_elts))
        elif isinstance(node.ctx, Store):
            assert input is not None
            if not isinstance(input, ListType):
                raise TypeAnalysisFailure('Store to List requires list type',
                                          node, self.store)
            for e in node.elts:
                self.visit(e, input.et)
    
    def visit_Tuple(self, node, input=None):
        # In load context:
        #     Result: tuple<elt_1, ..., elt_n>
        # In store context:
        #     Trigger: input = tuple<...> with len(elts) parts
        #       Action: elt_i <- input_i for each i
        if isinstance(node.ctx, Load):
            assert input is None
            return TupleType([self.visit(e) for e in node.elts])
        elif isinstance(node.ctx, Store):
            assert input is not None
            if (isinstance(input, TupleType) and
                len(input.ets) == len(node.elts)):
                for e, i in zip(node.elts, input.ets):
                    self.visit(e, i)
    
    # Other nodes.
    
    def visit_comprehension(self, node):
        # Trigger: iter = set<T> for some T
        #   Action: target <- T
        # Cond: cond = bool for each cond
        t_iter = self.visit(node.iter)
        if isinstance(t_iter, SetType):
            self.visit(node.target, t_iter.et)
        for cond in node.ifs:
            t_cond = self.visit(cond)
            if not t_cond.issubtype(booltype):
                raise TypeAnalysisFailure('Condition clause requires '
                                          'bool type', node, self.store)
    
    # IncAST nodes.
    
    def visit_Enumerator(self, node):
        # Trigger: iter = set<T> for some T
        #   Action: target <- T
        t_iter = self.visit(node.iter)
        if isinstance(t_iter, SetType):
            self.visit(node.target, t_iter.et)
    
    def visit_Comp(self, node):
        # Result: set<elt>
        for cl in node.clauses:
            if isinstance(cl, Enumerator):
                self.visit(cl)
            else:
                t_cl = self.visit(cl)
                if not t_cl.issubtype(booltype):
                    raise TypeAnalysisFailure('Condition clause requires '
                                              'bool type', node, self.store)
        t_resexp = self.visit(node.resexp)
        return SetType(t_resexp)
    
    def visit_Aggregate(self, node):
        ### TODO
        return bottomtype
    
    def visit_SetUpdate(self, node):
        # Cond: target <= set<top>
        t_target = self.visit(node.target)
        if not t_target.issubtype(SetType(toptype)):
            raise TypeAnalysisFailure('SetUpdate requires set type',
                                      node, self.store)
        self.visit(node.elem)
    
    def visit_MacroSetUpdate(self, node):
        # Cond: target <= set<top>
        # Cond: other <= set<top> if other is present
        t_target = self.visit(node.target)
        if not t_target.issubtype(SetType(toptype)):
            raise TypeAnalysisFailure('MacroSetUpdate requires set type',
                                      node, self.store)
        if node.other is not None:
            t_other = self.visit(node.other)
            if not t_other.issubtype(SetType(toptype)):
                raise TypeAnalysisFailure('MacroSetUpdate requires '
                                          'set type', node, self.store)
    
    visit_RCSetRefUpdate = visit_SetUpdate
    
    def visit_IsEmpty(self, node):
        # Result: bool
        # Cond: target <= set<top>
        t_target = self.visit(node.target)
        if not t_target.issubtype(SetType(toptype)):
            raise TypeAnalysisFailure('IsEmpty requires set type',
                                      node, self.store)
        return booltype
    
    def visit_GetRef(self, node):
        # Result: numbertype
        # Cond: target <= set<top>
        t_target = self.visit(node.target)
        if not t_target.issubtype(SetType(toptype)):
            raise TypeAnalysisFailure('IsEmpty requires set type',
                                      node, self.store)
        self.visit(node.elem)
        return numbertype
    
    def lookup_helper(self, node, check_default=False):
        # Cond: target = dict<K, V> for some K, V
        # Cond: key <= K
        # Result: V
        # Cond: default <= V if a default is applicable and provided
        t_target = self.visit(node.target)
        t_key = self.visit(node.key)
        if not isinstance(t_target, DictType):
            raise TypeAnalysisFailure('Lookup requires dict type',
                                       node, self.store)
        if not t_key.issubtype(t_target.kt):
            raise TypeAnalysisFailure('Lookup key does not fit dict '
                                      'key type', node, self.store)
        if check_default and node.default is not None:
            t_default = self.visit(node.default)
            if not t_default.issubtype(t_target.vt):
                raise TypeAnalysisFailure('Lookup default does not fit '
                                          'dict value type', node, self.store)
        return t_target.vt
    
    def visit_Lookup(self, node):
        return self.lookup_helper(node, check_default=True)
    
    def visit_ImgLookup(self, node):
        return self.lookup_helper(node)
    
    visit_RCImgLookup = visit_ImgLookup
    
    # Temporary stuff.
    
    def visit_SMLookup(self, node):
        ### TODO
        return bottomtype
    
    def visit_DemQuery(self, node):
        ### TODO
        return bottomtype
    
    def visit_NoDemQuery(self, node):
        ### TODO
        return bottomtype
    
    def visit_SetMatch(self, node):
        ### TODO
        return bottomtype
    
    def visit_DeltaMatch(self, node):
        ### TODO
        return bottomtype


#class TypeAnnotator(NodeTransformer):
#    
#    """Transformer that fills in type information for expressions
#    based on a store.
#    """
#    
#    def visit_


def analyze_types(tree, vartypes=None):
    if vartypes is None:
        vartypes = {}
    
    varnames = VarsFinder.run(tree)
    
    store = {var: vartypes.get(var, bottomtype)
             for var in varnames}
    
    TypeAnalyzer.run(tree, store)
    
    for k, v in store.items():
        print('  {} -- {}'.format(k, v))
    
    return store
