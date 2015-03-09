###############################################################################
# transform.py                                                                #
# Author: Jon Brandvein                                                       #
###############################################################################

"""Transformation procedure."""


__all__ = [
    'preprocess_tree',
    'transform_ast',
    'transform_source',
    'transform_file',
]


import time

from invinc.util.linecount import get_loc_source
from invinc.util.str import quote_items
import invinc.compiler.incast as L
from invinc.compiler.set import inc_all_relmatch
from invinc.compiler.comp import (
        patternize_comp, depatternize_all, inc_relcomp, 
        impl_auxonly_relcomp, comp_inc_needs_dem,
        comp_isvalid)
from invinc.compiler.aggr import (
        inc_aggr, flatten_smlookups, aggr_needs_batch, aggr_needs_dem,
        aggr_canuse_halfdemand)
from invinc.compiler.obj import to_pairdomain, to_objdomain
from invinc.compiler.demand import deminc_relcomp
from invinc.compiler.tup import (
        flatten_tuples, check_bad_setmatches, flatten_relations)
from invinc.compiler.cost import analyze_costs, eval_coststr

from .manager import get_clause_factory, make_manager
from .rewritings import (DistalgoImporter, get_distalgo_message_sets,
                         MacroSetUpdateRewriter,
                         SetTypeRewriter, ObjTypeRewriter,
                         UpdateRewriter, MinMaxRewriter,
                         eliminate_deadcode, PassEliminator,
                         RelationFinder)


class FunctionUniqueChecker(L.NodeVisitor):
    
    """Raise AssertionError if the same function name is defined more
    than once at the top level.
    """
    
    def process(self, tree):
        self.names = set()
        super().process(tree)
    
    def visit_FunctionDef(self, node):
        assert node.name not in self.names, \
            'Function {} defined multiple times'.format(node.name)
        self.names.add(node.name)

class OrigSetFinder(L.NodeVisitor):
    
    """Find all relation updates in the tree."""
    
    def process(self, tree):
        self.rels = set()
        super().process(tree)
        return self.rels
    
    def visit_SetUpdate(self, node):
        if isinstance(node.target, L.Name):
            self.rels.add(L.get_name(node.target))

class InputQueryMarker(L.QueryMapper):
    """Mark queries with an option to indicate that they are
    from (or correspond to a query in) the input program, as opposed
    to something introduced as a by-product of our transformation.
    """
    
    def map_Comp(self, node):
        new_options = dict(node.options)
        new_options['in_original'] = True
        return node._replace(options=new_options)
    
    def map_Aggregate(self, node):
        new_options = dict(node.options)
        new_options['in_original'] = True
        return node._replace(options=new_options)

def is_original(query):
    return query.options.get('in_original', False)

class OriginalUpdateCounter(L.NodeVisitor):
    
    """Count the number of outermost Maintenance nodes which are
    for one of the specified invariants and specified relations.
    """
    
    def __init__(self, rels, invs):
        super().__init__()
        self.rels = rels
        self.invs = invs
    
    def process(self, tree):
        self.count = 0
        super().process(tree)
        return self.count
    
    def visit_Maintenance(self, node):
        # Figure out whether this is an update to one of the
        # given sets by scanning the description string. Hackish.
        update_node = L.ps(node.desc)
        target = update_node.target
        is_relevant = (isinstance(target, L.Name) and
                       L.get_name(target) in self.rels)
        
        if node.name in self.invs and is_relevant:
            self.count += 1
            # Don't recurse. We don't want to double-count the update,
            # and there shouldn't be any original updates in the
            # inserted precode/postcode.
        else:
            self.generic_visit(node)


