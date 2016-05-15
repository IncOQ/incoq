"""Mask and tuple manipulations."""


__all__ = [
    'is_tuple_of_names',
    'tuplify',
    'detuplify',
    'mask_from_bounds',
    'keymask_from_len',
    'is_keymask',
    'break_keymask',
    'mapmask_from_len',
    'is_mapmask',
    'break_mapmask',
    'mask_is_allbound',
    'mask_is_allunbound',
    'split_by_mask',
    'combine_by_mask',
    'bind_by_mask',
]


from . import nodes as L


def is_tuple_of_names(node):
    return (isinstance(node, L.Tuple) and
            all(isinstance(elt, L.Name) for elt in node.elts))

def tuplify(names, *, unwrap=False):
    """Return a Tuple node of Name nodes for the given identifiers.
    If unwrap is True, there must be only one name given and a single
    Name node is returned.
    """
    if unwrap:
        assert len(names) == 1
        return L.Name(names[0])
    else:
        return L.Tuple([L.Name(n) for n in names])

def detuplify(tup):
    """Given a Tuple node of Name nodes, return a tuple of the
    identifiers.
    """
    if not is_tuple_of_names(tup):
        raise ValueError('Bad value to detuplify: {}'.format(tup))
    return tuple(elt.id for elt in tup.elts)


def mask_from_bounds(items, bound_items):
    """Return a mask that has one component corresponding to each
    element of items -- a bound component if the item is also in
    bound_items, and an unbound component otherwise.
    """
    # Make sure these aren't generators.
    len(items) and len(bound_items)
    maskstr = ''
    for i in items:
        if i in bound_items:
            maskstr += 'b'
        else:
            maskstr += 'u'
    return L.mask(maskstr)


# A keymask is a mask where all bound components and unbound
# components are consecutive to the left and right, respectively,
# e.g. "bbbuu". Keymasks are used for query result maps.

def keymask_from_len(nb, nu):
    """Return a keymask with the given number of bound and unbound
    components.
    """
    return L.mask('b' * nb + 'u' * nu)

def is_keymask(mask):
    """Return True if mask is a keymask."""
    try:
        break_keymask(mask)
    except ValueError:
        return False
    return True

def break_keymask(mask):
    """Given a keymask, return a pair of the number of bound and unbound
    components.
    """
    m = mask.m
    # i = index of first u = number of 'b's.
    i = m.find('u')
    if i == -1:
        i = len(m)
    bs, us = m[:i], m[i:]
    if not (all(c == 'b' for c in bs) and all(c == 'u' for c in us)):
        raise ValueError('Mask is not keymask')
    return len(bs), len(us)


# A mapmask is a mask where there are any number of bound components
# followed by exactly one unbound component, e.g. "bbbu". Mapmasks are
# used for SetFromMap nodes.

def mapmask_from_len(nb):
    """Return a mapmask with the given number of bound components."""
    return L.mask('b' * nb + 'u')

def is_mapmask(mask):
    """Return True if mask is a mapmask."""
    try:
        break_mapmask(mask)
    except ValueError:
        return False
    return True

def break_mapmask(mask):
    """Given a mapmask, return the number of bound components."""
    m = mask.m
    nb = len(m) - 1
    bs, us = m[:nb], m[nb:]
    if not (all(c == 'b' for c in bs) and all(c == 'u' for c in us)):
        raise ValueError('Mask is not mapmask')
    return nb


def mask_is_allbound(mask):
    """Return True if a mask contains only bound components."""
    return all(c == 'b' for c in mask.m)

def mask_is_allunbound(mask):
    """Return True if a mask contains only unbound components."""
    return all(c == 'u' for c in mask.m)


def split_by_mask(mask, items):
    """Return two lists that partition the elements of items in order.
    The first list has all elements corresponding to a bound component
    in mask, and the second list has all elements corresponding to an
    unbound component. The length of items must equal the number of
    components in the mask.
    """
    assert len(mask.m) == len(items)
    bounds, unbounds = [], []
    for c, i in zip(mask.m, items):
        if c == 'b':
            bounds.append(i)
        elif c == 'u':
            unbounds.append(i)
        else:
            assert()
    return bounds, unbounds


def combine_by_mask(mask, bounds, unbounds):
    """Return a single list that merges bounds and unbounds according
    to the sequence in mask. The combined lengths of bounds and unbounds
    must equal the number of components in the mask. This is effectively
    the inverse of split_by_mask().
    """
    assert len(mask.m) == len(bounds) + len(unbounds)
    result = []
    bi = iter(bounds)
    ui = iter(unbounds)
    for c in mask.m:
        if c == 'b':
            result.append(next(bi))
        elif c == 'u':
            result.append(next(ui))
        else:
            assert()
    return result


def bind_by_mask(mask, lhs, rhs):
    """Return code to bind the items in lhs that correspond
    to unbound components, to the corresponding parts of rhs.
    """
    vars = []
    for c, v in zip(mask.m, lhs):
        if c == 'b':
            vars.append('_')
        elif c == 'u':
            vars.append(v)
        else:
            assert()
    return (L.DecompAssign(vars, rhs),)
