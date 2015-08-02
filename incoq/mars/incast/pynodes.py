"""Utilities for Struct Python nodes, including conversion between
these nodes and native Python nodes.
"""


__all__ = [
    'python_nodes',
    
    # Programmatically include Python nodes.
    # ...
    
    # Programmatically re-export iAST features.
    # ...
    
    'Parser',
    
    # Additional Python-specific exports from iAST.
    'pyToStruct',
    'structToPy',
    'MacroProcessor',
    'ContextSetter',
]


from iast.python.python34 import (parse as _parse, extract_tree,
                                  make_pattern, Templater,
                                  pyToStruct, structToPy,
                                  MacroProcessor, ContextSetter,
                                  py_nodes as python_nodes)

from incoq.util.misc import flood_namespace

from . import iast_common
from .iast_common import ExtractMixin
from .unparse import Unparser


# Flood the module namespace with Python nodes and iAST exports.
flood_namespace(globals(), python_nodes)
flood_namespace(globals(), iast_common)


class Parser(ExtractMixin):
    
    """Struct Python parser/unparser."""
    
    @classmethod
    def action(cls, source, *, mode=None, subst=None,
               patterns=False):
        """Version of iast.python.python34.parse() that also runs
        extract_tree(), subst(), and can be used on patterns.
        """
        tree = _parse(source)
        tree = extract_tree(tree, mode)
        if patterns:
            tree = make_pattern(tree)
        if subst is not None:
            tree = Templater.run(tree, subst)
        return tree
    
    @classmethod
    def unaction(cls, tree):
        """Convert to source code string."""
        # The unparser package requires native Python nodes.
        if isinstance(tree, tuple):
            tree = tuple(structToPy(item) for item in tree)
        else:
            tree = structToPy(tree)
        return Unparser.to_source(tree)
