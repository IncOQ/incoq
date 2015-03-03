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

from .nodes import (AST, expr, Not, Index, Num, Enumerator,
                    Eq, NotEq, Lt, LtE, Gt, GtE, Is, IsNot, In, NotIn)
from .structconv import (NodeVisitor, NodeTransformer,
                         Unparser, export_structast)
from .error import ProgramError
from .util import NameGenerator, VarsFinder


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
    
    # Contravariant key types were also considered as a possibility.
    # This would affect each of the helpers below.
    
    def __str__(self): 
        return '{' + str(self.kt) + ': ' + str(self.vt) + '}'
    
    def issubtype_helper(self, other):
        return (self.kt.issubtype(other.kt) and
                self.vt.issubtype(other.vt))
    
    def join_helper(self, other, *, inverted=True):
        new_kt = self.kt.join(other.kt, inverted=inverted)
        new_vt = self.vt.join(other.vt, inverted=inverted)
        return self._replace(kt=new_kt, vt=new_vt)
    
    def match_against_helper(self, other):
        return [(self.kt, self.kt), (other.vt, other.vt)]
    
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
        t = store[self.name]
        assert isinstance(t, Type)
        return t


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
        super().__init__(node=node)
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
    assert isinstance(lower, Type) and isinstance(upper, Type)
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


class BaseConstraintGenerator:
    
    def add(self, node, *terms):
        # t1 <= ..., <= tn
        assert isinstance(node, AST)
        assert all(isinstance(t, Type) for t in terms)
        for lhs, rhs in pairs(terms):
            self.constrs.add((node, lhs, rhs))
    
    def addeqs(self, node, *terms):
        # t1 = ... = tn
        for lhs, rhs in pairs(terms):
            self.constrs.add((node, lhs, rhs))
            self.constrs.add((node, rhs, lhs))


