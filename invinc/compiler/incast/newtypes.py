"""Type analysis."""


__all__ = [
    'FrozenDictField',
    
    'Type',
    'toptype',
    'bottomtype',
    'PrimitiveType',
    'booltype',
    'numbertype',
    'strtype',
    'SeqType',
    'TupleType',
    'ListType',
    'SetType',
    'DictType',
    'ObjType',
    'TypeVar',
    
    'eval_typestr',
    
    'TypedUnparser',
    'unparse_structast_typed',
    
    'TypeAnalysisFailure',
    'analyze_types',
]


from numbers import Number
from simplestruct import Struct, Field, TypedField

from invinc.util.seq import pairs
from invinc.util.collections import frozendict

from .nodes import expr, Not, Index, Num, expr
from .structconv import (NodeVisitor, NodeTransformer,
                         Unparser, export_structast)
from .error import ProgramError
from .util import NameGenerator


class FrozenDictField(TypedField):
    
    """Field for frozendicts, with coercion from ordinary dicts."""
    
    def __init__(self, keytype=None, valuetype=None):
        super().__init__(frozendict)
        self.keytype = keytype
        self.valuetype = valuetype
    
    def copy(self):
        return type(self)(self.keytype, self.valuetype)
    
    def check(self, inst, value):
        if (self.keytype is not None and
            not all(isinstance(k, self.keytype) for k in value.keys())):
            raise TypeError('Key with bad type')
        if (self.valuetype is not None and
            not all(isinstance(v, self.valuetype) for v in value.values())):
            raise TypeError('Value with bad type')
    
    def normalize(self, inst, value):
        if not isinstance(value, frozendict):
            return frozendict(value)
        return value


class Type(Struct):
    
    def issubtype(self, other):
        """Return true if this type is a (non-strict) subtype of
        the other.
        """
        if self is bottomtype or other is toptype:
            return True
        elif self == other:
            return True
        elif type(self) == type(other):
            return self.issubtype_helper(other)
        else:
            return False
    
    def issubtype_helper(self, other):
        return False
    
    def matches(self, other):
        """True if this type and other have the same functor symbol
        and arity.
        """
        if type(self) == type(other):
            return self.matches_helper(other)
        else:
            return False
    
    def matches_helper(self, other):
        return True
    
    def match_against(self, other):
        """Return constraints for self <= other to hold, when
        self matches other. Return value is a list of constraints
        lhs <= rhs each represented as a pair (lhs, rhs).
        """
        assert self.matches(other)
        return self.match_against_helper(other)
    
    def match_against_helper(self, other):
        return []
    
    def join(self, *others, inverted=False):
        """Take the join (in the lattice sense) with one or more
        other types, returning a new type.
        
        If inverted is True, take the meet instead.
        """
        t = self
        for o in others:
            t = t.join_one(o, inverted=inverted)
        return t
    
    def join_one(self, other, *, inverted=False):
        top, bottom = toptype, bottomtype
        if inverted:
            top, bottom = bottom, top
        
        if top in [self, other]:
            return top
        elif self is bottom:
            return other
        elif other is bottom:
            return self
        # Neither top nor bottom.
        elif self == other:
            return self
        elif type(self) == type(other):
            return self.join_helper(other, inverted=inverted)
        else:
            return top
    
    def join_helper(self, other, *, inverted=False):
        """Join with one other type of the same class as this one.
        If inverted use meet instead.
        """
        return toptype if not inverted else bottomtype
    
    def meet(self, *others, inverted=False):
        """Take the lattice meet with one or more other types,
        returning a new type."""
        return self.join(*others, inverted=inverted)
    
    def expand(self, store):
        """Expand a type expression, given a typevar store
        (a mapping from typevar names to ground type expressions).
        """
        return self

class TopTypeClass(Type):
    """No type info."""
    
    singleton = None
    
    def __new__(cls):
        if cls.singleton is None:
            cls.singleton = super().__new__(cls)
        return cls.singleton
    
    def __str__(self):
        return 'Top'
toptype = TopTypeClass()

class BottomTypeClass(Type):
    """Conflicting type info."""
    
    singleton = None
    
    def __new__(cls):
        if cls.singleton is None:
            cls.singleton = super().__new__(cls)
        return cls.singleton
    
    def __str__(self):
        return 'Bottom'
bottomtype = BottomTypeClass()

class PrimitiveType(Type):
    t = TypedField(type)
    
    def __str__(self):
        return self.t.__name__
