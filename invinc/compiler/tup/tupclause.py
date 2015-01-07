"""Clauses for tuple relations."""


__all__ = [
    'TClause',
    'TClause_NoTC',
    'TupClauseFactory_Mixin',
]


from simplestruct.type import checktype
from simplestruct import TypedField

import invinc.compiler.incast as L
from invinc.compiler.set import Mask
from invinc.compiler.comp import (ClauseFactory, Rate, EnumClause,
                                vars_from_tuple)

from .tuprel import is_trel, get_trel, make_trel, trel_bindmatch


class TClause(EnumClause):
    
    """An enumerator over a tuple relation."""
    
    tup = TypedField(str)
    """Var for tuple object."""
    elts = TypedField(str, seq=True)
    """Vars for tuple elements."""
    
    @property
    def arity(self):
        return len(self.elts)
    
    typecheck = True
    
    # The elements of a tuple are reachable so long as the tuple
    # itself is. Therefore, we'll set the element positions as
    # constrained and force the tuple object position to get
    # constrained from somewhere else.
    @property
    def con_mask(self):
        return (False,) + tuple(True for _ in self.elts)
    
    @property
    def tagsin_mask(self):
        return (True,) + tuple(False for _ in self.elts)
    
    @property
    def tagsout_mask(self):
        return (False,) + tuple(True for _ in self.elts)
    
    def get_domain_constrs(self, prefix):
        constrs = []
        
        subdoms = [prefix + self.tup + '.' + str(i)
                   for i in range(1, len(self.elts) + 1)]
        constr = (prefix + self.tup, tuple(['<T>'] + subdoms))
        constrs.append(constr)
        
        for i, e in enumerate(self.elts, 1):
            constr = (prefix + self.tup + '.' + str(i), prefix + e)
            constrs.append(constr)
        
        return constrs
    
    def get_membership_constrs(self):
        edges = []
        
        for i, e in enumerate(self.elts, 1):
            edges.append((e, self.tup, i))
        
        return tuple(edges)
    
    @classmethod
    def from_AST(cls, node, factory):
        """Construct from enumerator of form
        
            (tupvar, elt1, ..., eltn) in _TUPN
        """
        checktype(node, L.Enumerator)
        
        lhs = L.get_vartuple(node.target)
        rel = L.get_name(node.iter)
        if not is_trel(rel):
            raise TypeError
        
        tup, *elts = lhs
        arity = get_trel(rel)
        assert arity == len(elts)
        
        return cls(tup, tuple(elts))
    
    def __init__(self, tup, elts):
        assert self.arity >= 2
        self.lhs = (tup,) + tuple(elts)
        self.rel = make_trel(self.arity)
        self.eltvars = vars_from_tuple(self.elts)
        super().__init__(self.lhs, self.rel)
    
    # TODO: Shouldn't rate() and get_code() also allow the special
    # case of going from all bound components to the tuple value
    # composed of these components, in constant time with no auxmap
    # needed?
    
    def rate(self, bindenv):
        mask = Mask.from_vars(self.lhs, bindenv)
        if mask.is_allunbound:
            return Rate.UNRUNNABLE
        elif mask.parts[0] == 'b':
            return Rate.CONSTANT
        return super().rate(bindenv)
    
    def get_determined_vars(self, bindenv):
        if self.tup in bindenv:
            # All elements are determined by the tuple variable.
            return self.eltvars
        else:
            # The tuple variable is determined by the elements.
            return (self.tup,)
    
    def get_code(self, bindenv, body):
        mask = Mask.from_vars(self.lhs, bindenv)
        assert not mask.is_allunbound
        return trel_bindmatch(make_trel(self.arity),
                              mask, self.lhs, body,
                              typecheck=self.typecheck)

class TClause_NoTC(TClause):
    
    """TClause without type checks in emitted code."""
    
    tup = TypedField(str)
    elts = TypedField(str, seq=True)
    
    typecheck = False


class TupClauseFactory_Mixin(ClauseFactory):
    
    """Factory that's aware of tuple clauses."""
    
    @classmethod
    def get_clause_kinds(cls):
        if cls.typecheck:
            tup_clauses = [TClause]
        else:
            tup_clauses = [TClause_NoTC]
        return tup_clauses + super().get_clause_kinds()
