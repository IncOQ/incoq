"""Clause logic."""


__all__ = [
    'Kind',
    
    'BaseClauseVisitor',
    'BaseClauseHandler',
    'ClauseVisitor',
    'ClauseHandler',
    
    'RelMemberHandler',
    'SingMemberHandler',
    'WithoutMemberHandler',
    'CondHandler',
    
    'CoreClauseVisitor',
]


from enum import Enum
from functools import partialmethod

from incoq.mars.incast import L


class Kind(Enum):
    Member = 1
    Cond = 2


class BaseClauseVisitor:
    
    """Provides a visitor/transformer framework over clauses.
    
    The ClauseVisitor framework is different from node visitors in that
    its cases are spread throughout ClauseHandler subclasses. Instead of
    having one class define a visitor or transformer, with one method
    for each kind of node, there is one ClauseHandler for each kind of
    node, with one method for each visit or transform operation. This
    allows us to group all the application logic for one kind of clause
    in one spot, at the expense of having to centrally define the same
    set of common operations across all classes in the visitor
    hierarchy.
    """
    
    def visit(self, operation, cl, *args, **kargs):
        clsname = cl.__class__.__name__
        handler = getattr(self, 'handle_' + clsname)
        method = getattr(handler, operation)
        return method(cl, *args, **kargs)
    
    # Individual dispatchers for each operation are defined as
    #     <op_name> = partialmethod('<op_name>')


class BaseClauseHandler:
    
    def __init__(self, visitor):
        self.visitor = visitor
        """Used to dispatch to children."""


class ClauseHandler(BaseClauseHandler):
    
    """Base class for clause handlers."""
    
    def kind(self, cl):
        """Return the kind of clause this is."""
        raise NotImplementedError
    
    def lhs_vars(self, cl):
        """For a membership clause, return a tuple of the variables on
        the left-hand side. For condition clauses, return the empty
        tuple.
        """
        raise NotImplementedError
    
    def rhs_rel(self, cl):
        """For a membership clause over a relation (including clauses
        that qualify their use of the relation, e.g. WithoutMember),
        return the name of the relation. For all other clauses, return
        None.
        """
        raise NotImplementedError
    
    def get_code(self, cl, bindenv, body):
        """Return code to run the body for all combination of LHS vars
        that satisfy the clause and that match the values of the bound
        variables (variables listed in bindenv).
        """
        raise NotImplementedError
    
    def rename_lhs_vars(self, cl, renamer):
        """For a membership clause, apply a renamer function to each
        LHS var and return the new clause. For condition clauses,
        perform a name substitution like for any other AST.
        """
        raise NotImplementedError
    
    def singletonize(self, cl, value):
        """For a membership clause over a relation, return a clause that
        has the same structure but whose right-hand side is a singleton
        set of value. For all other clauses raise an error.
        """
        raise NotImplementedError
    
    def subtract(self, cl, value):
        """For a membership clause, return a modified clause that does
        not run for the given value. For condition clauses, raise an
        error.
        """
        if self.visitor.kind(cl) is not Kind.Member:
            raise NotImplementedError
        return L.WithoutMember(cl, value)


class ClauseVisitor(BaseClauseVisitor):
    
    # Node types.
    
    handlercls_Member = ClauseHandler
    handlercls_RelMember = ClauseHandler
    handlercls_SingMember = ClauseHandler
    handlercls_WithoutMember = ClauseHandler
    handlercls_Cond = ClauseHandler
    
    def __init__(self):
        super().__init__()
        self.handle_Member = self.handlercls_Member(self)
        self.handle_RelMember = self.handlercls_RelMember(self)
        self.handle_SingMember = self.handlercls_SingMember(self)
        self.handle_WithoutMember = self.handlercls_WithoutMember(self)
        self.handle_Cond = self.handlercls_Cond(self)
    
    # Operations.
    
    kind = partialmethod(BaseClauseVisitor.visit, 'kind')
    lhs_vars = partialmethod(BaseClauseVisitor.visit, 'lhs_vars')
    rhs_rel = partialmethod(BaseClauseVisitor.visit, 'rhs_rel')
    get_code = partialmethod(BaseClauseVisitor.visit, 'get_code')
    rename_lhs_vars = partialmethod(BaseClauseVisitor.visit,
                                    'rename_lhs_vars')
    singletonize = partialmethod(BaseClauseVisitor.visit, 'singletonize')
    subtract = partialmethod(BaseClauseVisitor.visit, 'subtract')


