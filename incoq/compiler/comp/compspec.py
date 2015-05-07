"""Internal representation and logic for comprehensions."""


__all__ = [
    'CompSpec',
    
    'for_rel_code',
    'for_rels_union_code',
    'for_rels_union_disjoint_code',
    'make_comp_maint_code',
]


from simplestruct import Struct, TypedField

from incoq.util.type import checktype
from incoq.util.seq import pairs
from incoq.util.collections import OrderedSet, SetDict
from incoq.util.unify import apply_subst
import incoq.compiler.incast as L

from .clause import Clause, EnumClause
from .join import Join


class TupleTreeConstraintMaker(L.NodeVisitor):
    
    """Return a set of constraint equations for an expression in a
    given domain, to the extent that this expression is a tuple tree
    of variable names. When non-tuple-non-variable components are
    found, do not emit constraints for that part.
    """
    
    def __init__(self, rel, prefix):
        super().__init__()
        self.rel = rel
        """Name of relation domain that the whole expression belongs to."""
        self.prefix = prefix
    
    def process(self, tree):
        self.constrs = []
        
        self.path = []
        super().process(tree)
        assert len(self.path) == 0
        
        return self.constrs
    
    @property
    def current_domain(self):
        return '.'.join([self.rel] + [str(i) for i in self.path])
    
    def generic_visit(self, node):
        # Do not descend into other expression types.
        return
    
    def visit_Name(self, node):
        constr = (self.current_domain, self.prefix + node.id)
        self.constrs.append(constr)
    
    def visit_Tuple(self, node):
        # Produce the constraint that the current domain is a tuple
        # of correct arity.
        dom = self.current_domain
        subdoms = [dom + '.' + str(i) for i in range(1, len(node.elts) + 1)]
        constr = (dom, tuple(['<T>'] + subdoms))
        self.constrs.append(constr)
        
        # Produce constraints for each subterm.
        for i, elt in enumerate(node.elts, 1):
            self.path.append(i)
            self.visit(elt)
            self.path.pop()


