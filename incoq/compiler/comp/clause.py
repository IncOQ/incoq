"""Clause logic."""


__all__ = [
    'Kind',
    'ShouldFilter',
    'Priority',
    
    'BaseClauseVisitor',
    'BaseClauseHandler',
    'ClauseHandler',
    'ClauseVisitor',
    
    'assert_unique',
    
    'RelMemberHandler',
    'SingMemberHandler',
    'WithoutMemberHandler',
    'VarsMemberHandler',
    'SetFromMapMemberHandler',
    'CondHandler',
    
    'CoreClauseVisitor',
]


from enum import Enum, IntEnum
from functools import partialmethod
from collections import Counter

from incoq.compiler.incast import L


class Kind(Enum):
    Member = 1
    Cond = 2

class ShouldFilter(Enum):
    No = 1
    Yes = 2
    Intersect = 3

class Priority(IntEnum):
    """Priority for cost heuristic."""
    First = -1
    Constant = 1
    Normal = 10
    Unpreferred = 100


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
        try:
            result = method(cl, *args, **kargs)
        except NotImplementedError:
            raise NotImplementedError('{} on {}: {}'.format(
                                      operation, clsname, L.Parser.ts(cl)))
        return result
    
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
    
    # Mask functions like constrained_mask() return sequences of
    # booleans, one per LHS var, identifying whether or not that
    # position satisfies a property. lhsvars_in_varmask() is used
    # to translate these to the variables at those positions.
    
    def lhsvars_in_varmask(self, cl, mask, invert=False):
        """Helper for defining methods that return LHS vars that are in
        a position covered by the appropriate mask.
        """
        return tuple(v for v, m in zip(self.lhs_vars(cl), mask)
                       if m ^ invert)
    
    def constrained_mask(self, cl):
        """Bool mask identifying positions of constrained LHS vars."""
        # Default behavior: All LHS vars are constrained.
        return tuple(True for _ in self.lhs_vars(cl))
    
    def con_lhs_vars(self, cl):
        return self.lhsvars_in_varmask(cl, self.constrained_mask(cl))
    
    def uncon_lhs_vars(self, cl):
        return self.lhsvars_in_varmask(cl, self.constrained_mask(cl),
                                       invert=True)
    
    def uncon_vars(self, cl):
        """Return a tuple of all variables appearing in the clause,
        ignoring the constrained LHS var positions (although those
        variables may still be included due to other occurrences).
        """
        return self.uncon_lhs_vars(cl)
    
    # For filtering purposes, if there are no unconstrained components
    # then tags can be used to filter, and can be defined for, any
    # component. If there is at least one unconstrained component, then
    # tags can only filter the unconstrained components, and can only
    # be defined for the constrained components.
    
    def tagsin_mask(self, cl):
        """Mask for positions that can be used to filter the clause."""
        uncon = self.uncon_lhs_vars(cl)
        if len(uncon) == 0:
            return tuple(True for _ in self.lhs_vars(cl))
        else:
            return tuple(not m for m in self.constrained_mask(cl))
    
    def tagsout_mask(self, cl):
        """Mask for positions that can define new filters from this
        clause.
        """
        uncon = self.uncon_lhs_vars(cl)
        if len(uncon) == 0:
            return tuple(True for _ in self.lhs_vars(cl))
        else:
            return self.constrained_mask(cl)
    
    def tagsin_lhs_vars(self, cl):
        return self.lhsvars_in_varmask(cl, self.tagsin_mask(cl))
    
    def tagsout_lhs_vars(self, cl):
        return self.lhsvars_in_varmask(cl, self.tagsout_mask(cl))
    
    def should_filter(self, cl, bindenv):
        """For a membership clause, return whether a demand-filtered
        version of this clause should be used for a given binding
        environment. For a condition clause, return False.
        """
        if set(self.tagsin_lhs_vars(cl)).issubset(bindenv):
            return ShouldFilter.No
        else:
            return ShouldFilter.Yes
    
    def filter_needs_preds(self, cl):
        """Return whether a filter over this clause requires at least
        one predecessor tag.
        """
        return False
    
    def functionally_determines(self, cl, bindenv):
        """Return True if in the given binding environment, this clause
        can be satisfied at most once.
        """
        raise NotImplementedError
    
    def get_priority(self, cl, bindenv):
        """Return a priority for the cost heuristic based on the given
        binding environment, or None if running the clause in that
        environment is not allowed.
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
    
    def rename_rhs_rel(self, cl, renamer):
        """For a membership clause, apply a renamer function to the
        RHS relation and return the new clause. For condition clauses,
        no effect.
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
    handlercls_VarsMember = ClauseHandler
    handlercls_SetFromMapMember = ClauseHandler
    handlercls_Cond = ClauseHandler
    
    def __init__(self):
        super().__init__()
        self.handle_Member = self.handlercls_Member(self)
        self.handle_RelMember = self.handlercls_RelMember(self)
        self.handle_SingMember = self.handlercls_SingMember(self)
        self.handle_WithoutMember = self.handlercls_WithoutMember(self)
        self.handle_VarsMember = self.handlercls_VarsMember(self)
        self.handle_SetFromMapMember = self.handlercls_SetFromMapMember(self)
        self.handle_Cond = self.handlercls_Cond(self)
    
    # Visit operations added programmatically.

