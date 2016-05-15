"""Built-in features needed for input and output programs."""


__all__ = [
    'CONFIG',
    'SYMCONFIG',
    'QUERY',
    'resetdemand',
    'resetdemandfor',
    
    'index',
    
    'count',
    'sum',
    'min',
    'max',
    'min2',
    'max2',
    
    'isset',
    'hasfield',
    'ismap',
    'hasarity',
    
    'unwrap',
    
    'get_size',
    'get_size_for_namespace',
    
    'IncOQType',
    'Set',
    'CSet',
    'Map',
    'Obj',
    
    'Tree',
    
    'LRUSet',
]


from functools import wraps
from collections import Counter, OrderedDict
from functools import partial
import builtins

# From reprlib.
try:
    from _thread import get_ident
except ImportError:
    from _dummy_thread import get_ident

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
    if ((len(args) == 2 or len(args) == 3) and
        isinstance(args[0], str)):
        return args[1]
    else:
        pass

def resetdemand(*args, **kargs):
    pass

def resetdemandfor(*args, **kargs):
    pass


# Alias for subscripting/__getindex__.
def index(seq, ind):
    return seq[ind]


# Aggregate functions.
#
# - count() is aliased to len()
# - sum() is the same as the Python built-in
# - min() and max() are the same as the Python built-ins, except
#   that they return None when the input is empty

count = builtins.len
sum = builtins.sum
min = partial(builtins.min, default=None)
max = partial(builtins.max, default=None)

# Versions of min/max that return the lowest or highest argument,
# not counting Nones, and that return None if all arguments are None.

def min2(*args):
    return builtins.min(filter(lambda x: x is not None, args),
                        default=None)

def max2(*args):
    return builtins.max(filter(lambda x: x is not None, args),
                        default=None)


# Type checks.

def isset(value):
    return isinstance(value, (set, CSet))

def hasfield(value, attr):
    return hasattr(value, attr)

def ismap(value):
    return isinstance(value, dict)

def hasarity(value, k):
    return isinstance(value, tuple) and len(value) == k


def unwrap(set_):
    """Given a set of singleton tuples, return a Set consisting of the
    tuples' contents.
    """
    result = Set()
    for (elem,) in set_:
        result.add(elem)
    return result


def get_size(value, *, seen=None):
    """Return an integer representing the abstract size of a given
    value. For IncOQType instances, this is the number of children
    values -- elements, keys, values, etc. -- that are recursively
    contained, plus one for the parent value itself. For all other
    types of values this is just 1.
    
    If a value is reachable through multiple paths, each multiple
    path just contributes 1 to the overall count. This models the
    size taken for the value plus the size for pointers to the value.
    """
    # Invariants: Seen holds IncOQType values that have already been
    # explored. Worklist holds IncOQType values that have been found but
    # not yet explored. Count has been incremented for every pointer
    # that has been seen so far, but not for the children of any
    # unexplored IncOQType value.
    if seen is None:
        seen = set()
    count = 1
    worklist = set()
    if isinstance(value, IncOQType) and value not in seen:
        worklist.add(value)
    
    while len(worklist) > 0:
        v = worklist.pop()
        seen.add(v)
        children = v.get_children()
        count += len(children)
        # Grab all children that are IncOQTypes (and hence, safe to
        # hash), and that have not been seen. Eliminate duplicates
        # among these children too.
        to_explore = {c for c in children if isinstance(c, IncOQType)
                        if c not in seen}
        worklist.update(to_explore)
    return count


def get_size_for_namespace(namespace):
    """Return the number of entries in each Set, CSet, and Map in a
    namespace. This is used for counting the number of entries in
    top-level auxiliary structures in a transformed program's global
    namespace. Unlike get_size(), the stored data is not explored
    recursively.
    """
    size = 0
    for value in namespace.values():
        if isinstance(value, (Set, CSet)):
            size += len(value)
        elif isinstance(value, Map):
            size += len(value.keys())
            for v in value.values():
                if isinstance(v, (Set, CSet)):
                    size += len(v)
    return size


def limited_recursive_repr(func):
    """Like reprlib.recursive_repr(), but limited to a much smaller
    stack depth so that we avoid a stack overflow and also don't spend
    much time on string manipulation.
    """
    repr_running = set()
    limit = 10
    
    @wraps(func)
    def wrapper(self):
        # Based on the implementation of reprlib.recursive_repr().
        key = id(self), get_ident()
        if key in repr_running or len(repr_running) > limit:
            return '...'
        repr_running.add(key)
        try:
            result = func(self)
        finally:
            repr_running.discard(key)
        return result
    
    return wrapper


