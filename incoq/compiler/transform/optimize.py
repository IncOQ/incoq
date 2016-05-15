"""Rewritings for optimization."""


__all__ = [
    'unwrap_singletons',
]


from incoq.compiler.incast import L
from incoq.compiler.type import T


class SingletonUnwrapper(L.NodeTransformer):
    
    """Rewrite uses of singleton relations so that the singleton
    tuples are unwrapped, i.e. replaced by their contents.
    """
    
    def __init__(self, fresh_vars, rels):
        super().__init__()
        self.fresh_vars = fresh_vars
        self.rels = rels
    
    def visit_RelUpdate(self, node):
        var = next(self.fresh_vars)
        if node.rel in self.rels:
            asgn = L.Parser.pc('_VAR = _VALUE[0]',
                               subst={'_VAR': var, '_VALUE': node.elem})
            update = node._replace(elem=var)
            return asgn + (update,)
        else:
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
    
    def visit_DecompFor(self, node):
        if (isinstance(node.iter, L.Name) and
            node.iter.id in self.rels):
            if len(node.vars) != 1:
                raise L.TransformationError(
                    'Singleton unwrapping requires all DecompFor loops '
                    'over relation to have exactly one target variable')
            return L.For(node.vars[0], node.iter, node.body)
        return node
    
    # TODO: Properly handle comprehension clauses.
    # Requires figuring out a version of Membership clauses that
    # doesn't decompose the element.


def unwrap_singletons(tree, symtab):
    """Rewrite relations that use singleton tuple types so that the
    tuple contents are unpacked. Return the modified tree and a list
    of names of unwrapped relations. Modify types of symbols in the
    symbol table.
    
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
    
    sing_rel_names = {rel.name for rel in sing_rels}
    tree = SingletonUnwrapper.run(tree, symtab.fresh_names.vars,
                                  sing_rel_names)
    
    for rel in sing_rels:
        rel.type = T.Set(rel.type.elt.elts[0])
    
    return tree, sing_rel_names