class QueryFinder(L.NodeVisitor):
    
    """Find the next query to be transformed and return a pair of
    it along with helper information. Return (None, None) if there
    is no query to be transformed.
    
    To be eligible, the query must have an impl besides 'batch' and
    not have the 'notransform' or '_invalid' options. Innermost queries
    are handled first.
    """
    
    # Helper info format is a dictionary with entries:
    #   'impl':        impl to use (before considering fallbacks)
    #   'in_inccomp':  whether this query appears inside a
    #                  comprehension we expect to incrementalize
    #   'half_demand': (Aggregates only) whether to prefer the half-
    #                  demand strategy over normal demand
    
    class Found(BaseException):
        def __init__(self, node, info):
            self.node = node
            self.info = info
    
    def __init__(self, opman):
        super().__init__()
        self.opman = opman
    
    def get_query_impl(self, query):
        """Given a query, return its impl option if it exists,
        or the global default otherwise. This does not take into
        account optional fallbacks.
        """
        impl = self.opman.get_queryopt(query, 'impl')
        if impl is None:
            impl = self.opman.get_opt('default_impl')
        assert impl in ['batch', 'auxonly', 'inc', 'dem']
        return impl
    
    def process(self, tree):
        # Track the number of comprehensions we're currently inside
        # of that have an impl of 'inc' or 'dem' (i.e., a depth).
        # Used to decide whether an aggregate can fallback to 'inc'.
        self.inccomp_depth = 0
        
        # Traverse, but abort as soon as a query is found.
        try:
            super().process(tree)
        except self.Found as f:
            return f.node, f.info
        else:
            return None, None
    
    def visit_Comp(self, node):
        impl = self.get_query_impl(node)
        inccomp = impl in ['inc', 'dem']
        
        if inccomp:
            self.inccomp_depth += 1
        # (Can raise exception.)
        self.generic_visit(node)
        if inccomp:
            self.inccomp_depth -= 1
        
        # We only get here if there is no inner query to transform.
        if (impl != 'batch' and
            not self.opman.get_queryopt(node, 'notransform') and
            not node.options.get('_invalid', False)):
            info = {'impl': impl,
                    'in_inccomp': self.inccomp_depth > 0}
            raise self.Found(node, info)
    
    def visit_Aggregate(self, node):
        impl = self.get_query_impl(node)
        half_demand = self.opman.get_queryopt(node, 'aggr_halfdemand')
        if half_demand is None:
            half_demand = self.opman.get_opt('default_aggr_halfdemand')
        
        # (Can raise exception.)
        self.generic_visit(node)
        
        if (impl in ['inc', 'dem'] and
            not node.options.get('_invalid', False)):
            info = {'impl': impl,
                    'in_inccomp': self.inccomp_depth > 0,
                    'half_demand': half_demand}
            raise self.Found(node, info)


