###############################################################################
# collections.py                                                              #
# Author: Jon Brandvein                                                       #
###############################################################################

"""Miscellaneous collection types."""


__all__ = [
    'SetDict',
    'OrderedSetDict',
    'ListDict',
    
    'Registry',
    'SetRegistry',
]


import collections

from .orderedset import OrderedSet


# Shorthands for useful defaultdicts.

class DefaultDict(collections.defaultdict):
    
    kind = None
    
    def __init__(self, *args, **kargs):
        super().__init__(lambda: self.kind(), *args, **kargs)

class SetDict(DefaultDict):
    kind = set

class OrderedSetDict(DefaultDict):
    kind = OrderedSet

class ListDict(DefaultDict):
    kind = list


class Registry(dict):
    
    """Dictionary with strict updates."""
    
    # No args to constructor.
    def __init__(self):
        pass
    
    def register(self, key, value):
        if key in self:
            raise KeyError('"' + str(key) + '" already registered')
        super().__setitem__(key, value)
    
    def deregister(self, key):
        if key not in self:
            raise KeyError('Keyword "' + str(key) + '" not registered')
        super().__delitem__(key)
    
    __setitem__ = register
    __delitem__ = deregister
    
    # Ensure updates go through __setitem__.
    update = collections.MutableMapping.update


class SetRegistry(collections.MutableSet):
    
    """Collection of objects that have unique keys. The collection
    behaves both like a set of the objects and like a mapping from
    object keys to objects. Only the set interface can be used to
    update the registry.
    
    To use, subclass and override the elem_keys() method.
    """
    
    def elem_key(self, elem):
        """Maps elements to a unique key. The key type must be hashable."""
        return elem
    
    
    def __init__(self, seq=None):
        if seq is None:
            seq = []
        self.map = {}
        self.update(seq)
    
    def __eq__(self, other):
        return self is other
    
    __hash__ = None
    
    def __contains__(self, elem):
        key = self.elem_key(elem)
        return key in self.map
    
    def __iter__(self):
        return iter(self.map.values())
    
    def __len__(self):
        return len(self.map)
    
    def __getitem__(self, key):
        return self.map[key]
    
    def keys(self):
        return self.map.keys()
    
    def items(self):
        return self.map.items()
    
    def values(self):
        return self.map.values()
    
    def add(self, elem):
        key = self.elem_key(elem)
        if key in self.map:
            raise KeyError('Element with key "{}" already registered'.format(
                           str(key)))
        self.map[key] = elem
    
    def discard(self, elem):
        key = self.elem_key(elem)
        if key in self.map:
            del self.map[key]
    
    def update(self, seq):
        for item in seq:
            self.add(item)
