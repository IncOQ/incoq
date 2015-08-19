"""Pre- and post-processings applied at the IncAST level."""


__all__ = [
    'SetUpdateImporter',
    'AttributeDisallower',
    'GeneralCallDisallower',
    'RelUpdateExporter',
    
    # Main exports.
    'incast_preprocess',
    'incast_postprocess',
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


def incast_preprocess(tree, symtab):
    rels = list(symtab.get_relations().keys())
    # Recognize relation updates.
    tree = SetUpdateImporter.run(tree, rels)
    # Check to make sure certain general-case IncAST nodes
    # aren't used.
    AttributeDisallower.run(tree)
    GeneralCallDisallower.run(tree)
    return tree


def incast_postprocess(tree):
    # Turn relation updates back into set updates.
    tree = RelUpdateExporter.run(tree)
    return tree
