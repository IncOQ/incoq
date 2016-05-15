"""Rewriting for aggregates in comprehensions."""


__all__ = [
    'AggrMapReplacer',
    'AggrMapCompRewriter',
    'transform_comps_with_maps',
]


from collections import OrderedDict

from incoq.util.collections import OrderedSet
from incoq.compiler.incast import L
from incoq.compiler.symbol import S, N
from incoq.compiler.auxmap import SetFromMapInvariant, transform_setfrommap


class AggrMapReplacer(L.NodeTransformer):
    
    """Replace all occurrences of map lookups with fresh variables.
    Return the transformed AST, a list of new clauses binding the
    fresh variables, and a set of SetFromMap invariants that need
    to be transformed.
    
    This is intended to be used on each of a comprehension's clauses and
    its result expression, reusing the same transformer instance.
    """
    
    def __init__(self, fresh_names):
        super().__init__()
        self.fresh_names = fresh_names
        self.repls = OrderedDict()
        """Mapping from nodes to replacement variables."""
        self.sfm_invs = OrderedSet()
        """SetFromMap invariants."""
    
    def process(self, tree):
        self.new_clauses = []
        tree = super().process(tree)
        return tree, self.new_clauses, []
    
    def visit_DictLookup(self, node):
        node = self.generic_visit(node)
        
        # Only simple map lookups are allowed.
        assert isinstance(node.value, L.Name)
        assert L.is_tuple_of_names(node.key)
        assert node.default is None
        map = node.value.id
        keyvars = L.detuplify(node.key)
        
        var = self.repls.get(node, None)
        if var is None:
            mask = L.mapmask_from_len(len(keyvars))
            rel = N.SA_name(map, mask)
            
            # Create a fresh variable.
            self.repls[node] = var = next(self.fresh_names)
            
            # Construct a clause to bind it.
            vars = list(keyvars) + [var]
            new_clause = L.SetFromMapMember(vars, rel, map, mask)
            self.new_clauses.append(new_clause)
            
            # Construct a corresponding SetFromMap invariant.
            sfm = SetFromMapInvariant(rel, map, mask)
            self.sfm_invs.add(sfm)
        
        return L.Name(var)


class AggrMapCompRewriter(S.QueryRewriter):
    
    """Rewrite comprehension queries so that map lookups from aggregates
    are flattened into SetFromMap clauses. Return a pair of the new tree
    and a set of SetFromMap invariants that need to be transformed.
    """
    
    def process(self, tree):
        self.sfm_invs = OrderedSet()
        tree = super().process(tree)
        return tree, self.sfm_invs
    
    def rewrite_comp(self, symbol, name, comp):
        rewriter = AggrMapReplacer(self.symtab.fresh_names.vars)
        comp = L.rewrite_comp(comp, rewriter.process)
        self.sfm_invs.update(rewriter.sfm_invs)
        return comp


def transform_comps_with_maps(tree, symtab):
    """Rewrite all comprehensions containing map lookups, and
    incrementalize the corresponding SetFromMap invariants.
    """
    tree, sfm_invs = AggrMapCompRewriter.run(tree, symtab)
    for sfm in sfm_invs:
        tree = transform_setfrommap(tree, symtab, sfm)
    return tree
