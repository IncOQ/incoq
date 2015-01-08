"""Conversion between Struct and native formats of PyASTs,
and export of iast features, as well as parsing/unparsing.
"""


__all__ = [
    'import_structast',
    'export_structast',
    
    'parse_structast',
    'unparse_structast',
    
    # Re-exported from iast directly.
    'trim',
    'dump',
    'NodeVisitor',
    'NodeTransformer',
    'Templater',
    'MacroProcessor',
    'ContextSetter',
    'astargs',
    'literal_eval',
    'raw_match',
    'match',
    'MatchFailure',
]


import ast

from iast import (trim, dump, NodeVisitor, NodeTransformer,
                  raw_match, match, MatchFailure)
from iast.python.python34 import (make_pattern, extract_tree, Templater,
                                  parse as _parse, MacroProcessor,
                                  ContextSetter, astargs, literal_eval)

from .nodes import native_nodes, incast_nodes
from . import unparse


# TODO: simplify StructImporter and make it not rely on old iast.

class StructImporter:
    
    """Convert from native AST to Struct AST. Similar in purpose
    to iast.python.native.pyToStruct.
    """
    
    # We're using custom visitor logic here. We can't use
    # iast.NodeTransformer because we're not a Struct AST yet.
    # We can't use ast.NodeTransformer because we need to handle
    # being called on sequences. We can't use iast.python.native.
    # pyToStruct because we need to handle the Comment node type.
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
        
        new_nodetype = incast_nodes[node.__class__.__name__]
        return new_nodetype(*new_fields)
    
    def seq_visit(self, seq):
        new_seq = []
        for item in seq:
            new_value = self.visit(item)
            new_seq.append(new_value)
        return tuple(new_seq)


class StructExporter(NodeTransformer):
    
    """Convert from Struct AST to native AST. Similar in purpose
    to iast.python.native.structToPy."""
    
    # We don't use iast.python.native.structToPy because we need
    # to handle the Comment node.
    
    def seq_visit(self, seq):
        new_seq = super().seq_visit(seq)
        return list(new_seq)
    
    def generic_visit(self, node):
        repls = {}
        for field in node._fields:
            value = getattr(node, field)
            result = self.visit(value)
            repls[field] = result
        
        new_nodetype = native_nodes[node.__class__.__name__]
        return new_nodetype(**repls)

def import_structast(tree):
    """Convert from native AST to Struct AST."""
    return StructImporter().visit(tree)

def export_structast(tree):
    """Convert from Struct AST to native AST."""
    return StructExporter.run(tree)


def parse_structast(source, *, mode=None, subst=None, patterns=False):
    """Version of iast.python.native.parse() that also runs
    extract_tree(), subst(), and can be used on patterns.
    """
    tree = _parse(source)
    tree = extract_tree(tree, mode)
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
    """Unparse from Struct AST to source code."""
    tree = export_structast(tree)
    return Unparser.to_source(tree)