class CompSpec(Struct):
    
    """Internal format for comprehensions."""
    
    join = TypedField(Join)
    resexp = TypedField(L.AST)
    params = TypedField(str, seq=True, unique=True)
    
    @classmethod
    def from_comp(cls, node, factory):
        """Construct from Comp node. Requires a ClauseFactory."""
        checktype(node, L.Comp)
        
        join = Join.from_comp(node, factory)
        
        return cls(join, node.resexp, node.params)
    
    def __new__(cls, join, resexp, params):
        if params is None:
            params = []
        return super().__new__(cls, join, resexp, params)
    
    def __init__(self, join, resexp, params):
        # Determine whether we can conservatively say the result
        # expression is duplicate safe. Used for rc-elimination
        # and for the special case of iterating over comps in
        # For loops.
        #
        # We know it's safe if the result expression is injective
        # and makes use of all local variables.
        localvars = set(self.join.enumvars) - set(self.params)
        resvars = set(L.VarsFinder.run(resexp, ignore_functions=True))
        self.is_duplicate_safe = (resvars.issuperset(localvars) and
                                  L.is_injective(resexp))
    
    def __str__(self):
        param_str = ((', '.join(self.params) + ' -> ')
                     if len(self.params) > 0 else '')
        proj_str = L.ts(self.resexp)
        join_str = str(self.join)
        return '{}{{{} : {}}}'.format(param_str, proj_str, join_str)
    
    def to_comp(self, options):
        clauses = tuple(cl.to_AST() for cl in self.join.clauses)
        return L.Comp(resexp=self.resexp,
                      clauses=clauses,
                      params=self.params,
                      options=options)
    
    def to_pattern(self):
        """Produce a semantically equivalent CompSpec whose join
        utilizes pattern matching.
        """
        # Unify variables.
        new_join, subst = self.join.elim_equalities(self.params)
        new_resexp = L.Templater.run(self.resexp, subst)
        resvars = L.VarsFinder.run(new_resexp, ignore_functions=True)
        
        # Make wildcards.
        keepvars = set(self.params) | set(resvars)
        new_join = new_join.make_wildcards(keepvars)
        
        return self._replace(join=new_join, resexp=new_resexp)
    
    def to_nonpattern(self):
        """Opposite of to_pattern(). Produce a semantically equivalent
        CompSpec whose join does not rely on pattern matching.
        """
        # Split variables.
        new_join = self.join.make_equalities(self.params)
        
        # Eliminate wildcards.
        new_join = new_join.elim_wildcards()
        
        return self._replace(join=new_join)
    
    def without_params(self, flat=False):
        """Produce a CompSpec where the result expression is rewritten
        as a tuple of the parameters and the old result expression, and
        where the parameters are turned into locals.
        
        If flat is True, the old result expression must be a tuple,
        and the new one is formed by concatenating a tuple of the
        parameters with the old result expression.
        """
        if flat:
            assert isinstance(self.resexp, L.Tuple)
            elts = self.params + self.resexp.elts
        else:
            elts = self.params + (self.resexp,)
        new_resexp = L.tuplify(elts)
        return self._replace(resexp=new_resexp, params=())
    
    def with_uset(self, uset_name, uset_params, *,
                  force=False):
        """Produce a CompSpec with an additional U-set constraint."""
        if len(uset_params) == 0 and not force:
            return self
        
        uset_clause = EnumClause(uset_params, uset_name)
        new_clauses = (uset_clause,) + self.join.clauses
        new_join = self.join._replace(clauses=new_clauses)
        return self._replace(join=new_join)
    
    def get_uncon_params(self):
        """Return a tuple of the unconstrained parameters. The U-set
        must at minimum contain these parameters.
        
        To find them, we traverse the clauses from left to right and
        add unconstrained parameters to the result set as they appear.
        This means that the clauses must be runnable in a left-to-right
        order; otherwise it is an error.
        
        If the query has cyclic constraints, there may be multiple
        possible minimal sets of parameters. The one corresponding to
        this left-to-right traversal is chosen.
        """
        result = ()
        supported = set()
        for cl in self.join.clauses:
            # Vars that have an occurrence in this clause that is
            # not constrained by the clause.
            if cl.kind is Clause.KIND_ENUM:
                uncon_occ = OrderedSet(
                    v for v, bindocc in zip(cl.enumlhs, cl.con_mask)
                      if not bindocc if v != '_')
            else:
                uncon_occ = OrderedSet(cl.vars)
            
            # Add each new unconstrained var to the result.
            # They must be parameters.
            new_uncons = uncon_occ - supported
            for v in new_uncons:
                if v in self.params:
                    if v not in result:
                        result += (v,)
                else:
                    raise AssertionError('Unconstrained var {} is not a '
                                         'parameter'.format(v))
            
            # Any enumvar of this clause is now supported/constrained.
            supported.update(cl.enumvars)
        
        return result
    
    def get_domain_constraints(self, resultname):
        """Return a sequence of equations representing domain
        constraints induced by this comprehension. The equations
        follow the form of util.unify. Enumeration variables are
        uniquely prefixed with resultname. resultname is also used
        to name the result relation.
        
        This method should be used after pattern rewriting has already
        been performed, so equality constraints are represented by
        common pattern variables.
        """
        constrs = []
        prefix = resultname + '_'
        
        # Add constraints for each clause.
        for cl in self.join.clauses:
            constrs.extend(cl.get_domain_constrs(prefix))
        
        # Add constraints for result expression.
        resconstrs = TupleTreeConstraintMaker.run(
                            self.resexp, resultname, prefix)
        constrs.extend(resconstrs)
        
        return constrs
    
    def get_membership_constraints(self):
        """Return a mapping from enumeration variables to sets of
        dompaths they are constrained by.
        """
        edges = set()
        for cl in self.join.clauses:
            edges.update(cl.get_membership_constrs())
        
        edges_buu = SetDict()
        for x, y, i in edges:
            edges_buu[x].add((y, i))
        
        # Recursive DFS to find all paths through edges.
        # Assumes edges have no cycles.
        def find(x):
            results = []
            for y, i in edges_buu[x]:
                if y in self.join.rels:
                    results.append((y, [i]))
                else:
                    for end, path in find(y):
                        results.append((end, path + [i]))
            return results
        
        mapping = {}
        for x in self.join.enumvars:
            paths = find(x)
            mapping[x] = {'.'.join([y] + [str(i) for i in p if i is not None])
                          for y, p in paths}
        
        return mapping


def for_rel_code(vars, iter, body):
    """Generate code to run body once for each element in the valuation
    of iter. vars are bound to the components of each element. iter
    should evaluate to a relation or arity len(vars).
    """
    return L.pc('''
        for VARS in ITER:
            BODY
        ''', subst={'VARS': L.tuplify(vars, lval=True),
                    'ITER': iter,
                    '<c>BODY': body})