def transform_query(tree, manager, query, info):
    """Transform a single query. info is the dictionary returned
    by QueryFinder.
    """
    opman = manager.options
    comp_dem_fallback = opman.get_opt('comp_dem_fallback')
    aggr_batch_fallback = opman.get_opt('aggr_batch_fallback')
    aggr_dem_fallback = opman.get_opt('aggr_dem_fallback')
    impl = info['impl']
    in_inccomp = info['in_inccomp']
    
    if isinstance(query, L.Comp):
        # If we can't handle this query, flag it and skip it.
        if is_original(query) and not comp_isvalid(manager, query):
            new_options = dict(query.options)
            new_options['_invalid'] = True
            rewritten_query = query._replace(options=new_options)
            tree = L.QueryReplacer.run(tree, query, rewritten_query)
            
            manager.stats['queries skipped'] += 1
            if manager.options.get_opt('verbose'):
                print('Skipping query ' + L.ts(query))
            return tree
        
        # Flatten lookups (e.g. into aggregate result maps) first,
        # then rewrite patterns. (Opposite order fails to rewrite
        # all occurrences of vars in the condition, since our
        # renamer doesn't catch some cases like demparams of DEMQUERY
        # nodes.)
        rewritten_query = flatten_smlookups(query)
        tree = L.QueryReplacer.run(tree, query, rewritten_query)
        query = rewritten_query
        
        if not opman.get_opt('pattern_in'):
            rewritten_query = patternize_comp(query, manager.factory)
            tree = L.QueryReplacer.run(tree, query, rewritten_query)
            query = rewritten_query
        
        # See if fallback applies.
        if (impl == 'inc' and comp_inc_needs_dem(manager, query) and
            comp_dem_fallback):
            impl = 'dem'
        
        
        name = next(manager.compnamegen)
        
        if impl == 'auxonly':
            tree = impl_auxonly_relcomp(tree, manager, query, name)
            manager.stats['comps expanded'] += 1
        elif impl == 'inc':
            tree = inc_relcomp(tree, manager, query, name)
        elif impl == 'dem':
            tree = deminc_relcomp(tree, manager, query, name)
        else:
            assert()
        
        if impl in ['inc', 'dem']:
            if is_original(query):
                manager.stats['orig queries'] += 1
            manager.stats['incr queries'] += 1
            manager.stats['incr comps'] += 1
    
    elif isinstance(query, L.Aggregate):
        # 'auxonly' doesn't apply to aggregates, but may appear here if
        # it is selected as the default_impl. In any case, treat it as
        # 'batch'.
        if impl == 'auxonly':
            impl = 'batch'
        
        # See if fallbacks apply.
        
        if (impl in ['inc', 'dem'] and aggr_needs_batch(query) and
            aggr_batch_fallback):
            new_options = dict(query.options)
            new_options['_invalid'] = True
            rewritten_query = query._replace(options=new_options)
            tree = L.QueryReplacer.run(tree, query, rewritten_query)
            
            manager.stats['queries skipped'] += 1
            print('Skipping query ' + L.ts(query))
            return tree
        
        if (impl == 'inc' and (in_inccomp or aggr_needs_dem(query)) and
            aggr_dem_fallback):
            impl = 'dem'
        
        if impl in ['inc', 'dem']:
            name = next(manager.aggrnamegen)
            half_demand = (info['half_demand'] and
                           aggr_canuse_halfdemand(query))
            
            tree = inc_aggr(tree, manager, query, name,
                            demand=(impl=='dem'),
                            half_demand=half_demand)
            if is_original(query):
                manager.stats['orig queries'] += 1
            manager.stats['incr queries'] += 1
            manager.stats['incr aggrs'] += 1
        else:
            assert()
    
    
    # Helpful for those long-running transformations.
    manager.stats['queries processed'] += 1
    processed = manager.stats['queries processed']
    if processed % 100 == 0:
        print('---- Transformed {} queries so far  ----'.format(processed))
    
    return tree

def transform_all_queries(tree, manager):
    """Process all queries, innermost first."""
    query, info = QueryFinder.run(tree, manager.options)
    while query is not None:
        tree = transform_query(tree, manager, query, info)
        query, info = QueryFinder.run(tree, manager.options)
    
    # Mark any invalid comprehensions that weren't already found,
    # so we don't try to do any further relational operations on
    # them.
    class Marker(L.QueryMapper):
        def map_Comp(self, node):
            if not comp_isvalid(manager, node):
                new_options = dict(node.options)
                new_options['_invalid'] = True
                return node._replace(options=new_options)
    
    return Marker.run(tree)


def preprocess_tree(manager, tree, opts):
    
    opman = manager.options
    
    tree = DistalgoImporter.run(tree)
    tree = L.import_incast(tree)
    
    # Remove the runtimelib declaration.
    # It will be added back at the end.
    tree = L.remove_runtimelib(tree)
    
    # Complain if there are redundant function definitions.
    FunctionUniqueChecker.run(tree)
    
    # Grab all options.
    tree, opts = L.parse_options(tree, ext_opts=opts)
    nopts, qopts = opts
    opman.import_opts(nopts, qopts)
    
    # Fill in missing param/option info.
    tree, unused = L.attach_qopts_info(tree, opts)
    tree = L.infer_params(tree, obj_domain=opman.get_opt('obj_domain'))
    
    # Error if unused comps in options (prevent typos from causing
    # much frustration).
    if len(unused) > 0:
        raise L.ProgramError('Options given for non-existent queries: ' +
                             quote_items(L.ts(c) for c in unused))
    
    return tree, opman


