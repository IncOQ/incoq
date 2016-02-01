"""Built-in features needed for input and output programs."""


__all__ = [
    'CONFIG',
    'SYMCONFIG',
    'QUERY',
    
    'count',
    'min',
    'max',
    
    'IncOQType',
    'Set',
    'CSet',
    'Map',
    
    'Tree',
]


from reprlib import recursive_repr
from collections import Counter
from functools import partial
import builtins

from .tree import Tree


# These act as syntactic directives for the transformation system.
# Execution wise, they are no-ops.

def CONFIG(*args, **kargs):
    pass

def SYMCONFIG(*args, **kargs):
    pass

def QUERY(*args, **kargs):
    # QUERY is overloaded as both an expression annotation and a
    # top-level directive. First check for the annotation case,
    # where we have two positional arguments, the first of which
    # is a string (query name). In that case, return the wrapped
    # expression (second argument). Otherwise, no-op.
    if len(args) == 2 and isinstance(args[0], str):
        return args[1]
    else:
        pass


# Aggregate functions.
#
# - count() is aliased to len()
# - sum() is already provided by Python
# - min() and max() are the same as the Python built-ins, except
#   that they return None when the input is empty.

count = len
min = partial(builtins.min, default=None)
max = partial(builtins.max, default=None)


class IncOQType:
    
    """Base class for user-manipulated and queried collections."""
    
    def _fmt_helper(self, fmt):
        # Use object methods rather than dispatching via super()
        # because we don't want to invoke __str__() or __repr__()
        # from some mixin base class.
        f = {str: object.__str__,
             repr: object.__repr__}[fmt]
        return f(self)
    
    @recursive_repr()
    def __str__(self):
        return self._fmt_helper(str)
    
    @recursive_repr()
    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__,
                               self._fmt_helper(repr))
    
    # Ensure identity semantics.
    __hash__ = object.__hash__
    __eq__ = object.__eq__
    __ne__ = object.__ne__


class ImgLookupMixin:
    
    """Mixin for giving a set-like class the imglookup() and unwrap()
    operations. For CSets, the underlying count information is
    discarded.
    """
    
    def imglookup(self, mask, bounds):
        """Given a mask and values for the bound components, return
        a set of tuples of values for the unbound components.
        
        This is implemented as a straightforward linear-time iteration
        over the contents of the set.
        """
        # Check arity.
        k = len(mask)
        assert all(isinstance(item, tuple) and len(item) == k
                   for item in self)
        # Check number of bound components.
        bounds = list(bounds)
        assert len([c for c in mask if c == 'b']) == len(bounds)
        
        result = Set()
        for item in self:
            bs = [part for c, part in zip(mask, item) if c == 'b']
            us = [part for c, part in zip(mask, item) if c == 'u']
            if bs == bounds:
                result.add(tuple(us))
        return result
    
    def unwrap(self):
        """Assuming this set consists of singleton tuples (tuples with
        arity 1), return a new set consisting of the tuples' contents.
        """
        result = Set()
        for elem, in self:
            result.add(elem)
        return result


class SetFromMapMixin:
    
    """Mixin for giving a map-like class the setfrommap() operation."""
    
    def setfrommap(self, mask):
        nb = mask.count('b')
        nu = mask.count('u')
        # Check arity.
        assert all(isinstance(item, tuple) and len(item) == nb
                   for item in self.keys())
        assert nu == 1
        
        result = Set()
        for k, v in self.items():
            ki = iter(k)
            vi = iter([v])
            entry = tuple(next(ki) if c == 'b' else next(vi)
                          for c in mask)
            result.add(entry)
        return result


class Set(IncOQType, set, ImgLookupMixin):
    
    """IncOQ Set. This differs from Python sets in that it has identity
    semantics and can therefore be hashed.
    """
    
    # This class is mostly implemented by directly inheriting
    # from the built-in set, for speed. Each wrapper call to a
    # Python-level function introduces noticeable overhead.
    
    def _fmt_helper(self, fmt):
        return '{' + ', '.join(fmt(item) for item in self) + '}'
    
    # __getstate__() / __setstate__() for set suffice.
    
    # The built-in set class provides the following updates:
    #
    #   - add() and remove()
    #   - update() (union) and intersection_update()
    #   - difference_update() and symmetric_difference_update()
    #   - clear()
    #
    # The only other update we need to add is copy_update().
    
    def copy_update(self, other):
        if self is not other:
            self.clear()
            self.update(other)


class CSet(IncOQType, Counter, ImgLookupMixin):
    
    """Reference-counted set. Supports element-wise operations but
    not all of the bulk operations that Set has.
    """
    
    # Implemented on top of Counter for the most part. There's some
    # overhead for the element and refcount manipulation operations
    # since they're implemented in Python.
    
    def _fmt_helper(self, fmt):
        # Include reference counts for str() only.
        if fmt is str:
            return '{' + ', '.join(fmt(item) for item in self) + '}'
        elif fmt is repr:
            return ('{' + ', '.join(fmt(item) + ': ' + str(count)
                                    for item, count in self.items()) + '}')
        else:
            assert()
    
    # __getstate__() / __setstate__() for Counter suffice.
    
    # Basic operations.
    
    def add(self, item):
        """Strictly add an element with refcount 1."""
        assert item not in self
        self[item] = 1
    
    def remove(self, item):
        """Strictly remove an element with refcount 1."""
        assert self[item] == 1
        del self[item]
    
    def getcount(self, item):
        """Return the reference count of an existing element."""
        return self[item]
    
    def inccount(self, item):
        """Increment the refcount of an existing element."""
        assert item in self
        self[item] += 1
    
    def deccount(self, item):
        """Decrement the refcount of an existing element where the
        refcount is greater than 1."""
        assert self[item] > 1
        self[item] -= 1
    
    # elements(), update(), and clear() are provided by Counter.


class Map(IncOQType, dict, SetFromMapMixin):
    
    """Like dict, but with identity semantics."""
    
    def _fmt_helper(self, fmt):
        return ('{' + ', '.join('{}: {}'.format(fmt(key), fmt(value))
                                for key, value in self.items()) + '}')
    
    # Aliased to clear(). We use a separate name so as to not
    # syntactically conflict with the name of the set clearing
    # operation.
    dictclear = dict.clear
