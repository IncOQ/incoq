"""Type algebra and lattice.

The set of possible types is generated by finite applications of the
following type constructors:

    Core:
    - Top (any)
    - Bottom (void)
    
    Primitives:
    - Bool
    - Number
    - String
    
    Composites:
    - Tuple<T1, ..., Tn>
    - Set<T>
    - List<T>
    - Map<K, V>

Each type represents a domain of values, although multiple types may
have the same domain. Types are arranged in a lattice with order
operator <=. This order respects subtyping, i.e., A <= B implies that
A is a subtype of B (meaning values of A are also values of B). However,
the converse is not necessarily true: just because A is a subtype of B
does not mean that A <= B.

A <= B is defined to hold in only the following cases, plus those
cases that are implied by reflexivity and transitivity:

  - A is bottom or B is top
  
  - A is Tuple<T1, ..., Tn> and B is Tuple<S1, ..., Sn>, and
    Ti <= Si for each i in 1..n (covariance of tuple components)
  
  - A is Set<T> and B is Set<S>, and T <= S (covariance of set element)
  
  - A is List<T> and B is List<S>, and T <= S (covariance of list
    element)
  
  - A is Map<K1, V1> and B is Map<K2, V2>, and K1 <= K2 and V1 <= V2
    (covariance of keys and values)
"""


__all__ = [
    'Type',
    'Top',
    'Bottom',
    'Bool',
    'Number',
    'String',
    'Tuple',
    'Set',
    'List',
    'Map',
    
    'eval_typestr',
]


import numbers
from simplestruct import Struct, TypedField


class Type(Struct):
    
    """Base class for type algebra."""
    
    def order_helper(self, other, leftfunc, rightfunc):
        """Compare self to other, first using leftfunc(other) and
        falling back on rightfunc(self). If both return NotImplemented,
        False is returned. The reflexive case of self == other is
        always True.
        """
        if self == other:
            return True
        else:
            b = leftfunc(other)
            if b is NotImplemented:
                b = rightfunc(self)
                if b is NotImplemented:
                    return False
            return bool(b)
    
    def issmaller(self, other):
        """Return whether self <= other."""
        return self.order_helper(other, self.smaller_cmp,
                                 other.bigger_cmp)
    
    def smaller_cmp(self, other):
        """Helper for issmaller(). May return NotImplemented to defer to
        the other type's comparison function.
        """
        return NotImplemented
    
    def isbigger(self, other):
        """Return whether other <= self."""
        return self.order_helper(other, self.bigger_cmp,
                                 other.smaller_cmp)
    
    def bigger_cmp(self, other):
        """Helper for isbigger(). May return NotImplemented to defer to
        the other type's comparison function.
        """
        return NotImplemented
    
    def join(self, *others, inverted=False):
        """Return the join of this type and each type listed in others.
        If inverted is True, return the meet instead of the join.
        Types of None are ignored.
        """
        t = self
        for o in others:
            t = t.join_one(o, inverted=inverted)
        return t
    
    def join_one(self, other, *, inverted=False):
        """Handle join() for one other type."""
        if other is None:
            return self
        if self.issmaller(other):
            return other if not inverted else self
        elif other.issmaller(self):
            return self if not inverted else other
        else:
            return self.join_helper(other, inverted=inverted)
    
    def join_helper(self, other, *, inverted=False):
        """Handle join_one() for non-trivial cases, specifically,
        for cases when this type and other are not directly
        comparable.
        """
        return Top if not inverted else Bottom
    
    def meet(self, *others, inverted=False):
        """Opposite of join()."""
        return self.join(*others, inverted=not inverted)
    
    def widen(self, height):
        """Return a type no smaller than this one, whose type term
        tree height is no greater than the given limit.
        """
        if height == 0:
            return Top
        else:
            return self.widen_helper(height)
    
    def widen_helper(self, height):
        """Handle widen() for the case where height is not 0."""
        return self