for op in [
    'kind',
    'lhs_vars',
    'rhs_rel',
    'constrained_mask',
    'con_lhs_vars',
    'uncon_lhs_vars',
    'uncon_vars',
    'tagsin_mask',
    'tagsout_mask',
    'tagsin_lhs_vars',
    'tagsout_lhs_vars',
    'should_filter',
    'filter_needs_preds',
    'functionally_determines',
    'get_priority',
    'get_code',
    'rename_lhs_vars',
    'rename_rhs_rel',
    'singletonize',
    'subtract',
    ]:
    setattr(ClauseVisitor, op, partialmethod(ClauseVisitor.visit, op))


def assert_unique(vars):
    """Given a tuple of LHS vars, raise AssertionError if there are
    repeated vars (representing an equality pattern).
    """
    counts = Counter(vars)
    if not all(c == 1 for c in counts.values()):
        dups = [x for x, c in counts.items() if c > 1]
        raise AssertionError('LHS vars appear multiple times in same '
                             'clause: ' + ', '.join(dups))


class RelMemberHandler(ClauseHandler):
    
    def kind(self, cl):
        return Kind.Member
    
    def lhs_vars(self, cl):
        return cl.vars
    
    def rhs_rel(self, cl):
        return cl.rel
    
    def functionally_determines(self, cl, bindenv):
        return set(bindenv).issuperset(self.lhs_vars(cl))
    
    def get_priority(self, cl, bindenv):
        mask = L.mask_from_bounds(self.lhs_vars(cl), bindenv)
        
        if L.mask_is_allbound(mask):
            return Priority.Constant
        elif L.mask_is_allunbound(mask):
            return Priority.Unpreferred
        else:
            return Priority.Normal
    
    def get_code(self, cl, bindenv, body):
        vars = self.lhs_vars(cl)
        rel = self.rhs_rel(cl)
        assert_unique(vars)
        mask = L.mask_from_bounds(vars, bindenv)
        
        if L.mask_is_allbound(mask):
            comparison = L.Compare(L.tuplify(vars), L.In(), L.Name(rel))
            code = (L.If(comparison, body, ()),)
        
        elif L.mask_is_allunbound(mask):
            code = (L.DecompFor(vars, L.Name(rel), body),)
        
        else:
            bvars, uvars = L.split_by_mask(mask, vars)
            lookup = L.ImgLookup(L.Name(rel), mask, bvars)
            # Optimize in the case where there's only one unbound.
            if len(uvars) == 1:
                code = (L.For(uvars[0], L.Unwrap(lookup), body),)
            else:
                code = (L.DecompFor(uvars, lookup, body),)
        
        return code
    
    def rename_lhs_vars(self, cl, renamer):
        new_vars = tuple(renamer(v) for v in cl.vars)
        return cl._replace(vars=new_vars)
    
    def rename_rhs_rel(self, cl, renamer):
        # Implementation shared by object-clause subclasses.
        new_rel = renamer(self.rhs_rel(cl))
        return L.RelMember(self.lhs_vars(cl), new_rel)
    
    def singletonize(self, cl, value):
        return L.SingMember(self.lhs_vars(cl), value)


class SingMemberHandler(ClauseHandler):
    
    def kind(self, cl):
        return Kind.Member
    
    def lhs_vars(self, cl):
        return cl.vars
    
    def rhs_rel(self, cl):
        return None
    
    def uncon_vars(self, cl):
        return tuple(L.IdentFinder.find_vars(cl.value))
    
    def tagsin_mask(self, cl):
        return tuple(False for _ in self.lhs_vars(cl))
    
    def tagsout_mask(self, cl):
        return tuple(False for _ in self.lhs_vars(cl))
    
    def should_filter(self, cl, bindenv):
        return ShouldFilter.Intersect
    
    def functionally_determines(self, cl, bindenv):
        return True
    
    def get_priority(self, cl, bindenv):
        return Priority.Constant
    
    def get_code(self, cl, bindenv, body):
        assert_unique(cl.vars)
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
    
    def rename_rhs_rel(self, cl, renamer):
        return cl


