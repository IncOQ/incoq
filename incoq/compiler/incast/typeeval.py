"""Type analysis based on abstract interpretation."""


__all__ = [
    'TypeAnalysisFailure',
    'TypeAnalyzer',
    'analyze_types',
]


from incoq.util.seq import pairs

from .nodes import (Load, Store, Not, Eq, NotEq, Lt, LtE, Gt, GtE,
                    Is, IsNot, In, NotIn, Enumerator, expr, Name,
                    BitOr, BitXor, BitAnd)
from .structconv import AdvNodeTransformer
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


class TypeAnalyzer(AdvNodeTransformer):
    
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
    
    Expression node type fields are updated as they are passed
    up or down the tree.
    """
    
    def __init__(self, store=None):
        super().__init__()
        if store is None:
            store = {}
        self.store = store
    
    def top_helper(self, node, input=None):
        # Result: top
        node = self.generic_visit(node)
        return node._replace(type=toptype)
    
    # Statements.
    
    def visit_Delete(self, node):
        # Don't bother descending into children.
        pass
    
    def visit_Assign(self, node):
        # Action: target <- value for each target
        value = self.visit(node.value)
        targets = [self.visit(t, value.type) for t in node.targets]
        return node._replace(value=value, targets=targets)
    
    def visit_For(self, node):
        # Trigger: iter = set<T> for some T
        #   Action: target <- T
        iter = self.visit(node.iter)
        if isinstance(iter.type, SetType):
            target = self.visit(node.target, iter.type.et)
        else:
            target = node.target
        body = self.visit(node.body)
        orelse = self.visit(node.orelse)
        return node._replace(iter=iter, target=target,
                             body=body, orelse=orelse)
    
    # Expressions.
    
    def visit_BoolOp(self, node):
        # Result: bool
        # Cond: v <= bool for each value v
        values = [self.visit(v) for v in node.values]
        if not all(v.type.issubtype(booltype) for v in values):
            raise TypeAnalysisFailure('BoolOp has non-bool arg',
                                      node, self.store)
        return node._replace(values=values, type=booltype)
    
    def visit_BinOp(self, node):
        # If op is BitOr | BitXor | BitAnd:
        #     Result: join(left, right)
        # Otherwise:
        #     Result: number
        #     Cond: left <= number, right <= number
        left = self.visit(node.left)
        right = self.visit(node.right)
        if isinstance(node.op, (BitOr, BitXor, BitAnd)):
            resulttype = left.type.join(right.type)
            return node._replace(left=left, right=right, type=resulttype)
        else:
            if not (left.type.issubtype(numbertype) and
                    right.type.issubtype(numbertype)):
                raise TypeAnalysisFailure('BinOp has non-number arg',
                                          node, self.store)
            return node._replace(left=left, right=right, type=numbertype)
    
    def visit_UnaryOp(self, node):
        # If op is "not":
        #     Result: bool
        #     Cond: operand <= bool
        # Otherwise:
        #     Result: number
        #     Cond: operand <= number
        operand = self.visit(node.operand)
        resulttype = (booltype if isinstance(node.op, Not)
                      else numbertype)
        t = resulttype.join(operand.type)
        if not t.issubtype(resulttype):
            raise TypeAnalysisFailure('UnaryOp requires ' + str(resulttype),
                                      node, self.store)
        return node._replace(operand=operand, type=t)
    
    visit_Lambda = top_helper
    
    def visit_IfExp(self, node):
        # Result: join(body, orelse)
        # Cond: test <= bool
        test = self.visit(node.test)
        body = self.visit(node.body)
        orelse = self.visit(node.orelse)
        t = body.type.join(orelse.type)
        if not test.type.issubtype(booltype):
            raise TypeAnalysisFailure('IfExp requires bool condition',
                                      node, self.store)
        return node._replace(test=test, body=body, orelse=orelse, type=t)
    
    def visit_Dict(self, node):
        # Result: dict<join(keys), join(values)>
        keys = [self.visit(k) for k in node.keys]
        values = [self.visit(v) for v in node.values]
        t = DictType(bottomtype.join(*[k.type for k in keys]),
                        bottomtype.join(*[v.type for v in values]))
        return node._replace(keys=keys, value=values, type=t)
    
    def visit_Set(self, node):
        # Result: set<join(elts)>
        elts = [self.visit(e) for e in node.elts]
        t = SetType(bottomtype.join(*[e.type for e in elts]))
        return node._replace(elts=elts, type=t)
    
    def visit_ListComp(self, node):
        # Result: list<elt>
        generators = [self.visit(gen) for gen in node.generators]
        elt = self.visit(node.elt)
        t = ListType(elt.type)
        return node._replace(generators=generators, elt=elt, type=t)
    
    def visit_SetComp(self, node):
        # Result: set<elt>
        generators = [self.visit(gen) for gen in node.generators]
        elt = self.visit(node.elt)
        t = SetType(elt.type)
        return node._replace(generators=generators, elt=elt, type=t)
    
    def visit_DictComp(self, node):
        # Result: dict<key, value>
        generators = [self.visit(gen) for gen in node.generators]
        key = self.visit(node.key)
        value = self.visit(node.value)
        t = DictType(key.type, value.type)
        return node._replace(generators=generators,
                             key=key, value=value, type=t)
    
    visit_GeneratorExp = top_helper
    visit_Yield = top_helper
    visit_YieldFrom = top_helper
    
    def compare_helper(self, node, op, t_left, t_right):
        # If op is ordering:
        #     Cond: left and right are bottom, numbertype, or any tuple
        # If op is equality/identity or their negations:
        #     No action
        # If op is membership or its negation:
        #     Cond: right <= set<top> or right <= dict<top, top>
        def allowed(t):
            return (t.issubtype(booltype) or
                    t.issubtype(numbertype) or
                    t.issubtype(strtype) or
                    isinstance(t, TupleType) or
                    isinstance(t, ListType) or
                    isinstance(t, SetType) or
                    isinstance(t, DictType))
        
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
            if not (t_right.issubtype(SetType(toptype)) or
                    t_right.issubtype(DictType(toptype, toptype))):
                raise TypeAnalysisFailure('Membership comparison requires '
                                          'set on right-hand side',
                                          node, self.store)
    
    def visit_Compare(self, node):
        # Result: bool
        # Cond: compare_helper(left, op, right) for each pair
        values = (node.left,) + node.comparators
        values = [self.visit(v) for v in values]
        for (left, right), op in zip(pairs(values), node.ops):
            self.compare_helper(node, op, left.type, right.type)
        return node._replace(left=values[0], comparators=values[1:],
                             type=booltype)
    
    def visit_Call(self, node):
        ### TODO
        # ???
        node = self.generic_visit(node)
        return node._replace(type=bottomtype)
    
    def visit_Num(self, node):
        # Result: number
        return node._replace(type=numbertype)
    
    def visit_Str(self, node):
        # Result: str
        return node._replace(type=strtype)
    
    visit_Bytes = top_helper
    
    def visit_NameConstant(self, node):
        # If True/False:
        #     Result: bool
        # If None:
        #     Result: bottom
        if node.value in [True, False]:
            t = booltype
        else:
            # Arguably, None should be toptype since it is
            # definitively a value that doesn't fit into
            # other classifications. But this messes with
            # global variable initialization in some of the
            # distalgo examples (SELF_ID = None at the header
            # makes SELF_ID be considered to have top type).
            #
            # The tradeoff is that expressions like 5 + None
            # won't be caught as type errors.
            t = bottomtype
        return node._replace(type=t)
    
    visit_Ellipsis = top_helper
    
    # Context-dependent expressions.
    #
    # These nodes may appear in Load or Store context. These cases
    # are handled separately, since the dataflow goes in opposite
    # directions. Del context is ignored.
    
    def visit_Attribute(self, node, input=None):
        ### TODO
        return node._replace(type=bottomtype)
    
    def visit_Subscript(self, node, input=None):
        ### TODO
        return node._replace(type=bottomtype)
    
    visit_Starred = top_helper
    
    def visit_Name(self, node, input=None):
        # In load context:
        #     Result: store[id]
        # In store context:
        #     Action: store[id] <- input
        if isinstance(node.ctx, Load):
            assert input is None
            t = self.store[node.id]
            return node._replace(type=t)
        elif isinstance(node.ctx, Store):
            assert input is not None
            self.store[node.id] = t = self.store[node.id].join(input)
            return node._replace(type=t)
    
    def visit_List(self, node, input=None):
        # In load context:
        #     Result: list<join(elts)>
        # In store context:
        #     Cond: input = list<T> for some T
        #     Action: elt_i <- T for each i
        if isinstance(node.ctx, Load):
            assert input is None
            elts = [self.visit(e) for e in node.elts]
            t = ListType(bottomtype.join(*[e.type for e in elts]))
            return node._replace(elts=elts, type=t)
        elif isinstance(node.ctx, Store):
            assert input is not None
            if not isinstance(input, ListType):
                raise TypeAnalysisFailure('Store to List requires list type',
                                          node, self.store)
            elts = [self.visit(e, input.et) for e in node.elts]
            return node._replace(elts=elts, type=input)
    
    def visit_Tuple(self, node, input=None):
        # In load context:
        #     Result: tuple<elt_1, ..., elt_n>
        # In store context:
        #     Trigger: input = tuple<...> with len(elts) parts
        #       Action: elt_i <- input_i for each i
        if isinstance(node.ctx, Load):
            assert input is None
            elts = [self.visit(e) for e in node.elts]
            t = TupleType([e.type for e in elts])
            return node._replace(elts=elts, type=t)
        elif isinstance(node.ctx, Store):
            assert input is not None
            if (isinstance(input, TupleType) and
                len(input.ets) == len(node.elts)):
                elts = [self.visit(e, i)
                        for e, i in zip(node.elts, input.ets)]
                return node._replace(elts=elts, type=input)
    
    # Other nodes.
    
    def visit_comprehension(self, node):
        # Trigger: iter = set<T> for some T
        #   Action: target <- T
        # Cond: cond = bool for each cond
        iter = self.visit(node.iter)
        if isinstance(iter.type, SetType):
            target = self.visit(node.target, iter.type.et)
        else:
            target = node.target
        ifs = [self.visit(i) for i in node.ifs]
        for cond in ifs:
            if not cond.type.issubtype(booltype):
                raise TypeAnalysisFailure('Condition clause requires '
                                          'bool type', node, self.store)
        return node._replace(iter=iter, target=target, ifs=ifs)
    
    # IncAST nodes.
    
    def visit_Enumerator(self, node):
        # Trigger: iter = set<T> for some T
        #   Action: target <- T
        iter = self.visit(node.iter)
        if isinstance(iter.type, SetType):
            target = self.visit(node.target, iter.type.et)
        else:
            target = node.target
        return node._replace(iter=iter, target=target)
    
    def visit_Comp(self, node):
        # Result: set<elt>
        clauses = []
        for cl in node.clauses:
            if isinstance(cl, Enumerator):
                cl = self.visit(cl)
            else:
                cl = self.visit(cl)
                if not cl.type.issubtype(booltype):
                    raise TypeAnalysisFailure('Condition clause requires '
                                              'bool type', node, self.store)
            clauses.append(cl)
        resexp = self.visit(node.resexp)
        t = SetType(resexp.type)
        return node._replace(resexp=resexp, clauses=tuple(clauses), type=t)
    
    def visit_Aggregate(self, node):
        ### TODO
        node = self.generic_visit(node)
        return node._replace(type=bottomtype)
    
    def visit_SetUpdate(self, node):
        # Cond: target <= set<top>
        target = self.visit(node.target)
        if not target.type.issubtype(SetType(toptype)):
            raise TypeAnalysisFailure('SetUpdate requires set type',
                                      node, self.store)
        elem = self.visit(node.elem)
        
        # Hack: If target is a Name, update it and its store
        # variable to be at least set<target>.
        if isinstance(target, Name):
            t_target = target.type.join(SetType(elem.type))
            target = target._replace(type=t_target)
            self.store[target.id] = t_target
        
        return node._replace(target=target, elem=elem)
    
    def visit_MacroUpdate(self, node):
        # For set updates:
        #   Cond: target <= set<top>
        #   Cond: other <= set<top> if other is present
        # For map updates:
        #   Cond: target <= dict<top, top>
        #   Cond: other <= dict<top, top> if other is present
        if node.op in ['union', 'inter', 'diff', 'symdiff',
                       'assign', 'clear']:
            t_oper = SetType(toptype)
            t_oper_name = 'set'
        elif node.op in ['mapassign', 'mapclear']:
            t_oper = DictType(toptype, toptype)
            t_oper_name = 'dict'
        else:
            assert()
        failure = TypeAnalysisFailure('{} update requires {} type'.format(
                                      node.op, t_oper_name),
                                      node, self.store)
        target = self.visit(node.target)
        if not target.type.issubtype(t_oper):
            raise failure
        if node.other is not None:
            other = self.visit(node.other)
            if not other.type.issubtype(t_oper):
                raise failure
        else:
            other = None
        return node._replace(target=target, other=other)
    
    visit_RCSetRefUpdate = visit_SetUpdate
    
    def visit_IsEmpty(self, node):
        # Result: bool
        # Cond: target <= set<top>
        target = self.visit(node.target)
        if not target.type.issubtype(SetType(toptype)):
            raise TypeAnalysisFailure('IsEmpty requires set type',
                                      node, self.store)
        return node._replace(target=target, type=booltype)
    
    def visit_GetRef(self, node):
        # Result: numbertype
        # Cond: target <= set<top>
        target = self.visit(node.target)
        if not target.type.issubtype(SetType(toptype)):
            raise TypeAnalysisFailure('IsEmpty requires set type',
                                      node, self.store)
        elem = self.visit(node.elem)
        return node._replace(target=target, elem=elem, type=numbertype)
    
    def lookup_helper(self, node, check_default=False):
        # Cond: target = dict<K, V> for some K, V
        # Cond: key <= K
        # Result: V
        # Cond: default <= V if a default is applicable and provided
        target = self.visit(node.target)
        key = self.visit(node.key)
        if not isinstance(target.type, DictType):
            raise TypeAnalysisFailure('Lookup requires dict type',
                                       node, self.store)
        if not key.type.issubtype(target.type.kt):
            raise TypeAnalysisFailure('Lookup key does not fit dict '
                                      'key type', node, self.store)
        t = target.type.vt
        if check_default:
            if node.default is not None:
                default = self.visit(node.default)
                if not default.type.issubtype(target.type.vt):
                    raise TypeAnalysisFailure('Lookup default does not fit '
                                              'dict value type',
                                              node, self.store)
            else:
                default = None
            node = node._replace(target=target, key=key,
                                 default=default, type=t)
        else:
            node = node._replace(target=target, key=key, type=t)
        return node
    
    def visit_Lookup(self, node):
        return self.lookup_helper(node, check_default=True)
    
    def visit_ImgLookup(self, node):
        return self.lookup_helper(node)
    
    visit_RCImgLookup = visit_ImgLookup
    
    # Temporary stuff.
    
    def visit_SMLookup(self, node):
        ### TODO
        node = self.generic_visit(node)
        return node._replace(type=bottomtype)
    
    def visit_DemQuery(self, node):
        ### TODO
        node = self.generic_visit(node)
        return node._replace(type=bottomtype)
    
    def visit_NoDemQuery(self, node):
        ### TODO
        node = self.generic_visit(node)
        return node._replace(type=bottomtype)
    
    def visit_SetMatch(self, node):
        ### TODO
        node = self.generic_visit(node)
        return node._replace(type=bottomtype)
    
    def visit_DeltaMatch(self, node):
        ### TODO
        node = self.generic_visit(node)
        return node._replace(type=bottomtype)


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
    
    def widen(store):
        for n, t in store.items():
            store[n] = t.widen(10)
    
    count = 0
    limit = 10
    oldtree = None
    while count < limit:
        if tree == oldtree:
            break
        oldtree = tree
        tree = TypeAnalyzer.run(tree, store)
        widen(store)
        count += 1
    else:
        print('Type analysis cut off after {} iterations'.format(count))
    
#    for k, v in store.items():
#        print('  {} -- {}'.format(k, v))
    
    return tree, store
