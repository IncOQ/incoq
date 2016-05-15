"""IncAST node definitions and core node-based utilities."""


__all__ = [
    'incast_nodes',
    
    'ident_fields',
    
    'literal_eval',
    'frozen_literal_eval',
    
    # Programmatically include IncAST nodes.
    # ...
    
    # Programmatically re-export iAST features.
    # ...
]


from os.path import join, dirname
from iast import parse_asdl, nodes_from_asdl
from iast.node import ASDLImporter
from iast.python.python34 import literal_eval as _literal_eval

from incoq.util.misc import flood_namespace, freeze

from . import iast_common


# Read and generate nodes from incast.asdl.
incast_asdl_filename = join(dirname(__file__), 'incast.asdl')
with open(incast_asdl_filename, 'rt') as file:
    incast_asdl = parse_asdl(file.read())

incast_nodes = nodes_from_asdl(incast_asdl,
                               module=__name__,
                               typed=True)


# Generate a list of locations of fields that have "identifier" type.
# This is used to help visitors grab all occurrences of identifiers,
# filtering by context.
asdl_info = ASDLImporter().run(incast_asdl)
ident_fields = {}
for node, (fields, _base) in asdl_info.items():
    for fn, ft, _fq in fields:
        if ft == 'identifier':
            ident_fields.setdefault(node, []).append(fn)


# Patch the auto-generated node classes.
def mask_init(self, m):
    if not all(c == 'b' or c == 'u' for c in m):
        raise ValueError('Bad mask string: ' + repr(m))
    self.m = m
incast_nodes['mask'].__init__ = mask_init


# As it happens, the implementation of iAST's literal_eval() can be
# reused for IncAST.
literal_eval = _literal_eval

def frozen_literal_eval(tree):
    value = literal_eval(tree)
    value = freeze(value)
    return value


# Flood the module namespace with node definitions and iAST exports.
flood_namespace(globals(), incast_nodes)
flood_namespace(globals(), iast_common)