class RelMemberHandler(ClauseHandler):
    
    def kind(self, cl):
        return Kind.Member
    
    def lhs_vars(self, cl):
        return cl.vars
    
    def rhs_rel(self, cl):
        return cl.rel
    
    def get_code(self, cl, bindenv, body):
        mask = L.mask_from_bounds(cl.vars, bindenv)
        
        if L.mask_is_allbound(mask):
            comparison = L.Compare(L.tuplify(cl.vars), L.In(), L.Name(cl.rel))
            code = (L.If(comparison, body, ()),)
        
        elif L.mask_is_allunbound(mask):
            code = (L.DecompFor(cl.vars, L.Name(cl.rel), body),)
        
        else:
            bvars, uvars = L.split_by_mask(mask, cl.vars)
            lookup = L.ImgLookup(cl.rel, mask, bvars)
            code = (L.DecompFor(uvars, lookup, body),)
        
        return code
    
    def rename_lhs_vars(self, cl, renamer):
        new_vars = tuple(renamer(v) for v in cl.vars)
        return cl._replace(vars=new_vars)
    
    def singletonize(self, cl, value):
        return L.SingMember(cl.vars, value)


class SingMemberHandler(ClauseHandler):
    
    def kind(self, cl):
        return Kind.Member
    
    def lhs_vars(self, cl):
        return cl.vars
    
    def rhs_rel(self, cl):
        return None
    
    def get_code(self, cl, bindenv, body):
        mask = L.mask_from_bounds(cl.vars, bindenv)
        check_eq = L.Compare(L.tuplify(cl.vars), L.Eq(), cl.value)
        
        if L.mask_is_allbound(mask):
            code = (L.If(check_eq, body, ()),)
        
        elif L.mask_is_allunbound(mask):
            code = (L.DecompAssign(cl.vars, cl.value),)
            code += body
        
        else:
            code = L.bind_by_mask(mask, cl.vars, cl.value)
            code += (L.If(check_eq, body, ()),)
        
        return code
    
    def rename_lhs_vars(self, cl, renamer):
        new_vars = tuple(renamer(v) for v in cl.vars)
        return cl._replace(vars=new_vars)


class WithoutMemberHandler(ClauseHandler):
    
    def kind(self, cl):
        return Kind.Member
    
    def lhs_vars(self, cl):
        return self.visitor.lhs_vars(cl.cl)
    
    def rhs_rel(self, cl):
        return self.visitor.rhs_rel(cl.cl)
    
    def get_code(self, cl, bindenv, body):
        lhs_vars = self.visitor.lhs_vars(cl)
        new_body = L.Parser.pc('''
            if _VARS != _VALUE:
                _BODY
            ''', subst={'_VARS': L.tuplify(lhs_vars),
                        '_VALUE': cl.value,
                        '<c>_BODY': body})
        return self.visitor.get_code(cl.cl, bindenv, new_body)
    
    def rename_lhs_vars(self, cl, renamer):
        new_inner = self.visitor.rename_lhs_vars(cl.cl, renamer)
        return cl._replace(cl=new_inner)
    
    def singletonize(self, cl, value):
        new_inner = self.visitor.singletonize(cl.cl, value)
        return cl._replace(cl=new_inner)


class CondHandler(ClauseHandler):
    
    def kind(self, cl):
        return Kind.Cond
    
    def lhs_vars(self, cl):
        return ()
    
    def rhs_rel(self, cl):
        return None
    
    def get_code(self, cl, bindenv, body):
        return (L.If(cl.cond, body, []),)
    
    def rename_lhs_vars(self, cl, renamer):
        new_cond = L.apply_renamer(cl.cond, renamer)
        return cl._replace(cond=new_cond)


class CoreClauseVisitor(ClauseVisitor):
    
    handlercls_RelMember = RelMemberHandler
    handlercls_SingMember = SingMemberHandler
    handlercls_WithoutMember = WithoutMemberHandler
    handlercls_Cond = CondHandler
