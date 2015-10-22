"""Join and comprehension logic.

A Join is a special case of a comprehension where the result expression
is a tuple of all the variables appearing on the left-hand sides of the
membership clauses, and where there are no bound variables. Joins are
an essential part of the incremental transformation.
"""


__all__ = [
    'CompInfoFactory',
    'CompInfo',
]


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
