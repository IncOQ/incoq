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
    'literal_eval',
]


from iast.python.python34 import (parse as _parse, extract_tree,
                                  make_pattern, Templater,
                                  pyToStruct, structToPy,
                                  MacroProcessor, ContextSetter,
                                  literal_eval,
                                  py_nodes as python_nodes)

from incoq.util.misc import flood_namespace, new_namespace

from . import iast_common
from .iast_common import ExtractMixin
from .unparse import Unparser

P = new_namespace(python_nodes)


# Flood the module namespace with Python nodes and iAST exports.
flood_namespace(globals(), python_nodes)
flood_namespace(globals(), iast_common)


class CommentUnparser(Unparser):
    
    """Unparser that turns a special COMMENT construct into
    an actual lexical comment in the emitted source code.
    
    The recognized pattern has the form:
    
        Expr(Call(Name('COMMENT', Load()),
                  [Str(<TEXT>)],
                  [], None, None))
    """
    
    # Dependency injection: Make the unparser use our Struct AST nodes.
    ast = P
    
    def _Expr(self, tree):
        value = tree.value
        if (isinstance(value, P.Call) and
            isinstance(value.func, P.Name) and
            value.func.id == 'COMMENT' and
            isinstance(value.func.ctx, P.Load) and
            len(value.args) == 1 and
            isinstance(value.args[0], P.Str) and
            len(value.keywords) == 0 and
            value.starargs is None and
            value.kwargs is None):
            
            text = value.args[0].s
            lines = text.split('\n')
            for line in lines:
                self.fill('# ' + line)
        
        else:
            super()._Expr(tree)


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
        return CommentUnparser.to_source(tree)
