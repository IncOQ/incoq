"""Node definitions for IncAST, with type information."""


__all__ = [
    'TypeAdder',
    
    # Add in nodes_untyped.__all__
]


from simplestruct import Field
from iast import NodeTransformer

from .nodes_untyped import (__all__ as untyped_all, native_nodes,
                            incast_nodes as incast_nodes_untyped)

__all__.extend(untyped_all)


incast_nodes = incast_nodes_untyped.copy()

# Programmatically generate new versions of all the expr subclasses
# so they contain a "type" field.
expr_node = incast_nodes['expr']
for name, node in incast_nodes.items():
    if issubclass(node, expr_node) and node is not expr_node:
        # Copy the old class's namespace.
        namespace = node.__dict__.copy()
        fields = node._fields + ('type',)
        namespace['_fields'] = fields
        namespace['__module__'] = __name__
        namespace['type'] = Field(default=None)
        # The only base class is expr, which itself remains unchanged.
        assert node.__bases__ == (expr_node,)
        new_node = type(name, (expr_node,), namespace)
        incast_nodes[name] = new_node

globals().update(incast_nodes)


class TypeAdder(NodeTransformer):
    
    """Replace untyped expression nodes with typed ones.
    Use None as the type.
    """
    
    def node_visit(self, node):
        node = self.generic_visit(node)
        
        if isinstance(node, incast_nodes_untyped['expr']):
            new_nodetype = incast_nodes[node.__class__.__name__]
            fieldvals = [getattr(node, f) for f in node._fields]
            fieldvals += [None]
            node = new_nodetype(*fieldvals)
        
        return node
