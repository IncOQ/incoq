###############################################################################
# orderedset.py                                                               #
# Author: Jon Brandvein, adapted from Raymond Hettinger                       #
###############################################################################

"""Ordered set type."""

# This is an ordered set recipe by Raymond Hettinger (MIT licensed).
# See http://code.activestate.com/recipes/576694/ (r7).
#
# Modifications by Jon Brandvein:
# - added named forms for missing operators, including issubset(),
#   update, etc.
# - added reversed operators
# - added from_union() constructor



__all__ = [
    'OrderedSet',
]


import collections


# -- Begin recipe --
KEY, PREV, NEXT = range(3)

class OrderedSet(collections.MutableSet):

    def __init__(self, iterable=None):
        self.end = end = [] 
        end += [None, end, end]         # sentinel node for doubly linked list
        self.map = {}                   # key --> [key, prev, next]
        if iterable is not None:
            self |= iterable

    def __len__(self):
        return len(self.map)

    def __contains__(self, key):
        return key in self.map

    def add(self, key):
        if key not in self.map:
            end = self.end
            curr = end[PREV]
            curr[NEXT] = end[PREV] = self.map[key] = [key, curr, end]

    def discard(self, key):
        if key in self.map:        
            key, prev, next = self.map.pop(key)
            prev[NEXT] = next
            next[PREV] = prev

    def __iter__(self):
        end = self.end
        curr = end[NEXT]
        while curr is not end:
            yield curr[KEY]
            curr = curr[NEXT]

    def __reversed__(self):
        end = self.end
        curr = end[PREV]
        while curr is not end:
            yield curr[KEY]
            curr = curr[PREV]

    def pop(self, last=True):
        if not self:
            raise KeyError('set is empty')
        key = next(reversed(self)) if last else next(iter(self))
        self.discard(key)
        return key

    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, list(self))

    def __eq__(self, other):
        if isinstance(other, OrderedSet):
            return len(self) == len(other) and list(self) == list(other)
        # Note by Jon: Fixed bug for when other object is not iterable
        # or has non-hashable elements. Changed semantics so that we do
        # not compare equal with non-set iterables.
        elif isinstance(other, set):
            return set(self) == other
        else:
            return False

    def __del__(self):
        # Note by Jon: I've observed error conditions that seem to
        # emanate from this destructor upon program close, but
        # I don't know how to track it down or fix it. In the meantime,
        # it doesn't seem to be a problem.
        self.clear()                    # remove circular references
    
# -- End recipe --
    
    # We need to override __and__ becaues the implementation inherited
    # from collections.Set preserves the order of the RHS, not the LHS.
    def __and__(self, other):
        from collections import Iterable
        if not isinstance(other, Iterable):
            return NotImplemented
        return self._from_iterable(value for value in self if value in other)
    
    # The collections.MutableSet base class only provides the operator
    # forms of set operations, not the named forms that the built-in
    # set class has. The following definitions add these built-in
    # names. Note that in some cases the built-in operators require
    # that the other type is a set, so these definitions convert the
    # other argument to a set when necessary.
    
    def issubset(self, other):
        return self <= set(other)
    
    def issuperset(self, other):
        return self >= set(other)
    
    def union(self, other):
        return self | set(other)
    
    def intersection(self, other):
        return self & set(other)
    
    def difference(self, other):
        return self - set(other)
    
    def symmetric_difference(self, other):
        return self ^ set(other)
    
    def copy(self):
        return type(self)(self)
    
    def update(self, *others):
        for it in others:
            self |= it
    
    def intersection_update(self, *others):
        for it in others:
            self &= it
    
    def difference_update(self, *others):
        for it in others:
            self -= it
    
    def symmetric_difference_update(self, other):
        self ^= other
    
    # The built-in set type requires that the right-hand argument of
    # its binary operators are of set type. Our semantics for the case
    # of <set> <op> <OrderedSet> are to coerce the OrderedSet to a set
    # and proceed with the operation as normal.
    
    def __rand__(self, other):
        if isinstance(other, set):
            return other & set(self)
        return NotImplemented
    
    def __ror__(self, other):
        if isinstance(other, set):
            return other | set(self)
        return NotImplemented
    
    def __rsub__(self, other):
        if isinstance(other, set):
            return other - set(self)
        return NotImplemented
    
    def __rxor__(self, other):
        if isinstance(other, set):
            return other ^ set(self)
        return NotImplemented
    
    def __rle__(self, other):
        if isinstance(other, set):
            return other <= set(self)
        return NotImplemented
    
    def __rlt__(self, other):
        if isinstance(other, set):
            return other < set(self)
        return NotImplemented
    
    def __rgt__(self, other):
        if isinstance(other, set):
            return other > set(self)
        return NotImplemented
    
    def __rge__(self, other):
        if isinstance(other, set):
            return other >= set(self)
        return NotImplemented
    
    def __req__(self, other):
        if isinstance(other, set):
            return other == set(self)
        return NotImplemented
    
    def __rne__(self, other):
        if isinstance(other, set):
            return other != set(self)
        return NotImplemented
    
    # These helpers are useful for taking an ordered union with minimal
    # extra code.
    
    def update_union(self, seqs):
        """Update with the union of the given sequence of iterators."""
        for seq in seqs:
            self.update(seq)
    
    @classmethod
    def from_union(cls, seqs):
        """Construct from the union of the given sequence of iterators."""
        inst = cls()
        inst.update_union(seqs)
        return inst
