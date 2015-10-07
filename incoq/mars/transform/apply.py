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
from incoq.mars.config import Config
from incoq.mars.symtab import SymbolTable
from incoq.mars.auxmap import AuxmapFinder, AuxmapTransformer, define_map

from .py_rewritings import py_preprocess, py_postprocess
from .incast_rewritings import incast_preprocess, incast_postprocess
from .optimize import unwrap_singletons


def debug_symbols(symtab, illtyped, badsyms):
    print('---- Symbol info ----')
    print(symtab.dump_symbols())
    print('---- Ill-typed nodes ----')
    for node in illtyped:
        print(L.Parser.ts(node))
    print('---- Ill-typed symbols ----')
    print(', '.join(sym.name for sym in symtab.symbols.values()
                             if sym in badsyms))


def preprocess_tree(tree, symtab, config):
    """Return a preprocessed tree. Store symbol declarations
    in the symbol table.
    """
    tree = py_preprocess(tree, symtab, config)
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
        define_map(auxmap, symtab)
    tree = AuxmapTransformer.run(tree, auxmaps)
    return tree


def transform_ast(input_ast, *, options=None):
    """Take in a Python AST and return the transformed AST."""
    tree = input_ast
    if options is None:
        options = {}
    
    config = Config()
    config.update(**options)
    
    symtab = SymbolTable()
    tree = preprocess_tree(tree, symtab, config)
    
    illtyped, badsyms = do_typeinference(tree, symtab)
    
    if config.verbose:
        debug_symbols(symtab, illtyped, badsyms)
    
    # Incrementalize image-set lookups with auxiliary maps.
    tree = transform_auxmaps(tree, symtab)
    
    if config.unwrap_singletons:
        tree, rel_names = unwrap_singletons(tree, symtab)
        if config.verbose and len(rel_names) > 0:
            print('Unwrapped relations: ' + ', '.join(sorted(rel_names)))
    
    tree = postprocess_tree(tree, symtab)
    
    return tree


def transform_source(input_source, *, options=None):
    """Take in the Python source code to a module and return the
    transformed source code.
    """
    tree = P.Parser.p(input_source)
    tree = transform_ast(tree, options=options)
    source = P.Parser.ts(tree)
    # All good human beings have trailing newlines in their
    # text files.
    source = source + '\n'
    return source


def transform_file(input_file, output_file, *, options=None):
    """Take in input and output file-like objects, and write to the
    output the transformed Python code corresponding to the input.
    """
    source = input_file.read()
    source = transform_source(source, options=options)
    output_file.write(source)


def transform_filename(input_filename, output_filename, *, options=None):
    """Take in an input and output path, and write to the output
    the transformed Python file for the given input file.
    """
    with open(input_filename, 'rt') as file:
        source = file.read()
    source = transform_source(source, options=options)
    with open(output_filename, 'wt') as file:
        file.write(source)