booltype = PrimitiveType(bool)
numbertype = PrimitiveType(Number)
strtype = PrimitiveType(str)

class TupleType(Type):
    ets = TypedField(Type, seq=True)
    
    def __str__(self):
        return '(' + ', '.join(str(et) for et in self.ets) + ')'
    
    def issubtype_helper(self, other):
        if len(self.ets) != len(other.ets):
            return False
        return all(et1.issubtype(et2)
                   for et1, et2 in zip(self.ets, other.ets))
    
    def matches_helper(self, other):
        return len(self.ets) == len(other.ets)
    
    def match_against_helper(self, other):
        return [(et1, et2) for et1, et2 in zip(self.ets, other.ets)]
    
    def join_helper(self, other, *, inverted=False):
        top = toptype if not inverted else bottomtype
        if len(self.ets) != len(other.ets):
            return top
        new_ets = [et1.join(et2, inverted=inverted)
                   for et1, et2 in zip(self.ets, other.ets)]
        return self._replace(ets=new_ets)
    
    def expand(self, store):
        new_ets = [et.expand(store) for et in self.ets]
        return self._replace(ets=new_ets)

class SeqType(Type):
    et = TypedField(Type)
    brackets = '??'
    
    def __str__(self):
        return self.brackets[0] + str(self.et) + self.brackets[1]
    
    def issubtype_helper(self, other):
        return self.et.issubtype(other.et)
    
    def join_helper(self, other, inverted=False):
        new_et = self.et.join(other.et, inverted=inverted)
        return self._replace(et=new_et)
    
    def match_against_helper(self, other):
        return [(self.et, other.et)]
    
    def expand(self, store):
        new_et = self.et.expand(store)
        return self._replace(et=new_et)

class ListType(SeqType):
    _inherit_fields = True
    brackets = '[]'

class SetType(SeqType):
    _inherit_fields = True
    brackets = '{}'

class DictType(Type):
    kt = TypedField(Type)
    vt = TypedField(Type)
    
    def __str__(self): 
        return '{' + str(self.kt) + ': ' + str(self.vt) + '}'
    
    def issubtype_helper(self, other):
        # Contravariant keys.
        return (other.kt.issubtype(self.kt) and
                self.vt.issubtype(other.vt))
    
    def join_helper(self, other, *, inverted=True):
        # Note that key types are contravariant, so we flip inverted.
        new_kt = self.kt.join(other.kt, inverted=not inverted)
        new_vt = self.vt.join(other.vt, inverted=inverted)
        return self._replace(kt=new_kt, vt=new_vt)
    
    def match_against_helper(self, other):
        # Flip key.
        return [(other.kt, self.kt), (self.vt, other.vt)]
    
    def expand(self, store):
        new_kt = self.kt.expand(store)
        new_vt = self.vt.expand(store)
        return self._replace(kt=new_kt, vt=new_vt)

class ObjType(Type):
    name = TypedField(str)
    
    def matches_helper(self, other):
        return False
    
    def __str__(self):
        return self.name

class TypeVar(Type):
    name = TypedField(str)
    
    def __str__(self):
        return '<' + self.name + '>'
    
    def illegalop(self, other):
        raise NotImplementedError('Illegal operation for non-ground '
                                  'type expression')
    
    issubtype = illegalop
    matches = illegalop
    match_against = illegalop
    join = illegalop
    
    def expand(self, store):
        return store[self.name]


def eval_typestr(s):
    """eval() a string representing a type expression."""
    ns = {k: v for k, v in globals().items()
               if isinstance(v, Type) or
                  (isinstance(v, type) and issubclass(v, Type))}
    return eval(s, ns)


class TypedUnparser(Unparser):
    
    """Unparser that includes type information for all expression
    nodes.
    """
    
    def dispatch(self, tree):
        show_type = isinstance(tree, expr) and tree.type is not None
        
        if show_type:
            self.write('(')
        super().dispatch(tree)
        if show_type:
            self.write(' : ' + str(tree.type) + ')')

def unparse_structast_typed(tree):
    """As structconv.unparse_structast(), but with type info."""
    return TypedUnparser.to_source(tree)


def add_fresh_typevars(tree):
    """Add fresh typevars to all expression nodes."""
    namegen = NameGenerator('_T{}')
    tvars = set()
    class Trans(NodeTransformer):
        def visit(self, node):
            node = super().visit(node)
            if isinstance(node, expr):
                tname = next(namegen)
                node = node._replace(type=TypeVar(tname))
                tvars.add(tname)
            return node
    return Trans.run(tree), tvars

