"""Join and comprehension logic.

A Join is a special case of a comprehension where the result expression
is a tuple of all the variables appearing on the left-hand sides of the
membership clauses, and where there are no bound variables. Joins are
an essential part of the incremental transformation.
"""


__all__ = [
    'SelfJoin',
    
    'ClauseTools',
    'CoreClauseTools',
    
    'JoinExpander',
]


from enum import Enum

from incoq.util.collections import OrderedSet
from incoq.mars.incast import L

from .clause import ClauseVisitor, CoreClauseVisitor


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


class ClauseTools(ClauseVisitor):
    
    """Clause and comprehension tools that rely on clause visitors."""
    
    def lhs_vars_from_clauses(self, clauses):
        """Return a tuple of all LHS vars appearing in the given clauses, in
        order, without duplicates.
        """
        vars = OrderedSet()
        for cl in clauses:
            vars.update(self.lhs_vars(cl))
        return tuple(vars)
    
    def lhs_vars_from_comp(self, comp):
        return self.lhs_vars_from_clauses(comp.clauses)
    
    def make_join_from_clauses(self, clauses):
        """Create a join from the given clauses."""
        lhs_vars = self.lhs_vars_from_clauses(clauses)
        resexp = L.tuplify(lhs_vars)
        return L.Comp(resexp, clauses)
    
    def make_join_from_comp(self, comp):
        return self.make_join_from_clauses(comp.clauses)
    
    def is_join(self, comp):
        lhs_vars = self.lhs_vars_from_clauses(comp.clauses)
        try:
            res_vars = L.detuplify(comp.resexp)
        except ValueError:
            return False
        return res_vars == lhs_vars
    
    def get_code_for_clauses(self, clauses, bindenv, body):
        """Produce code for running body once for each combination of
        variables for all clauses that match the values of the bound
        variables. Bound variables are given in bindenv. No clause
        reordering is done.
        """
        # Determine the binding environments that each clause's code
        # will have. Start with the bound variables for the first
        # clause, then add each clause's enumeration variables.
        bindenvs = [set(bindenv)]
        for cl in clauses:
            newenv = set(bindenvs[-1])
            newenv.update(self.lhs_vars(cl))
            bindenvs.append(newenv)
        
        # Build code, innermost to outermost.
        code = body
        for bindenv, cl in reversed(list(zip(bindenvs, clauses))):
            code = self.get_code(cl, bindenv, code)
        
        return code
    
    def get_maint_join(self, comp, i, value, *,
                       selfjoin=SelfJoin.Without):
        """Given a join, produce a maintenance join for the clause at
        index i, handling self-joins using the given strategy.
        """
        assert self.is_join(comp)
        # Other strategies not supported at the moment.
        assert selfjoin is SelfJoin.Without
        assert 0 <= i < len(comp.clauses)
        
        rel = self.rhs_rel(comp.clauses[i])
        if rel is None:
            raise ValueError('Cannot bind clause: ' + str(self.clauses[i]))
        
        # Left clauses unchanged.
        new_clauses = list(comp.clauses[:i])
        # Clause i becomes bound to changed value.
        bound_clause = self.singletonize(comp.clauses[i], value)
        new_clauses.append(bound_clause)
        # Remaining clauses added as is, except if over changed relation.
        for cl in comp.clauses[i+1:]:
            if self.rhs_rel(cl) == rel:
                new_clauses.append(self.subtract(cl, value))
            else:
                new_clauses.append(cl)
        
        return comp._replace(clauses=new_clauses)


class CoreClauseTools(ClauseTools, CoreClauseVisitor):
    pass


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
    
    def __init__(self, clausetools, queries, query_params):
        super().__init__()
        self.clausetools = clausetools
        """ClauseTools instance."""
        self.queries = queries
        """Names of queries that wrap joins that are to be expanded.
        If None, expand all rewritable joins.
        """
        self.query_params = query_params
        """Mapping from query name to tuple of parameters."""
    
    def visit_DecompFor(self, node):
        ct = self.clausetools
        
        node = super().generic_visit(node)
        
        # Skip if the RHS isn't a comprehension query for which
        # expansion was requested.
        if not (isinstance(node.iter, L.Query) and
                node.iter.name in self.queries and
                isinstance(node.iter.query, L.Comp)):
            return node
        comp = node.iter.query
        
        # Check that it's a join and the variables match the loop target.
        if not (ct.is_join(comp) and
                ct.lhs_vars_from_comp(comp) == node.vars):
            return node
        
        params = self.query_params[node.iter.name]
        return ct.get_code_for_clauses(comp.clauses, params, node.body)