class WithoutMemberHandler(ClauseHandler):
    
    def kind(self, cl):
        return Kind.Member
    
    def lhs_vars(self, cl):
        return self.visitor.lhs_vars(cl.cl)
    
    def rhs_rel(self, cl):
        return self.visitor.rhs_rel(cl.cl)
    
    def uncon_vars(self, cl):
        inner_result = self.visitor.uncon_vars(cl.cl)
        outer_result = tuple(L.IdentFinder.find_vars(cl.value))
        return inner_result + outer_result
    
    def tagsin_mask(self, cl, bindenv):
        return self.visitor.tagsin_mask(cl.cl, bindenv)
    
    def tagsout_mask(self, cl, bindenv):
        return self.visitor.tagsout_mask(cl.cl, bindenv)
    
    def should_filter(self, cl, bindenv):
        return self.visitor.should_filter(cl.cl, bindenv)
    
    def functionally_determines(self, cl, bindenv):
        return self.visitor.functionally_determines(cl.cl, bindenv)
    
    def get_priority(self, cl, bindenv):
        return self.visitor.get_priority(cl.cl, bindenv)
    
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
    
    def rename_rhs_rel(self, cl, renamer):
        new_inner = self.visitor.rename_rhs_rel(cl.cl, renamer)
        return cl._replace(cl=new_inner)
    
    def singletonize(self, cl, value):
        new_inner = self.visitor.singletonize(cl.cl, value)
        return cl._replace(cl=new_inner)


class VarsMemberHandler(ClauseHandler):
    
    def kind(self, cl):
        return Kind.Member
    
    def lhs_vars(self, cl):
        return cl.vars
    
    def rhs_rel(self, cl):
        return None
    
    def uncon_vars(self, cl):
        # Technically, parameters of comprehensions on the right-hand
        # side may or may not be constrained, but we won't bother with
        # that distinction here.
        return tuple(L.IdentFinder.find_vars(cl.iter))
    
    def rename_lhs_vars(self, cl, renamer):
        new_vars = tuple(renamer(v) for v in cl.vars)
        return cl._replace(vars=new_vars)
    
    def rename_rhs_rel(self, cl, renamer):
        return cl


class SetFromMapMemberHandler(RelMemberHandler):
    
    def functionally_determines(self, cl, bindenv):
        mask = L.mask_from_bounds(cl.vars, bindenv)
        if mask == cl.mask:
            return True
        
        return super().functionally_determines(cl, bindenv)
    
    def get_priority(self, cl, bindenv):
        mask = L.mask_from_bounds(cl.vars, bindenv)
        if mask == cl.mask:
            return Priority.Constant
        
        return super().get_priority(cl, bindenv)
    
    def get_code(self, cl, bindenv, body):
        assert_unique(cl.vars)
        mask = L.mask_from_bounds(cl.vars, bindenv)
        keyvars, valvar = L.split_by_mask(cl.mask, cl.vars)
        valvar = valvar[0]
        
        # Can also handle all-unbound case by iterating over dict.items(),
        # but requires fresh var for decomposing key tuple.
        
        if L.mask_is_allbound(mask):
            comparison = L.Parser.pe('_KEY in _MAP and _MAP[_KEY] == _VALUE',
                                     subst={'_MAP': cl.map,
                                            '_KEY': L.tuplify(keyvars),
                                            '_VALUE': valvar})
            code = (L.If(comparison, body, ()),)
        
        elif mask == cl.mask:
            code = L.Parser.pc('''
                if _KEY in _MAP:
                    _VALUE = _MAP[_KEY]
                    _BODY
                ''', subst={'_MAP': cl.map,
                            '_KEY': L.tuplify(keyvars),
                            '_VALUE': valvar,
                            '<c>_BODY': body})
        
        else:
            code = super().get_code(cl, bindenv, body)
        
        return code


class CondHandler(ClauseHandler):
    
    def kind(self, cl):
        return Kind.Cond
    
    def lhs_vars(self, cl):
        return ()
    
    def rhs_rel(self, cl):
        return None
    
    def uncon_vars(self, cl):
        return tuple(L.IdentFinder.find_vars(cl.cond))
    
    def should_filter(self, cl, bindenv):
        return ShouldFilter.No
    
    def functionally_determines(self, cl, bindenv):
        return True
    
    def get_priority(self, cl, bindenv):
        vars = L.IdentFinder.find_vars(cl.cond)
        if set(vars).issubset(set(bindenv)):
            return Priority.Constant
        else:
            return None
    
    def get_code(self, cl, bindenv, body):
        return (L.If(cl.cond, body, []),)
    
    def rename_lhs_vars(self, cl, renamer):
        new_cond = L.apply_renamer(cl.cond, renamer)
        return cl._replace(cond=new_cond)
    
    def rename_rhs_rel(self, cl, renamer):
        return cl


class CoreClauseVisitor(ClauseVisitor):
    
    handlercls_RelMember = RelMemberHandler
    handlercls_SingMember = SingMemberHandler
    handlercls_WithoutMember = WithoutMemberHandler
    handlercls_VarsMember = VarsMemberHandler
    handlercls_SetFromMapMember = SetFromMapMemberHandler
    handlercls_Cond = CondHandler
