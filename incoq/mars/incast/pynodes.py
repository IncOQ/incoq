"""Utilities for Struct Python nodes, including conversion between
these nodes and native Python nodes.
"""


__all__ = [
    'python_nodes',
    
    # Programmatically include Python nodes.
    # ...
    
    'Parser',
    
    # Exports from iast.
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

from .unparse import Unparser


# Flood the module namespace with python nodes.
for name, node in python_nodes.items():
    __all__.append(name)
    globals()[name] = node


class Parser:
    
    """Namespace for parsing functions."""
    
    @classmethod
    def parse(cls, source, *, mode=None, #subst=None,
              patterns=False):
        """Version of iast.python.python34.parse() that also runs
        extract_tree(), subst(), and can be used on patterns.
        """
        tree = _parse(source)
        tree = extract_tree(tree, mode)
        if patterns:
            tree = make_pattern(tree)
#        if subst is not None:
#            tree = Templater.run(tree, subst)
        return tree
    
    # Aliases and shorthands.
    
    @classmethod
    def p(cls, *args, **kargs):
        return cls.parse(*args, **kargs)
    
    @classmethod
    def pc(cls, *args, **kargs):
        return cls.p(*args, mode='code', **kargs)
    
    @classmethod
    def ps(cls, *args, **kargs):
        return cls.p(*args, mode='stmt', **kargs)
    
    @classmethod
    def pe(cls, *args, **kargs):
        return cls.p(*args, mode='expr', **kargs)
    
    @classmethod
    def unparse(cls, tree):
        """Convert to source code string."""
        # The unparser package requires native Python nodes.
        tree = structToPy(tree)
        return Unparser.to_source(tree)
    
    @classmethod
    def ts(cls, *args, **kargs):
        return cls.unparse(*args, **kargs)
