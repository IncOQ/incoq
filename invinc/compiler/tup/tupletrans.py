"""Flattening of tuples in comprehensions.

Each nested tuple on the LHS of an enumerator gets replaced.
The top-level is not replaced, nor are any tuples anywhere else
in the comprehension. Fresh variables take their place, and new
enumerators over tuple relations are inserted immediately after
their use.
"""


__all__ = [
    'flatten_tuples_comp',
    'flatten_tuples_allcomps',
    'flatten_tuples',
]


from invinc.util.collections import OrderedSet
import invinc.compiler.incast as L

from .tuprel import make_trel, get_trel


class TupleFlattener(L.NodeTransformer):
    
    def __init__(self, tupvar_namer):
        super().__init__()
        self.tupvar_namer = tupvar_namer
        self.trels = OrderedSet()
    
    def process(self, tree):
        self.new_clauses = []
        tree = super().process(tree)
        return tree, self.new_clauses
    
    def visit_Enumerator(self, node):
        # If LHS is a tuple, skip over the top level.
        # Either way, don't descend into RHS.
        if isinstance(node.target, L.Tuple):
            elts = self.visit(node.target.elts)
            new_target = node.target._replace(elts=elts)
            return node._replace(target=new_target)
        else:
            new_target = self.generic_visit(node.target)
            return node._replace(target=new_target)
    
    def visit_Tuple(self, node):
        # No need to recurse, that's taken care of by the caller
        # of this visitor.
        tupvar = self.tupvar_namer.next()
        arity = len(node.elts)
        trel = make_trel(arity)
        elts = (L.sn(tupvar),) + node.elts
        new_cl = L.Enumerator(L.tuplify(elts, lval=True),
                              L.ln(trel))
        self.new_clauses.append(new_cl)
        self.trels.add(trel)
        return L.sn(tupvar)

def flatten_tuples_comp(comp):
    """Flatten away nested tuples. Return the modified comprehension
    and an OrderedSet of tuple relations used.
    """
    tupvar_namer = L.NameGenerator(fmt='_tup{}', counter=1)
    flattener = TupleFlattener(tupvar_namer)
    comp = L.rewrite_compclauses(comp, flattener.process,
                                 after=True, enum_only=True, recursive=True)
    return comp, flattener.trels

def flatten_tuples_allcomps(tree):
    """Flatten nested tuples in all comprehensions. Return the modified
    tree and an OrderedSet of all tuple relations used.
    """
    class Flattener(L.QueryMapper):
        
        def process(self, tree):
            self.trels = OrderedSet()
            tree = super().process(tree)
            return tree, self.trels
        
        def map_Comp(self, node):
            new_comp, new_trels = flatten_tuples_comp(node)
            self.trels.update(new_trels)
            return new_comp
    
    return Flattener.run(tree)


def flatten_tuples(tree):
    """Flatten all nested tuples in a program. Return the modified
    program.
    """
    tree, _trels = flatten_tuples_allcomps(tree)
    return tree
