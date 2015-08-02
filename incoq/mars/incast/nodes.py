"""IncAST node definitions and core node-based utilities."""


__all__ = [
    'incast_nodes',
    
    # Programmatically include IncAST nodes.
    # ...
    
    # Programmatically re-export iAST features.
    # ...
]


from os.path import join, dirname

from iast import parse_asdl, nodes_from_asdl

from incoq.util.misc import flood_namespace

from . import iast_common


# Read and generate nodes from incast.asdl.
incast_asdl_filename = join(dirname(__file__), 'incast.asdl')
with open(incast_asdl_filename, 'rt') as file:
    incast_asdl = parse_asdl(file.read())

incast_nodes = nodes_from_asdl(incast_asdl,
                               module=__name__,
                               typed=True)

# Flood the module namespace with node definitions and iAST exports.
flood_namespace(globals(), incast_nodes)
flood_namespace(globals(), iast_common)
