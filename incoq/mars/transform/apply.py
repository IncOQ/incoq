"""Application of the overall transformation."""


__all__ = [
    'QueryNodeFinder',
    
    'transform_ast',
    'transform_source',
    'transform_file',
    'transform_filename',
]


import sys
from itertools import chain
from collections import OrderedDict
import builtins

from incoq.mars.incast import L, P
from incoq.mars.symbol import S, N
from incoq.mars.auxmap import transform_auxmaps
from incoq.mars.comp import (
    CoreClauseTools, transform_comp_query,
    rewrite_all_comps_with_patterns)
from incoq.mars.demand import transform_comp_query_with_filtering
from incoq.mars.aggr import incrementalize_aggr, transform_comps_with_maps
from incoq.mars.obj import (ObjClauseVisitor, ObjClauseVisitor_NoTC,
                            flatten_objdomain, unflatten_objdomain)

from .py_rewritings import py_preprocess, py_postprocess
from .incast_rewritings import incast_preprocess, incast_postprocess
from . import relation_rewritings
from .misc_rewritings import (mark_query_forms, unmark_normal_impl,
                              rewrite_vars_clauses, lift_firstthen)
from .optimize import unwrap_singletons
from .param_analysis import (analyze_params, analyze_demand_params,
                             transform_demand)


class ObjClauseTools(CoreClauseTools, ObjClauseVisitor):
    pass

class ObjClauseTools_NoTC(CoreClauseTools, ObjClauseVisitor_NoTC):
    pass


def debug_symbols(symtab, illtyped, badsyms):
    symtab.print('---- Symbol info ----')
    symtab.print(symtab.dump_symbols())
    symtab.print('---- Ill-typed nodes ----')
    for node in illtyped:
        symtab.print(L.Parser.ts(node))
    symtab.print('---- Ill-typed symbols ----')
    symtab.print(', '.join(sym.name for sym in symtab.symbols.values()
                                    if sym in badsyms))


class QueryNodeFinder(L.NodeVisitor):
    
    """Return a mapping from query name to query expression.
    
    If first is given, return only a tuple of the name and expression of
    the first query found, or None if there is no query. The first query
    is innermost and topmost in the program.
    
    If ignore is given, do not include any query in this sequence.
    """
    
    class Done(BaseException):
        def __init__(self, result):
            self.result = result
    
    def __init__(self, *, first=False, ignore=None):
        super().__init__()
        self.first = first
        self.ignore = ignore
    
    def process(self, tree):
        if self.first:
            try:
                super().process(tree)
            except self.Done as e:
                return e.result
            else:
                return None
        else:
            self.queries = OrderedDict()
            super().process(tree)
            return self.queries
    
    def visit_Query(self, node):
        self.generic_visit(node)
        
        if self.ignore is not None and node.name in self.ignore:
            return
        
        if self.first:
            raise self.Done((node.name, node.query))
        
        # Otherwise...
        if node.name in self.queries:
            if node.query != self.queries[node.name]:
                raise L.ProgramError('Multiple inconsistent expressions for '
                                     'query {}'.format(node.name))
        else:
            self.queries[node.name] = node.query


def preprocess_tree(tree, symtab):
    """Take in a Python AST tree, as well as a symbol table and global
    configuration. Populate the symbol table and configuration, and
    return the preprocessed IncAST tree.
    """
    # Preprocess at the Python level. Obtain parsed information
    # about symbols and directives.
    tree, decls, info = py_preprocess(tree)
    
    # Define symbols for declared relations and maps.
    rels = []
    maps = []
    for var, kind in decls:
        if kind == 'Set':
            rels.append(var)
            symtab.define_relation(var)
        elif kind == 'Map':
            maps.append(var)
            symtab.define_map(var)
        else:
            assert()
    
    # Create query names for parsed query info, and note the attributes.
    query_name_map = {}
    query_name_attrs = {}
    for q, d in info.query_info:
        name = next(symtab.fresh_names.queries)
        query_name_map[q] = name
        query_name_attrs[name] = d
    
    # Continue preprocessing.
    # Maps in the input program aren't currently handled.
    tree = incast_preprocess(tree, fresh_vars=symtab.fresh_names.vars,
                             query_name_map=query_name_map)
    
    # Define symbols for queries.
    queries = QueryNodeFinder.run(tree)
    for name, query in queries.items():
        symtab.define_query(name, node=query)
    
    # Use parsed directive info to update the global config and
    # symbol-specific config.
    for d in info.config_info:
        symtab.config.parse_and_update(**d)
    for name, d in info.symconfig_info:
        symtab.apply_symconfig(name, d)
    for name, d in query_name_attrs.items():
        symtab.apply_symconfig(name, d)
    
    return tree