def subst_typevars(tree, store):
    """Substitute typevars into all expression nodes."""
    class Trans(NodeTransformer):
        def visit(self, node):
            node = super().visit(node)
            if isinstance(node, expr):
                assert isinstance(node.type, TypeVar)
                node = node._replace(type=store[node.type.name])
            return node
    return Trans.run(tree)


class TypeAnalysisFailure(ProgramError):
    
    def __init__(self, node, constraint, store):
        self.node = node
        self.constraint = constraint
        self.store = store
    
    def __str__(self):
        lhs, rhs = self.constraint
        return ('Type analysis failed on constraint {} <= {} '
                '(expanded form: {} <= {})'.format(
                lhs, rhs, lhs.expand(self.store), rhs.expand(self.store)))

def apply_constraint(store, lower, upper, node=None):
    """Apply constraints to a typevar store. The store is modified
    in-place. If at any point the constraints become unsatisfiable,
    raise TypeAnalysisFailure.
    
    Types of variables and expression nodes are held in the store.
    Each constraint has form lhs <= rhs. There are three cases:
    
      1) rhs is a typevar: this typevar is updated to be the
         join of the expansions of lhs and rhs.
    
      2) the expansions of lhs and rhs (with respect to the
         current store) have compatible functor symbols/arities:
         new constraints are generated/applied for corresponding
         subterms, respecting variance.
    
      3) otherwise: if the expansions of the lhs and rhs do not
         satisfy the subtype relation, raise TypeAnalysisFailure.
    """
    lhs = lower.expand(store)
    rhs = upper.expand(store)
    # Case 1.
    if isinstance(upper, TypeVar):
        new = lhs.join(rhs)
        store[upper.name] = new
    # Case 2.
    elif lhs.matches(rhs):
        # We don't want to expand away typevars in the
        # new smaller constraints. Only expand a typevar
        # if it is the top-level term on the left-hand side
        # (the right hand side case is handled above).
        if isinstance(lower, TypeVar):
            lower = store[lower.name]
        constrs = lower.match_against(upper)
        for c_lhs, c_rhs in constrs:
            apply_constraint(store, c_lhs, c_rhs, node=node)
    # Case 3.
    else:
        if not lhs.issubtype(rhs):
            raise TypeAnalysisFailure(node, (lower, upper), store)


class ConstraintGenerator(NodeVisitor):
    
    """Generates constraints over typevars based on AST."""
    
    def __init__(self, objtypes=None):
        super().__init__()
        if objtypes is None:
            self.objtypes = {}
        self.objtypes = objtypes
    
    def process(self, tree):
        self.constrs = set()
        super().process(tree)
        return self.constrs
    
    def add(self, node, *terms):
        # t1 <= ..., <= tn
        for lhs, rhs in pairs(terms):
            self.constrs.add((node, lhs, rhs))
    
    def addeqs(self, node, *terms):
        # t1 = ... = tn
        for lhs, rhs in pairs(terms):
            self.constrs.add((node, lhs, rhs))
            self.constrs.add((node, rhs, lhs))
    
    # Statements.
    
    def visit_Assign(self, node):
        # rhs <= lhs
        self.generic_visit(node)
        for t in node.targets:
            self.add(node, node.value.type, t.type)
    
    def visit_SetUpdate(self, node):
        # set<elem> <= target <= set<top>
        self.generic_visit(node)
        self.add(node, SetType(node.elem.type),
                 node.target.type, SetType(toptype))
    
    def visit_MacroSetUpdate(self, node):
        # set<bottom> <= target <= set<top>
        # if other is present:
        #    set<bottom> <= other <= target
        self.generic_visit(node)
        self.add(node, SetType(bottomtype),
                 node.target.type, SetType(toptype))
        if node.other is not None:
            self.add(node, SetType(bottomtype),
                     node.other.type, node.target.type)
    
    visit_RCSetRefUpdate = visit_SetUpdate
    
    # Expressions.
    
    def visit_BoolOp(self, node):
        # bool = node = operands
        terms = [node.type] + [v.type for v in node.values]
        self.addeqs(node, booltype, *terms)
    
    def visit_BinOp(self, node):
        # number = node = left = right
        terms = [node.type, node.left.type, node.right.type]
        self.addeqs(node, numbertype, *terms)
    
    def visit_UnaryOp(self, node):
        # if "not":
        #    bool = node = operand
        # otherwise:
        #    number = node = operand
        t = booltype if isinstance(node.op, Not) else numbertype
        terms = [node.type, node.operand.type]
        self.addeqs(node, t, *terms)
    
    # no constraints for Lambda
    
    def visit_IfExp(self, node):
        # truepart <= node
        # falsepart <= node
        # cond = bool
        self.add(node, node.body.type, node.type)
        self.add(node, node.orelse.type, node.type)
        self.addeqs(node, booltype, node.test.type)
    
    def visit_Str(self, node):
        # node = str
        self.addeqs(node, node.type, strtype)
    
    def visit_Name(self, node):
        # node = vartype
        self.addeqs(node, node.type, TypeVar(node.id))
    
    def visit_Tuple(self, node):
        # node = tuple<elt1, ..., eltn>
        self.generic_visit(node)
        t = TupleType([elt.type for elt in node.elts])
        self.addeqs(node, node.type, t)
     
