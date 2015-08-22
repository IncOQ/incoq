"""Type algebra and analysis.

Types are domains of values, ordered in a lattice by set inclusion.
The type constructors are:

    Core:
    - Top (any; set of all values)
    - Bottom (void; empty set)
    
    Primitives:
    - Bool
    - Number
    - String
    
    Composites:
    - Union<T1, ..., Tn>
    - Tuple<T1, ..., Tn>
    - Set<T>

A is a subtype of B iff one of the following cases applies:

  - A is bottom or B is top
  
  - A and B are Tuple types with the same arity, and all component
    types of A are subtypes of the corresponding component types
    of B (i.e., tuple types are covariant)
  
  - A and B are Set types and the element type of A is a subtype
    of the element type of B (i.e., set types are covariant)

Type analysis works via abstract interpretation. Each syntactic
construct has an interpretation function that monotonically maps
from the types of its inputs to the types of its outputs. Each
construct also has upper-bound constraints on the allowed types
for its inputs. The meaning of the interpretation function is that,
if the input values are of the appropriate input types, then the
output values are of the appropriate output types. Likewise, the
meaning of the upper-bound constraints is that if the input values
are subtypes of the upper bounds, then execution of the construct
does not cause a type error.

The abstract interpretation initializes all symbols' types to Bottom,
meaning that they have no possible values (known so far) and are safe
to use in all syntactic constructs. It then iteratively (and
monotonically) increases the symbols' types by lattice-joining them
with the output type of any construct that writes to them. Once
fixed point is achieved, we know that no symbol will ever receive
a value at runtime that is not of the inferred type.

The program is well-typed if each upper bound constraint is satisfied
by the inferred types of its inputs. We do not necessarily require
programs to be well-typed. 
"""


__all__ = [
    'Type',
    'Top',
    'Bottom',
    'Bool',
    'Number',
    'String',
    'Union',
    'Tuple',
    'Set',
]


import numbers
from simplestruct import Struct, TypedField


class Type(Struct):
    
    """Base class for type algebra."""
    
    # For ease of implementation, the join operation may produce a
    # bigger type than the true least upper bound, and likewise, meet
    # may produce a smaller type than the greatest lower bound.
    
    def order_helper(self, other, leftfunc, rightfunc):
        """Compare self to other, first using leftfunc(other) and
        falling back on rightfunc(self) if it returns NotImplemented.
        Always return True if self == other.
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
    
    def issubtype(self, other):
        """Return True if this type is a non-strict subtype of the
        other.
        """
        return self.order_helper(other, self.issubtype_cmp,
                                 other.issupertype_cmp)
    
    def issubtype_cmp(self, other):
        """Return whether this type is a non-strict subtype of other.
        May return NotImplemented to defer to the other type's
        comparison function.
        """
        return NotImplemented
    
    def issupertype(self, other):
        """Return True if this type is a non-strict supertype of the
        other.
        """
        return self.order_helper(other, self.issupertype_cmp,
                                 other.issubtype_cmp)
    
    def issupertype_cmp(self, other):
        """Return whether this type is a non-strict supertype of other.
        May return NotImplemented to defer to the other type's
        comparison function.
        """
        return NotImplemented
    
    def join(self, *others, inverted=False):
        """Return a type that is at least as big as the lattice join
        of this type and each type listed in others. If inverted is
        True, instead return a type that is at least as small as the
        meet.
        """
        t = self
        for o in others:
            t = t.join_one(o, inverted=inverted)
        return t
    
    def join_one(self, other, *, inverted=False):
        """Handle join() for one other type."""
        if self.issubtype(other):
            return other if not inverted else self
        elif other.issubtype(self):
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


class TopClass(Type):
    
    """Singleton for Top."""
    
    singleton = None
    
    def __new__(cls):
        if cls.singleton is None:
            cls.singleton = super().__new__(cls)
        return cls.singleton
    
    def __str__(self):
        return 'Top'
    
    def issupertype_cmp(self, other):
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
    
    def issubtype_cmp(self, other):
        return True

Bottom = BottomClass()


class Primitive(Type):
    
    """Built-in type."""
    
    # Note that t is a Python class, not a Type.
    t = TypedField(type)
    
    def __str__(self):
        return self.t.__name__

Bool = Primitive(bool)
Number = Primitive(numbers.Number)
String = Primitive(str)


class Union(Type):
    
    """Untagged sum type."""
    
    # The subtyping, join, and meet rules for this type are currently
    # implemented very coarsely. This is ok because this type is only
    # used for upper-bound constraints at the moment.
    
    # Currently, duplicate types in the union are not eliminated.
    
    elts = TypedField(Type, seq=True)
    
    def __str__(self):
        return '(' + ' | '.join(str(e) for e in self.elts) + ')'
    
    def issupertype_cmp(self, other):
        # This rule isn't complete. It checks for whether other is
        # an element in this union, but not whether other is itself
        # a union of a subset of our elements. Likewise, a union of
        # a single domain is equal to (and hence a subtype of) that
        # domain, and an empty union is equal to (subtype of) Bottom.
        if any(other.issubtype(e) for e in self.elts):
            return True
        return NotImplemented


class Tuple(Type):
    
    """Tuple type. For tuples of the same arity, covariant in the
    component types.
    """
    
    elts = TypedField(Type, seq=True)
    
    def __str__(self):
        return '(' + ', '.join(str(e) for e in self.elts) + ')'
    
    def issubtype_cmp(self, other):
        if type(self) != type(other):
            return NotImplemented
        if len(self.elts) != len(other.elts):
            return NotImplemented
        return all(e1.issubtype(e2)
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


class Set(Type):
    
    """Set type. Covariant in element type."""
    
    elt = TypedField(Type)
    
    def __str__(self):
        return '{' + str(self.elt) + '}'
    
    def issubtype_cmp(self, other):
        if type(self) != type(other):
            return NotImplemented
        return self.elt.issubtype(other.elt)
    
    def join_helper(self, other, *, inverted=False):
        top = Top if not inverted else Bottom
        if type(self) != type(other):
            return top
        new_elt = self.elt.join(other.elt, inverted=inverted)
        return self._replace(elt=new_elt)
