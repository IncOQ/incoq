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
    'FunctionTypeChecker',
    'TypeAnalysisStepper',
    'analyze_types',
    'analyze_expr_type',
]


from functools import wraps

from incoq.util.collections import OrderedSet
from incoq.compiler.incast import L

from .types import *


class FunctionTypeChecker:
    
    """Determine if a function call is well-typed."""
    
    def get_sequence_elt(self, t_seq, seq_cls):
        """As in the TypeAnalysisStepper method, but instead of marking
        bad nodes, return None.
        """
        t_seq = t_seq.join(seq_cls(Bottom))
        if not t_seq.issmaller(seq_cls(Top)):
            return None
        return t_seq.elt
    
    # Mapping from name of builtin function to a pair of its expected
    # argument types and its return type.
    #
    # For polymorphic functions, define a custom handler.
    simple_builtin_funcs = {
        'Set': ([], Set(Bottom)),
    }
    
    def typeof_print(self, node, t_args):
        return Top
    
    def typeof_list(self, node, t_args):
        if len(t_args) != 1:
            return None
        
        t_elt = self.get_sequence_elt(t_args[0], Sequence)
        if t_elt is None:
            return None
        return List(t_elt)
    
    def typeof_sorted(self, node, t_args):
        if len(t_args) != 1:
            return None
        
        t_elt = self.get_sequence_elt(t_args[0], Sequence)
        if t_elt is None:
            return None
        return List(t_elt)
    
    def get_call_type(self, node, t_args):
        """Given a Call node and a list of types for each of its
        arguments, return the type of the Call's result. If the
        Call is ill-typed/unknown, return None.
        """
        assert len(t_args) == len(node.args)
        
        # See if it matches one of the simple built-in cases.
        if node.func in self.simple_builtin_funcs:
            t_params, t_result = self.simple_builtin_funcs[node.func]
            assert len(t_params) == len(t_args)
            # Check that each actual argument is a subtype of the
            # parameter types.
            for t_param, t_arg in zip(t_params, t_args):
                if not t_arg.issmaller(t_param):
                    return None
            return t_result
        
        # Otherwise, if it's a built-in that we have a handler for,
        # dispatch to it.
        handler_name = 'typeof_' + node.func
        handler = getattr(self, handler_name, None)
        if handler is not None:
            return handler(node, t_args)
        
        # Otherwise, it's unknown.
        return None