def postprocess_tree(tree, symtab):
    """Return a post-processed tree."""
    # Get declaration info for relation and map symbols.
    decls = []
    for sym in chain(symtab.get_relations().values(),
                     symtab.get_maps().values()):
        decls.append((sym.name, sym.decl_constructor, sym.decl_comment))
    
    tree = incast_postprocess(tree)
    tree = py_postprocess(tree, decls=decls, header=symtab.header)
    return tree


def transform_query(tree, symtab, query):
    assert query.impl is not S.Unspecified
    
    if isinstance(query.node, L.Comp):
        
        if query.impl == S.Normal:
            success = False
        
        elif query.impl == S.Inc:
            tree = transform_comp_query(tree, symtab, query)
            success = True
        
        elif query.impl == S.Filtered:
            symtab.print('  Comp: ' + L.Parser.ts(query.node))
            tree = transform_comp_query_with_filtering(tree, symtab, query)
            success = True
        
        else:
            assert()
    
    elif isinstance(query.node, (L.Aggr, L.AggrRestr)):
        
        if query.impl == S.Normal:
            success = False
        
        elif query.impl == S.Inc:
            result_var = 'A_' + query.name
            tree = incrementalize_aggr(tree, symtab, query, result_var)
            # Transform any aggregate map lookups inside comprehensions,
            # including incrementalizing the SetFromMaps used in the
            # additional comp clauses.
            tree = transform_comps_with_maps(tree, symtab)
            success = True
        
        else:
            assert()
    
    else:
        raise L.ProgramError('Unknown query kind: {}'.format(
                             query.node.__class__.__name__))
    return tree, success


def transform_queries(tree, symtab):
    def findnext():
        return QueryNodeFinder.run(tree, first=True,
                                   ignore=symtab.ignored_queries)
    
    symtab.print('==== Incrementalizing queries ====')
    result = findnext()
    while result is not None:
        query_name, _query_node = result
        symtab.print('Incrementalizing {}...'.format(query_name))
        query = symtab.get_queries()[query_name]
        tree, success = transform_query(tree, symtab, query)
        if not success:
            symtab.print('  FAILED')
            symtab.ignored_queries.add(query_name)
        result = findnext()
    return tree


def transform_ast(input_ast, *, options=None):
    """Take in a Python AST and return the transformed AST and the
    symbol table.
    """
    tree = input_ast
    if options is None:
        options = {}
    
    config = S.Config()
    config.update(**options)
    
    symtab = S.SymbolTable()
    symtab.config = config
    tree = preprocess_tree(tree, symtab)
    
    if config.auto_query:
        tree = mark_query_forms(tree, symtab)
    
    # Set global default values.
    for q in symtab.get_queries().values():
        if q.impl is S.Unspecified:
            q.impl = symtab.config.default_impl
    # Correct aggregate impls.
    for q in symtab.get_queries().values():
        if isinstance(q.node, L.Aggr) and q.impl is S.Filtered:
            q.impl = S.Inc
    # Eliminate nodes for Normal impl queries.
    tree = unmark_normal_impl(tree, symtab)
    
    # Replace membership conditions with membership clauses.
    tree = relation_rewritings.rewrite_memberconds(tree, symtab)
    # Expand bulk updates. SetClear is not expanded until after we
    # convert occurrences to RelClear.
    tree = relation_rewritings.expand_bulkupdates(tree, symtab)
    # Recognize relation updates.
    tree = relation_rewritings.specialize_rels_and_maps(tree, symtab)
    # Expand SetClear and DictClear.
    tree = relation_rewritings.expand_clear(tree, symtab)
    
    # Make symbols for non-relation, non-map variables.
    names = L.IdentFinder.find_vars(tree)
    names.difference_update(symtab.get_relations().keys(),
                            symtab.get_maps().keys())
    for name in names:
        symtab.define_var(name)
    
    # Run type inference.
    illtyped, badsyms = symtab.run_type_inference(tree)
    
