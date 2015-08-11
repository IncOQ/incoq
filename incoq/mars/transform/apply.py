"""Application of the overall transformation."""


__all__ = [
    'transform_ast',
    'transform_source',
    'transform_file',
]


from incoq.mars.incast import L, P
from incoq.mars.symtab import SymbolTable
from incoq.mars.auxmap import AuxmapFinder, AuxmapTransformer

from .rewritings import (ExpressionPreprocessor, RuntimeImportPreprocessor,
                         MainCallRemover, preprocess_vardecls,
                         SetUpdateImporter,
                         AttributeDisallower, GeneralCallDisallower,
                         RelUpdateExporter,
                         postprocess_vardecls, MainCallAdder,
                         RuntimeImportPostprocessor, PassPostprocessor)


def preprocess_tree(tree, symtab):
    """Return a preprocessed tree. Store relation declarations
    in the symbol table.
    """
    # Admit some constructs as syntactic sugar that would otherwise
    # be excluded from IncAST.
    tree = ExpressionPreprocessor.run(tree)
    
    # Get rid of import statement and qualifiers for the runtime
    # library.
    tree = RuntimeImportPreprocessor.run(tree)
    
    # Get rid of main boilerplate.
    tree = MainCallRemover.run(tree)
    
    # Get relation declarations.
    tree, rels = preprocess_vardecls(tree)
    symtab.rels.update(rels)
    
    # Import into IncAST.
    tree = L.import_incast(tree)
    
    # Recognize relation updates.
    tree = SetUpdateImporter.run(tree, symtab.rels)
    
    # Check to make sure certain general-case IncAST nodes
    # aren't used.
    AttributeDisallower.run(tree)
    GeneralCallDisallower.run(tree)
    
    return tree


def postprocess_tree(tree, symtab):
    """Return a post-processed tree."""
    # Turn relation updates back into set updates.
    tree = RelUpdateExporter.run(tree)
    
    # Export back to Python.
    tree = L.export_incast(tree)
    
    # Add in declarations for relations.
    tree = postprocess_vardecls(tree, symtab.rels, symtab.maps)
    
    # Add in main boilerplate, if main() is defined.
    tree = MainCallAdder.run(tree)
    
    # Add the runtime import statement.
    tree = RuntimeImportPostprocessor.run(tree)
    
    # Correct any missing Pass statements.
    tree = PassPostprocessor.run(tree)
    
    return tree


def transform_auxmaps(tree, symtab):
    auxmaps = AuxmapFinder.run(tree)
    symtab.maps.update(auxmap.map for auxmap in auxmaps)
    tree = AuxmapTransformer.run(tree, auxmaps)
    return tree


def transform_ast(input_ast):
    """Take in a Python AST and return the transformed AST."""
    tree = input_ast
    
    symtab = SymbolTable()
    tree = preprocess_tree(tree, symtab)
    
    # Incrementalize image-set lookups with auxiliary maps.
    tree = transform_auxmaps(tree, symtab)
    
    tree = postprocess_tree(tree, symtab)
    
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
