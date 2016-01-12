"""Convenience tools."""


__all__ = [
    'set_update',
    'rel_update',
    'insert_rel_maint',
    'set_update_name',
    'apply_renamer',
]


from . import nodes as L
from .pyconv import Parser


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