class TopClass(Type):
    
    """Singleton for Top."""
    
    singleton = None
    
    def __new__(cls):
        if cls.singleton is None:
            cls.singleton = super().__new__(cls)
        return cls.singleton
    
    def __str__(self):
        return 'Top'
    
    def bigger_cmp(self, other):
        return True

Top = TopClass()


class BottomClass(Type):
    
    """Singleton for Bottom."""
    
    singleton = None
    
    def __new__(cls):
        if cls.singleton is None:
            cls.singleton = super().__new__(cls)
        return cls.singleton
    
    def __str__(self):
        return 'Bottom'
    
    def smaller_cmp(self, other):
        return True

Bottom = BottomClass()


class Primitive(Type):
    
    """Built-in type."""
    
    # Note that t holds a Python class, not a Type.
    t = TypedField(type)
    
    def __str__(self):
        return self.t.__name__

Bool = Primitive(bool)
Number = Primitive(numbers.Number)
String = Primitive(str)


class Tuple(Type):
    
    """Tuple type. For tuples of the same arity, covariant in the
    component types.
    """
    
    elts = TypedField(Type, seq=True)
    
    def __str__(self):
        return '(' + ', '.join(str(e) for e in self.elts) + ')'
    
    def smaller_cmp(self, other):
        if type(self) != type(other):
            return NotImplemented
        if len(self.elts) != len(other.elts):
            return NotImplemented
        return all(e1.issmaller(e2)
                   for e1, e2 in zip(self.elts, other.elts))
    
    def join_helper(self, other, *, inverted=False):
        top = Top if not inverted else Bottom
        if type(self) != type(other):
            return top
        if len(self.elts) != len(other.elts):
            return top
        new_elts = [e1.join(e2, inverted=inverted)
                    for e1, e2 in zip(self.elts, other.elts)]
        return self._replace(elts=new_elts)
    
    def widen_helper(self, height):
        new_elts = [e.widen(height - 1) for e in self.elts]
        return self._replace(elts=new_elts)


class SequenceTypeBase(Type):
    
    """Base class for types of sequences of homogeneous elements.
    Covariant in element type.
    """
    
    elt = TypedField(Type)
    
    def __str__(self):
        raise NotImplementedError
    
    def smaller_cmp(self, other):
        if type(self) != type(other):
            return NotImplemented
        return self.elt.issmaller(other.elt)
    
    def join_helper(self, other, *, inverted=False):
        top = Top if not inverted else Bottom
        if type(self) != type(other):
            return top
        new_elt = self.elt.join(other.elt, inverted=inverted)
        return self._replace(elt=new_elt)
    
    def widen_helper(self, height):
        new_elt = self.elt.widen(height - 1)
        return self._replace(elt=new_elt)


class Set(SequenceTypeBase):
    
    """Set type."""
    
    _inherit_fields = True
    
    def __str__(self):
        return '{' + str(self.elt) + '}'


class List(SequenceTypeBase):
    
    """List type."""
    
    _inherit_fields = True
    
    def __str__(self):
        return '[' + str(self.elt) + ']'


class Map(Type):
    
    """Map type."""
    
    key = TypedField(Type)
    value = TypedField(Type)
    
    def __str__(self):
        return '{{{}: {}}}'.format(self.key, self.value)
    
    def smaller_cmp(self, other):
        if type(self) != type(other):
            return NotImplemented
        return (self.key.issmaller(other.key) and
                self.value.issmaller(other.value))
    
    def join_helper(self, other, *, inverted=False):
        top = Top if not inverted else Bottom
        if type(self) != type(other):
            return top
        new_key = self.key.join(other.key, inverted=inverted)
        new_value = self.value.join(other.value, inverted=inverted)
        return self._replace(key=new_key, value=new_value)
    
    def widen_helper(self, height):
        new_key = self.key.widen(height - 1)
        new_value = self.value.widen(height - 1)
        return self._replace(key=new_key, value=new_value)


def eval_typestr(s):
    """Eval a string to construct a type expression."""
    ns = {k: v for k, v in globals().items()
               if (isinstance(v, Type) or
                   (isinstance(v, type) and issubclass(v, Type)))}
    return eval(s, ns)