def elim_inputrel_params(tree, input_rels):
    """For sets that are input relations, remove these sets from
    the parameter lists of queries.
    """
    # XXX: Do this for aggregates as well?
    class Trans(L.QueryMapper):
        def map_Comp(self, node):
            params = tuple(p for p in node.params if p not in input_rels)
            if params != node.params:
                return node._replace(params=params)
    
    return Trans.run(tree)


def transform_ast(tree, *, nopts=None, qopts=None):
    """Take a PyAST and return a transformed output PyAST.
    
    nopts and qopts, if not None, specify additional normal and query
    options respectively. They have dictionary format and override the
    input tree's own option specifications.
    """
    t1 = time.process_time()
    
    if nopts is None:
        nopts = {}
    if qopts is None:
        qopts = {}
    nopts = nopts.copy()
    qopts = qopts.copy()
    
    manager = make_manager()
    
    tree, opman = preprocess_tree(manager, tree, (nopts, qopts))
    
    verbose = opman.get_opt('verbose')
    objdomain = opman.get_opt('obj_domain')
    objdomain_out = objdomain and opman.get_opt('obj_domain_out')
    typecheck = opman.get_opt('maint_emit_typechecks')
    
    manager.factory = get_clause_factory(use_objdomain=objdomain_out,
                                         use_typecheck=typecheck)
    
    # Rewrite set/obj types.
    tree = SetTypeRewriter.run(tree, manager.namegen,
                               set_literals=True, orig_set_comps=False)
    tree = ObjTypeRewriter.run(tree)
    
    # Rewrite macro updates.
    tree = MacroSetUpdateRewriter.run(tree)
    
    input_rels = list(opman.get_opt('input_rels'))
    # Find additional input relations.
    if opman.get_opt('autodetect_input_rels'):
        detected_rels = RelationFinder.run(tree)
        input_rels.extend(r for r in detected_rels
                          if r not in input_rels)
    
    # Get type annotations and cost annotations/
    typeann = opman.get_opt('var_types')
    vartypes = {k: L.parse_typestr(v) for k, v in typeann.items()}
    manager.vartypes = vartypes
    
    flatten_rels = opman.get_opt('flatten_rels')
    
    # DistAlgo message sets may be considered as relations
    # and get flattened.
    if opman.get_opt('flatten_distalgo_messages'):
        for s in get_distalgo_message_sets(tree):
            if s not in flatten_rels:
                flatten_rels.append(s)
            if s not in input_rels:
                input_rels.append(s)
    
    # Do the flattening.
    if len(flatten_rels) > 0:
        if verbose:
            print('Flattening relations: ' + ', '.join(flatten_rels))
        # This will also update the manager vartypes.
        tree = flatten_relations(tree, flatten_rels, manager)
    
    tree = elim_inputrel_params(tree, input_rels)
    
    tree = manager.analyze_types(tree)
    
    # Go to the pair domain.
    if objdomain:
        tree = to_pairdomain(tree, manager, input_rels)
    
    # Rewrite non-trivial update operands.
    tree = UpdateRewriter.run(tree, manager.namegen)
    # Rewrite min/max of set unions.
    # Note: Since this happens after pair-domain transformation,
    # we may end up not turning some aggregate arguments into
    # comps.
    tree = MinMaxRewriter.run(tree)
    
    # Flatten nested tuples in queries.
    tree = flatten_tuples(tree)
    
    # Mark all the queries that exist right now as being from
    # the input program, so we can track statistics for input
    # queries versus intermediate queries that we create.
    tree = InputQueryMarker.run(tree)
    original_sets = OrigSetFinder.run(tree)
    
    # Incrementalize queries.
    tree = transform_all_queries(tree, manager)
    
    if not opman.get_opt('pattern_out'):
        tree = depatternize_all(tree, manager.factory)
    
    tree = SetTypeRewriter.run(tree, manager.namegen,
                               set_literals=False, orig_set_comps=True)
    
    tree = manager.analyze_types(tree)
    
    if opman.get_opt('analyze_costs'):
        print('Analyzing costs')
        tree, costs = analyze_costs(manager, tree, warn=True)
