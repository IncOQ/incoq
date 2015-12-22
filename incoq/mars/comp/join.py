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
    
    def rhs_rels_from_comp(self, comp):
        rels = OrderedSet()
        for cl in comp.clauses:
            rel = self.rhs_rel(cl)
            if rel is not None:
                rels.add(rel)
        return tuple(rels)
    
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
    
    def comp_rename_lhs_vars(self, comp, renamer):
        new_clauses = [self.rename_lhs_vars(cl, renamer)
                       for cl in comp.clauses]
        new_resexp = L.apply_renamer(comp.resexp, renamer)
        
        return comp._replace(resexp=new_resexp,
                             clauses=new_clauses)
    
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
    
    def get_loop_for_join(self, comp, body):
        """Given a join, create code for iterating over it and running
        body.
        """
        assert self.is_join(comp)
        vars = self.lhs_vars_from_comp(comp)
        return (L.DecompFor(vars, comp, body),)
    
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
    
    def get_maint_join_union(self, comp, rel, value, *,
                             selfjoin=SelfJoin.Without):
        """Given a join and an update to a relation, return the
        maintenance joins whose union forms the complete set of
        changes.
        """
        joins = []
        for i, cl in enumerate(comp.clauses):
            if self.rhs_rel(cl) == rel:
                join = self.get_maint_join(comp, i, value,
                                           selfjoin=selfjoin)
                joins.append(join)
        return tuple(joins)
    
    def get_maint_code(self, fresh_vars, comp, result_var, update, *,
                       selfjoin=SelfJoin.Without,
                       counted):
        """Given a comprehension (not necessarily a join) and an
        update to a relation, return the maintenance code -- i.e.,
        the update to the stored result variable looped for each
        maintenance join.
        
        If counted is False, generate non-counted set updates.
        """
        assert isinstance(update, L.RelUpdate)
        assert isinstance(update.op, (L.SetAdd, L.SetRemove))
        
        fresh_var_prefix = next(fresh_vars)
        result_elem_var = fresh_var_prefix + '_result'
        # Prefix LHS vars in the comp to guarantee fresh names for their
        # use in maintenance code.
        renamer = lambda x: fresh_var_prefix + '_' + x
        comp = self.comp_rename_lhs_vars(comp, renamer)
        
        body = ()
        body += (L.Assign(result_elem_var, comp.resexp),)
        body += L.rel_update(result_var, update.op, result_elem_var,
                             counted=counted)
        
        join = self.make_join_from_comp(comp)
        maint_joins = self.get_maint_join_union(
                        join, update.rel, L.Name(update.elem),
                        selfjoin=selfjoin)
        
        code = ()
        for maint_join in maint_joins:
            code += self.get_loop_for_join(maint_join, body)
        
        return code


class CoreClauseTools(ClauseTools, CoreClauseVisitor):
    pass
