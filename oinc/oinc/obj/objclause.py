"""Comprehension clauses over M/F-sets."""


__all__ = [
    'MClause',
    'MClause_NoTC',
    'FClause',
    'FClause_NoTC',
    'MapClause',
    'MapClause_NoTC',
    'ObjClauseFactory_Mixin',
]


from simplestruct.type import checktype
from simplestruct import Field

import invinc.incast as L
from invinc.set import Mask
from invinc.comp import (ClauseFactory, Rate, EnumClause)
from invinc.comp.clause import ABCStruct

from .match import mset_bindmatch, fset_bindmatch, mapset_bindmatch
from .pairrel import (is_mrel, make_mrel, is_frel, get_frel_field, make_frel,
                      is_maprel, make_maprel)


class MClause(EnumClause, ABCStruct):
    
    """An enumerator over the M-set."""
    
    cont = Field(str)
    item = Field(str)
    
    pat_mask = (False, True)
    con_mask = (False, True)
    tagsin_mask = (True, False)
    tagsout_mask = (False, True)
    
    def get_domain_constrs(self, prefix):
        return ()
    
    def get_membership_constrs(self):
        return ()
    
    typecheck = True
    
    @classmethod
    def from_expr(cls, node):
        """Construct from a membership expression
        
            (<var>, <var>) in _M
        """
        checktype(node, L.AST)
        
        left, op, right = L.get_cmp(node)
        checktype(op, L.In)
        lhs = L.get_vartuple(left)
        assert len(lhs) == 2
        cont, item = lhs
        rel = L.get_name(right)
        assert is_mrel(rel)
        return cls(cont, item)
    
    @classmethod
    def from_AST(cls, node, factory):
        """Construct from Enumerator node of form
        
            (<var>, <var>) in _M
        """
        checktype(node, L.Enumerator)
        
        lhs = L.get_vartuple(node.target)
        rel = L.get_name(node.iter)
        if not len(lhs) == 2:
            raise TypeError
        cont, item = lhs
        if not is_mrel(rel):
            raise TypeError
        return cls(cont, item)
    
    def __init__(self, cont, item):
        self.lhs = (cont, item)
        self.rel = make_mrel()
        super().__init__(self.lhs, self.rel)
    
    def rate(self, bindenv):
        mask = Mask.from_vars(self.lhs, bindenv)
        if mask.is_allunbound:
            return Rate.UNRUNNABLE
        return super().rate(bindenv)
    
    def get_code(self, bindenv, body):
        mask = Mask.from_vars(self.lhs, bindenv)
        bvars, uvars, _eqs = mask.split_vars(self.lhs)
        return mset_bindmatch(mask, bvars, uvars, body,
                              typecheck=self.typecheck)

class MClause_NoTC(MClause):
    
    """MClause without type checks in emitted code."""
    
    cont = Field(str)
    item = Field(str)
    
    typecheck = False


class FClause(EnumClause, ABCStruct):
    
    """An enumerator over an F-set."""
    
    cont = Field(str)
    item = Field(str)
    field = Field(str)
    
    pat_mask = (False, True)
    con_mask = (False, True)
    tagsin_mask = (True, False)
    tagsout_mask = (False, True)
    
    def get_domain_constrs(self, prefix):
        return ()
    
    def get_membership_constrs(self):
        return ()
    
    typecheck = True
    
    @classmethod
    def from_expr(cls, node):
        """Construct from a membership expression
        
            (<var>, <var>) in _F_<field>
        """
        checktype(node, L.AST)
        
        left, op, right = L.get_cmp(node)
        checktype(op, L.In)
        lhs = L.get_vartuple(left)
        assert len(lhs) == 2
        cont, item = lhs
        rel = L.get_name(right)
        assert is_frel(rel)
        field = get_frel_field(rel)
        return cls(cont, item, field)
    
    @classmethod
    def from_AST(cls, node, factory):
        """Construct from Enumerator node of form
        
            (<var>, <var>) in _F_<field>
        """
        checktype(node, L.Enumerator)
        
        lhs = L.get_vartuple(node.target)
        rel = L.get_name(node.iter)
        if not len(lhs) == 2:
            raise TypeError
        cont, item = lhs
        if not is_frel(rel):
            raise TypeError
        field = get_frel_field(rel)
        return cls(cont, item, field)
    
    def __init__(self, cont, item, field):
        self.lhs = (cont, item)
        self.rel = make_frel(field)
        super().__init__(self.lhs, self.rel)
    
    def rate(self, bindenv):
        mask = Mask.from_vars(self.lhs, bindenv)
        if mask.is_allunbound:
            return Rate.UNRUNNABLE
        elif mask == Mask.OUT:
            return Rate.CONSTANT
        return super().rate(bindenv)
    
    def get_determined_vars(self, bindenv):
        if self.cont in bindenv and self.item != '_':
            return (self.item,)
        else:
            return ()
    
    def get_code(self, bindenv, body):
        mask = Mask.from_vars(self.lhs, bindenv)
        bvars, uvars, _eqs = mask.split_vars(self.lhs)
        return fset_bindmatch(self.field, mask, bvars, uvars, body,
                              typecheck=self.typecheck)

