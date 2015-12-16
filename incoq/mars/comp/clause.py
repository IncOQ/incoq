"""Clause logic."""


__all__ = [
    'ClauseInfo',
    'RelMemberInfo',
    'SingMemberInfo',
    'WithoutMemberInfo',
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
    def lhs_vars(self):
        """For membership clauses, left-hand side of the clause. For
        condition clauses, the empty sequence.
        """
        raise NotImplemented
    
    def get_code(self, bindenv, body):
        """Return code to run body for each combination of values of
        lhs vars consistent with the values of the bound vars, given
        by bindenv.
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
    def lhs_vars(self):
        return self.vars
    
    def get_code(self, bindenv, body):
        mask = L.mask_from_bounds(self.vars, bindenv)
        bvars, uvars = L.split_by_mask(mask, self.vars)
        lookup = L.ImgLookup(self.rel, mask, bvars)
        return (L.DecompFor(uvars, lookup, body),)


class SingMemberInfo(ClauseInfo):
    
    _inherit_fields = True
    
    @property
    def vars(self):
        return self.cl.vars
    
    @property
    def value(self):
        return self.cl.value
    
    @property
    def lhs_vars(self):
        return self.vars
    
    def get_code(self, bindenv, body):
        mask = L.mask_from_bounds(self.vars, bindenv)
        bindcode = L.bind_by_mask(mask, self.vars, self.value)
        return bindcode + body


class WithoutMemberInfo(ClauseInfo):
    
    _inherit_fields = True
    
    inner = TypedField(ClauseInfo)
    
    @property
    def value(self):
        return self.cl.value
    
    @property
    def lhs_vars(self):
        return self.inner.lhs_vars
    
    def get_code(self, bindenv, body):
        new_body = L.Parser.pc('''
            if VARS != VALUE:
                BODY
            ''', subst={'VARS': L.tuplify(self.lhs_vars),
                        'VALUE': self.value,
                        '<c>BODY': body})
        return self.inner.get_code(bindenv, new_body)


class CondInfo(ClauseInfo):
    
    _inherit_fields = True
    
    @property
    def cond(self):
        return self.cl.cond
    
    @property
    def lhs_vars(self):
        return ()
    
    def get_code(self, bindenv, body):
        return (L.If(self.cond, body, []),)


class ClauseInfoFactory:
    
    """Given a clause node, produce a ClauseInfo object of the
    appropriate type to wrap it.
    """
    
    def make_clause_info(self, node):
        handler_name = 'handle_' + node.__class__.__name__
        handler = getattr(self, handler_name, None)
        if handler is None:
            raise ValueError('No handler for unknown clause {}'.format(
                             node.__class__.__name__))
        return handler(node)
    
    def handle_RelMember(self, node):
        return RelMemberInfo(node)
    
    def handle_SingMember(self, node):
        return SingMemberInfo(node)
    
    def handle_WithoutMember(self, node):
        inner = self.make_clause_info(node.cl)
        return WithoutMemberInfo(node, inner)
    
    def handle_Cond(self, node):
        return CondInfo(node)
