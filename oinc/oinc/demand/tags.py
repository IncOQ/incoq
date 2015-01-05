"""Tag-based demand transformation strategy."""


__all__ = [
    'make_structures',
    'prune_structures',
    'get_used_filters',
    'structures_to_comps',
    'uset_to_comp',
    'filter_comps',
]


from types import SimpleNamespace
from operator import attrgetter

from simplestruct import Struct, Field, TypedField

from oinc.set import Mask
from oinc.comp import Clause, EnumClause, inst_wildcards, Join, CompSpec
import oinc.incast as L

from .demclause import DemClause


KIND_TAG = 'TAG'
KIND_FILTER = 'FILTER'
KIND_USET = 'USET'


class Tag(Struct):
    kind = KIND_TAG
    
    i = TypedField(int)
    """Index of query enumerator for which tag is introduced."""
    name = TypedField(str)
    """Name of tag set."""
    var = TypedField(str)
    """Query variable being tagged."""
    lhs = TypedField(str, seq=True)
    """LHS of the query enumerator."""
    rel = TypedField(str)
    """Relation being projected. This is either the original relation
    iterated by the query enumerator, or else a filter over it.
    """

class Filter(Struct):
    kind = KIND_FILTER
    
    i = TypedField(int)
    """Index of query enumerator for which filter is introduced."""
    name = TypedField(str)
    """Name of filter set."""
    lhs = TypedField(str, seq=True)
    """LHS of the query enumerator."""
    rel = TypedField(str)
    """RHS of the query enumerator, i.e., set being filtered."""
    preds = TypedField(str, seq=True)
    """Names of predecessor tags."""

class USet(Struct):
    kind = KIND_USET
    
    i = TypedField(int)
    """Index of query enumerator where the subquery is iterated over."""
    name = TypedField(str)
    """Name of associated demand name."""
    vars = TypedField(str, seq=True)
    """Vars that get passed to the demand functions as parameters."""
    preds = Field()
    """Names of predecessor tags, or None if using clauses."""
    pred_clauses = Field()
    """Predecessor clauses, or None if using tags."""


class DemStructures(Struct):
    _immutable = False
    
    tags = Field()
    filters = Field()
    usets = Field()
    
    @property
    def structs(self):
        """All tags, filters, and usets, returned in dependency order."""
        # Tags must come after the filters at their own enumerator.
        # Relies on stability of list.sort.
        structs = self.filters + self.usets + self.tags
        structs.sort(key=attrgetter('i'))
        return structs


def make_structures_create(clauses):
    """Return a DemStructures object with partially-constructed
    tag/filter/uset values. They are missing values for the name,
    rel, and preds/pred_clauses fields.
    """
    # Use SimpleNamespace, to allow partially constructed state.
    SN_Tag = SN_Filter = SN_USet = SimpleNamespace
    
    # Initialize structures, leaving some fields blank.
    
    # For each enumerator, make a tag for the enumvars that appear
    # in a taggable position.
    tags = [SN_Tag(kind=KIND_TAG,
                   i=i,
                   name=None,
                   var=v,
                   lhs=e.enumlhs,
                   rel=None)
            for i, e in enumerate(clauses)
            if e.kind is e.KIND_ENUM
            for v in e.enumvars_tagsout]
    
    # Make a filter for each enumerator that is not over a
    # demand-driven subquery.
    filters = [SN_Filter(kind=KIND_FILTER,
                         i=i,
                         name=None,
                         lhs=e.enumlhs,
                         rel=e.enumrel,
                         preds=None)
               for i, e in enumerate(clauses)
               if e.kind is e.KIND_ENUM
               if not e.has_demand]
    
    # Make a uset for each enumerator over a demand-driven subquery.
    usets = [SN_USet(kind=KIND_USET,
                     i=i,
                     name=e.demname,
                     vars=e.demparams,
                     preds=None,
                     pred_clauses=None)
             for i, e in enumerate(clauses)
             if e.kind is e.KIND_ENUM
             if e.has_demand]
    
    return DemStructures(tags=tags, filters=filters, usets=usets)

def make_structures_name(qname, ds):
    """Fill in name information, in-place."""
    tags = ds.tags
    filters = ds.filters
    
    # The number gets excluded if the name is unambiguous.
    
    for i, t in enumerate(tags):
        others = [t2 for t2 in tags if t2.var == t.var]
        prev_others = [t2 for t2 in tags[:i] if t2.var == t.var]
        numstr = (str(len(prev_others) + 1)
                  if len(others) > 1 else '')
        t.name = '{}_T{}{}'.format(qname, t.var, numstr)
    
    for i, f in enumerate(filters):
        others = [f2 for f2 in filters if f2.rel == f.rel]
        prev_others = [f2 for f2 in filters[:i] if f2.rel == f.rel]
        numstr = (str(len(prev_others) + 1)
                  if len(others) > 1 else '')
        f.name = '{}_d{}{}'.format(qname, f.rel, numstr)