class IncOQType:
    
    """Base class for user-manipulated and queried collections."""
    
    def _fmt_helper(self, fmt):
        # Use object methods rather than dispatching via super()
        # because we don't want to invoke __str__() or __repr__()
        # from some mixin base class.
        f = {str: object.__str__,
             repr: object.__repr__}[fmt]
        return f(self)
    
    @limited_recursive_repr
    def __str__(self):
        return self._fmt_helper(str)
    
    @limited_recursive_repr
    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__,
                               self._fmt_helper(repr))
    
    # Ensure identity semantics.
    __hash__ = object.__hash__
    __eq__ = object.__eq__
    __ne__ = object.__ne__
    
    def get_children(self):
        raise NotImplementedError


class ImgLookupMixin:
    
    """Mixin for giving a set-like class the imglookup() operation.
    For CSets, the underlying count information is discarded.
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
        # Always use repr() on the items, even if we were called as
        # str(), to conform to the built-in set's behavior.
        return '{' + ', '.join(repr(item) for item in self) + '}'
    
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
    
    def get_children(self):
        return [e for e in self]


class CSet(IncOQType, Counter, ImgLookupMixin):
    
    """Reference-counted set. Supports element-wise operations but
    not all of the bulk operations that Set has.
    """
    
    # Implemented on top of Counter for the most part. There's some
    # overhead for the element and refcount manipulation operations
    # since they're implemented in Python.
    
    def _fmt_helper(self, fmt):
        # Include reference counts for str() only.
        # Always use repr() for the items.
        if fmt is str:
            return '{' + ', '.join(repr(item) for item in self) + '}'
        elif fmt is repr:
            return ('{' + ', '.join(repr(item) + ': ' + str(count)
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
    
    def get_children(self):
        # Counts are not relevant to our space usage for get_size().
        return [e for e in self]


class Map(IncOQType, dict, SetFromMapMixin):
    
    """Like dict, but with identity semantics."""
    
    def _fmt_helper(self, fmt):
        return ('{' + ', '.join('{}: {}'.format(fmt(key), fmt(value))
                                for key, value in self.items()) + '}')
    
    def dictcopy_update(self, other):
        if self is not other:
            self.clear()
            self.update(other)
    
    # Aliased to clear(). We use a separate name so as to not
    # syntactically conflict with the name of the set clearing
    # operation.
    dictclear = dict.clear
    
    def get_children(self):
        # Both keys and values are children.
        return list(self.keys()) + list(self.values())


class Obj(IncOQType):
    
    """IncOQ object with identity semantics."""
    
    def __init__(self, **init):
        for k, v in init.items():
            setattr(self, k, v)
    
    def get_fields(self):
        """Return a list of (name, value) pairs for each field defined
        on this object (instance), in alphabetic order.
        """
        return [(attr, value) for attr, value in sorted(self.__dict__.items())
                              if not attr.startswith('_')]
    
    def _fmt_helper(self, fmt):
        return ', '.join(attr + '=' + fmt(value)
                         for attr, value in self.get_fields())
    
    def asdict(self):
        return dict(self.get_fields())
    
    def get_children(self):
        return [value for _attr, value in self.get_fields()]


class LRUSet(IncOQType, OrderedDict):
    
    """A set augmented with least-recently-used tracking. Supports
    element-wise operations and clear.
    """
    
    # Implemented on top of OrderedDict where all values are None.
    
    def __init__(self, elems=()):
        super().__init__()
        for e in elems:
            self[e] = None
    
    def _fmt_helper(self, fmt):
        return ('{' + ', '.join('{}'.format(fmt(key))
                                for key in self.keys()) + '}')
    
    def add(self, elem):
        assert elem not in self
        self[elem] = None
    
    def remove(self, elem):
        del self[elem]
    
    def clear(self):
        OrderedDict.clear(self)
    
    def ping(self, elem):
        """Bump elem to the beginning of the LRU priority."""
        self.move_to_end(elem)
    
    def peek(self):
        """Return the last / lowest priority element, or None if empty."""
        return next(iter(self), None)
    
    def pop(self):
        """Remove and return the last / lowest priority element. Must
        not be empty.
        """
        elem = next(iter(self))
        del self[elem]
        return elem
