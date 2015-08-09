"""Built-in features needed for input and output programs."""


__all__ = [
    'OPTIONS',
    
    'IncOQType',
    'Set',
]


from reprlib import recursive_repr


# These act as syntactic directives for the transformation system.
# Execution wise, they are no-ops.

def OPTIONS(*args, **kargs):
    pass


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
    __ne__ = object.__ne__


class Set(IncOQType, set):
    
    """IncOQ Set. This differs from Python sets in that it has identity
    semantics and can therefore be hashed.
    """
    
    # This class is mostly implemented by directly inheriting
    # from the built-in set, for speed. Each wrapper call to a
    # Python-level function introduces noticeable overhead.
    
    def _fmt_helper(self, fmt):
        return '{' + ', '.join(fmt(item) for item in self) + '}'
    
    def __getstate__(self):
        return set(self)
    
    def __setstate__(self, state):
        self.update(state)
    
    # The built-in set class provides the following updates:
    #
    #   - add() and remove()
    #   - update() (union) and intersection_update()
    #   - difference_update() and symmetric_difference_update()
    #   - clear()
    #
    # The only other update we need to add is assign_update().
    
    def assign_update(self, other):
        if self is not other:
            self.clear()
            self.update(other)
