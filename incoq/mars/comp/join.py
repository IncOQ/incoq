"""Join and comprehension logic.

A Join is a special case of a comprehension where the result expression
is a tuple of all the variables appearing on the left-hand sides of the
membership clauses, and where there are no bound variables. Joins are
an essential part of the incremental transformation.
"""


__all__ = [
    'match_member_cond',
    'match_eq_cond',
    'make_eq_cond',
    
    'SelfJoin',
    
    'ClauseTools',
    'CoreClauseTools',
]


from enum import Enum

from incoq.util.collections import OrderedSet, Partitioning
from incoq.mars.incast import L

from .clause import ClauseVisitor, CoreClauseVisitor


member_cond_pattern = L.Cond(L.Compare(L.PatVar('LHS'), L.In(),
                                       L.Name(L.PatVar('REL'))))

def match_member_cond(tree):
    """If tree is a condition clause with form <vars> in <rel>, return
    a pair of a tuple of the vars and the rel. Otherwise return None.
    """
    result = L.match(member_cond_pattern, tree)
    if result is None:
        return None
    lhs, rel = result['LHS'], result['REL']
    if not L.is_tuple_of_names(lhs):
        return None
    vars = L.detuplify(lhs)
    return vars, rel

eq_cond_pattern = L.Cond(L.Compare(L.Name(L.PatVar('LEFT')), L.Eq(),
                                   L.Name(L.PatVar('RIGHT'))))

def match_eq_cond(tree):
    """If tree is a condition clause with form <var> == <var>, return
    a pair of the variables. Otherwise return None.
    """
    result = L.match(eq_cond_pattern, tree)
    if result is None:
        return None
    else:
        return result['LEFT'], result['RIGHT']

def make_eq_cond(left, right):
    """Make a condition of form <var> == <var>."""
    return L.Cond(L.Compare(L.Name(left), L.Eq(), L.Name(right)))



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
    
    def uncon_lhs_vars_from_comp(self, comp):
        """Return a tuple of unconstrained variables.
        
        An variable is unconstrained if it appears in a clause at a
        position that is not constrained, and if it appears in no prior
        clause at a constrained position.
        
        For cyclic object queries like
        
            {(x, y) for y in x for x in y},
        
        after translating into clauses over M, there are two possible
        sets of unconstrained vars: {x} and {y}. This function processes
        clauses left-to-right, so {x} will be chosen.
        """
        uncon = OrderedSet()
        supported = set()
        for cl in comp.clauses:
            uncon.update(v for v in self.uncon_vars(cl)
                           if v not in supported)
            supported.update(self.con_lhs_vars(cl))
        return tuple(uncon)
    
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
        # Don't apply to non-lhs vars in condition and result
        # expressions.
        lhs_vars = self.lhs_vars_from_comp(comp)
        lhsonly_renamer = lambda x: renamer(x) if x in lhs_vars else x
        
        new_clauses = [self.rename_lhs_vars(cl, lhsonly_renamer)
                       for cl in comp.clauses]
        new_resexp = L.apply_renamer(comp.resexp, lhsonly_renamer)
        
        return comp._replace(resexp=new_resexp,
                             clauses=new_clauses)
    
    def rewrite_with_patterns(self, comp, keepvars):
        """Produce an optimized comprehension that is equivalent under
        pattern matching semantics. Eliminate conditions of the form
        x == y, replacing all occurrences of y with x. Also for each
        condition clause that tests for membership, replace it with
        a proper membership clause.
        
        keepvars is a set of variable identifiers that are not to be
        eliminated. When exactly one variable of an equality condition
        is in keepvars, the other variable is eliminated. When both
        variables are in keepvars, the condition is left alone and
        neither variable is eliminated.
        """
        # We use a union-find data structure, where the partitions
        # are equality classes of the LHS variables. The representative
        # element of each partition is the one that survives.
        part = Partitioning()
        new_clauses = []
        for cl in comp.clauses:
            # Convert conditions expressing membership to the
            # appropriate clause type.
            result = match_member_cond(cl)
            if result is not None:
                vars, rel = result
                cl = L.RelEnum(vars, rel)
            
            # If it's not an equation condition, emit it to new_clauses
            # and skip.
            result = match_eq_cond(cl)
            if result is None:
                new_clauses.append(cl)
                continue
            left, right = result
            
            # If both are in keepvars, emit and skip.
            if left in keepvars and right in keepvars:
                new_clauses.append(cl)
                continue
            
            # Flip if necessary due to keepvars.
            if right in keepvars and left not in keepvars:
                left, right = right, left
            
            # Refine partitioning, do not emit to new_clauses.
            part.equate(left, right)
        
        subst = part.to_subst()
        comp = comp._replace(clauses=new_clauses)
        comp = self.comp_rename_lhs_vars(comp, lambda x: subst.get(x, x))
        return comp
    
    def elim_sameclause_eqs(self, comp):
        """Rewrite a comprehension so that the same variable does
        not appear multiple times on the left-hand side of the same
        membership clause. Introduce fresh variables and equality
        condition clauses.
        """
        # Counter for how many new instances were needed for each LHS var.
        duplicate_count = {}
        # Set of LHS vars seen in current clause.
        seen_here = set()
        # List of new pairs of equated LHS vars for current clause.
        eqs = []
        
        def renamer(x):
            if x in seen_here:
                # Multiple occurrence, rename.
                duplicate_count.setdefault(x, 1)
                duplicate_count[x] += 1
                new_x = x + '_' + str(duplicate_count[x])
                eqs.append((x, new_x))
            else:
                # First time in this clause, leave alone.
                new_x = x
            
            seen_here.add(x)
            return new_x
        
        new_clauses = []
        for cl in comp.clauses:
            seen_here = set()
            eqs = []
            
            cl = self.rename_lhs_vars(cl, renamer)
            new_clauses.append(cl)
            
            # Add condition clauses.
            for left, right in eqs:
                cond = make_eq_cond(left, right)
                new_clauses.append(cond)
        
        return comp._replace(clauses=new_clauses)
    
    def rewrite_resexp_with_params(self, comp, params):
        """Assuming the result expression is a tuple expression,
        rewrite it to prepend components for the given parameter
        variables.
        """
        lhs_vars = self.lhs_vars_from_comp(comp)
        assert set(params).issubset(set(lhs_vars))
        assert isinstance(comp.resexp, L.Tuple)
        
        new_resexp = L.Tuple(tuple(L.Name(p) for p in params) +
                             comp.resexp.elts)
        return comp._replace(resexp=new_resexp)
    
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
    
    def get_loop_for_join(self, comp, body, query_name):
        """Given a join, create code for iterating over it and running
        body. The join is wrapped in a Query node with the given name.
        """
        assert self.is_join(comp)
        vars = self.lhs_vars_from_comp(comp)
        return (L.DecompFor(vars, L.Query(query_name, comp), body),)
    
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
    
    def get_maint_code(self, fresh_vars, fresh_join_names,
                       comp, result_var, update, *,
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
            join_name = next(fresh_join_names)
            code += self.get_loop_for_join(maint_join, body, join_name)
        
        return code


class CoreClauseTools(ClauseTools, CoreClauseVisitor):
    pass