class ConstraintGenerator(NodeVisitor, BaseConstraintGenerator):
    
    """Generates constraints over typevars based on AST."""
    
    def process(self, tree):
        self.constrs = set()
        super().process(tree)
        return self.constrs
    
    # Statements.
    
    def visit_Assign(self, node):
        # rhs <= lhs
        self.generic_visit(node)
        for t in node.targets:
            self.add(node, node.value.type, t.type)
    
    def visit_For(self, node):
        # set<bottom> <= iter <= set<target>
        self.generic_visit(node)
        self.add(node, SetType(bottomtype),
                 node.iter.type, SetType(node.target.type))
    
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
    
    def seq_helper(self, node, seqtype):
        # seq<elt> <= node for each elt
        self.generic_visit(node)
        for elt in node.elts:
            self.add(node, seqtype(elt.type), node.type)
    
    def seqcomp_helper(self, node, seqtype):
        # seq<elt> = node
        self.generic_visit(node)
        self.addeqs(node, node.type, seqtype(node.elt.type))
    
    def visit_BoolOp(self, node):
        # bool = node = operands
        terms = [node.type] + [v.type for v in node.values]
        self.addeqs(node, booltype, *terms)
    
    def visit_BinOp(self, node):
        # number = node = left = right
        self.generic_visit(node)
        terms = [node.type, node.left.type, node.right.type]
        self.addeqs(node, numbertype, *terms)
    
    def visit_UnaryOp(self, node):
        # if "not":
        #    bool = node = operand
        # otherwise:
        #    number = node = operand
        self.generic_visit(node)
        t = booltype if isinstance(node.op, Not) else numbertype
        terms = [node.type, node.operand.type]
        self.addeqs(node, t, *terms)
    
    # No constraints for Lambda.
    
    def visit_IfExp(self, node):
        # truepart <= node
        # falsepart <= node
        # cond = bool
        self.generic_visit(node)
        self.add(node, node.body.type, node.type)
        self.add(node, node.orelse.type, node.type)
        self.addeqs(node, booltype, node.test.type)
    
    def visit_Dict(self, node):
        # dict<bottom, bottom> <= node <= dict<top, top>
        # dict<k, v> <= node for each k, v pair
        self.generic_visit(node)
        self.add(node, DictType(bottomtype, bottomtype),
                 node.type, DictType(toptype, toptype))
        for k, v in zip(node.keys, node.values):
            self.add(node, DictType(k.type, v.type), node.type)
    
    def visit_Set(self, node):
        self.seq_helper(node, SetType)
    
    def visit_ListComp(self, node):
        self.seqcomp_helper(node, ListType)
    
    def visit_SetComp(self, node):
        self.seqcomp_helper(node, SetType)
    
    def visit_DictComp(self, node):
        # dict<key, value> = node
        self.generic_visit(node)
        self.addeqs(node, node.type, DictType(node.key, node.value))
    
    # No constraints for GeneratorExp, Yield, or YieldFrom.
    
    def compare_helper(self, node, op, lhs, rhs):
        # if arithmetic:
        #    number = node = lhs = rhs
        # otherwise if (negation of) equality/identity:
        #    node = bool
        #    lhs = rhs
        # otherwise (membership check):
        #    set<lhs> <= rhs <= set<top>
        if isinstance(op, (Lt, LtE, Gt, GtE)):
            self.addeqs(node, numbertype, node.type, lhs.type, rhs.type)
        elif isinstance(op, (Eq, NotEq, Is, IsNot)):
            self.addeqs(node, booltype, node.type)
            self.addeqs(node, lhs.type, rhs.type)
        elif isinstance(op, (In, NotIn)):
            self.add(node, SetType(lhs.type), rhs.type, SetType(toptype))
        else:
            assert()
    
    def visit_Compare(self, node):
        self.generic_visit(node)
        for (lhs, rhs), op in zip(pairs((node.left,) + node.comparators),
                                  node.ops):
            self.compare_helper(node, op, lhs, rhs)
    
    def visit_Call(self, node):
        ### Probably need special cases here.
        self.generic_visit(node)
    
    def visit_Num(self, node):
        # node = number
        self.addeqs(node, node.type, numbertype)
    
    def visit_Str(self, node):
        # node = str
        self.addeqs(node, node.type, strtype)
    
    # No constraints for Bytes.
    
    def visit_NameConstant(self, node):
        # if True/False:
        #    node = bool
        # otherwise (None):
        #    no constraint
        if node.value in [True, False]:
            self.add(node, node.type, booltype)
    
    # No constraints for Ellipsis.
    
    # No constraints for Starred.
    
    def visit_Name(self, node):
        # node = vartype
        self.addeqs(node, node.type, TypeVar(node.id))
    
    def visit_List(self, node):
        return self.seq_helper(node, ListType)
    
    def visit_Tuple(self, node):
        # node = tuple<elt1, ..., eltn>
        self.generic_visit(node)
        t = TupleType([elt.type for elt in node.elts])
        self.addeqs(node, node.type, t)
    
    def visit_IsEmpty(self, node):
        # node = bool
        # set<bottom> <= target <= set<top>
        self.generic_visit(node)
        self.addeqs(node, node.type, booltype)
        self.add(node, SetType(bottomtype),
                 node.target.type, SetType(toptype))
    
    def visit_GetRef(self, node):
        # node = numbertype
        # set<elem> <= target <= set<top>
        self.generic_visit(node)
        self.addeqs(node, node.type, numbertype)
        self.add(node, SetType(node.elem.type),
                 node.target.type, SetType(toptype))
    
    def map_helper(self, node):
        # dict<bottom, bottom> <= target <= dict<top, top>
        # target <= dict<top, node>
        # dict<bottom, node> <= target
        self.add(node, DictType(bottomtype, bottomtype),
                 node.target.type, DictType(toptype, toptype))
        self.add(node, node.target.type, DictType(toptype, node.type))
        self.add(node, DictType(bottomtype, node.type), node.target.type)
    
    def visit_Lookup(self, node):
        # map constraints
        # dict<bottom, default> <= target
        self.generic_visit(node)
        self.map_helper(node)
        self.add(node, DictType(bottomtype, node.default.type),
                 node.target.type)
    
    def visit_ImgLookup(self, node):
        # map constraints
        # set<bottom> <= node <= set<top>
        self.generic_visit(node)
        self.map_helper(node)
        self.add(node, SetType(bottomtype), node.type, SetType(toptype))
    
    visit_RCImgLookup = visit_ImgLookup
    
    def visit_SMLookup(self, node):
        # dict<bottom, set<node>> <= target <= dict<top, set<node>>
        self.generic_visit(node)
        self.add(node, DictType(bottomtype, SetType(node.type)),
                 node.target.type, DictType(toptype, SetType(node.type)))
    
    def visit_DemQuery(self, node):
        # node = value
        self.addeqs(node, node.type, node.value.type)
    
    def visit_NoDemQuery(self, node):
        # node = value
        self.addeqs(node, node.type, node.value.type)
    
    # SetMatch and DeltaMatch omitted.
    # Requires analysis of mask for types.
    
    def visit_Comp(self, node):
        # set<resexp> = node
        # for each if, cond = bool
        self.generic_visit(node)
        self.add(node, node.resexp.type, node.type)
        for c in node.clauses:
            if isinstance(c, Enumerator):
                continue
            self.add(node, c.type, booltype)
    
    def visit_Aggregate(self, node):
        # all:
        #    set<bottom> <= value <= set<top>
        # count:
        #    node = number
        # sum:
        #    node = number
        #    value <= set<number>
        # min/max:
        #    set<node> = value
        self.generic_visit(node)
        self.add(node, SetType(bottomtype),
                 node.value.type, SetType(toptype))
        if node.op == 'count':
            self.addeqs(node, node.type, numbertype)
        elif node.op == 'sum':
            self.addeqs(node, node.type, numbertype)
            self.add(node, node.value.type, SetType(numbertype))
        elif node.op in ['min', 'max']:
            self.addeqs(node, SetType(node.type), node.value.type)
        else:
            assert()
    
    # Other nodes.
    
    def visit_comprehension(self, node):
        # set<bottom> <= iter <= set<target>
        # for each if, cond = bool
        self.generic_visit(node)
        self.add(node, SetType(bottomtype),
                 node.iter.type, SetType(node.target.type))
        for c in node.ifs:
            self.addeqs(node, c.type, booltype)
    
    def visit_Enumerator(self, node):
        # set<bottom> <= iter <= set<target>
        self.generic_visit(node)
        self.add(node, SetType(bottomtype),
                 node.iter.type, SetType(node.target.type))


