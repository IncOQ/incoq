"""Join logic."""


__all__ = [
    'CompInfoFactory',
    'CompInfo',
]


from simplestruct import Struct, TypedField
from incoq.mars.incast import L

from .clause import ClauseInfo, ClauseInfoFactory


# Definition must come before CompInfo due to use in TypedField.
class CompInfoFactory(ClauseInfoFactory):
    
    """Extension of ClauseInfoFactory that can also take comprehension
    nodes to produce a CompInfo object.
    """
    
    def make_comp_info(self, node, boundvars):
        assert isinstance(node, L.Comp)
        clauses = []
        for cl in node.clauses:
            cl_info = self.make_clause_info(cl)
            clauses.append(cl_info)
        return CompInfo(self, clauses, boundvars, node.resexp)


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
    
    def get_code(self, body):
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
            newenv.update(cl_info.lhsvars)
            bindenvs.append(newenv)
        
        # Build code, innermost to outermost.
        code = body
        for bindenv, cl_info in reversed(list(zip(bindenvs, self.clauses))):
            code = cl_info.get_code(bindenv, code)
        
        return code
