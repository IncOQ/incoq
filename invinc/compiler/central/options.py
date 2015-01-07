"""Transformation options management."""


__all__ = [
    'OptionsManager',
]


from copy import deepcopy as dc

from invinc.util.str import quote_items
from invinc.util.collections import frozendict
from invinc.compiler.incast import ProgramError


class DefaultNormalOptions:
    verbose =               False
    """If True, output extra information to stdout."""
    
    eol =                   'native'
    """End-of-line markers to use for generated Python file.
    Can be 'lf', 'crlf', or 'native'.
    """
    
    mode =                  'normal'
    """Action to take.
        'normal':      Transform/incrementalize
        'outline':     Only emit outline of maintenance code
    """
    
    obj_domain =            False
    """If True, the input program is expressed in the object domain."""
    obj_domain_out =        True
    """If False, the output program is left in the pair domain
    instead of being converted back to the object domain.
    """
    
    input_rels =            []
    """List of names of sets in the input program that are relations
    and therefore do not need to be flattened. Relations must not be
    aliased or nested inside other values.
    """
    
    autodetect_input_rels = False
    """If True, automatically detect sets in the input program that
    can be considered as relations.
    """
    
    pattern_in =            False
    """If True, the input program is expressed with pattern matching."""
    pattern_out =           False
    """If True, the output program uses pattern matching. Note that
    the output program will not be runnable as Python code.
    """
    
    flatten_rels =          []
    """List of names of relations to try to flatten. Applicable to
    relational domain programs.
    """
    
    flatten_distalgo_messages = True
    """Automatically add sets whose names fit the form of DistAlgo's
    received/sent message sets to flatten_rels. Also treat these sets
    as relations (input_rels).
    """
    
    default_impl =          'batch'
    """Default implementation for queries. One of 'batch', 'auxonly',
    'inc', or 'dem'. 
    """
    
    default_uset_force =    False
    """Default uset_force for queries using inc or dem."""
    
    default_aggr_halfdemand = False
    """Default aggr_halfdemand for queries."""
    
    aggr_batch_fallback =   True
    """If True, allow aggregate queries to fallback on batch
    implementation when they don't fit the form we incrementalize.
    """
    
    aggr_dem_fallback =     True
    """If True, allow aggregate queries specified to use inc to be
    upgraded to using dem if it is required due to 1) appearing in an
    incrementalized comprehension or 2) having a demand-driven operand.
    """
    
    comp_dem_fallback =     True
    """If True, allow comprehension queries specified to use inc to be
    upgraded to using dem if it is required for handling a subquery.
    """ 
    
    default_instrument =    False
    """If True, instrument transformed queries for correctness
    by default.
    """
    
    selfjoin_strat =        'das'
    """Selects what implementation strategy to use to handle self-joins.
    Allowed values are 'das', 'sub', 'aug', 'assume_disjoint', and
    'assume_disjoint_verify'.
    """
    
    maint_emit_typechecks = True
    """If False, omit the type checks around object-domain maintenance
    clauses.
    """
    tag_checks =            True
    """If True, guard maintenance comprehensions with a demand check."""
    single_tag =            False
    """If True, each query variable only gets one tag."""
    subdem_tags =           True
    """If True, subquery demand invariants are defined based on tags
    for its demand parameters in the outer query. Otherwise, define
    subquery demand invariants based on the join of preceding clauses
    in the outer query.
    """
    rc_elim =               True
    """If True, eliminate reference counts where possible."""
    deadcode_elim =         True
    """If False, do not run deadcode elimination."""
    
    clause_priorities =     frozendict()
    """Dictionary mapping from relation_mask identifiers to a numerical
    join heuristic ranking. See invinc/comp/order.py.
    """
    
    maint_inline =          False
    """If True, maintenance code is inlined."""
    
    analyze_costs =         False
    """If True, emit cost analysis information for each function."""


