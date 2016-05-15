"""Translation between object and pair domains."""


__all__ = [
    'PairDomainImporter',
    'PairDomainExporter',
]


from incoq.compiler.incast import L
from incoq.compiler.symbol import N


class PairDomainImporter(L.NodeTransformer):
    
    """Transform set, object, and map updates to the pair domain."""
    
    # There are no tuple updates since tuples are immutable.
    
    def __init__(self, fresh_vars, objrels):
        super().__init__()
        self.fresh_vars = fresh_vars
        self.objrels = objrels
    
    def badnode(self, node):
        raise L.TransformationError('{} nodes should not be present when '
                                    'converting to the pair domain'.format(
                                    node.__class__.__name__))
    
    def visit_SetUpdate(self, node):
        if not isinstance(node.op, (L.SetAdd, L.SetRemove)):
            return
        if not self.objrels.M:
            return
        
        pair = L.Tuple([node.target, node.value])
        var = next(self.fresh_vars)
        return (L.Assign(var, pair),
                L.RelUpdate(N.M, node.op, var))
    
    visit_SetBulkUpdate = badnode
    visit_SetClear = badnode
    
    def visit_DictAssign(self, node):
        if not self.objrels.MAP:
            return
        
        triple = L.Tuple([node.target, node.key, node.value])
        var = next(self.fresh_vars)
        return (L.Assign(var, triple),
                L.RelUpdate(N.MAP, L.SetAdd(), var))
    
    def visit_DictDelete(self, node):
        if not self.objrels.MAP:
            return
        
        lookup = L.DictLookup(node.target, node.key, None)
        triple = L.Tuple([node.target, node.key, lookup])
        var = next(self.fresh_vars)
        return (L.Assign(var, triple),
                L.RelUpdate(N.MAP, L.SetRemove(), var))
    
    visit_DictClear = badnode
    
    def visit_AttrAssign(self, node):
        if node.attr not in self.objrels.Fs:
            return
        
        pair = L.Tuple([node.obj, node.value])
        var = next(self.fresh_vars)
        return (L.Assign(var, pair),
                L.RelUpdate(N.F(node.attr), L.SetAdd(), var))
    
    def visit_AttrDelete(self, node):
        if node.attr not in self.objrels.Fs:
            return
        
        lookup = L.Attribute(node.obj, node.attr)
        pair = L.Tuple([node.obj, lookup])
        var = next(self.fresh_vars)
        return (L.Assign(var, pair),
                L.RelUpdate(N.F(node.attr), L.SetRemove(), var))


class PairDomainExporter(L.NodeTransformer):
    
    """Transform all special relation updates back to the object domain."""
    
    def visit_RelUpdate(self, node):
        if isinstance(node.op, L.SetAdd):
            is_add = True
        elif isinstance(node.op, L.SetRemove):
            is_add = False
        else:
            return
        rel = node.rel
        elem = L.Name(node.elem)
        
        if N.is_M(rel):
            set_ = L.Subscript(elem, L.Num(0))
            value = L.Subscript(elem, L.Num(1))
            code = (L.SetUpdate(set_, node.op, value),)
        
        elif N.is_F(rel):
            attr = N.get_F(rel)
            obj = L.Subscript(elem, L.Num(0))
            value = L.Subscript(elem, L.Num(1))
            if is_add:
                code = (L.AttrAssign(obj, attr, value),)
            else:
                code = (L.AttrDelete(obj, attr),)
        
        elif N.is_MAP(rel):
            map = L.Subscript(elem, L.Num(0))
            key = L.Subscript(elem, L.Num(1))
            value = L.Subscript(elem, L.Num(2))
            if is_add:
                code = (L.DictAssign(map, key, value),)
            else:
                code = (L.DictDelete(map, key),)
        
        else:
            code = node
        
        return code
