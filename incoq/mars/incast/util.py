"""Convenience tools."""


__all__ = [
    'tuplify',
    'detuplify',
    'mask_from_bounds',
    'split_by_mask',
    'bind_by_mask',
    'insert_rel_maint',
]


from . import nodes as L


def tuplify(names):
    """Return a Tuple node of Name nodes for the given identifiers."""
    return L.Tuple([L.Name(n) for n in names])

def detuplify(tup):
    """Given a Tuple node of Name nodes, return a tuple of the
    identifiers.
    """
    if not (isinstance(tup, L.Tuple) and
            all(isinstance(elt, L.Name) for elt in tup.elts)):
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


def insert_rel_maint(update_code, maint_code, op):
    """Insert maintenance code around update code. The maintenance
    goes afterwards for additions and before for removals.
    """
    if isinstance(op, L.SetAdd):
        return update_code + maint_code
    elif isinstance(op, L.SetRemove):
        return maint_code + update_code
    else:
        assert()
