"""Join and comprehension logic.

A Join is a special case of a comprehension where the result expression
is a tuple of all the variables appearing on the left-hand sides of the
membership clauses, and where there are no bound variables. Joins are
an essential part of the incremental transformation.
"""


__all__ = [
    'CompInfoFactory',
    'CompInfo',
    
    'JoinExpander',
]


from enum import Enum

from simplestruct import Struct, TypedField

from incoq.util.collections import OrderedSet
from incoq.mars.incast import L

from .clause import ClauseInfo, ClauseInfoFactory


def lhs_vars_from_clauses(clauses):
    """Return a tuple of all lhs_vars appearing in the given clauses, in
    order, without duplicates.
    """
    vars = OrderedSet()
    for cl_info in clauses:
        vars.update(cl_info.lhs_vars)
    return tuple(vars)


# Definition must come before CompInfo due to use in TypedField.
class CompInfoFactory(ClauseInfoFactory):
    
    """Extension of ClauseInfoFactory that can also take comprehension
    nodes to produce a CompInfo object.
    """
    
    def make_comp_info(self, node, boundvars):
        """Construct a CompInfo object from a Comp AST node and the
        given bound variables.
        """
        assert isinstance(node, L.Comp)
        clauses = []
        for cl in node.clauses:
            cl_info = self.make_clause_info(cl)
            clauses.append(cl_info)
        return CompInfo(self, clauses, boundvars, node.resexp)
    
    def make_join(self, clauses):
        """Construct a join from the given clauses."""
        lhs_vars = lhs_vars_from_clauses(clauses)
        return CompInfo(self, clauses, [], L.tuplify(lhs_vars))


class CompInfo(Struct):
    
    """Encapsulates a Comp node and provides utilities for
    incrementalization.
    """
    
    class SelfJoin(Enum):
        """Strategies for handling self-joins when binding clauses."""
        Without = 1
        """Use WithoutMember for all subsequent clauses over the same
        relation as the bound clause.
        """
        # Other possibilities include adding the element (for running
        # maintenance before additions / after removals), or doing
        # nothing at all (for when a differential assignment set is
        # used).
    
    factory = TypedField(CompInfoFactory)
    """Factory to use for constructing ClauseInfo and other CompInfo
    objects.
    """
    clauses = TypedField(ClauseInfo, seq=True)
    """Clauses in the join."""
    boundvars = TypedField(str, seq=True)
    """Bound variables, e.g. parameters of a query, or update variables
    for maintenance code.
    """
    resexp = TypedField(L.expr)
    """Expression to evaluate for each satisfying combination of
    variables.
    """
    
    @property
    def lhs_vars(self):
        """Return a tuple of all lhs_vars appearing in the clauses, in
        order, without duplicates.
        """
        return lhs_vars_from_clauses(self.clauses)
    
    @property
    def is_join(self):
        """True if the result expression is a tuple of each enumeration
        variable (in order) and there are no bound variables.
        """
        if len(self.boundvars) > 0:
            return False
        try:
            vars = L.detuplify(self.resexp)
        except ValueError:
            return False
        return vars == self.lhs_vars
    
    def get_clause_code(self, body):
        """Produce code for running the comprehension clauses, i.e.
        running body once for each satisfying combination of values
        for all clauses. Clauses are run in left-to-right order, with
        the boundvars initially bound.
        """
        # Determine the binding environments that each clause's code
        # will have. Start with the bound variables for the first
        # clause, then add each clause's enumeration variables.
        bindenvs = [set(self.boundvars)]
        for cl_info in self.clauses:
            newenv = set(bindenvs[-1])
            newenv.update(cl_info.lhs_vars)
            bindenvs.append(newenv)
        
        # Build code, innermost to outermost.
        code = body
        for bindenv, cl_info in reversed(list(zip(bindenvs, self.clauses))):
            code = cl_info.get_code(bindenv, code)
        
        return code
    
    def bind_clause(self, i, value, *,
                    selfjoin=SelfJoin.Without):
        """Return a join where the clause at index i is bound to value.
        Self-joins are handled appropriately. This CompInfo must be
        a join.
        """
        assert self.is_join
        # Other strategies not supported at the moment.
        assert selfjoin is self.SelfJoin.Without
        assert 0 <= i < len(self.clauses)
        
        rel = self.clauses[i].rhs_rel
        if rel is None:
            raise ValueError('Cannot bind clause: ' + str(self.clauses[i]))
        
        new_clauses = list(self.clauses[:i])
        
        bound_clause = self.clauses[i]
        bound_clause = self.factory.make_sing(bound_clause, value)
        new_clauses.append(bound_clause)
        
        for cl in self.clauses[i+1:]:
            if cl.rhs_rel == rel:
                new_clauses.append(self.factory.make_without(cl, value))
            else:
                new_clauses.append(cl)
        
        return self.factory.make_join(new_clauses)


class JoinExpander(L.NodeTransformer):
    
    """Rewrites DecompFor loops over joins by expanding the join into
    its nested clauses.
    
    A DecompFor loop is rewritable if the right-hand side is a Query
    node wrapping a Comp node that is a join, and if the target of
    the loop consists of the same variables (in the same order) as
    those returned by the join.
    
    A rewritable DecompFor loop is rewritten if the query name matches
    one of the given names. Other occurrences of the query are ignored.
    """
    
    def __init__(self, comp_info_map, queries):
        super().__init__()
        self.comp_info_map = comp_info_map
        """Mapping from query names to CompInfo objects."""
        self.queries = queries
        """Names of queries that wrap joins that are to be expanded.
        If None, expand all rewritable joins.
        """
    
    def visit_DecompFor(self, node):
        node = super().generic_visit(node)
        
        # Check that the RHS is a query that is in the comp_info_map
        # and in queries.
        if not isinstance(node.iter, L.Query):
            return node
        comp_info = self.comp_info_map.get(node.iter.name, None)
        if comp_info is None:
            return node
        if node.iter.name not in self.queries:
            return node
        
        # Check that it's a join and the variables match the loop target.
        if not (comp_info.is_join and comp_info.lhs_vars == node.vars):
            return node
        
        return comp_info.get_clause_code(node.body)
