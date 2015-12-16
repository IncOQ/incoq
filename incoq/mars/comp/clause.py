"""Clause logic."""


__all__ = [
    'ClauseInfo',
    'RelMemberInfo',
    'SingMemberInfo',
    'WithoutMemberInfo',
    'CondInfo',
    
    'ClauseInfoFactory',
]


from enum import Enum

from simplestruct import Struct, TypedField

from incoq.mars.incast import L


class ClauseInfo(Struct):
    
    """This is the base class for objects that encapsulate a clause and
    provide features relevant for incrementalization.
    """
    
    class Kind(Enum):
        Member = 1
        Cond = 2
    
    kind = None
    
    cl = TypedField(L.clause)
    """AST of clause wrapped by this object."""
    
    @property
    def lhs_vars(self):
        """For membership clauses, left-hand side of the clause. For
        condition clauses, the empty sequence.
        """
        raise NotImplemented
    
    @property
    def rhs_rel(self):
        """For membership clauses over relations (including those that
        use it in a modified way, e.g. WithoutMember), the relation
        name. For all other clauses, None.
        """
        raise NotImplemented
    
    def get_code(self, bindenv, body):
        """Return code to run body for each combination of values of
        lhs vars consistent with the values of the bound vars, given
        by bindenv.
        """
        raise NotImplemented
    
    # Transformations. Each of these methods returns the AST for a
    # transformed clause, which is processed into a ClauseInfo object
    # by ClauseInfoFactory.
    
    def make_sing(self, value):
        """For clauses with non-None rhs_rel, return a version of the
        clause with the relation membership replaced by a singleton
        membership clause. For other clauses raise an error.
        """
        raise NotImplemented
    
    def make_without(self, value):
        """For membership clauses, return the clause wrapped in a
        without membership clause. For conditions raise an error.
        """
        assert self.kind is self.Kind.Member
        return L.WithoutMember(self.cl, value)


class RelMemberInfo(ClauseInfo):
    
    kind = ClauseInfo.Kind.Member
    
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
    
    @property
    def rhs_rel(self):
        return self.rel
    
    def get_code(self, bindenv, body):
        mask = L.mask_from_bounds(self.vars, bindenv)
        bvars, uvars = L.split_by_mask(mask, self.vars)
        lookup = L.ImgLookup(self.rel, mask, bvars)
        return (L.DecompFor(uvars, lookup, body),)
    
    def make_sing(self, value):
        return L.SingMember(self.vars, value)


class SingMemberInfo(ClauseInfo):
    
    kind = ClauseInfo.Kind.Member
    
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
    
    @property
    def rhs_rel(self):
        return None
    
    def get_code(self, bindenv, body):
        mask = L.mask_from_bounds(self.vars, bindenv)
        bindcode = L.bind_by_mask(mask, self.vars, self.value)
        return bindcode + body


class WithoutMemberInfo(ClauseInfo):
    
    kind = ClauseInfo.Kind.Member
    
    _inherit_fields = True
    
    inner = TypedField(ClauseInfo)
    
    @property
    def value(self):
        return self.cl.value
    
    @property
    def lhs_vars(self):
        return self.inner.lhs_vars
    
    @property
    def rhs_rel(self):
        return self.inner.rhs_rel
    
    def get_code(self, bindenv, body):
        new_body = L.Parser.pc('''
            if VARS != VALUE:
                BODY
            ''', subst={'VARS': L.tuplify(self.lhs_vars),
                        'VALUE': self.value,
                        '<c>BODY': body})
        return self.inner.get_code(bindenv, new_body)
    
    def make_sing(self, value):
        new_inner_cl_ast = self.inner.make_sing(value)
        return L.WithoutMember(new_inner_cl_ast, self.value)


class CondInfo(ClauseInfo):
    
    kind = ClauseInfo.Kind.Cond
    
    _inherit_fields = True
    
    @property
    def cond(self):
        return self.cl.cond
    
    @property
    def lhs_vars(self):
        return ()
    
    @property
    def rhs_rel(self):
        return None
    
    def get_code(self, bindenv, body):
        return (L.If(self.cond, body, []),)


class ClauseInfoFactory:
    
    """Factor for producing ClauseInfo objects, both from Clause ASTs
    and other ClauseInfo objects.
    """
    
    # Visitor style dispatch approach to generating ClauseInfos from
    # clause nodes.
    
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
    
    # Transformations.
    
    def make_sing(self, cl, value):
        cl_ast = cl.make_sing(value)
        return self.make_clause_info(cl_ast)
    
    def make_without(self, cl, value):
        cl_ast = cl.make_without(value)
        return self.make_clause_info(cl_ast)
