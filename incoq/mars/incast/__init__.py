"""Basic features for manipulating Python and IncAST code."""


from . import nodes
from . import pynodes as P
from . import pyconv


class L:
    """Namespace for IncAST language operations."""

def export_L(namespace):
    """Export operations from a given namespace into the L namespace."""
    for k, v in namespace.__dict__.items():
        setattr(L, k, v)

export_L(nodes)
export_L(pyconv)
