"""Exceptions that support source code printing."""


__all__ = [
    'ProgramError',
    'format_exception_with_ast',
    'print_exc_with_ast',
]


import sys
import traceback


class ProgramError(Exception):
    
    """Problem in the program being transformed. Generally syntactic
    in nature, but may be detected during the middle of transformation.
    """
    
    @classmethod
    def ts(cls, tree):
        """Unparse method to use for AST."""
        # Use the unparser in __init__.py. We can't use
        # structconv.unparse_structast() because the tree
        # may be an IncAST, not a PyAST.
        from . import ts
        return ts(tree)
    
    def __init__(self, *args, node=None, ast_context=None, **kargs):
        super().__init__(*args, **kargs)
        self.node = node
        self.ast_context = ast_context
    
    @classmethod
    def format_ast_context(cls, ast_context):
        """Return a source-code representation of the program, marking
        the occurrence of the node where the problem occurred.
        """
        # Currently we zoom out from the source of the problem,
        # up the ast_context stack, printing more and more code
        # to give context.
        #
        # A better solution may be to print the whole program and
        # enclose the offending node with something like triple
        # angled brackets. But this requires more sophistication
        # in how we reconstruct the location of the offending node
        # in the tree. The information in the node stack alone
        # is likely not enough.
        s = 'AST context (most local node last):\n'
        for node in ast_context:
            s += '==== {} ====\n'.format(type(node).__name__)
            s += cls.ts(node) + '\n'
        return s
    
    @classmethod
    def format_exception(cls, *args,
                         node=None, ast_context=None,
                         **kargs):
        """Like traceback.format_exception(), but also include
        AST context info if present.
        """
        msg = traceback.format_exception(*args, **kargs)
        
        try:
            # This might fail if the tree is malformed or there
            # is a bug in our source-generating code.
            if ast_context is not None:
                msg += '\n' + cls.format_ast_context(ast_context)
            elif node is not None:
                msg += 'Error at {} node:\n{}'.format(
                            type(node).__name__,
                            cls.ts(node))
        except Exception:
            msg += 'Error while attempting to get detailed information:\n'
            msg += traceback.format_exc(**kargs)
        
        return msg
    
    def format_self(self, *args, **kargs):
        """As above, but pull ast context info from this exception
        instance.
        """
        return self.format_exception(
                    *args,
                    node=self.node, ast_context=self.ast_context,
                    **kargs)

def format_exception_with_ast(exctype, value, tb, **kargs):
    """Like traceback.format_exception(), but return additional AST
    context info if the exception is a ProgramError.
    """
    if isinstance(value, ProgramError):
        return value.format_self(exctype, value, tb, **kargs)
    else:
        return traceback.format_exception(exctype, value, tb, **kargs)

def print_exc_with_ast(*, file=None, **kargs):
    """Like traceback.print_exc(), but print additional AST context
    info in case of ProgramError.
    """
    if file is None:
        file = sys.stderr
    msg = format_exception_with_ast(*sys.exc_info(), **kargs)
    print(''.join(msg), file=file)