class FClause_NoTC(FClause):
    
    """FClause without type checks in emitted code."""
    
    cont = Field(str)
    item = Field(str)
    field = Field(str)
    
    typecheck = False


class MapClause(EnumClause, ABCStruct):
    
    """An enumerator over the MAP set."""
    
    map = Field(str)
    key = Field(str)
    value = Field(str)
    
    pat_mask = (False, True, True)
    con_mask = (False, False, True)
    tagsin_mask = (True, False, False)
    tagsout_mask = (False, True, True)
    
    def get_domain_constrs(self, prefix):
        return ()
    
    def get_membership_constrs(self):
        return ()
    
    typecheck = True
    
    @classmethod
    def from_expr(cls, node):
        """Construct from a membership expression
        
            (<var>, <var>, <var>) in _MAP
        """
        checktype(node, L.AST)
        
        left, op, right = L.get_cmp(node)
        checktype(op, L.In)
        lhs = L.get_vartuple(left)
        assert len(lhs) == 3
        map, key, value = lhs
        rel = L.get_name(right)
        assert is_maprel(rel)
        return cls(map, key, value)
    
    @classmethod
    def from_AST(cls, node, factory):
        """Construct from Enumerator node of form
        
            (<var>, <var>, <var>) in _MAP
        """
        checktype(node, L.Enumerator)
        
        lhs = L.get_vartuple(node.target)
        rel = L.get_name(node.iter)
        if not len(lhs) == 3:
            raise TypeError
        map, key, value = lhs
        if not is_maprel(rel):
            raise TypeError
        return cls(map, key, value)
    
    def __init__(self, map, key, value):
        self.lhs = (map, key, value)
        self.rel = make_maprel()
        super().__init__(self.lhs, self.rel)
    
    def rate(self, bindenv):
        mask = Mask.from_vars(self.lhs, bindenv)
        if mask.is_allunbound:
            return Rate.UNRUNNABLE
        elif (mask.parts[0] == 'b' and
              (mask.parts[1] == 'b' or mask.parts[1] == '1')):
            return Rate.CONSTANT
        return super().rate(bindenv)
    
    def get_code(self, bindenv, body):
        mask = Mask.from_vars(self.lhs, bindenv)
        bvars, uvars, _eqs = mask.split_vars(self.lhs)
        return mapset_bindmatch(mask, bvars, uvars, body,
                                typecheck=self.typecheck)

class MapClause_NoTC(MapClause):
    
    """MapClause without type checks in emitted code."""
    
    map = Field(str)
    key = Field(str)
    value = Field(str)
    
    typecheck = False


class ObjClauseFactory_Mixin(ClauseFactory):
    
    """Factory that's aware of object clauses."""
    
    objdomain = True
    """Hook for disabling object domain clauses."""
    
    @classmethod
    def get_clause_kinds(cls):
        if cls.objdomain:
            if cls.typecheck:
                pair_clauses = [MClause, FClause, MapClause]
            else:
                pair_clauses = [MClause_NoTC, FClause_NoTC, MapClause_NoTC]
        else:
            pair_clauses = []
        return pair_clauses + super().get_clause_kinds()
