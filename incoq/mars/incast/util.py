"""Convenience tools."""


__all__ = [
    'set_update',
    'rel_update',
    'insert_rel_maint',
    'insert_rel_maint_call',
    'set_update_name',
    'apply_renamer',
    'Unwrapper',
    'is_injective',
    'get_setunion',
]


from incoq.util.collections import OrderedSet

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


def insert_rel_maint_call(node, func_name):
    """Insert a call to a maintenance function before/after a SetAdd
    or SetRemove, with the element passed as the sole argument.
    """
    assert isinstance(node, L.RelUpdate)
    assert isinstance(node.op, (L.SetAdd, L.SetRemove))
    code = (node,)
    call_code = (L.Expr(L.Call(func_name, [L.Name(node.elem)])),)
    code = insert_rel_maint(code, call_code, node.op)
    return code


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


class Unwrapper(L.NodeTransformer):
    
    """Add an Unwrap node around all Query nodes with one of the
    specified names.
    """
    
    def __init__(self, names):
        super().__init__()
        self.names = names
    
    def visit_Query(self, node):
        node = self.generic_visit(node)
        if node.name in self.names:
            node = L.Unwrap(node)
        return node


def is_injective(expr):
    """Return whether an expression can be guaranteed to be injective,
    i.e., always returns distinct outputs for distinct inputs.
    """
    class Visitor(L.NodeVisitor):
        def process(self, tree):
            self.injective = True
            super().process(tree)
            return self.injective
        
        def generic_visit(self, node):
            self.injective = False
        
        def ok_leaf(self, node):
            return
        
        visit_Num = ok_leaf
        visit_Str = ok_leaf
        visit_NameConstant = ok_leaf
        visit_Name = ok_leaf
        
        def visit_Tuple(self, node):
            for e in node.elts:
                self.visit(e)
    
    assert isinstance(expr, L.expr)
    return Visitor.run(expr)


def get_setunion(tree):
    """Given a set union of several expressions, return a list of the
    expressions. If the given tree is not a union, return a list with
    it as the only element.
    """
    class Visitor(L.NodeVisitor):
        def process(self, tree):
            self.parts = []
            super().process(tree)
            return self.parts
        
        def generic_visit(self, node):
            # Don't recurse. Only traverse BinOps of BitOrs.
            self.parts.append(node)
        
        def visit_BinOp(self, node):
            if isinstance(node.op, L.BitOr):
                self.visit(node.left)
                self.visit(node.right)
            else:
                self.parts.append(node)
    return Visitor.run(tree)
