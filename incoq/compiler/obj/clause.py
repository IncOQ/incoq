"""Relational clauses for object-domain concepts."""


__all__ = [
    'MMemberHandler',
    'FMemberHandler',
    'MAPMemberHandler',
    'TUPMemberHandler',
    
    'MMemberHandler_NoTC',
    'FMemberHandler_NoTC',
    'MAPMemberHandler_NoTC',
    'TUPMemberHandler_NoTC',
    
    'ObjClauseVisitor',
    'ObjClauseVisitor_NoTC',
]


from incoq.compiler.incast import L
from incoq.compiler.symbol import N
from incoq.compiler.comp import (ClauseVisitor, RelMemberHandler,
                             Priority, assert_unique)


# rename_rhs_rel() can be used to go from an object clause to an
# ordinary RelMember clause, but not vice versa.


class MMemberHandler(RelMemberHandler):
    
    use_typecheck = True
    
    def lhs_vars(self, cl):
        return (cl.set, cl.elem)
    
    def rhs_rel(self, cl):
        return N.M
    
    def constrained_mask(self, cl):
        return (False, True)
    
    def filter_needs_preds(self, cl):
        return True
    
    def get_code(self, cl, bindenv, body):
        vars = self.lhs_vars(cl)
        assert_unique(vars)
        mask = L.mask_from_bounds(vars, bindenv)
        
        if L.mask_is_allbound(mask):
            comparison = L.Compare(L.Name(cl.elem), L.In(), L.Name(cl.set))
            code = (L.If(comparison, body, ()),)
            needs_typecheck = True
        
        elif mask == L.mask('bu'):
            code = (L.For(cl.elem, L.Name(cl.set), body),)
            needs_typecheck = True
        
        else:
            code = super().get_code(cl, bindenv, body)
            needs_typecheck = False
        
        if needs_typecheck and self.use_typecheck:
            code = (L.If(L.IsSet(L.Name(cl.set)), code, ()),)
        
        return code
    
    def rename_lhs_vars(self, cl, renamer):
        set = renamer(cl.set)
        elem = renamer(cl.elem)
        return cl._replace(set=set, elem=elem)


class FMemberHandler(RelMemberHandler):
    
    use_typecheck = True
    
    def lhs_vars(self, cl):
        return (cl.obj, cl.value)
    
    def rhs_rel(self, cl):
        return N.F(cl.attr)
    
    def constrained_mask(self, cl):
        return (False, True)
    
    def filter_needs_preds(self, cl):
        return True
    
    def functionally_determines(self, cl, bindenv):
        mask = L.mask_from_bounds(self.lhs_vars(cl), bindenv)
        
        if mask == L.mask('bu'):
            return True
        else:
            return super().functionally_determines(cl, bindenv)
    
    def get_priority(self, cl, bindenv):
        mask = L.mask_from_bounds(self.lhs_vars(cl), bindenv)
        
        if mask == L.mask('bu'):
            return Priority.Constant
        else:
            return super().get_priority(cl, bindenv)
    
    def get_code(self, cl, bindenv, body):
        vars = self.lhs_vars(cl)
        assert_unique(vars)
        mask = L.mask_from_bounds(vars, bindenv)
        
        if L.mask_is_allbound(mask):
            comparison = L.Compare(L.Name(cl.value), L.Eq(),
                                   L.Attribute(L.Name(cl.obj), cl.attr))
            code = (L.If(comparison, body, ()),)
            needs_typecheck = True
        
        elif mask == L.mask('bu'):
            code = (L.Assign(cl.value, L.Attribute(L.Name(cl.obj), cl.attr)),)
            code += body
            needs_typecheck = True
        
        else:
            code = super().get_code(cl, bindenv, body)
            needs_typecheck = False
        
        if needs_typecheck and self.use_typecheck:
            code = (L.If(L.HasField(L.Name(cl.obj), cl.attr), code, ()),)
        
        return code
    
    def rename_lhs_vars(self, cl, renamer):
        obj = renamer(cl.obj)
        value = renamer(cl.value)
        return cl._replace(obj=obj, value=value)


