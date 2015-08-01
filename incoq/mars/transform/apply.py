"""Application of the overall transformation."""


__all__ = [
    'transform_ast',
    'transform_source',
    'transform_file',
]


from incoq.mars.incast import L, P

from .rewritings import (ImportPreprocessor, AttributeDisallower,
                         GeneralCallDisallower)


def transform_ast(input_ast):
    """Take in a Python AST and return the transformed AST."""
    tree = input_ast
    
    # Do some Python rewritings in order to admit some syntactic
    # features that would otherwise be excluded by IncAST.
    tree = ImportPreprocessor.run(tree)
    # Import into IncAST.
    tree = L.import_incast(tree)
    # Check to make sure certain general-case IncAST nodes
    # aren't used.
    AttributeDisallower.run(tree)
    GeneralCallDisallower.run(tree)
    
    # Export back to Python.
    tree = L.export_incast(tree)
    
    return tree


def transform_source(input_source):
    """Take in the Python source code to a module and return the
    transformed source code.
    """
    tree = P.Parser.p(input_source)
    tree = transform_ast(tree)
    source = P.Parser.ts(tree)
    return source


def transform_file(input_filename, output_filename):
    """Take in an input and output path, and write to the output
    the transformed Python file for the given input file.
    """
    with open(input_filename, 'rt') as file:
        source = file.read()
    source = transform_source(source)
    with open(output_filename, 'wt') as file:
        file.write(source)
