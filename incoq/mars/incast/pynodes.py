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

from . import iast_common
from .iast_common import ExtractMixin
from .unparse import Unparser


# Flood the module namespace with python nodes.
for name, node in python_nodes.items():
    __all__.append(name)
    globals()[name] = node

# Flood the module namespace with iAST exports.
for k, v in iast_common.__dict__.items():
    __all__.append(k)
    globals()[k] = v


class Parser(ExtractMixin):
    
    """Namespace for parsing functions."""
    
    @classmethod
    def action(cls, source, *, mode=None, #subst=None,
               patterns=False):
        """Version of iast.python.python34.parse() that also runs
        extract_tree(), subst(), and can be used on patterns.
        """
        tree = _parse(source)
        tree = extract_tree(tree, mode)
        if patterns:
            tree = make_pattern(tree)
        # TODO: Re-enable subst
#        if subst is not None:
#            tree = Templater.run(tree, subst)
        return tree
    
    @classmethod
    def unaction(cls, tree):
        """Convert to source code string."""
        # The unparser package requires native Python nodes.
        tree = structToPy(tree)
        return Unparser.to_source(tree)
