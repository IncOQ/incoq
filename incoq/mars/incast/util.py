"""Convenience tools."""


__all__ = [
    'is_tuple_of_names',
    'tuplify',
    'detuplify',
    'mask_from_bounds',
    'split_by_mask',
    'bind_by_mask',
    'set_update',
    'rel_update',
    'insert_rel_maint',
    'set_update_name',
    'apply_renamer',
]


from . import nodes as L
from .pyconv import Parser


def is_tuple_of_names(node):
    return (isinstance(node, L.Tuple) and
            all(isinstance(elt, L.Name) for elt in node.elts))

def tuplify(names):
    """Return a Tuple node of Name nodes for the given identifiers."""
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


_add_template = '''
if _ELEM not in _SET:
    _SET.{REL}add(_ELEM)
else:
    _SET.{REL}inccount(_ELEM)
'''
_remove_template = '''
if _SET.getcount(_ELEM) == 1:
    _SET.{REL}remove(_ELEM)
else:
    _SET.{REL}deccount(_ELEM)
'''

def set_update(set_, op, elem, *, counted, rel=False):
    """Make a counted or uncounted set add or remove operation."""
    assert isinstance(op, (L.SetAdd, L.SetRemove))
    
    if counted:
        subst = {'_SET': set_, '_ELEM': elem}
        template = {L.SetAdd: _add_template,
                    L.SetRemove: _remove_template}[op.__class__]
        template = template.format(REL='rel' if rel else '')
        code = Parser.pc(template, subst=subst)
    else:
        nodecls = L.RelUpdate if rel else L.SetUpdate
        code = (nodecls(set_, op, elem),)
    return code

def rel_update(rel, op, elem, *, counted):
    return set_update(rel, op, elem,
                      counted=counted, rel=True)


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


def set_update_name(op):
    return {L.SetAdd: 'add',
            L.SetRemove: 'remove',
            L.IncCount: 'inccount',
            L.DecCount: 'deccount'}[op.__class__]


def apply_renamer(tree, renamer):
    """Apply a renamer function to each Name node."""
    class Trans(L.NodeTransformer):
        def visit_Name(self, node):
            new_id = renamer(node.id)
            return node._replace(id=new_id)
    return Trans.run(tree)
