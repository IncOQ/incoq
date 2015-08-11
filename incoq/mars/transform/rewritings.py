"""Pre- and post-processing rewritings."""


__all__ = [
    'SetUpdateImporter',
    'AttributeDisallower',
    'GeneralCallDisallower',
    'RelUpdateExporter',
]


from incoq.mars.incast import L


class SetUpdateImporter(L.NodeTransformer):
    
    """Replace SetUpdate nodes on known relations variables with
    RelUpdate nodes.
    """
    
    def __init__(self, rels):
        super().__init__()
        self.rels = rels
    
    def visit_SetUpdate(self, node):
        if (isinstance(node.target, L.Name) and
            node.target.id in self.rels):
            return L.RelUpdate(node.target.id, node.op, node.value)
        return node


class AttributeDisallower(L.NodeVisitor):
    
    """Fail if there are any Attribute nodes in the tree."""
    
    def visit_Attribute(self, node):
        raise TypeError('IncAST does not allow attributes')


class GeneralCallDisallower(L.NodeVisitor):
    
    """Fail if there are any GeneralCall nodes in the tree."""
    
    def visit_GeneralCall(self, node):
        raise TypeError('IncAST function calls must be directly '
                        'by function name')


class RelUpdateExporter(L.NodeTransformer):
    
    def visit_RelUpdate(self, node):
        return L.SetUpdate(L.Name(node.rel), node.op, node.value)
