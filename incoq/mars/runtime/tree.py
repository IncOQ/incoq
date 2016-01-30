"""Balanced binary search tree; requires bintrees package."""


__all__ = [
    'Tree',
]


try:
    from bintrees import FastAVLTree
    HAVE_TREES = True
except ImportError:
    HAVE_TREES = False


if HAVE_TREES:
    class Tree(FastAVLTree):
        
        """Binary search tree that modifies the bintrees class by having
        min and max return just the key, not the item pair. It is
        expected that the values will be set to None and ignored.
        
        The __min__() and __max__() operations are non-strict, so that
        they return None if the tree is empty.
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
