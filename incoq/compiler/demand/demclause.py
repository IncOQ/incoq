"""Demand-related clauses."""


__all__ = [
    'DemClause',
    'DemClauseFactory_Mixin',
]


from simplestruct import TypedField
from simplestruct.type import checktype

import incoq.compiler.incast as L
from incoq.compiler.set import Mask
from incoq.compiler.comp import Rate, Clause
from incoq.compiler.comp.clause import (ABCStruct, ClauseFactory,
                                       apply_subst_tuple)


class DemClause(Clause, ABCStruct):
    
    """An enumerator clause who's RHS is the result of a query with
    demand.
    """
    
    kind = Clause.KIND_ENUM
    
    inc_safe = False
    
    cl = TypedField(Clause)
    """Underlying clause."""
    demname = TypedField(str)
    """Demand name."""
    demparams = TypedField(str, seq=True)
    """Demand parameters."""
    
    @property
    def pat_mask(self):
        return self.cl.pat_mask
    
    @property
    def con_mask(self):
        assert len(self.enumlhs) == len(self.cl.con_mask)
        # The underlying mask position must be True and the
        # corresponding var can't be a demparam.
        return tuple(b and v not in self.demparams
                     for v, b in zip(self.enumlhs, self.cl.con_mask))
    
    @property
    def tagsin_mask(self):
        return (v in self.demparams
                for v in self.enumlhs) 
    
    @property
    def tagsout_mask(self):
        return (v not in self.demparams
                for v in self.enumlhs)
    
    @classmethod
    def from_AST(cls, node, factory):
        """Construct from Enumerator node of form
        
            <vars> in DemQuery(...)
        """
        checktype(node, L.Enumerator)
        
        if not isinstance(node.iter, L.DemQuery):
            raise TypeError
        if not all(isinstance(a, L.Name) for a in node.iter.args):
            raise TypeError
        demname = node.iter.demname
        demparams = tuple(a.id for a in node.iter.args)
        rhs = node.iter.value
        
        innernode = node._replace(iter=rhs)
        innerclause = factory.from_AST(innernode)
        
        return cls(innerclause, demname, demparams)
    
    def __init__(self, cl, demname, demparams):
        for attr in [
            'isdelta', 'enumlhs', 'enumrel',
            'vars', 'eqvars', 'constvars', 'robust']:
            setattr(self, attr, getattr(cl, attr))
    
    def to_AST(self):
        code = self.cl.to_AST()
        assert isinstance(code, L.Enumerator)
        code = code._replace(
                    iter=L.DemQuery(self.demname,
                                    tuple(L.ln(p) for p in self.demparams),
                                    code.iter))
        return code
    
    def rewrite_subst(self, subst, factory):
        new_cl = self.cl.rewrite_subst(subst, factory)
        new_demparams = apply_subst_tuple(self.demparams, subst)
        return self._replace(cl=new_cl, demparams=new_demparams)
    
    def rewrite_rel(self, rel, factory):
        new_cl = self.cl.rewrite_rel(rel, factory)
        return self._replace(cl=new_cl)
    
    def subtract_inner(self, excl, factory):
        new_cl = self.cl.subtract_inner(excl, factory)
        return self._replace(cl=new_cl)
    
    def fits_string(self, mask, s):
        return self.cl.fits_string(mask, s)
    
    def rate(self, bindenv):
        # Require demand parameters to be bound.
        mask = Mask.from_vars(self.enumlhs, bindenv)
        bounds, _unbounds, _eqs = mask.split_vars(self.cl.lhs)
        
        if not set(bounds).issuperset(set(self.demparams)):
            return Rate.UNRUNNABLE
        
        return self.cl.rate(bindenv)
    
    def get_code(self, bindenv, body):
        # Just stick a DemQuery node in before the regular code.
        # TODO: This is a little ugly in that it results in
        # littering the code with "None"s. Maybe make a special
        # case in the translation of DemQuery to avoid this.
        code = self.cl.get_code(bindenv, body)
        new_node = L.Expr(value=L.DemQuery(
                    self.demname,
                    tuple(L.ln(p) for p in self.demparams),
                    None))
        code = (new_node,) + code
        return code


class DemClauseFactory_Mixin(ClauseFactory):
    
    @classmethod
    def get_clause_kinds(cls):
        dem_clauses = [DemClause]
        return dem_clauses + super().get_clause_kinds()
