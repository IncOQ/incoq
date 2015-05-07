"""Aggregates inside comprehensions."""


__all__ = [
    'flatten_smlookups',
]


from collections import OrderedDict
import incoq.compiler.incast as L


class LookupReplacer(L.NodeTransformer):
    
    """Replaces each unique SMLookup expression, or SMLookup expression
    wrapped in a DemQuery node, with a fresh variable. Returns the new
    tree and a list of clauses defining the new variables.
    
    Does not traverse the RHS of an enumerator.
    """
    
    def __init__(self, namer):
        super().__init__()
        self.namer = namer
        """Generator for fresh names."""
        self.repls = OrderedDict()
        """Mapping from nodes to replacement variables."""
    
    def process(self, tree):
        # Mark nodes that are wrapped by DemQuery nodes so we know not
        # to treat them separately.
        self.demwrapped_nodes = set()
        self.new_clauses = []
        tree = super().process(tree)
        return tree, self.new_clauses
    
    def visit_Enumerator(self, node):
        # Don't touch the RHS. We don't want to clobber an SMLookup
        # in a clause added by a previous run of flatten_smlookups.
        target = self.visit(node.target)
        node._replace(target=target)
    
    def visit_SMLookup(self, node):
        node = self.generic_visit(node)
        
        if node in self.demwrapped_nodes:
            return node
        
        sm = node
        assert sm.default is None
        
        v = self.repls.get(node, None)
        if v is not None:
            var = v
        else:
            self.repls[node] = var = next(self.namer)
            cl_target = L.sn(var)
            cl_iter = L.Set((sm,))
            new_cl = L.Enumerator(cl_target, cl_iter)
            self.new_clauses.append(new_cl)
        
        return L.ln(var)
    
    def visit_DemQuery(self, node):
        self.demwrapped_nodes.add(node.value)
        node = self.generic_visit(node)
        
        if not isinstance(node.value, L.SMLookup):
            return node
        sm = node.value
        assert sm.default is None
        
        v = self.repls.get(node, None)
        if v is not None:
            # Reuse existing entry.
            var = v
        else:
            # Create new entry.
            self.repls[node] = var = next(self.namer)
            # Create accompanying clause. Has form
            #    var in DEMQUERY(..., {smlookup})
            # The clause constructor logic will later rewrite that,
            # or else fail if there's a syntax problem.
            cl_target = L.sn(var)
            cl_iter = node._replace(value=L.Set((sm,)))
            new_cl = L.Enumerator(cl_target, cl_iter)
            self.new_clauses.append(new_cl)
        
        return L.ln(var)


def flatten_smlookups(comp):
    """Given a comprehension, flatten any demand-driven setmap lookups
    (e.g. for aggregates).
    """
    namer = L.NameGenerator('_av{}')
    replacer = LookupReplacer(namer)
    return L.rewrite_compclauses(comp, replacer.process)