class StoreConstraintGenerator(NodeVisitor, BaseConstraintGenerator):
    
    """Generate constraints for Attribute and Subscript nodes,
    which depend on the current state of the typevar store.
    """
    
    def __init__(self, store, objtypes=None):
        self.store = store
        if objtypes is None:
            self.objtypes = {}
        self.objtypes = objtypes
    
    def process(self, tree):
        self.constrs = set()
        super().process(tree)
        return self.constrs
    
    def visit_Subscript(self, node):
        # Handle the ad hoc polymorphism of overloading the
        # subscript operator for dictionaries, lists, and tuples.
        #
        # The rules are based on the current store for the
        # subscripted value. We're careful not to constrain
        # typevars from above because the inputs may rise
        # in the lattice as the fixpoint continues. This
        # is tricky because we need to keep in mind the
        # distinction between typevars and ground type terms.
        #
        # if value is top:
        #    top <= node
        #    top <= key
        # otherwise if value is a dict<K, V>:
        #    (note that K and V are possibly ground terms,
        #     not typevars)
        #    dict<key, bottom> <= value
        #    V <= node
        # otherwise if value is a list<T>:
        #    number <= key
        #    T <= node
        # otherwise if value is a tuple<T1, ..., Tn>:
        #    if key is an integer constant i:
        #       Ti <= node
        #    otherwise:
        #       number <= key
        #       Tj <= node for each j
        # otherwise:
        #    no constraints
        
        self.generic_visit(node)
        if not isinstance(node.slice, Index):
            return
        vt = node.value.type
        vt_exp = vt.expand(self.store)
        kt = node.slice.value.type
        rt = node.type
        
        if vt_exp is toptype:
            self.add(node, toptype, vt)
            self.add(node, toptype, kt)
        elif isinstance(vt_exp, DictType):
            self.add(node, DictType(kt, bottomtype), vt)
            self.add(node, vt_exp.vt, rt)
        elif isinstance(vt_exp, ListType):
            self.add(node, numbertype, kt)
            self.add(node, vt_exp.et, rt)
        elif isinstance(vt_exp, TupleType):
            if (isinstance(node.slice.value, Num) and
                0 <= node.slice.value.n < len(vt_exp.ets)):
                self.add(node, vt_exp.ets[node.slice.value.n], rt)
            else:
                self.add(node, numbertype, kt)
                for et in vt_exp.ets:
                    self.add(node, et, rt)
        else:
            # No constraints.
            pass
    
#    def visit_Attribute(self, node):
#        # if object in objtypes:
#        #    node = objtypes[object][attribute]
#        
#        ### TODO: Special cases for methods, e.g. ".elements()".
#        
#        self.generic_visit(node)
#        if node.value.type.expand(self.store)
        
        ###
        
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
    
#    def visit_Subscript(self, node):
#        
#        pass
    
    
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


def analyze_types(tree, vartypes=None, objtypes=None):
    """Analyze types."""
    if vartypes is None:
        vartypes = {}
    
    varnames = VarsFinder.run(tree)
    
    # Plug in fresh type variables
    tree, tvars = add_fresh_typevars(tree)
    # Initialize the store with entries for expression typevars
    # and variable typevars.
    store = {tvar: bottomtype for tvar in tvars}
    store.update({var: vartypes.get(var, bottomtype)
                  for var in varnames})
    
    # Get static (non-store-dependent) constraints.
    constrs = ConstraintGenerator.run(tree)
    
    # Fixed-point computation to solve constraints.
    # Bailout if it takes too many iterations.
    limit = 20
    count = 0
    changed = True
    while changed and count < limit:
        changed = False
        oldstore = store.copy()
        
        # Generate new store-dependent constraints.
        new_constrs = StoreConstraintGenerator.run(tree, store)
        new_constrs.difference_update(constrs)
        if len(new_constrs) > 0:
            changed = True
        constrs.update(new_constrs)
        
        # Apply all constraints.
        for node, lhs, rhs in constrs:
            apply_constraint(store, lhs, rhs, node=node)
        
        changed |= oldstore != store
        count += 1
    
    print('Iterated type analysis {} times'.format(count))
    tree = subst_typevars(tree, store)
    new_vartypes = {name: store[name] for name in varnames}
    return tree, new_vartypes
