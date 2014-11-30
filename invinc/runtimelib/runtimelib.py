###############################################################################
# runtimelib.py                                                               #
# Author: Jon Brandvein                                                       #
###############################################################################

"""This module includes features needed for input programs to be
executable as Python code, such as straightforward implementations of
queries. It also includes data type definitions and utilities for
instrumentation.
"""


__all__ =[
    'OPTIONS',
    'QUERYOPTIONS',
    'NODEMAND',
    'allow_profile',
    
    'setmatch',
    'count',
    'len_',
    'max2',
    'min2',
    
    'get_structure_sizes',
    'get_total_structure_size',
    'ENSURE_EQUAL',
    
    'Type',
    'Obj',
    'Set',
    'RCSet',
    'Map',
    
    'MSet',
    'FSet',
    'MAPSet',
    
    'Tree',
    
    'LRUSet',
]


from collections import Counter
import builtins

try:
    from bintrees import FastAVLTree
    HAVE_TREES = True
except ImportError:
    HAVE_TREES = False

from .lru import LRUTracker


# ---- Helpers ----

def tupify(items):
    """Return a tuple of the given items, or just the singular value
    if items is a singleton list.
    """
    if len(items) == 1:
        return items[0]
    else:
        return tuple(items)

def display_helper(item):
    """Formatting helper that does not expand containers."""
    if not isinstance(item, Type):
        return str(item)
    else:
        return '<{} at {}>'.format(
            type(item).__name__,
            hex(id(item)))


# ---- Instrumentation utilities ----

def get_structure_sizes(namespace):
    """Return a dictionary mapping from structure name to size, for each
    structure in a module's global namespace. For set-like objects, the
    structure size is its length. For image maps, it's the number of
    image sets plus the sum of their sizes.
    """
    return {name: obj.get_structure_size()
            for name, obj in namespace.items()
            if isinstance(obj, Type)}

def get_total_structure_size(namespace):
    """Return the total structure size taken by all structures in a
    module's global namespace.
    """
    return sum(get_structure_sizes(namespace).values())

def ENSURE_EQUAL(value, expvalue):
    """Raise AssertionError if the two values are not equal.
    Return the value otherwise.
    
    Values are compared for equality by seeing whether their string
    representations are the same. This is not robust.
    """
    if str(value) != str(expvalue):
        raise AssertionError('Semantic failure: expressions not equal')
    return value


# ---- Directive helpers ----

# Used to specify options in the transformation.
# No effect at runtime.

def OPTIONS(*args, **kargs):
    pass

def QUERYOPTIONS(*args, **kargs):
    pass

def NODEMAND(value):
    return value

def allow_profile(f):
    """If "profile" is provided in builtins, alias for that.
    Otherwise, no-op. This is useful for writing kernprof-able
    scripts that also run without profiling.
    """
    profile = getattr(builtins, 'profile', None)
    return profile(f) if profile else f


# ---- Batch implementations of queries ----

def _tuplematch(item, mask, key):
    """Match a single tuple against a mask and key. If it matches,
    return a pair of True and a list of the unbound values. If it
    doesn't, return a pair of False and None.
    """ 
    b_parts = []
    u_parts = []
    for part, c in zip(item, mask):
        if c == 'b':
            b_parts.append(part)
        elif c == 'u':
            u_parts.append(part)
        elif c.isdigit() and c != '0':
            n = int(c)
            if part != item[n - 1]:
                return False, None
        elif c == 'w':
            pass
        else:
            assert()
    
    if tupify(b_parts) == key:
        return True, u_parts
    else:
        return False, None

def setmatch(rel, mask, key):
    """Tuple set (relation) pattern matching."""
    
    # Normalize mask string.
    mask = {'out': 'bu', 'in': 'ub'}.get(mask, mask)
    
    assert all(c == 'b' or
               c == 'u' or
               (c.isdigit() and c != '0') or
               c == 'w'
               for c in mask)
    
    # Special case: If the mask is just 'w', always succeed
    # with the empty tuple. (Not sure if this is formally
    # the right thing to do or not.)
    if mask == 'w':
        return {()}
    
    result = Set()
    for item in rel:
        # Skip elements that are not tuples or that are tuples
        # with the wrong length.
        if not (isinstance(item, tuple) and
                len(item) == len(mask)):
            continue
        
        does_match, u_parts = _tuplematch(item, mask, key)
        
        if does_match:
            result.add(tupify(u_parts))
    
    return result

