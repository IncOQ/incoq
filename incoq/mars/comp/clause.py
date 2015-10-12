"""Clause logic."""


__all__ = [
    'ClauseInfo',
    'RelMemberInfo',
    'CondInfo',
    
    'ClauseInfoFactory',
]


from simplestruct import Struct, TypedField

from incoq.mars.incast import L


class ClauseInfo(Struct):
    
    """This is the base class for objects that encapsulate a clause and
    provide features relevant for incrementalization.
    """
    
    cl = TypedField(L.clause)
    """AST of clause wrapped by this object."""
    
    @property
    def lhsvars(self):
        """For membership clauses, left-hand side of the clause. For
        condition clauses, the empty sequence.
        """
        raise NotImplemented


class RelMemberInfo(ClauseInfo):
    
    _inherit_fields = True
    
    @property
    def vars(self):
        return self.cl.vars
    
    @property
    def rel(self):
        return self.cl.rel
    
    @property
    def lhsvars(self):
        return self.vars
    
    def get_code(self, bindenv, body):
        mask = L.mask_from_bounds(self.vars, bindenv)
        bvars, uvars = L.split_by_mask(mask, self.vars)
        lookup = L.ImgLookup(self.rel, mask, bvars)
        return (L.DecompFor(uvars, lookup, body),)


class CondInfo(ClauseInfo):
    
    _inherit_fields = True
    
    @property
    def cond(self):
        return self.cl.cond
    
    @property
    def lhsvars(self):
        return ()
    
    def get_code(self, bindenv, body):
        return (L.If(self.cond, body, []),)


class ClauseInfoFactory:
    
    """Given a clause node, produce a ClauseInfo object of the
    appropriate type to wrap it.
    """
    
    def make_info(self, node):
        handler_name = 'handle_' + node.__class__.__name__
        handler = getattr(self, handler_name, None)
        if handler is None:
            raise ValueError('No handler for unknown clause {}'.format(
                             node.__class__.__name__))
        return handler(node)
    
    def handle_RelMember(self, node):
        return RelMemberInfo(node)
    
    def handle_Cond(self, node):
        return CondInfo(node)
