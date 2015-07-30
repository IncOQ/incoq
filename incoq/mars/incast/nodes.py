"""IncAST node definitions and core node-based utilities."""


__all__ = [
    'incast_nodes',
    
    # Programmatically include incast nodes.
    # ...
    
    # Re-exported from iast directly.
    'trim',
    'dump',
    'NodeVisitor',
    'AdvNodeVisitor',
    'NodeTransformer',
    'AdvNodeTransformer',
    'PatVar',
]


from os.path import join, dirname

from iast import (parse_asdl, nodes_from_asdl,
                  trim, dump, NodeVisitor, AdvNodeVisitor,
                  NodeTransformer, AdvNodeTransformer,
                  PatVar)


# Read and generate nodes from incast.asdl.
incast_asdl_filename = join(dirname(__file__), 'incast.asdl')
with open(incast_asdl_filename, 'rt') as file:
    incast_asdl = parse_asdl(file.read())

incast_nodes = nodes_from_asdl(incast_asdl,
                               module=__name__,
                               typed=True)

# Flood the module namespace with node definitions.
for name, node in incast_nodes.items():
    __all__.append(name)
    globals()[name] = node