#    debug_symbols(symtab, illtyped, badsyms)
    
    # Rewrite in the pair-domain, if the program is object-domain.
    if config.obj_domain:
        tree = relation_rewritings.relationalize_clauses(tree, symtab)
        tree = flatten_objdomain(tree, symtab)
        symtab.clausetools = ObjClauseTools()
        symtab.clausetools_notc = ObjClauseTools_NoTC()
    else:
        symtab.clausetools = CoreClauseTools()
        symtab.clausetools_notc = CoreClauseTools()
    
    # Normalize to relations.
    tree = relation_rewritings.relationalize_comp_queries(tree, symtab)
    # Rewrite memberships over subqueries as VARS clauses.
    # (In the object domain, this would be done differently
    # due to tuple wrapping/unwrapping.)
    tree = rewrite_vars_clauses(tree, symtab)
    
    # Before we can transform for demand, we need to know the demand
    # params. Before we can do that, we need to rewrite patterns in
    # comprehensions to ensure that parameters are constrained by
    # equalities. Before we can do that, we need to do basic parameter
    # analysis so that the rewriting doesn't discard a parameter in
    # favor of a local.
    
    # Infer parameter information.
    analyze_params(tree, symtab)
    # Rewrite patterns.
    tree = rewrite_all_comps_with_patterns(tree, symtab)
    # Infer demand parameter information.
    analyze_demand_params(tree, symtab)
    # Transform for demand.
    tree = transform_demand(tree, symtab)
    
    # Incrementalize queries.
    tree = transform_queries(tree, symtab)
    
#    if config.verbose:
#        print('---- Ignored queries ----')
#        for sym in symtab.get_queries().values():
#            if sym.name in symtab.ignored_queries:
#                print('{:<10} {}'.format(sym.name + ':',
#                                        L.Parser.ts(sym.node)))
    
    symtab.print('Incrementalizing auxiliary maps')
    
    # Lift FirstThen nodes above Unwrap nodes so Unwraps can be
    # incrementalized.
    tree = lift_firstthen(tree, symtab)
    
    # Incrementalize image-set lookups with auxiliary maps.
    tree = transform_auxmaps(tree, symtab)
    
    if config.obj_domain:
        tree = unflatten_objdomain(tree, symtab)
    
    if config.unwrap_singletons:
        tree, rel_names = unwrap_singletons(tree, symtab)
        if len(rel_names) > 0:
            symtab.print('Unwrapped relations: ' +
                         ', '.join(sorted(rel_names)))
    
    if config.elim_dead_relations:
        tree = relation_rewritings.eliminate_dead_relations(tree, symtab)
    
    # Get comment header.
    header = []
    for query in symtab.get_queries().values():
        if query.display:
            header.append(query.decl_comment)
    symtab.header = header
    
    # Turn relation updates back into set updates.
    tree = relation_rewritings.unspecialize_rels_and_maps(tree, symtab)
    
    tree = postprocess_tree(tree, symtab)
    
    return tree, symtab


def transform_source(input_source, *, options=None):
    """Take in the Python source code to a module and return the
    transformed source code and the symbol table.
    """
    tree = P.Parser.p(input_source)
    tree, symtab = transform_ast(tree, options=options)
    source = P.Parser.ts(tree)
    # All good human beings have trailing newlines in their
    # text files.
    source = source + '\n'
    return source, symtab


def transform_file(input_file, output_file, *, options=None):
    """Take in input and output file-like objects, and write to the
    output the transformed Python code corresponding to the input.
    Return the symbol table.
    """
    source = input_file.read()
    source, symtab = transform_source(source, options=options)
    output_file.write(source)
    return symtab


def transform_filename(input_filename, output_filename, *, options=None):
    """Take in an input and output path, and write to the output
    the transformed Python file for the given input file. Return the
    symbol table.
    
    If the pretend option is given, write to standard output instead of
    the output file. If "-" is given as the input or output filename,
    use standard input or standard output respectively. If there is an
    error reading or transforming the input file, do not open, write to,
    or truncate the output file.
    """
    input_file = None
    output_file = None
    
    stdinput = input_filename == '-'
    try:
        if stdinput:
            input_file = sys.stdin
        else:
            input_file = open(input_filename, 'rt')
        source = input_file.read()
    finally:
        if input_file is not None and not stdinput:
            input_file.close()
    
    source, symtab = transform_source(source, options=options)
    
    stdoutput = output_filename == '-' or symtab.config.pretend
    try:
        if stdoutput:
            output_file = sys.stdout
        else:
            output_file = open(output_filename, 'wt')
        output_file.write(source)
    finally:
        if output_file is not None and not stdoutput:
            output_file.close()
