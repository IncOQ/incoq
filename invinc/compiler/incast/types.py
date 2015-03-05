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
    'RefineType',
    'TypeVar',
    
    'eval_typestr',
    
    'TypedUnparser',
    'unparse_structast_typed',
]


from numbers import Number
from simplestruct import Struct, Field, TypedField

from invinc.util.collections import frozendict

from .nodes import (AST, expr, Not, Index, Num, Enumerator, Load, Store,
                    Eq, NotEq, Lt, LtE, Gt, GtE, Is, IsNot, In, NotIn)
from .structconv import NodeTransformer, AdvNodeVisitor, Unparser
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
        else:
            return self.issubtype_helper(other)
    
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
        if self.issubtype(other):
            return other if not inverted else self
        elif other.issubtype(self):
            return self if not inverted else other
        elif self == other:
            return self
        else:
            return self.join_helper(other, inverted=inverted)
    
    def join_helper(self, other, *, inverted=False):
        """Join with one other type of the same class as this one.
        If inverted use meet instead.
        """
        return toptype if not inverted else bottomtype
    
    def meet(self, *others, inverted=False):
        """Take the lattice meet with one or more other types,
        returning a new type."""
        return self.join(*others, inverted=not inverted)
    
    def expand(self, store):
        """Expand a type expression, given a typevar store
        (a mapping from typevar names to ground type expressions).
        """
        return self
    
    def widen(self, limit):
        """Return a widened type that replaces nested types with
        top if they are at least limit levels deep.
        """
        if limit == 0:
            return toptype
        else:
            return self.widen_helper(limit)
    
    def widen_helper(self, limit):
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
        if type(self) != type(other):
            return False
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
        if type(self) != type(other):
            return top
        if len(self.ets) != len(other.ets):
            return top
        new_ets = [et1.join(et2, inverted=inverted)
                   for et1, et2 in zip(self.ets, other.ets)]
        return self._replace(ets=new_ets)
    
    def expand(self, store):
        new_ets = [et.expand(store) for et in self.ets]
        return self._replace(ets=new_ets)
    
    def widen_helper(self, limit):
        new_ets = [et.widen(limit - 1) for et in self.ets]
        return self._replace(ets=new_ets)

class SeqType(Type):
    et = TypedField(Type)
    brackets = '??'
    
    def __str__(self):
        return self.brackets[0] + str(self.et) + self.brackets[1]
    
    def issubtype_helper(self, other):
        if type(self) != type(other):
            return False
        return self.et.issubtype(other.et)
    
    def join_helper(self, other, inverted=False):
        if type(self) != type(other):
            return toptype if not inverted else bottomtype
        new_et = self.et.join(other.et, inverted=inverted)
        return self._replace(et=new_et)
    
    def match_against_helper(self, other):
        return [(self.et, other.et)]
    
    def expand(self, store):
        new_et = self.et.expand(store)
        return self._replace(et=new_et)
    
    def widen_helper(self, limit):
        new_et = self.et.widen(limit - 1)
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
        if type(self) != type(other):
            return False
        return (self.kt.issubtype(other.kt) and
                self.vt.issubtype(other.vt))
    
    def join_helper(self, other, *, inverted=False):
        if type(self) != type(other):
            return toptype if not inverted else bottomtype
        new_kt = self.kt.join(other.kt, inverted=inverted)
        new_vt = self.vt.join(other.vt, inverted=inverted)
        return self._replace(kt=new_kt, vt=new_vt)
    
    def match_against_helper(self, other):
        return [(self.kt, self.kt), (other.vt, other.vt)]
    
    def expand(self, store):
        new_kt = self.kt.expand(store)
        new_vt = self.vt.expand(store)
        return self._replace(kt=new_kt, vt=new_vt)
    
    def widen_helper(self, limit):
        new_kt = self.kt.widen(limit - 1)
        new_vt = self.vt.widen(limit - 1)
        return self._replace(kt=new_kt, vt=new_vt)

class ObjType(Type):
    name = TypedField(str)
    
    def __str__(self):
        return self.name
    
    def matches_helper(self, other):
        return False

class RefineType(Type):
    name = TypedField(str)
    base = TypedField(Type)
    
    def __str(self):
        return self.name
    
    def issubtype_helper(self, other):
        return self.base.issubtype(other)
    
    def matches_helper(self, other):
        return False
    
    def join_helper(self, other, *, inverted=False):
        # My join with any type that's not directly comparable
        # is the same as my base's join with that type, since
        # my base is my only direct ancestor.
        #
        # My meet with any type that's not directly comparable
        # is bottom, since the only possible non-bottom subtypes
        # are other refinements, which would have no ancestors
        # that are incomparable to me.
        if not inverted:
            return self.base.join(other, inverted=inverted)
        else:
            return bottomtype
    
    def expand(self, store):
        new_base = self.base.expand(store)
        return self._replace(base=new_base)
    
    def widen_helper(self, limit):
        # Rather than lose information in the base, it's probably
        # better to just replace ourselves with the base.
        widened_base = self.base.widen(limit - 1)
        if self.base != widened_base:
            new_type = self.base.widen(limit)
        else:
            new_type = self
        return new_type

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