class TypeAnalysisStepper(L.AdvNodeVisitor):
    
    """Run one iteration of transfer functions for all the program's
    nodes. Return the store (variable -> type mapping) and a boolean
    indicating whether the store has been changed (i.e. whether new
    information was inferred).
    """
    
    def __init__(self, store, height_limit=None, unknown=Top,
                 fixed_vars=None):
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
        self.unknown = unknown
        """Type to use for variables not in the store. Should be Bottom,
        Top, or None. None indicates that an error should be raised for
        unknown variables.
        """
        if fixed_vars is None:
            fixed_vars = []
        self.fixed_vars = fixed_vars
        """Names of variables whose types cannot be changed by inference."""
    
    def process(self, tree):
        self.changed = False
        super().process(tree)
        return self.store
    
    def get_store(self, name):
        try:
            return self.store[name]
        except KeyError:
            if self.unknown is None:
                raise
            else:
                return self.unknown
    
    def update_store(self, name, type):
        if name in self.fixed_vars:
            return self.store[name]
        
        old_type = self.get_store(name)
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
    #    Fail            Mark an error at this node and return Top
    #
    # This syntax is augmented by If/Elif/Else and pattern matching,
    # e.g. iter == Set<T> introduces T as the element type of iter.
    # join(T1, T2) is the lattice join of T1 and T2.
    #
    # Expression visitors have a keyword argument 'type', and can be
    # used in read or write context. In read context, type is None.
    # In write context, type is the type passed in from context. In
    # both cases the type of the expression is returned. Handlers
    # that do not tolerate write context are decorated as @readonly;
    # they still run but record a well-typedness error.
    
    def get_sequence_elt(self, node, t_seq, seq_cls):
        """Given a sequence type, and a sequence type constructor
        (e.g. Sequence, List, or Set), return the element type of
        the sequence type. If the sequence type cannot safely be
        converted to the given type constructor's form (for instance
        if it is not actually a sequence), return Top and mark node
        as ill-typed.
        """
        # Join to ensure that we're looking at a type object that
        # is an instance of seq_cls, as opposed to some other type
        # object in the lattice.
        t_seq = t_seq.join(seq_cls(Bottom))
        if not t_seq.issmaller(seq_cls(Top)):
            self.mark_bad(node)
            return Top
        return t_seq.elt
    
    def get_map_keyval(self, node, t_map):
        """Given a map type, return its key and value type. If the
        given type cannot safely be converted to a map type, return
        a pair of Tops instead and mark the node as ill-typed.
        """
        t_map = t_map.join(Map(Bottom, Bottom))
        if not t_map.issmaller(Map(Top, Top)):
            self.mark_bad(node)
            return Top, Top
        return t_map.key, t_map.value
    
    def get_tuple_elts(self, node, t_tup, arity):
        """Given a tuple type, return the element types. If the given
        type cannot safely be converted to a tuple of the given arity,
        return arity many Tops, and mark node as ill-typed.
        """
        t_tup = t_tup.join(Tuple([Bottom] * arity))
        if not t_tup.issmaller(Tuple([Top] * arity)):
            self.mark_bad(node)
            return [Top] * arity
        return t_tup.elts
    
    # Use default handler for Return.
    
    def visit_For(self, node):
        # If join(iter, Sequence<Bottom>) == Sequence<T>:
        #   target := T
        # Else:
        #   target := Top
        #
        # Check iter <= Sequence<Top>
        t_iter = self.visit(node.iter)
        t_target = self.get_sequence_elt(node, t_iter, Sequence)
        self.update_store(node.target, type=t_target)
        self.visit(node.body)
    
    def visit_DecompFor(self, node):
        # If join(iter, Sequence<Tuple<Bottom, ..., Bottom>) ==
        #    Sequence<Tuple<T1, ..., Tn>>, n == len(vars):
        #   vars_i := T_i for each i
        # Else:
        #   vars_i := Top for each i
        #
        # Check iter <= Sequence<Tuple<Top, ..., Top>>
        n = len(node.vars)
        t_iter = self.visit(node.iter)
        t_target = self.get_sequence_elt(node, t_iter, Sequence)
        t_vars = self.get_tuple_elts(node, t_target, n)
        for v, t in zip(node.vars, t_vars):
            self.update_store(v, t)
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
        # If join(value, Tuple<Bottom, ..., Bottom>) ==
        #    Tuple<T1, ..., Tn>, n == len(vars):
        #   vars_i := T_i for each i
        # Else:
        #   vars_i := Top for each i
        #
        # Check value <= Tuple<Top, ..., Top>
        n = len(node.vars)
        t_value = self.visit(node.value)
        t_vars = self.get_tuple_elts(node, t_value, n)
        for v, t in zip(node.vars, t_vars):
            self.update_store(v, t)
    
    def visit_SetUpdate(self, node):
        # target := Set<value>
        # Check target <= Set<Top>
        t_value = self.visit(node.value)
        t_target = self.visit(node.target, type=Set(t_value))
        if not t_target.issmaller(Set(Top)):
            self.mark_bad(node)
    
    def visit_SetBulkUpdate(self, node):
        # If join(value, Set<Bottom>) == Set<T>:
        #   target := Set<T>
        # Else:
        #   target := Set<Top>
        #
        # Check value <= Set<Top> and target <= Set<Top>
        t_value = self.visit(node.value)
        t_elt = self.get_sequence_elt(node, t_value, Set)
        t_target = self.visit(node.target, type=Set(t_elt))
        if not (t_value.issmaller(Set(Top)) and
                t_target.issmaller(Set(Top))):
            self.mark_bad(node)
    
    def visit_SetClear(self, node):
        # target := Set<Bottom>
        # Check target <= Set<Top>
        t_target = self.visit(node.target, type=Set(Bottom))
        if not t_target.issmaller(Set(Top)):
            self.mark_bad(node)
    
    def visit_RelUpdate(self, node):
        # rel := Set<elem>
        # Check rel <= Set<Top>
        t_value = self.get_store(node.elem)
        t_rel = self.update_store(node.rel, Set(t_value))
        if not t_rel.issmaller(Set(Top)):
            self.mark_bad(node)
    
    def visit_RelClear(self, node):
        # rel := Set<Bottom>
        # Check rel <= Set<Top>
        t_rel = self.update_store(node.rel, Set(Bottom))
        if not t_rel.issmaller(Set(Top)):
            self.mark_bad(node)
    
    def visit_DictAssign(self, node):
        # target := Map<key, value>
        # Check target <= Map<Top, Top>
        t_key = self.visit(node.key)
        t_value = self.visit(node.value)
        t_target = self.visit(node.target, type=Map(t_key, t_value))
        if not t_target.issmaller(Map(Top, Top)):
            self.mark_bad(node)
    
    def visit_DictDelete(self, node):
        # target := Map<key, Bottom>
        # Check target <= Map<Top, Top>
        t_key = self.visit(node.key)
        t_target = self.visit(node.target, type=Map(t_key, Bottom))
        if not t_target.issmaller(Map(Top, Top)):
            self.mark_bad(node)
    
    def visit_DictClear(self, node):
        # target := Map<Bottom, Bottom>
        # Check target <= Map<Top, Top>
        t_target = self.visit(node.target, type=Map(Bottom, Bottom))
        if not t_target.issmaller(Map(Top, Top)):
            self.mark_bad(node)
    
    def visit_MapAssign(self, node):
        # map := Map<key, value>
        # Check map <= Map<Top, Top>
        t_key = self.get_store(node.key)
        t_value = self.get_store(node.value)
        t_map = self.update_store(node.map, Map(t_key, t_value))
        if not t_map.issmaller(Map(Top, Top)):
            self.mark_bad(node)
    
    def visit_MapDelete(self, node):
        # map := Map<key, Bottom>
        # Check map <= Map<Top, Top>
        t_key = self.get_store(node.key)
        t_map = self.update_store(node.map, Map(t_key, Bottom))
        if not t_map.issmaller(Map(Top, Top)):
            self.mark_bad(node)
    
    def visit_MapClear(self, node):
        # target := Map<Bottom, Bottom>
        # Check target <= Map<Top, Top>
        t_map = self.update_store(node.map, Map(Bottom, Bottom))
        if not t_map.issmaller(Map(Top, Top)):
            self.mark_bad(node)
    
    # Attribute handlers not implemented:
    # visit_AttrAssign
    # visit_AttrDelete 
    
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
        # Return join(body, orelse)
        # Check test <= Bool
        t_test = self.visit(node.test)
        t_body = self.visit(node.body)
        t_orelse = self.visit(node.orelse)
        if not t_test.issmaller(Bool):
            self.mark_bad(node)
        return t_body.join(t_orelse)
    
    @readonly
    def visit_GeneralCall(self, node, *, type=None):
        # Return Top
        self.generic_visit(node)
        return Top
    
    @readonly
    def visit_Call(self, node, *, type=None):
        checker = FunctionTypeChecker()
        t_args = [self.visit(a) for a in node.args]
        t_result = checker.get_call_type(node, t_args)
        if t_result is None:
            self.mark_bad(node)
            return Top
        return t_result
    
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
            return self.get_store(name)
        else:
            return self.update_store(name, type)
    
    @readonly
    def visit_List(self, node, *, type=None):
        # Return List<join(T1, ..., Tn)>
        t_elts = [self.visit(e) for e in node.elts]
        t_elt = Bottom.join(*t_elts)
        return List(t_elt)
    
    @readonly
    def visit_Set(self, node, *, type=None):
        # Return Set<join(T1, ..., Tn)>
        t_elts = [self.visit(e) for e in node.elts]
        t_elt = Bottom.join(*t_elts)
        return Set(t_elt)
    
    @readonly
    def visit_Tuple(self, node, *, type=None):
        # Return Tuple<elts>
        t_elts = [self.visit(e) for e in node.elts]
        return Tuple(t_elts)
    
    # TODO: More precise behavior requires adding objects to the
    # type algebra.
    
    visit_Attribute = default_expr_handler
    
    @readonly
    def visit_Subscript(self, node, *, type=None):
        # If value == Bottom:
        #   Return Bottom
        # Elif value == Tuple<T0, ..., Tn>:
        #   If index == Num(k) node, 0 <= k <= n:
        #     Return Tk
        #   Else:
        #     Return join(T0, ..., Tn)
        # Elif join(value, List<Bottom>) == List<T>:
        #   Return T
        # Else:
        #   Return Top
        #
        # Check value <= List<Top> or value is a Tuple
        # Check index <= Number
        t_value = self.visit(node.value)
        t_index = self.visit(node.index)
        if not t_index.issmaller(Number):
            self.mark_bad(node)
        
        # Try Tuple case first. Since we don't have a type for tuples
        # of arbitrary arity, we'll use an isinstance() check. This
        # may have to change if we add new subtypes of Tuple to the
        # lattice.
        if isinstance(t_value, Tuple):
            if (isinstance(node.index, L.Num) and
                0 <= node.index.n < len(t_value.elts)):
                return t_value.elts[node.index.n]
            else:
                return Bottom.join(*t_value.elts)
        
        # Otherwise, treat it as a list or list subtype.
        return self.get_sequence_elt(node, t_value, List)
    
    def visit_DictLookup(self, node, *, type=None):
        # If type != None:
        #   value := Map<Bottom, type>
        #
        # If join(value, Map<Bottom, Bottom>) == Map<K, V>:
        #   R = V
        # Else:
        #   R = Top
        # Return join(R, default)
        #
        # Check value <= Map<Top, Top>
        t_value = Map(Bottom, type) if type is not None else None
        t_value = self.visit(node.value, type=t_value)
        t_default = (self.visit(node.default)
                     if node.default is not None else None)
        t_value = t_value.join(Map(Bottom, Bottom))
        if not t_value.issmaller(Map(Top, Top)):
            self.mark_bad(node)
            return Top
        return t_value.value.join(t_default)
    
    visit_FirstThen = default_expr_handler
    
    @readonly
    def visit_ImgLookup(self, node, *, type=None):
        # Check rel <= Set<Top>
        # Return Set<Top>
        t_rel = self.visit(node.set)
        if not t_rel.issmaller(Set(Top)):
            self.mark_bad(node)
            return Top
        return Set(Top)
    
    @readonly
    def visit_SetFromMap(self, node, *, type=None):
        # Check map <= Map<Top, Top>
        # Return Set<Top>
        t_map = self.visit(node.map)
        if not t_map.issmaller(Map(Top, Top)):
            self.mark_bad(node)
            return Top
        return Set(Top)
    
    visit_Unwrap = default_expr_handler
    visit_Wrap = default_expr_handler
    
    visit_IsSet = default_expr_handler
    visit_HasField = default_expr_handler
    visit_IsMap = default_expr_handler
    visit_HasArity = default_expr_handler
    
    @readonly
    def visit_Query(self, node, *, type=None):
        # Return query
        return self.visit(node.query)
    
    @readonly
    def visit_Comp(self, node, *, type=None):
        # Return Set<resexp>
        for cl in node.clauses:
            self.visit(cl)
        t_resexp = self.visit(node.resexp)
        return Set(t_resexp)
    
    @readonly
    def visit_Member(self, node, *, type=None):
        # If join(iter, Set<Bottom>) == Set<T>:
        #   target := T
        # Else:
        #   target := Top
        #
        # Check iter <= Set<Top>
        t_iter = self.visit(node.iter)
        t_target = self.get_sequence_elt(node, t_iter, Set)
        self.visit(node.target, type=t_target)
    
    @readonly
    def visit_RelMember(self, node, *, type=None):
        # If join(rel, Set<Tuple<Bottom, ..., Bottom>>) ==
        #    Set<Tuple<T1, ..., Tn>>, n == len(vars):
        #   vars_i := T_i for each i
        # Else:
        #   vars_i := Top for each i
        #
        # Check rel <= Set<Tuple<Top, ..., Top>>
        n = len(node.vars)
        t_rel = self.get_store(node.rel)
        t_target = self.get_sequence_elt(node, t_rel, Set)
        t_vars = self.get_tuple_elts(node, t_target, n)
        for v, t in zip(node.vars, t_vars):
            self.update_store(v, t)
    
    @readonly
    def visit_SingMember(self, node, *, type=None):
        # If join(value, Tuple<Bottom, ..., Bottom>) ==
        #    Tuple<T1, ..., Tn>, n == len(vars):
        #   vars_i := T_i for each i
        # Else:
        #   vars_i := Top for each i
        #
        # Check value <= Tuple<Top, ..., Top>
        n = len(node.vars)
        t_value = self.visit(node.value)
        t_vars = self.get_tuple_elts(node, t_value, n)
        for v, t in zip(node.vars, t_vars):
            self.update_store(v, t)
    
    @readonly
    def visit_WithoutMember(self, node, *, type=None):
        # We don't have an easy way to propagate information into
        # the nested clause, or else we'd flow type information from
        # value to cl.target. Could fix by using the type parameter,
        # with the convention that for membership clauses, type is the
        # type of the element.
        self.generic_visit(node)
    
    @readonly
    def visit_VarsMember(self, node, *, type=None):
        # If join(iter, Set<Tuple<Bottom, ..., Bottom>>) ==
        #    Set<Tuple<T1, ..., Tn>>, n == len(vars):
        #   vars_i := T_i for each i
        # Else:
        #   vars_i := Top for each i
        #
        # Check iter <= Set<Tuple<Top, ..., Top>>
        n = len(node.vars)
        t_iter = self.visit(node.iter)
        t_target = self.get_sequence_elt(node, t_iter, Set)
        t_vars = self.get_tuple_elts(node, t_target, n)
        for v, t in zip(node.vars, t_vars):
            self.update_store(v, t)
    
    @readonly
    def visit_SetFromMapMember(self, node, *, type=None):
        # If join(rel, Set<Tuple<Bottom, ..., Bottom> ==
        #      Set<Tuple<T1, ..., Tn>> and
        #    join(map, Map<Tuple<Bottom, ..., Bottom>, Bottom> ==
        #      Map<Tuple<U1, ..., Un-1>, Un>, n == len(vars):
        #   vars_i := join(T_i, U_i) for each i
        # Else:
        #   vars_i := Top for each i
        #
        # Check map <= Map<Tuple<Bottom, ..., Bottom>, Bottom>
        # Check rel <= Set<Bottom, ..., Bottom>
        n = len(node.vars)
        t_rel = self.get_store(node.rel)
        t_relelt = self.get_sequence_elt(node, t_rel, Set)
        t_relvars = self.get_tuple_elts(node, t_relelt, n)
        t_map = self.get_store(node.map)
        t_key, t_value = self.get_map_keyval(node, t_map)
        t_keyvars = self.get_tuple_elts(node, t_key, n - 1)
        t_mapvars = list(t_keyvars) + [t_value]
        for v, t, u in zip(node.vars, t_relvars, t_mapvars):
            self.update_store(v, t.join(u))
    
    # Object domain clauses not implemented:
    # MMember
    # FMember
    # MAPMember
    # TUPMember
    
    @readonly
    def visit_Cond(self, node, *, type=None):
        self.visit(node.cond)
    
    def aggrop_helper(self, node, op, t_elt):
        # If op is count or op is sum:
        #   Check t_elt <= Number
        #   Return Number
        # Elif op is min or op is max:
        #   Return t_elt
        if isinstance(node.op, (L.Count, L.Sum)):
            if not t_elt.issmaller(Number):
                self.mark_bad(node)
                return Top
            return Number
        elif isinstance(node.op, (L.Min, L.Max)):
            return t_elt
        else:
            assert()
    
    @readonly
    def visit_Aggr(self, node, *, type=None):
        # If join(value, Set<Bottom>) == Set<T>:
        #   Return aggrop_helper(op, T)
        # Else:
        #   Return Top
        # Check value <= Set<Top>
        t_value = self.visit(node.value)
        t_elt = self.get_sequence_elt(node, t_value, Set)
        return self.aggrop_helper(node, node.op, t_elt)
    
    @readonly
    def visit_AggrRestr(self, node, *, type=None):
        # As for Aggr, except we have the additional condition:
        #
        # Check restr <= Set<Tuple<Top, ..., Top>> of arity |params|
        t_value = self.visit(node.value)
        t_elt = self.get_sequence_elt(node, t_value, Set)
        t = self.aggrop_helper(node, node.op, t_elt)
        
        n = len(node.params)
        t_restr = self.visit(node.restr)
        if not t_restr.issmaller(Set(Tuple([Top] * n))):
            self.mark_bad(node)
        
        return t
    
    # Remaining nodes require no handler.


def analyze_types(tree, store, fixed_vars=None):
    """Given a mapping from variable identifiers to types, return a
    modified version of the store that expands types according to the
    requirements of the program. Also return an OrderedSet of nodes
    where well-typedness is violated. Each type may only increase, not
    decrease. Variables not appearing in the store mapping are assumed
    to be Bottom.
    """
    store = dict(store)
    
    height_limit = 5
    limit = 20
    steps = 0
    analyzer = TypeAnalysisStepper(store, height_limit, unknown=Bottom,
                                   fixed_vars=fixed_vars)
    while analyzer.changed:
        if steps == limit:
            print('Warning: Type analysis did not converge after '
                  '{} steps'.format(limit))
            break
        store = analyzer.process(tree)
        steps += 1
    
    return store, analyzer.illtyped


def analyze_expr_type(tree, store):
    """Given an expression node, return its type evaluation under the
    given type store.
    """
    store = dict(store)
    height_limit = 5
    
    # Bypass TypeAnalysisStepper's process() method since it discards
    # type info. The given tree should not be a statement node.
    class Analyzer(TypeAnalysisStepper):
        process = L.AdvNodeVisitor.process
    
    type = Analyzer.run(tree, store, height_limit, unknown=Top)
    return type