# Aggregate query "sum" is already available as Python function.
# Aggregate query "count" is just Python len().
count = len

# Version of len that's not interpreted as a query.
len_ = len

# Max and min aggregates that operate on zero or more scalar arguments.
# Each argument is either an orderable value or None. The highest non-
# None value is returned, or None if all given values are None (or if
# no arguments were given.)
def max2(*args):
    res = None
    for x in args:
        if x is None:
            continue
        if res is None or x > res:
            res = x
    return res

def min2(*args):
    res = None
    for x in args:
        if x is None:
            continue
        if res is None or x < res:
            res = x
    return res


# ---- Types ----

class Type:
    
    """Base class for types."""
    
    def __getstate__(self):
        raise NotImplementedError
    
    def __setstate__(self, state):
        raise NotImplementedError
    
    # Make sure our subclasses don't accidentally inherit
    # the pickling implementation of built-in types unless
    # explicitly requested.
    __reduce__ = object.__reduce__
    __reduce_ex__ = object.__reduce_ex__
    
    # Ensure identity semantics.
    __hash__ = object.__hash__
    __eq__ = object.__eq__
    
    def get_structure_size(self):
        raise NotImplementedError


class Obj(Type):
    
    """Generic object type."""
    
    # Note that the built-in "object" class doesn't support field
    # assignment.
    
    def __repr__(self):
        if hasattr(self, 'name'):
            return 'Obj(' + self.name + ')'
        else:
            return super().__repr__()
    
    def get_structure_size(self):
        return 1
    
    def __getstate__(self):
        return self.__dict__
    
    def __setstate__(self, state):
        self.__dict__.update(state)


class Set(Type, set):
    
    """Set type."""
    
    # This is implemented by directly inheriting from set, for speed.
    # Each wrapper call to a Python-level function introduces
    # noticeable overhead.
    
    def __repr__(self):
        return '{' + ', '.join(display_helper(item) for item in self) + '}'
    
    # Standard update operations, aliased in order to bypass
    # transformation.
    
    def _add(self, elem):
        super().add(elem)
    
    def _remove(self, elem):
        super().remove(elem)
    
    def get_structure_size(self):
        return len(self)
    
    def __getstate__(self):
        return set(self)
    
    def __setstate__(self, state):
        self.update(state)


class RCSet(Type):
    
    """Reference-counted set type."""
    
    # We're gonna have some constant factor overhead when using this
    # class. It relies on collections.Counter, which is implemented
    # in Python. It wraps this class rather than extending an existing
    # collection. It has assertions, and uses built-in functions like
    # len() instead of calling special methods directly like __len__().
    # This could be mitigated by making alternate streamlined
    # definitions that are controlled with an INSTRUMENTING flag.
    #
    # (Note that an INSTRUMENTING flag would have to control how
    # a method is defined at class definition time, not the control
    # flow within a method. Otherwise checking the flag alone wastes
    # precious time.)
    
    # WISHLIST: Possible optimization: cut out indirection of __iter__()
    # by making this class subset set() and using the builtin
    # set.__iter__(). Would presumably save a little overhead for each
    # block of iterations over this set, especially useful when the set
    # is very small (so overhead is larger by comparison).
    
    def __init__(self):
        super().__init__()
        self.elems = Counter()
        """Map from element to its reference count."""
    
    def __repr__(self):
        return '{' + ', '.join(display_helper(item) for item in self) + '}'
    
    def __iter__(self):
        return iter(self.elems)
    
    def __len__(self):
        return len(self.elems)
    
    def __contains__(self, value):
        return value in self.elems
    
    def getref(self, value):
        """Return the reference count of an existing element."""
        return self.elems[value]
    
    def incref(self, value):
        """Increment the refcount of an existing element."""
        assert value in self.elems
        self.elems[value] += 1
    
    def decref(self, value):
        """Decrement the refcount of an existing element where the
        refcount is greater than 1."""
        assert self.elems[value] > 1
        self.elems[value] -= 1
    
    def add(self, value):
        """Strictly add an element with refcount 1."""
        assert value not in self.elems
        self.elems[value] = 1
    
    def remove(self, value):
        """Strictly remove an element with refcount 1."""
        assert self.elems[value] == 1
        del self.elems[value]
    
    def clear(self):
        self.elems.clear()
    
    def elements(self):
        return self.elems.elements()
    
    def get_structure_size(self):
        return len(self)
    
    def __getstate__(self):
        return self.elems
    
    def __setstate__(self, state):
        self.elems = state


