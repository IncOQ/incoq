"""Type checking and inference.

Type analysis works via abstract interpretation. Each syntactic
construct has a transfer function that monotonically maps from the
types of its inputs to the types of its outputs. Each construct also
has upper-bound constraints on the allowed types for its inputs.
The meaning of the transfer function is that, if the input values are
of the appropriate input types, then the output values are of the
appropriate output types. Likewise, the meaning of the upper-bound
constraints is that if the input values are subtypes of the upper
bounds, then execution of the construct does not cause a type error.

The abstract interpretation initializes all symbols' types to Bottom,
meaning that (so far) they have no possible values and are safe to use
in all syntactic constructs. It then iteratively (and monotonically)
increases the symbols' types by lattice-joining them with the output
type of any construct that writes to them. Once fixed point is achieved,
we know that no symbol will ever receive a value at runtime that is not
of the inferred type.

Ensuring termination requires widening, which is not currently done.

The program is well-typed if each upper bound constraint is satisfied
by the inferred types of its inputs. We do not necessarily require
programs to be well-typed.
"""


__all__ = [
    'TypeAnalysisStepper',
    'analyze_types',
]


from functools import wraps

from incoq.util.collections import OrderedSet
from incoq.mars.incast import L
from incoq.mars.types import *


class TypeAnalysisStepper(L.AdvNodeVisitor):
    
    """Run one iteration of transfer functions for all the program's
    nodes. Return the store (variable -> type mapping) and a boolean
    indicating whether the store has been changed (i.e. whether new
    information was inferred).
    """
    
    def __init__(self, store, height_limit=None):
        super().__init__()
        self.store = store
        """Mapping from symbol names to inferred types.
        Each type may only change in a monotonically increasing way.
        """
        self.height_limit = height_limit
        """Maximum height of type terms in the store. None for no limit."""
        self.illtyped = OrderedSet()
        """Nodes where the well-typedness constraints are violated."""
        self.changed = True
        """True if the last call to process() updated the store
        (or if there was no call so far).
        """
    
    def process(self, tree):
        self.changed = False
        super().process(tree)
        return self.store
    
    def update_store(self, name, type):
        old_type = self.store[name]
        new_type = old_type.join(type)
        if self.height_limit is not None:
            new_type = new_type.widen(self.height_limit)
        if new_type != old_type:
            self.changed = True
            self.store[name] = new_type
        return new_type
    
    def mark_bad(self, node):
        self.illtyped.add(node)
    
    def readonly(f):
        """Decorator for handlers for expression nodes that only
        make sense in read context.
        """
        @wraps(f)
        def wrapper(self, node, *, type=None):
            if type is not None:
                self.mark_bad(node)
            return f(self, node, type=type)
        return wrapper
    
    @readonly
    def default_expr_handler(self, node, *, type=None):
        """Expression handler that just recurses and returns Top."""
        self.generic_visit(node)
        return Top
    
    # Each visitor handler has a monotonic transfer function and
    # possibly a constraint for well-typedness.
    #
    # The behavior of each handler is described in a comment using
    # the following informal syntax.
    #
    #    X := Y          Assign the join of X and Y to X
    #    Check X <= Y    Well-typedness constraint that X is a
    #                    subtype of Y
    #    Return X        Return X as the type of an expression
    #
    # This syntax is augmented by If/Elif/Else and pattern matching,
    # e.g. iter == Set<T> introduces T as the element type of iter.
    #
    # Expression visitors have a keyword argument 'type', and can be
    # used in read or write context. In read context, type is None.
    # In write context, type is the type passed in from context. In
    # both cases the type of the expression is returned. Handlers
    # that do not tolerate write context are decorated as @readonly;
    # they still run but record a well-typedness error.
    
    # Use default handler for Return.
    
    def visit_For(self, node):
        # If iter == Bottom:
        #   target := Bottom
        # Elif iter == Set<T> or iter == List<T>:
        #   target := T
        # Else:
        #   target := Top
        #
        # Check iter <= Set<Top> or iter <= List<Top>
        t_iter = self.visit(node.iter)
        if t_iter is Bottom:
            t_target = Bottom
        elif t_iter.issmaller(Set(Top)) or t_iter.issmaller(List(Top)):
            # This might happen if we have a user-defined subtype of
            # Set/List. We need to retrieve the element type, but the
            # subtype is a different class that may not have one.
            # Unclear what to do in this case.
            if not isinstance(t_iter, (Set, List)):
                raise L.ProgramError('Cannot handle iteration over subtype '
                                     'of Set/List constructor')
            t_target = t_iter.elt
        else:
            t_target = Top
            self.mark_bad(node)
        self.update_store(node.target, type=t_target)
        self.visit(node.body)
    
    def visit_While(self, node):
        # Check test <= Bool
        t_test = self.visit(node.test)
        if not t_test.issmaller(Bool):
            self.mark_bad(node)
        self.visit(node.body)
    
    def visit_If(self, node):
        # Check test <= Bool
        t_test = self.visit(node.test)
        if not t_test.issmaller(Bool):
            self.mark_bad(node)
        self.visit(node.body)
        self.visit(node.orelse)
    
    # Use default handler for Pass, Break, Continue, and Expr.
    
    def visit_Assign(self, node):
        # target := value
        t_value = self.visit(node.value)
        self.update_store(node.target, t_value)
    
    def visit_DecompAssign(self, node):
        # If value == Bottom:
        #   vars_i := Bottom for each i
        # Elif value == Tuple<T1, ..., Tn>, n == len(vars):
        #   vars_i := T_i for each i
        # Else:
        #   vars_i := Top for each i
        #
        # Check value <= Tuple<T1, ..., Tn>
        n = len(node.vars)
        t_value = self.visit(node.value)
        if t_value is Bottom:
            t_vars = [Bottom] * n
        elif t_value.issmaller(Tuple([Top] * n)):
            # Reject subtypes, as above.
            if not isinstance(t_value, Tuple):
                raise L.ProgramError('Cannot handle decomposing assignment '
                                     'of subtype of Tuple constructor')
            t_vars = t_value.elts
        else:
            t_vars = [Top] * n
            self.mark_bad(node)
        for v, t in zip(node.vars, t_vars):
            self.update_store(v, t)
    
    def visit_SetUpdate(self, node):
        # target := Set<value>
        #
        # Check target <= Set<Top>
        t_value = self.visit(node.value)
        t_target = self.visit(node.target, type=Set(t_value))
        if not t_target.issmaller(Set(Top)):
            self.mark_bad(node)
    
    def visit_RelUpdate(self, node):
        # rel := Set<value>
        #
        # Check rel <= Set<Top>
        t_value = self.visit(node.value)
        t_rel = self.update_store(node.rel, Set(t_value))
        if not t_rel.issmaller(Set(Top)):
            self.mark_bad(node)
    
    # TODO: Requires adding map types to type algebra.
