"""Object-domain transformation."""


from .clause import *
from .comp import *
from .updates import *


def flatten_objdomain(tree, symtab):
    # Turn aggregate arguments into comprehensions.
    tree = rewrite_aggregates(tree, symtab)
    # Flatten comprehensions.
    tree, objrels = flatten_all_comps(tree, symtab)
    # Flatten updates.
    tree = PairDomainImporter.run(tree, symtab.fresh_names.vars, objrels)
    # Define symbols for M, F, etc.
    define_obj_relations(symtab, objrels)
    symtab.objrels = objrels
    return tree


def unflatten_objdomain(tree, symtab):
    # Unflatten updates.
    tree = PairDomainExporter.run(tree)
    return tree