#    # Expressions.
#    
#    
#    # No type info.
#    def visit_Lambda(self, node, ctxtype=toptype):
#        return self.generic_visit(node)
#    
#    # Expression is the same as the type of the two branches,
#    # or None if they disagree. No propagation is done between
#    # the branches. The condition is a bool.
#    def visit_IfExp(self, node, ctxtype=toptype):
#        test = self.visit(node.test, booltype)
#        body = self.visit(node.body, ctxtype)
#        orelse = self.visit(node.orelse, ctxtype)
#        t = toptype.unify(body.type, orelse.type)
#        return node._replace(test=test, body=body, orelse=orelse, type=t)
#    
#    # A set literal has set type {E} where E is the type of all
#    # the elements. E is None if the elements are heterogeneously
#    # typed.
#    #
#    # The same pattern is applied analogously to other literals.
#    #
#    # Comprehensions have their collection type, except that
#    # generators have no type.
#    
#    def visit_Dict(self, node, ctxtype=toptype):
#        # Get the context key/value types and recurse.
#        ckt = cvt = toptype
#        if isinstance(ctxtype, DictType):
#            ckt, cvt = ctxtype
#        keys = [self.visit(k, ckt) for k in node.keys]
#        values = [self.visit(v, cvt) for v in node.values]
#        # Get the actual inferred key/value types.
#        t = DictType(ckt.unify(*(k.type for k in keys)),
#                     cvt.unify(*(v.type for v in values)))
#        t = t.unify(ctxtype)
#        return node._replace(keys=keys, values=values, type=t)
#    
#    def seq_helper(self, node, ctxtype, seqtype):
#        """Helper for homogenously typed sequences."""
#        cet = toptype
#        if isinstance(ctxtype, seqtype):
#            cet, = ctxtype
#        elts = [self.visit(e, cet) for e in node.elts]
#        t = seqtype(cet.unify(*(e.type for e in elts)))
#        t = t.unify(ctxtype)
#        return node._replace(elts=elts, type=t)
#    
#    def visit_Set(self, node, ctxtype=toptype):
#        return self.seq_helper(node, toptype, SetType)
#    
#    def seqcomp_helper(self, node, ctxtype, seqtype):
#        """Helper for sequence comprehensions."""
#        cet = toptype
#        if isinstance(ctxtype, seqtype):
#            cet, = ctxtype
#        elt = self.visit(node.elt, cet)
#        generators = self.visit(node.generators)
#        t = seqtype(elt.type)
#        t = t.unify(ctxtype)
#        return node._replace(elt=elt, generators=generators, type=t)
#    
#    def visit_ListComp(self, node, ctxtype=toptype):
#        return self.seqcomp_helper(node, ctxtype, ListType)
#    
#    def visit_SetComp(self, node, ctxtype=toptype):
#        return self.seqcomp_helper(node, ctxtype, SetType)
#    
#    def visit_DictComp(self, node, ctxtype=toptype):
#        ckt = cvt = toptype
#        if isinstance(ctxtype, DictType):
#            ckt, cvt = ctxtype
#        key = self.visit(node.key, vkt)
#        value = self.visit(node.value, cvt)
#        generators = self.visit(node.generators)
#        t = DictType(key.type, value.type)
#        t = t.unify(ctxtype)
#        return node._replace(key=key, value=value,
#                             generators=generators, type=t)
#    
#    # No type info.
#    def visit_GeneratorExp(self, node, ctxtype=toptype):
#        return self.generic_visit(node)
#    
#    def visit_Yield(self, node, ctxtype=toptype):
#        node = self.generic_visit(node, ctxtype)
#        return node._replace(type=node.value.type)
#    
#    def visit_YieldFrom(self, node, ctxtype=toptype):
#        node = self.generic_visit(node, ctxtype)
#        return node._replace(type=node.value.type)
#    
#    # Comparison operators have boolean type.
#    def visit_Compare(self, node, ctxtype=toptype):
#        ### TODO: Add context type passing based on what
#        ### operator is used.
#        node = self.generic_visit(node)
#        t = ctxtype.unify(booltype)
#        return node._replace(type=t)
#    
#    ### TODO: Special case
#    def visit_Call(self, node, ctxtype=toptype):
#        node = self.generic_visit(node)
#        return node._replace(type=toptype)
#    
#    def visit_Num(self, node, ctxtype=toptype):
#        t = ctxtype.unify(numbertype)
#        return node._replace(type=t)
#    
#    def visit_Str(self, node, ctxtype=toptype):
#        t = ctxtype.unify(strtype)
#        return node._replace(type=t)
#    
#    # Untyped.
#    def visit_Bytes(self, node, ctxtype=toptype):
#        return node
#    
#    # True/False are booleans, None itself is untyped.
#    def visit_NameConstant(self, node, ctxtype=toptype):
#        node = self.generic_visit(node)
#        if node.value in [True, False]:
#            t = booltype
#        elif node.value is None:
#            t = toptype
#        else:
#            assert()
#        t = t.unify(ctxtype)
#        return node._replace(type=t)
#    
#    # Untyped.
#    def visit_Ellipsis(self, node, ctxtype=toptype):
#        return self.generic_visit(node)
#    
#    # The object must either have top type or else have the type
#    # of an object that defines the requested attribute.
#    def visit_Attribute(self, node, ctxtype=toptype):
#        ### TODO: Special cases for methods, e.g. ".elements()".
#        
#        # We can't generate the object type from its attribute type,
#        # so no context info to pass along.
#        value = self.visit(node.value)
#        vt = value.type
#        if vt is toptype:
#            t = toptype
#        elif isinstance(vt, ObjType):
#            attrs = self.objtypes[vt.name]
#            t = attrs.get(node.attr, bottomtype)
#        else:
#            t = bottomtype
#        t = t.unify(ctxtype)
#        return node._replace(value=value, type=t)
#    
#    # Subscripting a list or dict gives the element or value
#    # type respectively. Subscripting a tuple where the index
#    # is an integer constant gives the element type.
#    # Subscripting top gives top. Anything else is bottom.
#    def visit_Subscript(self, node, ctxtype=toptype):
#        # We can't generate the list/dict type from its
#        # element/value type, so no context info to pass along.
#        value = self.visit(node.value)
#        slice = self.visit(node.slice)
#        vt = value.type
#        if isinstance(vt, ListType):
#            t = vt.et
#        elif isinstance(vt, DictType):
#            t = vt.vt
#        elif isinstance(vt, TupleType):
#            if isinstance(slice, Index) and isinstance(slice.value, Num):
#                if 0 <= slice.value.n < len(vt.ets):
#                    t = vt.ets[slice.value.n]
#        elif vt is toptype:
#            t = toptype
#        else:
#            t = bottomtype
#        t = t.unify(ctxtype)
#        return node._replace(value=value, slice=slice, type=t)
#    
#    def visit_Starred(self, node, ctxtype=toptype):
#        node = self.generic_visit(node, ctxtype)
#        return node._replace(type=node.value.type)
#    
#    def visit_Name(self, node, ctxtype=toptype):
#        node = self.generic_visit(node)
#        t = self.vartypes.get(node.id, toptype)
#        t = t.unify(ctxtype)
#        self.vartypes[node.id] = t
#        return node._replace(type=t)
#    
#    def visit_List(self, node, ctxtype=toptype):
#        return self.seq_helper(node, toptype, ListType)
#    
#    def visit_Tuple(self, node, ctxtype=toptype):
#        # Can't use seq_helper() because tuples are
#        # hetereogenously typed.
#        nelems = len(node.elts)
#        cets = [toptype] * nelems
#        if isinstance(ctxtype, TupleType) and len(ctxtype.ets) == nelems:
#            cets = ctxtype.ets
#        elts = [self.visit(e, cet) for e, cet in zip(node.elts, cets)]
#        t = TupleType([elt.type for elt in elts])
#        t = t.unify(ctxtype)
#        return node._replace(elts=elts, type=t)
#    
#    # IncAST nodes follow.
#    
#    def visit_IsEmpty(self, node, ctxtype=toptype):
#        target = self.visit(node.target, SetType(toptype))
#        t = ctxtype.unify(booltype)
#        return node._replace(target=target, type=t)
#    
#    def visit_GetRef(self, node, ctxtype=toptype):
#        target = self.visit(node.target, SetType(toptype))
#        elem = self.visit(node.elem)
#        t = ctxtype.unify(numbertype)
#        return node._replace(target=target, elem=elem, type=t)
#    
#    def visit_Lookup(self, node, ctxtype=toptype):
#        target = self.visit(node.target, DictType(toptype, ctxtype))
#        key = self.visit(node.key)
#        default = self.visit(node.default, ctxtype)
#        t = ctxtype.unify(default.type)
#        return node._replace(target=target, key=key, default=default, type=t)
#    
#    def visit_ImgLookup(self, node, ctxtype=toptype):
#        t = ctxtype.unify(SetType(toptype))
#        key = self.visit(node.key)
#        target = self.visit(node.target, DictType(key.type, t))
#        if (isinstance(target.type, DictType) and
#            isinstance(target.type.vt, SetType)):
#            t = t.unify(target.type.vt.et)
#        return node._replace(target=target, key=key, type=t)
#    
#    visit_RCImgLookup = visit_ImgLookup
#    
#    def visit_SMLookup(self, node, ctxtype=toptype):
#        t = ctxtype
#        key = self.visit(node.key)
#        target = self.visit(node.target, SetType(t))
#        if (isinstance(target.type, DictType) and
#            isinstance(target.type.vt, SetType)):
#            t = t.unify(target.type.vt.et)
#        return node._replace(target=target, key=key, type=t)
#    
#    def visit_DemQuery(self, node, ctxtype=toptype):
#        args = self.visit(node.args)
#        value = self.visit(node.value, ctxtype)
#        t = ctxtype.unify(value.type)
#        return node._replace(args=args, value=value, type=t)
#    
#    def visit_NoDemQuery(self, node, ctxtype=toptype):
#        return self.generic_visit(node, ctxtype)
#    
#    def visit_SetMatch(self, node, ctxtype=toptype):
#        t = ctxtype.unify(SetType(toptype))
#        key = self.visit(node.key)
#        target = self.visit(node.target, t)
#        return node._replace(target=target, key=key, type=t)
#    
#    def visit_DeltaMatch(self, node, ctxtype=toptype):
#        t = ctxtype.unify(SetType(toptype))
#        elem = self.visit(node.elem)
#        target = self.visit(node.target, t)
#        return node._replace(target=target, elem=elem, type=t)
#    
#    def visit_Enumerator(self, node, ctxtype=toptype):
#        iter = self.visit(node.iter)
#        it = iter.type
#        tt = toptype
#        if isinstance(it, SetType):
#            tt = it.et
#        target = self.visit(node.target, tt)
#        return node._replace(target=target, iter=iter)
#    
#    def visit_Comp(self, node, ctxtype=toptype):
#        cet = toptype
#        if isinstance(ctxtype, SetType):
#            cet, = ctxtype
#        clauses = ()
#        for cl in node.clauses:
#            t = booltype if isinstance(cl, expr) else toptype
#            cl = self.visit(cl, t)
#            clauses += (cl,)
#        resexp = self.visit(node.resexp, cet)
#        t = ctxtype.unify(resexp.type)
#        return node._replace(resexp=resexp, clauses=clauses, type=t)
#    
#    def visit_Aggregate(self, node, ctxtype=toptype):
#        if node.op == 'count':
#            t = numbertype
#            at = toptype
#        elif node.op == 'sum':
#            t = at = numbertype
#        elif node.op in ['min', 'max']:
#            t = ctxtype
#            at = SetType(t)
#        else:
#            assert()
#        value = self.visit(node.value, at)
#        t = t.unify(ctxtype)
#        if node.op in ['min', 'max'] and isinstance(value.type, SetType):
#            t = t.unify(value.type.et)
#        return node._replace(value=value, type=t)

def analyze_types(tree, vartypes=None, objtypes=None):
    store = dict(vartypes)
    
    # Fixpoint with bailout.
    changed = True
    count = 0
    while changed and count < 10:
        oldstore = store.copy()
        tree = TypeAnalyzer.run(tree, store, objtypes)
        changed = store != oldstore
        count += 1
    print('Iterated type analysis {} times'.format(count))
    return tree, vartypes
