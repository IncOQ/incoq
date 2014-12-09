"""Conversion between struct representation and Python node
representation. Also exports tools for struct AST manipulation.
"""

# The Python node representation is the form of AST used in the
# standard library's "ast" module, and produced by ast.parse().
# We do not work in this representation. Our native representation
# uses the iast package, which defines nodes as instances of
# simplestruct.Struct. This module converts between the two formats,
# and provides node and AST-level manipulation tools without regard
# to the nodes' semantic meaning.


__all__ = [
    'import_structast',
    'export_structast',
    
    'parse_structast',
    'unparse_structast',
    
    'ProgramError',
    'format_exception_with_ast',
    'print_exc_with_ast',
    
    # Re-exported from iast directly.
    'trim',
    'dump',
    'NodeVisitor',
    'NodeTransformer',
    'Templater',
]


import ast
import copy
import sys
import traceback

import iast
from iast.node import trim, dump
from iast.visitor import NodeVisitor, NodeTransformer
from iast.pattern import make_pattern
from iast.pylang import extract_mod, Templater

from .nodes import incpy_nodes, incstruct_nodes
from . import unparse


# TODO: simplifiy StructImporter and make it not rely on old iast.

class StructImporter:
    
    """Convert from Python representation to struct representation."""
    
    # We're using custom visitor logic here. The tree is still in
    # Python node format so we can't use iast's transformer, and we
    # need to handle being called on sequences so we can't use
    # ast.NodeTransformer.
    #
    # The custom logic simply maps a function across the tree,
    # with no need to worry about the splicing logic of
    # NodeTransformer (since the function is 1:1).
    
    def visit(self, tree):
        if isinstance(tree, ast.AST):
            return self.node_visit(tree)
        elif isinstance(tree, list):
            return self.seq_visit(tree)
        else:
            return tree
    
    def node_visit(self, node):
        new_fields = []
        for field in node._fields:
            value = getattr(node, field)
            new_value = self.visit(value)
            new_fields.append(new_value)
        
        new_nodetype = incstruct_nodes[node.__class__.__name__]
        return new_nodetype(*new_fields)
    
    def seq_visit(self, seq):
        new_seq = []
        for item in seq:
            new_value = self.visit(item)
            new_seq.append(new_value)
        return tuple(new_seq)


class StructExporter(NodeTransformer):
    
    """Convert from struct representation to Python representation."""
    
    def seq_visit(self, seq):
        new_seq = super().seq_visit(seq)
        if new_seq is None:
            new_seq = seq
        return list(new_seq)
    
    def generic_visit(self, node):
        new_node = super().generic_visit(node)
        if new_node is None:
            new_node = node
        node = new_node
        new_nodetype = incpy_nodes[node.__class__.__name__]
        return new_nodetype(*(getattr(node, field) for field in node._fields))

def import_structast(tree):
    """Convert from Python representation to struct representation."""
    return StructImporter().visit(tree)

def export_structast(tree):
    """Convert from struct representation to Python representation."""
    return StructExporter.run(tree)


def parse_structast(source, *, mode=None, subst=None, patterns=False):
    """Version of iast.node.parse() that also runs extract_mod(),
    subst(), and can be used on patterns.
    """
    tree = iast.node.parse(source)
    tree = extract_mod(tree, mode)
    if patterns:
        tree = make_pattern(tree)
    if subst is not None:
        tree = Templater.run(tree, subst)
    return tree


class Unparser(unparse.Unparser):
    
    # Add Comment printing to standard unparser.
    
    def _Comment(self, node):
        if node.text:
            lines = node.text.split('\n')
        else:
            lines = []
        for line in lines:
            self.fill('# ' + line)

def unparse_structast(tree):
    """Unparse from AST to source code."""
    tree = export_structast(tree)
    return Unparser.to_source(tree)


class ProgramError(Exception):
    
    """Problem in the program being transformed. Generally syntactic
    in nature, but may be detected during the middle of transformation.
    """
    
    @classmethod
    def ts(cls, tree):
        """Unparse method to use for AST."""
        # Make sure we correctly handle IncAST nodes.
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
