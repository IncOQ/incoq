"""Translation between object and pair domains."""


__all__ = [
    'PairDomainImporter',
]


from incoq.mars.incast import L
from incoq.mars.symbol import N


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
        
        pair = L.Tuple([node.target, node.value])
        var = next(self.fresh_vars)
        return (L.Assign(var, pair),
                L.RelUpdate(N.M, node.op, var))
    
    visit_SetBulkUpdate = badnode
    visit_SetClear = badnode
    
    def visit_DictAssign(self, node):
        triple = L.Tuple([node.target, node.key, node.value])
        var = next(self.fresh_vars)
        return (L.Assign(var, triple),
                L.RelUpdate(N.MAP, L.SetAdd(), var))
    
    def visit_DictDelete(self, node):
        lookup = L.DictLookup(node.target, node.key, None)
        triple = L.Tuple([node.target, node.key, lookup])
        var = next(self.fresh_vars)
        return (L.Assign(var, triple),
                L.RelUpdate(N.MAP, L.SetRemove(), var))
    
    visit_DictClear = badnode
    
    def visit_AttrAssign(self, node):
        pair = L.Tuple([node.obj, node.value])
        var = next(self.fresh_vars)
        return (L.Assign(var, pair),
                L.RelUpdate(N.F(node.attr), L.SetAdd(), var))
    
    def visit_AttrDelete(self, node):
        lookup = L.Attribute(node.obj, node.attr)
        pair = L.Tuple([node.obj, lookup])
        var = next(self.fresh_vars)
        return (L.Assign(var, pair),
                L.RelUpdate(N.F(node.attr), L.SetRemove(), var))
