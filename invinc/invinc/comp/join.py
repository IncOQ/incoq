"""Joins, which are the basis for comprehensions."""


__all__ = [
    'DeltaInfo',
    'Join',
]


from itertools import chain
from collections import defaultdict

from simplestruct import Struct, Field

from util.type import checktype
from util.seq import elim_duplicates, pairs
from util.collections import Partitioning
import invinc.incast as L
from invinc.set import Mask

from .clause import Clause
from .order import AsymptoticOrderer


class DeltaInfo(Struct):
    
    """Information about maintenance joins."""
    
    rel = Field(str)
    """Delta relation."""
    elem = Field(L.AST)
    """Delta element expression AST."""
    lhs = Field(str, 'seq')
    """Delta clause LHS identifier list."""
    op = Field(str)
    """'add' or 'remove'."""
    
    @classmethod
    def from_options(cls, options):
        """Construct from comprehension options dict.
        If delta info isn't provided, return None instead
        of an instance.
        """
        if options is None or '_deltarel' not in options:
            return None
        
        rel = options['_deltarel']
        elem = options['_deltaelem']
        elem = L.pe(elem)
        lhs = options['_deltalhs']
        lhs = L.get_vartuple(L.pe(lhs))
        op = options['_deltaop']
        return cls(rel, elem, lhs, op)
    
    def __init__(self, rel, elem, lhs, op):
        assert op in ['add', 'remove']
    
    def updateopts(self, options):
        """Return a modified options dict with the delta keys set."""
        options = dict(options)
        options['_deltarel'] = self.rel
        options['_deltaelem'] = L.ts(self.elem)
        options['_deltalhs'] = L.ts(L.tuplify(self.lhs, lval=True))
        options['_deltaop'] = self.op
        return options