def for_rels_union_code(vars, iters, body, tempname, *,
                        verify_disjoint=False):
    """Generate code to run body once for each element in the union
    of the evaluations of iters. A temporary set is used to eliminate
    duplicates from the union.
    """
    assert len(iters) > 0
    if len(iters) == 1:
        return for_rel_code(vars, iters[0], body)
    
    code = L.pc('''
        TEMPSET = set()
        ''', subst={'TEMPSET': tempname})
    
    for iter in iters:
        if verify_disjoint:
            template = L.trim('''
                for S_VARS in ITER:
                    assert VARS not in TEMPSET
                    TEMPSET.add(VARS)
                ''')
        else:
            template = L.trim('''
                for S_VARS in ITER:
                    TEMPSET.nsadd(VARS)
                ''')
        code += L.pc(template,
             subst={'S_VARS': L.tuplify(vars, lval=True),
                    'ITER': iter,
                    'TEMPSET': tempname,
                    'VARS': L.tuplify(vars)})
    
    code += L.pc('''
        for VARS in TEMPSET:
            BODY
        del D_TEMPSET
        ''', subst={'VARS': L.tuplify(vars, lval=True),
                    'TEMPSET': tempname,
                    '<c>BODY': body,
                    'D_TEMPSET': L.dn(tempname)})
    
    return code

def for_rels_union_disjoint_code(vars, iters, body):
    """Generate code to run body once for each element in the union
    of the evaluations of iters. The union must be disjoint.
    """
    assert len(iters) > 0
    if len(iters) == 1:
        return for_rel_code(vars, iters[0], body)
    
    code = ()
    for iter in iters:
        code += L.pc('''
            for VARS in ITER:
                BODY
            ''', subst={'VARS': L.tuplify(vars, lval=True),
                        'ITER': iter,
                        '<c>BODY': body})
    
    return code


def make_comp_maint_code(spec, resrel, deltarel, op, elem, prefix, *,
                         maint_impl, rc, selfjoin):
    """Construct comprehension maintenance code. Return the code and
    a list of maintenance comprehensions used.
    
        spec:
          CompSpec of the comprehension to be computed incrementally.
        
        resrel:
          Name of the relation holding the saved result.
        
        deltarel:
          Name of the updated relation that triggered maintenance.
        
        op:
          Update operation ('add' or 'remove').
        
        elem:
          AST of the element added or removed to deltarel.
        
        prefix:
          The prefix to use for making fresh local variables.
        
        maint_impl:
          Value to use for the 'impl' option of emitted
          maintenance comprehensions ('batch' or 'auxonly').
        
        rc:
          Whether or not the incrementally computed comprehension
          uses reference counts ('yes', 'no', 'safe').
        
        selfjoin:
          Strategy for computing self-joins. Possible values:
            'sub':
              use subtractive clauses
              (Code must be placed after addition / before removal.)
            'aug':
              use augmented clauses
              (Code must be placed before addition / after removal.)
            'das':
              use a differential assignment set
            'assume_disjoint':
              naive, only valid if joins are disjoint
            'assume_disjoint_verify':
              naive, use das to assert disjoint at runtime
    """
    assert op in ['add', 'remove']
    assert maint_impl in ['batch', 'auxonly']
    assert rc in ['yes', 'no', 'safe']
    assert selfjoin in ['sub', 'aug', 'das', 'assume_disjoint',
                        'assume_disjoint_verify']
    
    assert deltarel in spec.join.rels
    
    if len(spec.params) > 0:
        raise ValueError('Cannot incrementalize comprehension with '
                         'parameters')
    
    # Get the maintenance comprehensions.
    disjoint_strat = (selfjoin if selfjoin in ['sub', 'aug']
                      else 'das')
    maint_joins = spec.join.get_maint_joins(elem, deltarel, op, prefix,
                                            disjoint_strat=disjoint_strat)
    maint_comps = [j.to_comp({'impl': maint_impl})
                   for j in maint_joins]
    # Get the maintenance joins' enumvars.
    assert all(j1.enumvars == j2.enumvars
               for j1, j2 in pairs(maint_joins))
    maint_projvars = maint_joins[0].enumvars
    
    # Decide whether the body is a normal update or
    # a reference-counted one.
    use_rc = {'yes': True,
              'no': False,
              'safe': not spec.is_duplicate_safe}[rc]
    if use_rc:
        op = 'rc' + op
    resvars = L.VarsFinder.run(spec.resexp, ignore_functions=True)
    resexp = L.prefix_names(spec.resexp, resvars, prefix)
    body = L.pc('''
        RES.OP(RESEXP)
        ''', subst={'RES': resrel,
                    '@OP': op,
                    'RESEXP': resexp})
    
    # Create code according to the choice of self-join strategy.
    if selfjoin in ['sub', 'aug', 'assume_disjoint']:
        code = for_rels_union_disjoint_code(
                        maint_projvars, maint_comps, body)
    else:
        dasprefix = prefix + 'DAS'
        ver_dis = selfjoin == 'assume_disjoint_verify'
        code = for_rels_union_code(
                        maint_projvars, maint_comps, body,
                        dasprefix, verify_disjoint=ver_dis)
    
    return code, maint_comps
