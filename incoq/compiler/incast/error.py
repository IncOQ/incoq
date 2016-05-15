"""Error formatting."""


__all__ = [
    'ProgramError',
    'TransformationError',
    'format_exception',
]


import sys
import traceback

from . import nodes as L
from .pyconv import Parser


class ProgramError(Exception):
    
    """Error in the input or intermediate program being transformed."""
    
    def __init__(self, *args, node=None, **kargs):
        super().__init__(*args, **kargs)
        self.node = node


class TransformationError(Exception):
    
    """Error in our internal state during the transformation."""


def format_exception(type, value, tb,
                     *args, ast_context=None, **kargs):
    """Version of traceback.format_exception() that prints IncAST
    context information after the rest of the traceback.
    """
    lines = traceback.format_exception(type, value, tb, *args, **kargs)
    if ast_context is None:
        ast_context = getattr(value, 'node', None)
    
    if ast_context is not None:
        # Format on one line if there are no breaks, otherwise
        # show an indented code block.
        source = Parser.ts(ast_context)
        multiline = '\n' in source
        if multiline:
            lines += ['AST context:\n']
            lines += ['    ' + line + '\n' for line in source.split('\n')]
        else:
            lines += ['AST context: ' + source + '\n']
    
    return lines


def print_exc(*, file=None, **kargs):
    """Wrapper, analogous to traceback.print_exc()."""
    if file is None:
        file = sys.stderr
    msg = format_exception(*sys.exc_info(), **kargs)
    print(''.join(msg), file=file)
