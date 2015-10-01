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
    'TypeAnalyzer',
]


from incoq.util.collections import OrderedSet
from incoq.mars.incast import L
from incoq.mars.types import *


class TypeAnalyzer(L.AdvNodeVisitor):
    
    def __init__(self, store):
        super().__init__()
        self.store = store
        """Mapping from symbol names to inferred types.
        Each type may only change in a monotonically increasing way.
        """
        self.errors = OrderedSet()
        """Nodes where the well-typedness constraints are violated."""
    
    def process(self, tree):
        super().process(tree)
        return self.store
    
    def update_store(self, name, type):
        self.store[name] = self.store[name].join(type)
    
    def mark_error(self, node):
        self.errors.add(node)
    
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
    # Some visitor handlers take a keyword argument 'type', which is
    # an input type passed in from the node's context. Handlers may
    # use the presence of this keyword argument to distinguish read
    # and write context.
    
    # Use default handler for Return.
    
    def visit_For(self, node):
        # If iter == Bottom:
        #   target := Bottom
        # Elif iter == Set<T>:
        #   target := T
        # Else:
        #   target := Top
        #
        # Check iter <= Set<Top>
        t_iter = self.visit(node.iter)
        if t_iter is Bottom:
            t_target = Bottom
        elif t_iter.issmaller(Set(Top)):
            # This might happen if we have a user-defined subtype of
            # Set. We need to retrieve the element type, but the subtype
            # is a different class that may not have one. Unclear what
            # to do in this case.
            if not isinstance(t_iter, Set):
                raise L.ProgramError('Cannot handle iteration over subtype '
                                     'of Set constructor')
            t_target = t_iter.elt
        else:
            t_target = Top
            self.mark_error(node)
        self.update_store(node.target, type=t_target)
        self.visit(node.body)
    
    def visit_While(self, node):
        # Check test <= Bool
        t_test = self.visit(node.test)
        if not t_test.issmaller(Bool):
            self.mark_error(node)
        self.visit(node.body)
    
    def visit_If(self, node):
        # Check test <= Bool
        t_test = self.visit(node.test)
        if not t_test.issmaller(Bool):
            self.mark_error(node)
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
            self.mark_error(node)
        for v, t in zip(node.vars, t_vars):
            self.update_store(v, t)
    
#    def visit_SetUpdate(self, node):
#        pass
    
#    def visit_RelUpdate(self, node):
#        pass
    
    # TODO:
    #   visit_DictAssign
    #   visit_DictDelete
    #   visit_MapAssign
    #   visit_MapDelete
    
    def visit_UnaryOp(self, node):
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
            self.mark_error(node)
        return t
    
    def visit_BoolOp(self, node):
        # Return Bool
        #
        # Check v <= Bool for v in values
        t_values = [self.visit(v) for v in node.values]
        if not all(t.issmaller(Bool) for t in t_values):
            self.mark_error(node)
        return Bool
    
    def visit_BinOp(self, node):
        # Return join(left, right)
        t_left = self.visit(node.left)
        t_right = self.visit(node.right)
        return t_left.join(t_right)
    
    def visit_Compare(self, node):
        # Return Bool.
        self.visit(node.left)
        self.visit(node.right)
        return Bool
    
    def visit_IfExp(self, node):
        # return join(body, orelse)
        #
        # Check test <= Bool
        t_test = self.visit(node.test)
        t_body = self.visit(node.body)
        t_orelse = self.visit(node.orelse)
        if not t_test.issmaller(Bool):
            self.mark_error(node)
        return t_body.join(t_orelse)
    
    # TODO:
    #   visit_GeneralCall
    #   visit_Call
    
    def visit_Num(self, node):
        # Return Number
        return Number
    
    def visit_Str(self, node):
        # Return String
        return String
    
    def visit_NameConstant(self, node):
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
            self.update_store(name, type)
    
    # TODO:
    #   visit_List
    
    def visit_Tuple(self, node):
        # Return Tuple<elts>
        t_elts = [self.visit(e) for e in node.elts]
        return Tuple(t_elts)
    
    # TODO:
    #   visit_Attribute
    #   visit_DictLookup
    #   visit_MapLookup
    #   visit_Imgset
    #   visit_Comp
    #   visit_Member
    #   visit_Cond
    
    # Remaining nodes require no handler.
