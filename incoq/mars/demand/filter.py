"""Tag and filter structures."""


__all__ = [
    'generate_structures',
]


from collections import defaultdict
from simplestruct import Struct, TypedField

from incoq.mars.incast import L
from incoq.mars.symbol import N


class Tag(Struct):
    _immutable = False
    
    i = TypedField(int)
    """Index of clause for which this tag is generated."""
    name = TypedField(str)
    """Name of this tag."""
    tag_var = TypedField(str)
    """Query variable controlled by this tag."""
    vars = TypedField(str, seq=True)
    """LHS vars for the clause this tag projects."""
    rel = TypedField(str)
    """Relation this tag projects -- either a relation in the original
    query (e.g., U) or a filter.
    """


class Filter(Struct):
    _immutable = False
    
    i = TypedField(int)
    """Index of clause for which this filter is generated."""
    name = TypedField(str)
    """Name of this filter."""
    vars = TypedField(str, seq=True)
    """LHS vars for the clause this filter is based on."""
    rel = TypedField(str)
    """Relation that this filter refines."""
    preds = TypedField(str, seq=True)
    """Names of predecessor tags for this filter."""


def generate_structures(clausetools, comp, query_name):
    """Return a list of tag and filter structures for the given
    comprehension, in dependency order.
    """
    assert isinstance(comp, L.Comp)
    ct = clausetools
    
    structures = []
    tags = []
    tags_by_var = defaultdict(lambda: [])
    tags_by_i = defaultdict(lambda: [])
    filters = []
    filters_by_rel = defaultdict(lambda: [])
    filters_by_pred = defaultdict(lambda: [])
    
    def add_filter(filter):
        structures.append(filter)
        filters.append(filter)
        filters_by_rel[filter.rel].append(filter)
        for p in filter.preds:
            filters_by_pred[p].append(filter)
    
    def add_tag(tag):
        structures.append(tag)
        tags.append(tag)
        tags_by_var[tag.tag_var].append(tag)
        tags_by_i[tag.i].append(tag)
    
    def get_preds(i, in_vars):
        """Return the names of all tags defined for clauses lower than
        clause i, over any of the variables listed in vars.
        """
        result = []
        for v in in_vars:
            for t in tags_by_var.get(v, []):
                if not t.i < i:
                    continue
                result.append(t.name)
        return result
    
    # Generate for each clause.
    for i, cl in enumerate(comp.clauses):
        vars = ct.lhs_vars(cl)
        in_vars = ct.uncon_lhs_vars(cl)
        out_vars = ct.con_lhs_vars(cl)
        rel = ct.rhs_rel(cl)
        if rel is None:
            raise L.TransformationError('Cannot generate tags and filter '
                                        'for clause: {}'.format(cl))
        
        # Generate a filter for this clause.
        if i != 0:
            n = len(filters_by_rel[rel]) + 1
            name = N.get_filter_name(query_name, rel, n)
            preds = get_preds(i, in_vars)
            filter = Filter(i, name, vars, rel, preds)
            add_filter(filter)
            filtered_rel = name
        else:
            # First clause acts as its own filter; no new structure.
            filtered_rel = rel
        
        # Generate a tag for each variable on the LHS.
        for var in out_vars:
            n = len(tags_by_var[var]) + 1
            name = N.get_tag_name(query_name, var, n)
            tag = Tag(i, name, var, vars, filtered_rel)
            add_tag(tag)
    
    # Remove numbers from names when not ambiguous.
    for filter in filters:
        if len(filters_by_rel[filter.rel]) == 1:
            name = N.get_filter_name(query_name, filter.rel, None)
            filter.name = name
            # Update linked tags.
            for tag in tags_by_i[filter.i]:
                tag.rel = name
    for tag in tags:
        if len(tags_by_var[tag.tag_var]) == 1:
            old_name = tag.name
            name = N.get_tag_name(query_name, tag.tag_var, None)
            tag.name = name
            # Update linked filters.
            for filter in filters_by_pred[old_name]:
                filter.preds = [name if t == old_name else t
                                for t in filter.preds]
    
    return structures