def make_structures_preds(clauses, ds, *,
                          singletag, subdem_tags):
    """Fill in predecessor information, in-place."""
    # If subdem_tags is True, we use the same predecessor-finding
    # logic for both filters and usets. Otherwise, we handle usets
    # separately below.
    if subdem_tags:
        needs_predtags = ds.filters + ds.usets
    else:
        needs_predtags = ds.filters
    
    for s in needs_predtags:
        e = clauses[s.i]
        s.preds = []
        for v in e.enumvars_tagsin:
            # Use tags introduced to the left of here.
            preds = [t.name for t in ds.tags
                            if t.var == v if t.i < s.i]
            # When using singletag, only choose the first
            # (leftmost) tag. The others will be pruned.
            if singletag:
                preds = preds[:1]
            s.preds.extend(preds)
        s.preds = tuple(s.preds)
    
    if not subdem_tags:
        for s in ds.usets:
            # Use the join of all clauses to the left of here.
            # Strip DEMQUERY from those clauses.
            preds = tuple(cl.cl if isinstance(cl, DemClause) else cl
                          for cl in clauses[:s.i])
            s.pred_clauses = preds

def make_structures_finish(clauses, ds, *, subdem_tags):
    """Get rid of filters that don't filter anything. Make tags
    refer to the right relation.
    """
    tags = ds.tags
    filters = ds.filters
    usets = ds.usets
    
    # Remove unnecessary filters.
    ds.filters = filters = [f for f in filters if len(f.preds) > 0]
    
    # Make sure appropriate u-set preds exist for each parameter
    # tracked in that u-set.
    if subdem_tags:
        tags_by_name = {t.name: t for t in tags}
        for u in usets:
            for v in u.vars:
                if not any(tags_by_name[p].var == v for p in u.preds):
                    raise AssertionError(
                        'Outer comprehension does not have a tag to '
                        'constrain subquery parameter "{}" '
                        '(clauses: {})'.format(
                        v, ', '.join(str(c) for c in clauses)))
    else:
        for u in usets:
            for v in u.vars:
                if not any(v in cl.enumvars for cl in u.pred_clauses):
                    raise AssertionError(
                        'Outer comprehension does not have a clause '
                        'to constraint subquery parameter "{}" '
                        '(clauses: {})'.format(
                        v, ', '.join(str(c) for c in clauses)))
    
    # We could at this point get rid of tags that are not predecessors
    # to any filter, but we will have more information about what we
    # can remove after we know the join orders of the maintenance
    # comprehensions.
    
    # Set up tags to refer to filters, or the original iterated
    # relation if the filter was removed or it's a uset.
    for t in tags:
        for f in filters:
            if t.i == f.i:
                t.rel = f.name
                break
        else:
            t.rel = clauses[t.i].enumrel

def make_structures(clauses, qname, *, singletag, subdem_tags):
    """Generate tag/filter/uset structures for the given clauses
    and query name. Return the structures in dependency order.
    """
    ds = make_structures_create(clauses)
    make_structures_name(qname, ds)
    make_structures_preds(clauses, ds,
                          singletag=singletag, subdem_tags=subdem_tags)
    make_structures_finish(clauses, ds,
                           subdem_tags=subdem_tags)
    
    # Convert from SimpleNamespace to Struct objects.
    # If we screwed up, here's where we'll get a type error.
    ds.tags = [Tag(t.i, t.name, t.var, t.lhs, t.rel)
               for t in ds.tags]
    ds.filters = [Filter(f.i, f.name, f.lhs, f.rel, f.preds)
                  for f in ds.filters]
    ds.usets = [USet(u.i, u.name, u.vars, u.preds, u.pred_clauses)
                for u in ds.usets]
    
    return ds


def prune_structures(ds, used_indices, *, subdem_tags):
    """Remove tags and filters that are not needed, given a sequence
    of indices of query enumerators for which filters are needed.
    Modify ds in-place.
    """
    tags = ds.tags
    filters = ds.filters
    usets = ds.usets
    
    # Index from tag name to tag object.
    tags_by_name = None
    # Index from tag object to list of filters and usets
    # who have this tag as a predecessor.
    inv_preds = None
    def recompute():
        nonlocal tags_by_name, inv_preds
        
        tags_by_name = {t.name: t for t in tags}
        
        if subdem_tags:
            uses_predtags = filters + usets
        else:
            uses_predtags = filters
        
        inv_preds = {t: [] for t in tags}
        for s in uses_predtags:
            for tname in s.preds:
                t = tags_by_name[tname]
                inv_preds[t].append(s)
    
    # Remove filters that are both unrequested and do not define
    # useful tags. Remove tags that are not predecessors to useful
    # filters or to usets. Repeat until fixed point.
    changed = True
    while changed:
        changed = False
        recompute()
        
        for t in list(tags):
            if len(inv_preds[t]) == 0:
                tags.remove(t)
                changed = True
        
        for f in list(filters):
            if not (f.i in used_indices or
                    any(t.rel == f.name for t in tags)):
                filters.remove(f)
                changed = True