class Join(Struct):
    
    """A join of one or more enumerator clauses and zero or more
    condition clauses. No definite order, cost, or code.
    
    Note that joins do not project out variables, unlike
    comprehensions.
    """
    
    clauses = Field(Clause, 'seq')
    """Sequence of clauses."""
    factory = Field()
    """Clause factory to use."""
    delta = Field()
    """DeltaInfo or None."""
    
    @classmethod
    def from_comp(cls, node, factory):
        """Construct from Comp node, ignoring the result expression.
        factory is used to construct clauses from their ASTs.
        """
        checktype(node, L.Comp)
        clauses = [factory.from_AST(clast) for clast in node.clauses]
        delta = DeltaInfo.from_options(node.options)
        return cls(clauses, factory, delta)
    
    def __init__(self, clauses, factory, delta):
        assert len(clauses) > 0
        
        # Derived data.
        
        self.enumvars = elim_duplicates(tuple(chain.from_iterable(
                            cl.enumvars for cl in self.clauses)))
        """Tuple of all enumeration variables used by the clauses."""
        
        self.vars = elim_duplicates(tuple(chain.from_iterable(
                            cl.vars for cl in self.clauses)))
        """Tuple of all variables used by the clauses."""
        
        self.rels = elim_duplicates(tuple( \
                        cl.enumrel for cl in self.clauses
                        if cl.enumrel is not None))
        """Tuple of all sets iterated by the clauses."""
        
        self.robust = all(cl.robust for cl in self.clauses)
        """True if this join is meaningful when moved to a different
        program point. Required for incrementalization.
        """
        self.inc_safe = all(cl.inc_safe for cl in self.clauses)
        """True if this join is safe to incrementalize, aside from
        issues of robustness.
        """
        
        self.has_wildcards = any(cl.has_wildcards for cl in self.clauses)
        
        self.has_demand = any(cl.has_demand for cl in self.clauses)
    
    def __str__(self):
        return ', '.join(str(cl) for cl in self.clauses)
    
    def to_comp(self, options):
        """Create a corresponding Comp node."""
        clauses = tuple(cl.to_AST() for cl in self.clauses)
        if self.delta is not None:
            options = self.delta.updateopts(options)
        return L.Comp(L.tuplify(self.enumvars),
                      clauses, (), options)
    
    def rewrite_subst(self, subst):
        """Return a modified Join that renames according to the given
        substitution mapping.
        """
        new_clauses = [self.factory.rewrite_subst(cl, subst)
                       for cl in self.clauses]
        return self._replace(clauses=new_clauses)
    
    def prefix_enumvars(self, prefix):
        """Return a modified Join that has the given prefix on each
        enumeration variable.
        """
        subst = {var: prefix + var for var in self.enumvars}
        return self.rewrite_subst(subst)
    
    def elim_equalities(self, keepvars):
        """Produce a semantically equivalent join that eliminates
        equality conditions by unifying the equated variables.
        For instance, a condition "x == y" will be eliminated, and
        all occurrences of y in the remaining clauses will be replaced
        by uses of x.
        
        Variables that are listed in sequence keepvars will not be
        eliminated. If y is in keepvars and x is not, then uses of
        x will be renamed to y, not vice versa. If both x and y are
        in keepvars, the condition will be skipped and the variables
        not unified.
        
        Condition clauses that express a relational membership
        constraint are turned into enumerators.
        
        The new join and the variable substitution are returned.
        
        This operation is idempotent.
        """
        part = Partitioning()
        new_clauses = []
        for cl in self.clauses:
            # Handle converting membership conditions to enumerators.
            if cl.kind is Clause.KIND_COND:
                cl = self.factory.membercond_to_enum(cl)
            
            # Skip if not an equation.
            if cl.eqvars is None:
                new_clauses.append(cl)
                continue
            lhs, rhs = cl.eqvars
            
            # Skip if both are keepvars.
            if lhs in keepvars and rhs in keepvars:
                new_clauses.append(cl)
                continue
            
            # Flip if necessary, to ensure keepvars are preserved.
            if rhs in keepvars and lhs not in keepvars:
                lhs, rhs = rhs, lhs
            
            part.equate(lhs, rhs)
        
        subst = part.to_subst()
        new_join = self._replace(clauses=new_clauses)
        new_join = new_join.rewrite_subst(subst)
        return new_join, subst
    
    def make_wildcards(self, keepvars):
        """Produce a semantically equivalent join in which enumeration
        variables that occur only once are replaced by wildcards. This
        excludes cases where the variable occurs twice in the same
        clause, or where it occurs in condition clauses.
        
        Variables in keepvars are also excluded from this processing.
        
        This operation is idempotent.
        """
        single_use = []
        for i, cl in enumerate(self.clauses):
            other_clauses = self.clauses[:i] + self.clauses[i+1:]
            for var in cl.enumvars:
                # Protect keepvars.
                if var in keepvars:
                    continue
                # Check for multiple occurrences in this clause.
                if cl.enumlhs.count(var) > 1:
                    continue
                # Check for any occurrence in other clauses.
                if any(var in cl2.vars for cl2 in other_clauses):
                    continue
                
                single_use.append(var)
        
        subst = {var: '_' for var in single_use}
        return self.rewrite_subst(subst)
    
    def make_equalities(self, boundvars):
        """Opposite of elim_equalities(). Produce a semantically
        equivalent join in which no enumeration variable appears more
        than once among the left-hand sides of all enumerators (whether
        in the same clause or different clauses). Multiple occurrences
        of the same variable get renamed to fresh variables, with new
        condition clauses added to equate the fresh variables to the
        first variable.
        
        Variables that appear in boundvars are considered to have
        occurred once already outside the join.
        
        Enumerators in which all enumeration variables have been
        replaced in this manner get turned into condition clauses.
        
        Some occurrences inside enumerators are not replaced,
        depending on the clause's pat_mask field.
        """
        # Map from each enum var to a counter, used to make fresh
        # identifiers for its occurrences. 
        repl_counts = defaultdict(lambda: 0)
        # Map from each enum var to a list of the names that will
        # be used to replace its occurrences, in order. Occurrences
        # that should not be replaced map to themselves in the list.
        # If the var is in boundvars, there is one extra occurrence
        # at the front of the list. Occurrences inside condition
        # clauses are not accounted for in the list.
        repl_map = defaultdict(lambda: [])
        
        def add_repl_occ(v):
            """Process an occurrence that is subject to renaming."""
            # Ignore wildcards.
            if v == '_':
                return
            # First occurrence is not renamed, later occurrences are.
            repl_counts[v] += 1
            occ_name = (v if repl_counts[v] == 1
                        else v + '_' + str(repl_counts[v]))
            repl_map[v].append(occ_name)
        
        def add_skip_occ(v):
            """Process an occurrence that is left unchanged."""
            # Wildcards should not occur.
            # (Not sure about this, could make it just skip, like above.)
            assert v != '_'
            repl_map[v].append(v)
        
        for v in boundvars:
            add_repl_occ(v)
        
        # Process occurrences in the clauses. In addition,
        # all-bound enumerators get turned into condition clauses.
        new_clauses = []
        for cl in self.clauses:
            # Skip conditions.
            if cl.kind is Clause.KIND_COND:
                new_clauses.append(cl)
                continue
            
            # All-bound enum becomes a condition.
            if set(cl.enumlhs).issubset(repl_counts):
                cl = self.factory.enum_to_membercond(cl)
                new_clauses.append(cl)
                continue
            
            # Normal case.
            for v, p in zip(cl.enumlhs, cl.pat_mask):
                if p:
                    add_repl_occ(v)
                else:
                    add_skip_occ(v)
            new_clauses.append(cl)
        
        # Create new condition clauses to equate the new variables.
        new_conds = []
        for v in self.enumvars:
            repl_list = repl_map[v]
            for v1, v2 in pairs(repl_list):
                # No equality needed for identity replacements.
                if v == v2:
                    continue
                condcl = self.factory.from_AST(L.cmpeq(L.ln(v1), L.ln(v2)))
                new_conds.append(condcl)
        
        # Define a substitution that calls a function to consume
        # the next identifier from the appropriate list.
        # For boundvars, start replacing at the second slot onward.
        
        for v in repl_map:
            if v in boundvars:
                repl_map[v].pop(0)
        
        def var_renamer(v):
            return repl_map[v].pop(0)
        
        # Use rewrite_lhs(), not rewrite_subst().
        # We don't want to rewrite demparams, for instance.
        subst = {v: var_renamer for v in self.enumvars}
        new_clauses = [self.factory.rewrite_lhs(cl, subst)
                          if cl.kind is Clause.KIND_ENUM else cl
                       for cl in new_clauses]
        
        # Insert each new condition clause immediately after both
        # equated variables have been seen.
        # For each clause in new_join, pull in the applicable cond
        # clauses and delete them from the new_conds list.
        new_clauses_with_conds = []
        seenvars = set(boundvars)
        for cl in new_clauses:
            new_clauses_with_conds.append(cl)
            seenvars.update(cl.enumvars)
            
            for condcl in list(new_conds):
                lhs, rhs = condcl.eqvars
                if lhs in seenvars and rhs in seenvars:
                    new_conds.remove(condcl)
                    new_clauses_with_conds.append(condcl)
        assert len(new_conds) == 0
        
        return self._replace(clauses=new_clauses_with_conds)
    
    def elim_wildcards(self):
        """Opposite of make_wildcards(). Produce a semantically
        equivalent join in which wildcards have been replaced by
        fresh variables.
        """
        fresh_names = L.NameGenerator(fmt='_v{}', counter=1)
        subst = {'_': lambda _: fresh_names.next()}
        
        new_clauses = [self.factory.rewrite_lhs(cl, subst)
                          if cl.kind is Clause.KIND_ENUM else cl
                       for cl in self.clauses]
        return self._replace(clauses=new_clauses)
        
    
    def get_maint_joins(self, elem, rel, op, prefix, *,
                        disjoint_strat):
        """Derive maintenance joins for when relation rel is updated
        by a single-element change of elem. Apply a prefix to these
        joins.
        
        If this join is not robust, TypeError is raised.
        
        disjoint_strat controls what strategy is used to ensure
        maintenance joins are disjoint.
        
            'das': No strategy; joins are not necessarily disjoint
            'sub': Subtractive clauses are used for clauses over
                rel to the right of the delta clause
            'aug': Augmented clauses are used for clauses over
                rel to the right of the delta clause
        """
        assert disjoint_strat in ['das', 'sub', 'aug']
        augmented = disjoint_strat == 'aug'
        
        for cl in self.clauses:
            if not (cl.robust and cl.inc_safe):
                raise AssertionError('Cannot incrementally maintain '
                                     'join with fragile clause: ' + str(cl))
        
        clauses = list(self.prefix_enumvars(prefix).clauses)
        
        maint_joins = []
        for i, cl in enumerate(clauses):
            if cl.enumrel == rel:
                # Emit a join with this clause as the delta clause.
                delta = self.factory.bind(cl, elem, augmented=augmented)
                prev_clauses = clauses[:i]
                succ_clauses = clauses[i+1:]
                
                if disjoint_strat in ['sub', 'aug']:
                    rewriter = {'sub': self.factory.subtract,
                                'aug': self.factory.augment}[disjoint_strat]
                    succ_clauses = \
                        [rewriter(cl, elem) if cl.enumrel == rel else cl
                         for cl in succ_clauses]
                
                new_clauses = prev_clauses + [delta] + succ_clauses
                join = self._replace(clauses=new_clauses)
                join = join._replace(delta=DeltaInfo(
                                        rel, elem, cl.enumlhs, op))
                maint_joins.append(join)
        
        return maint_joins
    
    def get_ordering(self, init_bounds, *, orderer=None):
        """Get a clause ordering for a join. init_bounds is a sequence
        of the initially bound variables. orderer is the AsymptoticOrderer
        instance to use; if not provided, one will be created.
        """
        if orderer is None:
            orderer = AsymptoticOrderer()
        
        return orderer.get_order(enumerate(self.clauses), init_bounds)
    
    def get_code(self, init_bounds, body, *, orderer=None,
                 augmented):
        """Make code for executing body once for each tuple in the
        join. init_bounds and orderer are as for get_ordering().
        """
        ordering = self.get_ordering(init_bounds, orderer=orderer)
        clauses = [cl for _i, cl, _bindenv in ordering]
        
        # TODO: The work of maintaining a bindenv should be refactored
        # into the ordering logic. In fact, it's already there, just
        # not exposed.
        
        bindenvs = [set(init_bounds)]
        for cl in clauses:
            bindenvs.append(set(bindenvs[-1]).union(cl.enumvars))
        
        code = body
        for bindenv, cl in reversed(list(zip(bindenvs, clauses))):
            code = cl.get_code(bindenv, code)
        
        return code
