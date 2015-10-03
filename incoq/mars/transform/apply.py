"""Application of the overall transformation."""


__all__ = [
    'transform_ast',
    'transform_source',
    'transform_file',
    'transform_filename',
]


from incoq.mars.incast import L, P
from incoq.mars.types import Bottom
from incoq.mars.type_analysis import analyze_types
from incoq.mars.symtab import SymbolTable
from incoq.mars.auxmap import AuxmapFinder, AuxmapTransformer

from .py_rewritings import py_preprocess, py_postprocess
from .incast_rewritings import incast_preprocess, incast_postprocess


def debug_symbols(symtab, illtyped, badsyms):
    print('---- Symbol info ----')
    print(symtab.dump_symbols())
    print('---- Ill-typed nodes ----')
    for node in illtyped:
        print(L.Parser.ts(node))
    print('---- Ill-typed symbols ----')
    print(', '.join(sym.name for sym in symtab.symbols.values()
                             if sym in badsyms))


def preprocess_tree(tree, symtab):
    """Return a preprocessed tree. Store symbol declarations
    in the symbol table.
    """
    tree = py_preprocess(tree, symtab)
    tree = L.import_incast(tree)
    tree = incast_preprocess(tree, symtab)
    return tree


def postprocess_tree(tree, symtab):
    """Return a post-processed tree."""
    tree = incast_postprocess(tree)
    tree = L.export_incast(tree)
    tree = py_postprocess(tree, symtab)
    return tree


def do_typeinference(tree, symtab):
    """Run type inference, update symbol type info.
    Return a list of nodes where well-typedness is violated,
    and a list of variables where their max type is exceeded.
    """
    # Retrieve current type information (the type store).
    store = {name: sym.min_type if sym.type is None else sym.type 
             for name, sym in symtab.symbols.items()}
    
    # Apply analysis, update saved type info.
    store, illtyped = analyze_types(tree, store)
    badsyms = set()
    for name, type in store.items():
        sym = symtab.symbols[name]
        sym.type = type
        if not type.issmaller(sym.max_type):
            badsyms.add(sym)
    return illtyped, badsyms


def transform_auxmaps(tree, symtab):
    auxmaps = AuxmapFinder.run(tree)
    for auxmap in auxmaps:
        if auxmap.rel not in symtab.get_relations():
            raise L.ProgramError('Cannot make auxiliary map for image-set '
                                 'lookup over non-relation variable {}'
                                 .format(auxmap.rel))
    for auxmap in auxmaps:
        symtab.define_map(auxmap.map)
    tree = AuxmapTransformer.run(tree, auxmaps)
    return tree


def transform_ast(input_ast):
    """Take in a Python AST and return the transformed AST."""
    tree = input_ast
    
    symtab = SymbolTable()
    tree = preprocess_tree(tree, symtab)
    
    illtyped, badsyms = do_typeinference(tree, symtab)
    
#    debug_symbols(symtab, illtyped, badsyms)
    
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
    # All good human beings have trailing newlines in their
    # text files.
    source = source + '\n'
    return source


def transform_file(input_file, output_file):
    """Take in input and output file-like objects, and write to the
    output the transformed Python code corresponding to the input.
    """
    source = input_file.read()
    source = transform_source(source)
    output_file.write(source)


def transform_filename(input_filename, output_filename):
    """Take in an input and output path, and write to the output
    the transformed Python file for the given input file.
    """
    with open(input_filename, 'rt') as file:
        source = file.read()
    source = transform_source(source)
    with open(output_filename, 'wt') as file:
        file.write(source)
