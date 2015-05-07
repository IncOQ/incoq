###############################################################################
# partitioning.py                                                             #
# Author: Jon Brandvein                                                       #
###############################################################################

"""Partitioning type."""


__all__ = [
    'Partitioning',
    'SingleAssignmentDict',
]


from collections import MutableMapping

from incoq.util.seq import pairs


class Partitioning:
    
    """Simple class to do union-find. Not particularly efficient,
    but deterministic.
    """
    
    # Each partition is a list, and the partitioning as a whole is
    # a list of these lists. Lists of lists are used rather than
    # sets to ensure determinism (e.g., for predictable unit test
    # results).
    #
    # Invariant: The partitions are disjoint.
    
    @classmethod
    def from_equivs(cls, equivs):
        """Form from a sequence of possibly non-disjoint equivalence
        classes. Equivalence classes of size 1 are ignored.
        """
        part = cls()
        for eq in equivs:
            for x, y in pairs(eq):
                part.equate(x, y)
        return part
    
    def __init__(self, partitions=[]):
        # Two levels of copying (not arbitrarily deep copy).
        self.partitions = [list(part) for part in partitions]
        
        # Check invariant.
        self._check_disjointness()
    
    def elements(self):
        return [elem for part in self.partitions for elem in part]
    
    def _check_disjointness(self):
        all_elems = self.elements()
        assert len(set(all_elems)) == len(all_elems)
    
    def equate(self, x, y):
        """Update the partitioning to ensure that x and y are in the
        same partition, merging their respective partitions if they
        exist and are distinct.
        
        This operation will always move y into x's partition rather than
        the other way around. This means that the representative of x's
        partition (which is x itself if it is a singleton partition) is
        not changed by this operation. This is useful e.g. for helping
        to ensure that x is preserved in the final set of
        representatives.
        """
        if x == y:
            return
        
        # Find partitions.
        px = py = None
        for part in self.partitions:
            if x in part:
                px = part
            if y in part:
                py = part
        
        # Create new partition.
        if px is None and py is None:
            pxy = [x, y]
            self.partitions.append(pxy)
        
        # Merge existing partitions.
        elif px is not None and py is not None:
            if px is py:
                pass
            else:
                self.partitions.remove(py)
                px.extend(py)
        
        # Add one element to existing partition.
        elif px is not None and py is None:
            px.append(y)
        elif px is None and py is not None:
            # Make x the new representative of py.
            py.insert(0, x)
        
        else:
            assert()
    
    def find(self, x):
        """Return the representative element for x's partition.
        If x is not in the partitioning, return x.
        """
        for part in self.partitions:
            if x in part:
                return part[0]
        else:
            return x
    
    def to_sets(self):
        """Return frozenset-of-frozensets representation."""
        return frozenset(frozenset(p) for p in self.partitions)
    
    def to_subst(self):
        """Return a mapping from each element to its representative."""
        return {elem: self.find(elem) for elem in self.elements()}


class SingleAssignmentDict(MutableMapping, dict):
    
    """A mapping that raises an error if an attempt is made to
    change the value of a key without first deleting it.
    """
    
    __slots__ = ()
    
    # Be careful to use the dict methods, not the
    # MutableMapping abstract stub methods.
    
    __getitem__ = dict.__getitem__
    __delitem__ = dict.__delitem__
    __iter__ = dict.__iter__
    __len__ = dict.__len__
    
    def __setitem__(self, key, value):
        if key in self:
            assert self[key] == value, \
                'Inconsistent values for key {}: {} and {}'.format(
                key, self[key], value)
        dict.__setitem__(self, key, value)
