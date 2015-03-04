"""Type analysis based on abstract interpretation."""


__all__ = [
    'TypeAnalysisFailure',
    'TypeAnalyzer',
]


from invinc.util.seq import pairs

from .nodes import (Load, Store, Not, Eq, NotEq, Lt, LtE, Gt, GtE,
                    Is, IsNot, In, NotIn)
from .structconv import AdvNodeVisitor
from .error import ProgramError
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
    
    def process(self, tree):
        self.store = {}
        self.output = []
        super().process(tree)
        return self.output
    
    def top_helper(self, node, input=None):
        # Result: top
        self.generic_visit(node)
        return toptype
    
    # Statements.
    
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
    
#    def visit_Dict(self, node):
#        pass
    
#    def visit_Set(self, node):
#        pass
    
#    def visit_ListComp(self, node):
#        pass
    
#    def visit_SetComp(self, node):
#        pass
    
#    def visit_DictComp(self, node):
#        pass
    
    visit_GeneratorExp = top_helper
    visit_Yield = top_helper
    visit_YieldFrom = top_helper
    
    def compare_helper(self, node, op, t_left, t_right):
        # If op is ordering:
        #     Cond: left <= number, right <= number
        # If op is equality/identity or their negations:
        #     No action
        # If op is membership or its negation:
        #     Cond: right <= set<top>
        if isinstance(op, (Lt, LtE, Gt, GtE)):
            if not (t_left.issubtype(numbertype) and
                    t_right.issubtype(numbertype)):
                raise TypeAnalysisFailure('Order comparison requires '
                                          'number operands',
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
        for (t_left, t_right), op in zip(pairs(t_values), node.ops):
            self.compare_helper(node, op, t_left, t_right)
        return booltype
    
    def visit_Call(self, node):
        ### TODO
        # ???
        self.generic_visit(node)
        return toptype
    
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
    
#    def visit_Attribute(self, node, input=None):
#        pass
    
#    def visit_Subscript(self, node, input=None):
#        pass
    
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
            self.store[node.id] = input
    
    def visit_List(self, node, input=None):
        # In load context:
        #     Result: list<join(*elts)>
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
        #     Cond: input = tuple<...> with len(elts) parts
        #     Action: elt_i <- input_i for each i
        if isinstance(node.ctx, Load):
            assert input is None
            return TupleType([self.visit(e) for e in node.elts])
        elif isinstance(node.ctx, Store):
            assert input is not None
            if not (isinstance(input, TupleType) and
                    len(input.ets) == len(node.elts)):
                raise TypeAnalysisFailure('Store to tuple requires '
                                          'tuple type', node, self.store)
            for e, i in zip(node.elts, input.ets):
                self.visit(e, i)
    
    
    
    # Temporary stuff.
    
    def visit_Assign(self, node, input=None):
        # Action: target <- value for each target
        t_value = self.visit(node.value)
        for t in node.targets:
            self.visit(t, t_value)
    
    def visit_Expr(self, node):
        val = self.visit(node.value)
        self.output.append(val)