class Map(Type, dict):
    
    """Map type."""
    
    def __repr__(self):
        return '{' + ', '.join(display_helper(k) + ': ' + str(v)
                               for k, v in self.items()) + '}'
    
    _NO_DEFAULT = object()
    def singlelookup(self, key, default=_NO_DEFAULT):
        """If this method is used, the value must be a singleton set.
        Return the singular element of the set.
        """
        try:
            image = self[key]
        except KeyError:
            if default is not self._NO_DEFAULT:
                return default
            else:
                raise
        
        assert len(image) == 1
        return next(iter(image))
    
    def get_structure_size(self):
        total = len(self)
        for v in self.values():
            if isinstance(v, set):
                total += len(v)
            elif isinstance(v, (set, Set, RCSet)):
                total += v.get_structure_size()
        return total
    
    def __getstate__(self):
        return dict(self)
    
    def __setstate__(self, state):
        self.update(state)


class PairSet(Set):
    
    """Special set for modeling object-domain relationships. Updates to
    these sets will also trigger corresponding updates to the
    represented object-domain values.
    """


class MSet(PairSet):
    
    """M-set for set membership."""
    
    def add(self, pair):
        cont, item = pair
        assert not isinstance(cont, PairSet)
        cont.add(item)
        super().add(pair)
    
    def remove(self, pair):
        cont, item = pair
        cont.remove(item)
        super().remove(pair)


class FSet(PairSet):
    
    """F-set for object fields."""
    
    def __init__(self, field):
        super().__init__()
        self.field = field
    
    def add(self, pair):
        cont, item = pair
        setattr(cont, self.field, item)
        super().add(pair)
    
    def remove(self, pair):
        cont, _item = pair
        delattr(cont, self.field)
        super().remove(pair)

class MAPSet(PairSet):
    
    """MAP-set for maps."""
    
    def add(self, e):
        map, key, value = e
        assert not isinstance(map, PairSet)
        map[key] = value
        super().add(e)
    
    def remove(self, e):
        map, key, value = e
        del map[key]
        super().remove(e)


if HAVE_TREES:
    class Tree(FastAVLTree):
        
        """Tree subclass with non-strict min/max operations, that
        return just the key (not the item pair). This simplifies
        our generated maintenance code; the user-visible min/max
        operations still require a non-empty set.
        """
        
        def __min__(self):
            if len(self) == 0:
                return None
            else:
                return super().__min__()[0]
        
        def __max__(self):
            if len(self) == 0:
                return None
            else:
                return super().__max__()[0]

else:
    def Tree(*args, **kargs):
        raise NotImplementedError(
            'Could not import bintrees library; Incrementalized min/max '
            'aggregates unavailable')


class LRUSet(Set):
    
    """A Set augmented with cache access operations. The cache does
    not change the semantics of additions and removals; it operates
    independently and must be queried separately.
    """
    
    def __init__(self):
        super().__init__()
        self.cache = LRUTracker()
    
    def add(self, elem):
        super().add(elem)
        self.cache.add(elem)
    
    def remove(self, elem):
        super().remove(elem)
        self.cache.remove(elem)
    
    def ping(self, elem):
        """Ping an element already in the set, bumping it to the
        front of the LRU cache.
        """
        self.cache.ping(elem)
    
    def peek(self):
        """Return the element that would be removed next."""
        return self.cache.peek()
    
    def __getstate__(self):
        return (set(self), self.cache)
    
    def __setstate__(self, state):
        contents, cache = state
        self.update(contents)
        self.cache = cache