#    visit_DictAssign
#    visit_DictDelete
#    visit_MapAssign
#    visit_MapDelete
    
    @readonly
    def visit_UnaryOp(self, node, *, type=None):
        # If op == Not:
        #   Return Bool
        #   Check operand <= Bool
        # Else:
        #   Return Number
        #   Check operand <= Number
        t_operand = self.visit(node.operand)
        if isinstance(node.op, L.Not):
            t = Bool
        else:
            t = Number
        if not t_operand.issmaller(t):
            self.mark_bad(node)
        return t
    
    @readonly
    def visit_BoolOp(self, node, *, type=None):
        # Return Bool
        #
        # Check v <= Bool for v in values
        t_values = [self.visit(v) for v in node.values]
        if not all(t.issmaller(Bool) for t in t_values):
            self.mark_bad(node)
        return Bool
    
    @readonly
    def visit_BinOp(self, node, *, type=None):
        # Return join(left, right)
        t_left = self.visit(node.left)
        t_right = self.visit(node.right)
        return t_left.join(t_right)
    
    @readonly
    def visit_Compare(self, node, *, type=None):
        # Return Bool.
        self.visit(node.left)
        self.visit(node.right)
        return Bool
    
    @readonly
    def visit_IfExp(self, node, *, type=None):
        # return join(body, orelse)
        #
        # Check test <= Bool
        t_test = self.visit(node.test)
        t_body = self.visit(node.body)
        t_orelse = self.visit(node.orelse)
        if not t_test.issmaller(Bool):
            self.mark_bad(node)
        return t_body.join(t_orelse)
    
    # TODO:
    #   visit_GeneralCall
    #   visit_Call
    
    @readonly
    def visit_Num(self, node, *, type=None):
        # Return Number
        return Number
    
    @readonly
    def visit_Str(self, node, *, type=None):
        # Return String
        return String
    
    @readonly
    def visit_NameConstant(self, node, *, type=None):
        # For True/False:
        #   Return Bool
        # For None:
        #   Return Top
        if node.value in [True, False]:
            return Bool
        elif node.value is None:
            return Top
        else:
            assert()
    
    def visit_Name(self, node, *, type=None):
        # Read or update the type in the store, depending on
        # whether we're in read or write context.
        name = node.id
        if type is None:
            return self.store[name]
        else:
            return self.update_store(name, type)
    
    @readonly
    def visit_List(self, node, *, type=None):
        # Return List<join(T1, ..., Tn)>
        t_elts = [self.visit(e) for e in node.elts]
        t_elt = Bottom.join(*t_elts)
        return List(t_elt)
    
    @readonly
    def visit_Tuple(self, node, *, type=None):
        # Return Tuple<elts>
        t_elts = [self.visit(e) for e in node.elts]
        return Tuple(t_elts)
    
    # TODO: More precise behavior requires adding objects and map types
    # to the type algebra.
    
    visit_Attribute = default_expr_handler
    visit_DictLookup = default_expr_handler
    visit_MapLookup = default_expr_handler
    visit_Imgset = default_expr_handler
    
    # TODO: Comprehensions not handled yet.
    
    visit_Comp = default_expr_handler
    visit_Member = default_expr_handler
    visit_Cond = default_expr_handler
    
    # Remaining nodes require no handler.


def analyze_types(tree, store):
    """Given a mapping, store, from variable identifiers to types,
    return a modified version of the store that expands types according
    to the requirements of the program. Also return an OrderedSet of
    nodes where well-typedness is violated. Each type may only increase,
    not decrease. Each variable in the program must appear in the given
    store mapping.
    """
    store = dict(store)
    
    height_limit = 5
    limit = 20
    steps = 0
    analyzer = TypeAnalysisStepper(store, height_limit)
    while analyzer.changed:
        if steps == limit:
            print('Warning: Type analysis did not converge after '
                  '{} steps'.format(limit))
            break
        store = analyzer.process(tree)
        steps += 1
    
    return store, analyzer.illtyped