#        for k, v in costs.items():
#            print('{}  --  {}'.format(k, v))
#        tree, costs, domain_subst = analyze_costs(manager, tree, warn=True)
#        manager.stats['funccosts'] = costs
#        manager.stats['domain_subst'] = domain_subst
#        manager.stats['invariants'] = manager.invariants
    
    # For debugging type information.
#    print(L.ts_typed(tree))
    
    # Incrementalize setmatch queries.
    check_bad_setmatches(tree)
    tree = inc_all_relmatch(tree, manager)
    
    # Count updates to original queries.
    updatecount = OriginalUpdateCounter.run(
                    tree, original_sets, manager.original_queryinvs)
    manager.stats['orig updates'] = updatecount
    
    # Eliminate deadcode.
    # Must happen before we return to obj domain, where there
    # could be aliasing.
    if opman.get_opt('deadcode_elim'):
        tree = eliminate_deadcode(
                tree,
                obj_domain_out = opman.get_opt('obj_domain_out'),
                verbose=verbose)
    
    # Go back to the object domain.
    if opman.get_opt('obj_domain') and opman.get_opt('obj_domain_out'):
        tree = to_objdomain(tree, manager)
    
    if opman.get_opt('mode') == 'outline':
        tree = L.maint_skeleton(tree)
    
    # Inline maintenance code if requested.
    # Otherwise, just eliminate unused maintenance functions.
    maintfunc_pred = lambda n: n.startswith('_maint_')
    if opman.get_opt('maint_inline'):
        if verbose:
            print('Inlining maintenance functions')
        funcnames = list(L.FuncDefLister.run(tree, maintfunc_pred).keys())
        tree = L.inline_functions(tree, funcnames)
    else:
        if verbose:
            print('Eliminating dead functions')
        tree = L.elim_deadfuncs(tree, maintfunc_pred)
    
    # Expand maintenance nodes away.
    tree = L.MaintExpander.run(tree)
    
    # Eliminate redundant Pass statements. Occurs after eliminating
    # Maint nodes, since that flattens multiple bodies of code
    # together and makes it possible to eliminate more Passes.
    if opman.get_opt('deadcode_elim'):
        tree = PassEliminator.run(tree)
    
    # Add header comments.
    tree = tree._replace(body=tuple(manager.header_comments) + tree.body)
    
    # Convert back to Python AST format.
    tree = L.add_runtimelib(tree)
    tree = L.export_program(tree)
    
    t2 = time.process_time()
    manager.stats['trans time'] = t2 - t1
    
    if verbose:
        print()
    
    return tree, manager

def transform_source(source, *, nopts=None, qopts=None):
    """Like transform_ast, but from source code to source code."""
    tree = L.p(source)
    
    tree, manager = transform_ast(tree, nopts=nopts, qopts=qopts)
    
    result = L.ts(tree)
    manager.stats['lines'] = get_loc_source(result)
    return result, manager

def transform_file(in_filename, out_filename, *, nopts=None, qopts=None):
    """Like transform_ast, but from file to file, and no return value."""
    with open(in_filename, 'r') as in_file:
        in_source = in_file.read()
    
    out_source, manager = transform_source(in_source, nopts=nopts, qopts=qopts)
    
    eol = manager.options.get_opt('eol')
    eol = {'lf': '\n', 'crlf': '\r\n', 'native': None}[eol]
    
    with open(out_filename, 'w', newline=eol) as out_file:
        out_file.write(out_source)
    
    return manager.stats