### Below this point has not been refactored.

def get_used_filters(ds, ordering, use_tag_checks):
    """Take in the demand structures for a query, and an ordering of
    clauses for one of the query's maintenance comps. Return a set of
    the clause indices for which filter relations are used.
    """
    # Ignore conditions.
    ordering = [(i, cl, bindenv) for i, cl, bindenv in ordering
                if cl.kind is Clause.KIND_ENUM]
    
    filters = ds.filters
    filters_by_index = {f.i: f for f in filters}
    
    used_indices = set()
    for i, cl, bindenv in ordering:
        if cl.kind is Clause.KIND_COND:
            continue
        if i not in filters_by_index:
            continue
        
        # Singleton clauses are filtered if we're doing tag checks.
        deltamask = Mask.from_vars(cl.enumlhs, cl.enumlhs)
        if cl.isdelta and (use_tag_checks or deltamask.has_wildcards):
            used_indices.add(i)
        
        # Consult clause rules.
        elif cl.needs_filtering(bindenv):
            used_indices.add(i)
    
    return used_indices


def structures_to_comps(ds, factory):
    """Convert tags and filters to comprehensions that define them.
    Return pairs of comps and their names, in dependency order.
    Ignore usets.
    """
    tags_by_name = {t.name: t for t in ds.tags}
    result = []
    
    for s in ds.structs:
        if s.kind is KIND_TAG:
            cl = EnumClause(s.lhs, s.rel)
            spec = CompSpec(Join([cl], factory, None), L.ln(s.var), [])
        elif s.kind is KIND_FILTER:
            cls = []
            for tname in s.preds:
                t = tags_by_name[tname]
                cls.append(EnumClause([t.var], t.name))
            # Be sure to replace wildcards with fresh vars.
            lhs = inst_wildcards(s.lhs)
            cls.append(EnumClause(lhs, s.rel))
            spec = CompSpec(Join(cls, factory, None), L.tuplify(lhs), [])
        elif s.kind is KIND_USET:
            continue
        else:
            assert()
        
        result.append((s.name, spec.to_comp({})))
    
    return result

def uset_to_comp(ds, uset, factory, first_clause):
    """Convert a uset to a comprehension."""
    subdem_tags = uset.preds is not None
    
    if subdem_tags:
        tags_by_name = {t.name: t for t in ds.tags}
        clauses = []
        for tname in uset.preds:
            t = tags_by_name[tname]
            clauses.append(EnumClause([t.var], t.name))
    else:
        clauses = uset.pred_clauses
    
    # As an odd special case, if there are no preds,
    # use an emptiness test on the first enumerator,
    # which should be a U-set.
    if len(clauses) == 0:
        assert first_clause.kind is Clause.KIND_ENUM
        assert uset.i != 0, 'Can\'t make demand invariant for inner ' \
            'query; it is the first clause'
        cl = EnumClause(tuple('_' for _ in first_clause.enumlhs),
                        first_clause.enumrel)
        clauses.append(cl)
    
    spec = CompSpec(Join(clauses, factory, None), L.tuplify(uset.vars), [])
    return spec.to_comp({})


def filter_comps(tree, factory, ds, comps, use_tag_checks, *,
                 augmented, subdem_tags):
    """Transform maintenance comps to use filters. Return the
    modified tree and the structs that are actually needed by
    one or more of the comps.
    
    If augmented is True, uses of filters for the delta relation
    are modified to subtract the delta element. 
    """
    filters = ds.filters
    index_to_filtername = {f.i: f.name for f in filters}
    
    used_indices = set()
    for comp in comps:
        spec = CompSpec.from_comp(comp, factory)
        join = spec.join
        
        ordering = join.get_ordering(spec.params)
        
        new_used_indices = get_used_filters(ds, ordering, use_tag_checks)
        
        new_clauses = []
        for i, cl in enumerate(join.clauses):
            if i in new_used_indices:
                if cl.isdelta:
                    new_cl = factory.rewrite_rel(cl, index_to_filtername[i])
                    new_clauses.append(new_cl)
                    if use_tag_checks:
                        check_cl = EnumClause(cl.lhs, index_to_filtername[i])
                        new_clauses.append(check_cl)
                else:
                    new_cl = factory.rewrite_rel(
                                            cl, index_to_filtername[i])
                    if augmented:
                        if cl.enumrel == join.delta.rel:
                            new_cl = factory.subtract_inner(
                                                new_cl, join.delta.elem)
                    new_clauses.append(new_cl)
            else:
                new_clauses.append(cl)
        new_join = join._replace(clauses=new_clauses)
        
        new_spec = spec._replace(join=new_join)
        new_comp = new_spec.to_comp(comp.options)
        
        tree = L.QueryReplacer.run(tree, comp, new_comp)
        
        used_indices |= new_used_indices
    
    prune_structures(ds, used_indices, subdem_tags=subdem_tags)
    return tree, ds
