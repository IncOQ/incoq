"""Filtering and filtered incrementalization."""


__all__ = [
    'transform_comp_query_with_filtering',
]


from incoq.compiler.comp.trans import (
    transform_firsthalf, transform_secondhalf, transform_comp_query)

from .filter import StructureGenerator


def transform_comp_query_with_filtering(tree, symtab, query):
    """Do all the transformation associated with incrementalizing a
    comprehension query using filtering.
    """
    # Incrementalize the query as normal, but don't process maintenance
    # joins yet.
    tree = transform_firsthalf(tree, symtab, query)
    
    # Define tag and filter structures and incrementalize them in order.
    # Note that query.node is changed by the first half of
    # incrementalization.
    generator = StructureGenerator(symtab, query.node, query.name)
    generator.make_structs()
    generator.simplify_names()
    generator.prune_tags()
    for struct in generator.structs:
        symtab.print('  Tag/Filter: {}'.format(struct.name))
        comp = generator.make_comp(struct)
        struct_query = symtab.define_query(
            struct.name, node=comp,
            struct_for_query=query.name)
        tree = transform_comp_query(tree, symtab, struct_query)
    symtab.stats['tags_created'] += len(generator.tags)
    symtab.stats['filters_created'] += len(generator.filters)
    
    # Associate query with filters.
    query.filters = generator.make_filter_list()
    
    # Now process maintenance joins.
    tree = transform_secondhalf(tree, symtab, query)
    
    return tree