class DefaultQueryOptions:
    params =                ()
    """Query parameters."""
    uset_mode =             'uncon'
    """Controls what parameters get tracked by the U-set.
        'none':      no U-set
        'all':       all parameters are tracked
        'uncon':     unconstrained parameters only
        'explicit':  consult uset_params
    """
    uset_params =           ()
    """If uset_mode is 'explicit', parameters to track in the U-set."""
    uset_force =            None
    """If True, use a nullary uset when incrementalizing with demand.
    If None, use default.
    """
    uset_lru =              None
    impl =                  None
    """Implementation mode for a query.
        None:        use global options to decide
        'batch':     batch computation
        'auxonly':   batch computation for aggregates, batch with
                     incremental auxiliary maps for comprehensions
        'inc':       incremental computation
        'dem':       demand-filtered incremental computation
    """
    aggr_halfdemand =       None
    """If True, aggregate queries using demand will use the
    "half-demand" strategy where possible. If None, use the global
    default value.
    """
    instrument =            None
    """If True, instrument the query for correctness, so that its
    value is computed both straightforwardly and incrementally
    and dynamically compared for equality. If None, rely on the
    global default.
    
    Implemented only for inc on comprehensions at the moment.
    """
    notransform =           False
    """If True, do not transform, even if default_impl says to. This is
    for internal use by generated queries.
    """
    maint_impl =            'auxonly'
    """Implementation mode to use for maintenance comprehensions
    that help to incrementally compute this comprehension. Can be
    'batch' or 'auxonly'.
    """
    no_rc =                 False
    """If True, omit reference counts for this comprehension, even
    if they would normally be required. Requires global option
    rc_elim be set to True.
    """
    
    _deltarel =             None
    """(Internal) If this join is a maintenance join, name of the
    delta relation for which it was formed. Otherwise None.
    """
    _deltaelem =            None
    """(Internal) If this join is a maintenance join, source code
    for the delta element for which it was formed. Otherwise None.
    """
    _deltalhs =             None
    """(Internal) If this join is a maintenance join, source code
    for the LHS of the delta clause for which it was formed.
    Otherwise None.
    """
    _deltaop =              None
    """(Internal) If this join is a maintenance join, string
    indicating if the operation was 'add' or 'delete'. Otherwise
    None.
    """
    
    _invalid =              False
    """(Internal) Set True if this query cannot be transformed
    due to not satisfying syntactic requirements.
    """

defaultnormaloptions = {k: v for k, v in DefaultNormalOptions.__dict__.items()
                        if not k.startswith('_')}
defaultqueryoptions = {k: v for k, v in DefaultQueryOptions.__dict__.items()
                       if not k.startswith('_')}


class OptionsManager:
    
    """Manages access to program options."""
    
    normal_defaults = defaultnormaloptions
    query_defaults = defaultqueryoptions
    
    def __init__(self):
        self.nopts = {}
        """Normal options."""
        # Query options are stored on the individual query nodes.
    
    @classmethod
    def validate_nopts(cls, nopts):
        """Check that all normal options keys are recognized."""
        illegal_normal_keys = \
            set(nopts.keys()) - set(cls.normal_defaults.keys())
        if illegal_normal_keys:
            raise ProgramError('Invalid options: ' +
                               quote_items(illegal_normal_keys))
    
    @classmethod
    def validate_qopts(cls, qopts):
        """Check that all query options keys are recognized."""
        for d in qopts.values():
            illegal_query_keys = \
                set(d.keys()) - set(cls.query_defaults.keys())
            if illegal_query_keys:
                raise ProgramError('Invalid query options: ' +
                                   quote_items(illegal_query_keys))
    
    def import_opts(self, nopts, qopts):
        """Validate an opts structure, and set our nopts."""
        self.validate_nopts(nopts)
        self.validate_qopts(qopts)
        self.nopts.update(nopts)
    
    def get_opt(self, key):
        """Retrieve a normal option, using the default as a fallback."""
        default = dc(self.normal_defaults[key])
        return self.nopts.get(key, default)
    
    def set_opt(self, key, value):
        """Set a normal option."""
        if key not in self.normal_defaults.keys():
            raise ProgramError('Invalid option: ' + key)
        self.nopts[key] = value
    
    def del_opt(self, key):
        """Delete a normal option (so the default will be used)."""
        if key not in self.normal_defaults.keys():
            raise ProgramError('Invalid option: ' + key)
        self.nopts.pop(key, None)
    
    # Although query options are stored on the node, access is mediated
    # by the OptionsManager to catch invalid keys and access default
    # values. Write access to options requires rewriting the actual
    # query node.
    
    def get_queryopt(self, query, key):
        """Retrieve a query option, using the default as a fallback."""
        default = dc(self.query_defaults[key])
        return query.options.get(key, default)
