###############################################################################
# seq.py                                                                      #
# Author: Jon Brandvein                                                       #
###############################################################################

"""Miscellaneous helpers pertaining to sequences and collections."""


__all__ = [
    'zip_strict',
    'no_duplicates',
    'get_duplicates',
    'elim_duplicates',
    'map_tuple',
    'map_tuple_rec',
    'pairs',
]


from itertools import tee, zip_longest


def zip_strict(*iterables):
    """Like zip(), but raise AssertionError if all iterables do not
    exhaust at the same time.
    """
    sentinel = object()
    for elem in zip_longest(*iterables, fillvalue=sentinel):
        if sentinel in elem:
            raise AssertionError('Iterables not exhausted at same time')
        yield elem


def no_duplicates(seq):
    """Returns True if seq contains no duplicate elements,
    False otherwise.
    """
    return len(set(seq)) == len(seq)


def get_duplicates(seq):
    """Given a list with duplicates, return a list without the unique
    items and with just the first occurrence of the duplicate items.
    """
    from collections import Counter
    counts = Counter(seq)
    return list(set(item for item in seq if counts[item] > 1))


def elim_duplicates(seq):
    """Given a sequence with duplicates, return a sequence of the same
    type with only the first occurrence of each item. The sequence's
    type must be constructable from an iterator.
    """
    result = []
    for item in seq:
        if item not in result:
            result.append(item)
    return type(seq)(result)


def map_tuple(func, val):
    """If val is a tuple or a list or n components, return an n-item
    tuple or list of the result of applying func to each component.
    If val is any other type, just apply func to it and return the
    result.
    """
    if isinstance(val, (tuple, list)):
        return type(val)(func(item) for item in val)
    else:
        return func(val)


def map_tuple_rec(func, val):
    """As above, but apply recursively to sub-tuples and sub-lists
    (func is applied post-recursively).
    """
    if isinstance(val, (tuple, list)):
        return type(val)(map_tuple_rec(func, item) for item in val)
    else:
        return func(val)


# Taken from the documentation of the itertools module.
# Renamed from "pairwise" to "pairs", since "pairwise" typically
# means product.
def pairs(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)