class MAPMemberHandler(RelMemberHandler):
    
    use_typecheck = True
    
    def lhs_vars(self, cl):
        return (cl.map, cl.key, cl.value)
    
    def rhs_rel(self, cl):
        return N.MAP
    
    def constrained_mask(self, cl):
        return (False, True, True)
    
    def filter_needs_preds(self, cl):
        return True
    
    def functionally_determines(self, cl, bindenv):
        mask = L.mask_from_bounds(self.lhs_vars(cl), bindenv)
        
        if mask == L.mask('bbu'):
            return True
        else:
            return super().functionally_determines(cl, bindenv)
    
    def get_priority(self, cl, bindenv):
        mask = L.mask_from_bounds(self.lhs_vars(cl), bindenv)
        
        if mask == L.mask('bbu'):
            return Priority.Constant
        else:
            return super().get_priority(cl, bindenv)
    
    def get_code(self, cl, bindenv, body):
        vars = self.lhs_vars(cl)
        assert_unique(vars)
        mask = L.mask_from_bounds(vars, bindenv)
        
        lookup_expr = L.DictLookup(L.Name(cl.map), L.Name(cl.key), None)
        
        if L.mask_is_allbound(mask):
            comparison = L.Compare(L.Name(cl.value), L.Eq(), lookup_expr)
            code = (L.If(comparison, body, ()),)
            needs_typecheck = True
        
        elif mask == L.mask('bbu'):
            code = (L.Assign(cl.value, lookup_expr),)
            code += body
            needs_typecheck = True
        
        elif mask == L.mask('buu'):
            items_expr = L.Parser.pe('_MAP.items()', subst={'_MAP': cl.map})
            code = (L.DecompFor([cl.key, cl.value], items_expr, body),)
            needs_typecheck = True
        
        else:
            code = super().get_code(cl, bindenv, body)
            needs_typecheck = False
        
        if needs_typecheck and self.use_typecheck:
            code = (L.If(L.IsMap(L.Name(cl.map)), code, ()),)
        
        return code
    
    def rename_lhs_vars(self, cl, renamer):
        map = renamer(cl.map)
        key = renamer(cl.key)
        value = renamer(cl.value)
        return cl._replace(map=map, key=key, value=value)


class TUPMemberHandler(RelMemberHandler):
    
    use_typecheck = True
    
    def lhs_vars(self, cl):
        return (cl.tup,) + cl.elts
    
    def rhs_rel(self, cl):
        return N.TUP(len(cl.elts))
    
    def constrained_mask(self, cl):
        return (False,) + tuple(True for _ in cl.elts)
    
    def filter_needs_preds(self, cl):
        return True
    
    def functionally_determines(self, cl, bindenv):
        mask = L.mask_from_bounds(self.lhs_vars(cl), bindenv)
        
        if mask.m[0] == 'b':
            return True
        else:
            return super().functionally_determines(cl, bindenv)
    
    def get_priority(self, cl, bindenv):
        mask = L.mask_from_bounds(self.lhs_vars(cl), bindenv)
        
        if mask.m[0] == 'b':
            return Priority.Constant
        else:
            return super().get_priority(cl, bindenv)
    
    def get_code(self, cl, bindenv, body):
        vars = self.lhs_vars(cl)
        assert_unique(vars)
        mask = L.mask_from_bounds(vars, bindenv)
        
        comparison = L.Compare(L.Name(cl.tup), L.Eq(), L.tuplify(cl.elts))
        
        if L.mask_is_allbound(mask):
            code = (L.If(comparison, body, ()),)
            needs_typecheck = True
        
        elif mask.m.startswith('b'):
            elts_mask = L.mask_from_bounds(cl.elts, bindenv)
            code = L.bind_by_mask(elts_mask, cl.elts, L.Name(cl.tup))
            if L.mask_is_allunbound(elts_mask):
                code += body
            else:
                code += (L.If(comparison, body, ()),)
            needs_typecheck = True
        
        elif mask == L.mask('u' + 'b' * len(cl.elts)):
            code = (L.Assign(cl.tup, L.tuplify(cl.elts)),)
            code += body
            needs_typecheck = False
        
        else:
            raise L.TransformationError('Cannot emit code for TUP clause '
                                        'that would require an auxiliary '
                                        'map; use demand filtering')
        
        if needs_typecheck and self.use_typecheck:
            code = (L.If(L.HasArity(L.Name(cl.tup), len(cl.elts)), code, ()),)
        
        return code
    
    def rename_lhs_vars(self, cl, renamer):
        tup = renamer(cl.tup)
        elts = [renamer(elt) for elt in cl.elts]
        return cl._replace(tup=tup, elts=elts)


class MMemberHandler_NoTC(MMemberHandler):
    use_typecheck = False
class FMemberHandler_NoTC(FMemberHandler):
    use_typecheck = False
class MAPMemberHandler_NoTC(MAPMemberHandler):
    use_typecheck = False
class TUPMemberHandler_NoTC(TUPMemberHandler):
    use_typecheck = False


class ObjClauseVisitor(ClauseVisitor):
    
    handlercls_MMember = MMemberHandler
    handlercls_FMember = FMemberHandler
    handlercls_MAPMember = MAPMemberHandler
    handlercls_TUPMember = TUPMemberHandler
    
    def __init__(self):
        super().__init__()
        self.handle_MMember = self.handlercls_MMember(self)
        self.handle_FMember = self.handlercls_FMember(self)
        self.handle_MAPMember = self.handlercls_MAPMember(self)
        self.handle_TUPMember = self.handlercls_TUPMember(self)


class ObjClauseVisitor_NoTC(ObjClauseVisitor):
    
    handlercls_MMember = MMemberHandler_NoTC
    handlercls_FMember = FMemberHandler_NoTC
    handlercls_MAPMember = MAPMemberHandler_NoTC
    handlercls_TUPMember = TUPMemberHandler_NoTC
