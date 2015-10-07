"""Rewritings for optimization."""


__all__ = [
    'flatten_singletons',
]


from incoq.mars.incast import L
import incoq.mars.types as T


class SingletonUnwrapper(L.NodeTransformer):
    
    """Rewrite uses of singleton relations so that the singleton
    tuples are unwrapped, i.e. replaced by their contents.
    """
    
    def __init__(self, fresh_vars, rels):
        super().__init__()
        self.fresh_vars = fresh_vars
        self.rels = rels
    
    def visit_RelUpdate(self, node):
        # TODO: Should generic_visit() over value, but if we redo
        # RelUpdate nodes to have no expressions (just variables)
        # that's not needed.
        if node.rel in self.rels:
            new_value = L.Parser.pe('_VALUE[0]',
                                    subst={'_VALUE': node.value})
            node = node._replace(value=new_value)
        return node
    
    def visit_For(self, node):
        if (isinstance(node.iter, L.Name) and
            node.iter.id in self.rels):
            var = next(self.fresh_vars)
            new_stmt = L.Parser.ps('_OLDVAR = (_VAR,)',
                                   subst={'_VAR': var,
                                          '_OLDVAR': node.target})
            new_body = (new_stmt,) + node.body
            node = node._replace(target=var, body=new_body)
        return node
    
    # TODO: Properly handle comprehension clauses.
    # Requires figuring out a version of Membership clauses that
    # doesn't decompose the element.


def flatten_singletons(tree, symtab):
    """Rewrite relations that use singleton tuple types so that the
    tuple contents are unpacked.
    
    This will change the types of relations, and add packing and
    unpacking operations at their uses, which should be eliminated
    by a follow-up optimization.
    """
    relations = symtab.get_relations()
    sing_rels = set()
    for relsym in relations.values():
        t = relsym.type
        if (isinstance(t, T.Set) and
            isinstance(t.elt, T.Tuple) and
            len(t.elt.elts) == 1):
            sing_rels.add(relsym)
    
    tree = SingletonUnwrapper.run(tree, symtab.fresh_vars,
                                  {rel.name for rel in sing_rels})
    
    for rel in sing_rels:
        rel.type = T.Set(rel.type.elt.elts[0])
    
    return tree
