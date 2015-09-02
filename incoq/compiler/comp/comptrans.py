"""Comprehension transformation."""


__all__ = [
    'IncComp',
    
    'make_inccomp',
    'inc_relcomp_helper',
    'inc_relcomp',
    'inc_changetrack',
    'impl_auxonly_relcomp',
    'patternize_comp',
    'depatternize_comp',
    'patternize_all',
    'depatternize_all',
    'comp_inc_needs_dem',
    'comp_isvalid',
    'split_eqwild_clauses',
]

import itertools

import incoq.compiler.incast as L
from incoq.compiler.set import Mask

from .clause import EnumClause
from .join import Join
from .compspec import make_comp_maint_code, CompSpec


def get_uset_params(spec, mode, explicit):
    """Return a tuple of the parameters that make it into the U-set
    under the given mode.
    """
    
    if mode == 'none':
        return ()
    
    elif mode == 'all':
        return spec.params
    
    elif mode == 'uncon':
        return spec.get_uncon_params()
    
    elif mode == 'explicit':
        assert set(explicit).issubset(spec.params)
        return tuple(p for p in spec.params if p in explicit)
    
    else:
        assert()


class IncComp:
    
    """A comprehension along with incrementalization info."""
    
    def __init__(self, comp, spec, name, use_uset, uset_name, uset_params,
                 rc, selfjoin, maint_impl, outsideinvs, uset_lru,
                 eager_demand_params):
        self.comp = comp
        self.spec = spec 
        self.name = name
        self.use_uset = use_uset
        self.uset_name = uset_name
        self.uset_params = uset_params
        self.rc = rc
        self.selfjoin = selfjoin
        self.maint_impl = maint_impl
        self.outsideinvs = outsideinvs
        self.uset_lru = uset_lru
        self.eager_demand_params = eager_demand_params
        
        self.change_tracker = False
        
        assert maint_impl in ['batch', 'auxonly']


class RelcompMaintainer(L.OuterMaintTransformer):
    
    """Relational comprehension maintenance transformer.
    
    If inccomp.change_tracker is True, instead of creating code to
    maintain the result, create code to add all changes that would
    be performed, whether addition or removal, to the result set.
    This requires that reference counting not be used.
    """
    
    def __init__(self, manager, inccomp):
        super().__init__(inccomp.outsideinvs)
        self.manager = manager
        self.inccomp = inccomp
        
        self.demnames = [cl.demname for cl in inccomp.spec.join.clauses]
        
        name = inccomp.name
        rels = self.inccomp.spec.join.rels
        self.addfuncs = {rel: '_maint_{}_{}_add'.format(name, rel)
                         for rel in rels}
        self.removefuncs = {rel: '_maint_{}_{}_remove'.format(name, rel)
                            for rel in rels}
    
    def process(self, tree):
        self.maint_comps = []
        tree = super().process(tree)
        return tree, self.maint_comps
    
    def visit_Module(self, node):
        resinit = L.pe('RCSet()')
        
        code = L.pc('''
            RES = RESINIT
            ''', subst={'RES': self.inccomp.name,
                        'RESINIT': resinit})
        
        rc = {'yes': True,
              'no': False,
              'safe': not self.inccomp.spec.is_duplicate_safe} \
              [self.inccomp.rc]
        
        if not rc:
            self.manager.stats['rcsets simplified'] += 1
        
        for rel in self.inccomp.spec.join.rels:
            prefix1 = self.manager.namegen.next_prefix()
            prefix2 = self.manager.namegen.next_prefix()
            
            add_code, add_comps = make_comp_maint_code(
                self.inccomp.spec, self.inccomp.name,
                rel, 'add', L.pe('_e'),
                prefix1,
                maint_impl=self.inccomp.maint_impl,
                rc=rc,
                selfjoin=self.inccomp.selfjoin)
            
            remove_code, remove_comps = make_comp_maint_code(
                self.inccomp.spec, self.inccomp.name,
                rel, 'remove', L.pe('_e'),
                prefix2,
                maint_impl=self.inccomp.maint_impl,
                rc=rc,
                selfjoin=self.inccomp.selfjoin)
            
            self.maint_comps.extend(add_comps)
            self.maint_comps.extend(remove_comps)
            
            code += L.pc('''
                def ADDFUNC(_e):
                    ADDCODE
                def REMOVEFUNC(_e):
                    REMOVECODE
                ''', subst={'<def>ADDFUNC': self.addfuncs[rel],
                            '<c>ADDCODE': add_code,
                            '<def>REMOVEFUNC': self.removefuncs[rel],
                            '<c>REMOVECODE': remove_code})
            
            vt = self.manager.vartypes
            for e in self.inccomp.spec.join.enumvars:
                if e in vt:
                    vt[prefix1 + e] = vt[e]
                    vt[prefix2 + e] = vt[e]
        
        node = node._replace(body=code + node.body)
        node = self.generic_visit(node)
        return node
    
    def helper(self, node, var, op, elem):
        assert op in ['add', 'remove']
        
        # Maintenance goes after addition updates and before removals,
        # except when we're using augmented code, which relies on the
        # value of the set *without* the updated element.
        after_add = self.inccomp.selfjoin != 'aug'
        is_add = op == 'add'
        
        if self.inccomp.change_tracker:
            # For change trackers, all removals turn into additions,
            # but are still run in the same spot they would have been.
            funcdict = self.addfuncs
        else:
            funcdict = self.addfuncs if is_add else self.removefuncs
        
        func = funcdict[var]
        code = L.pc('FUNC(ELEM)',
                    subst={'FUNC': func,
                           'ELEM': elem})
        
        if after_add ^ is_add:
            precode = code
            postcode = ()
        else:
            precode = ()
            postcode = code
        
        # Respect outsideinvs. This ensures that demand invariant
        # maintenance is inserted before/after the query maintenance.
        return self.with_outer_maint(node, self.inccomp.name, L.ts(node),
                                     precode, postcode)
    
    def visit_SetUpdate(self, node):
        node = self.generic_visit(node)
        
        if not node.is_varupdate():
            return node
        var, op, elem = node.get_varupdate()
        if var not in self.inccomp.spec.join.rels:
            return node
        
        return self.helper(node, var, op, elem)


class CompReplacer(L.NodeTransformer):
    
    """Replace comp queries with uses of their saved results."""
    
    def __init__(self, manager, inccomp):
        super().__init__()
        self.manager = manager
        self.inccomp = inccomp
    
    def process(self, tree):
        self.manager.add_invariant(self.inccomp.name, self.inccomp)
        return super().process(tree)
    
    def get_res_code(self):
        """Return code (expression) to lookup the result."""
        params = self.inccomp.comp.params
        
        if len(params) > 0:
            resexp = self.inccomp.spec.resexp
            assert isinstance(resexp, L.Tuple)
            resexp_arity = len(resexp.elts)
            n_rescomponents = resexp_arity - len(params)
            
            maskstr = 'b' * len(params) + 'u' * n_rescomponents
            masknode = Mask(maskstr).make_node()
            paramsnode = L.tuplify(params)
            
            code = L.pe('''
                setmatch(RES, MASK, PARAMS)
                ''', subst={'RES': L.ln(self.inccomp.name),
                            'MASK': masknode,
                            'PARAMS': paramsnode})
        
        else:
            code = L.ln(self.inccomp.name)
        
        return code
    
    def visit_Module(self, node):
        # Recurse after adding the query function.
        # (Probably doesn't matter.)
        
        if self.inccomp.use_uset:
            name = self.inccomp.name
            lrulimit = self.inccomp.uset_lru
            demparams = self.inccomp.uset_params
            specstr = str(self.inccomp.spec)
            
            maker = L.DemfuncMaker(name, specstr, demparams, lrulimit)
            code = maker.make_alldem()
            
            node = node._replace(body=code + node.body)
        
        node = self.generic_visit(node)
        
        return node
    
    def visit_NoDemQuery(self, node):
        # If a comp is wrapped in a NoDemQuery and gets incrementalized,
        # make sure to strip the Demand node that got added around it.
        was_comp = isinstance(node.value, L.Comp)
        
        node = self.generic_visit(node)
        
        if was_comp and isinstance(node.value, L.DemQuery):
            node = node.value.value
        
        return node
    
    def visit_Comp(self, node):
        node = self.generic_visit(node)
        
        if node != self.inccomp.comp:
            return node
        
        if self.inccomp.use_uset:
            code = L.DemQuery(self.inccomp.name,
                              tuple(L.ln(p) for p in self.inccomp.uset_params),
                              self.get_res_code())
        else:
            code = self.get_res_code()
        
        return code


class AuxonlyTransformer(L.NodeTransformer):
    
    """Implement a relcomp using clause ordering and auxiliary maps."""
    
    # There are two kinds of translations.
    #
    #   - Ordinary uses of comprehensions get replaced with a
    #     call to a query function.
    #
    #   - Iterations over comprehensions get replaced with a direct
    #     implementation, without need of a separate query function
    #     or temporary result set. This only applies if the resexp
    #     syntactically matches the loop target (they are the same
    #     variable or tuple of variables), and if the comp is
    #     duplicate-safe. 
    #
    # The query function is not created if there are no ordinary
    # uses to require it.
    
    def __init__(self, manager, comp, name, *, augmented):
        self.manager = manager
        self.comp = comp
        self.name = name
        self.augmented = augmented
        
        spec = CompSpec.from_comp(self.comp, manager.factory)
        self.spec = spec
        
        self.need_func = False
    
    def visit_Module(self, node):
        spec = self.spec
        
        node = self.generic_visit(node)
        
        code = L.pc('''
            result.nsadd(RESEXP)
            ''', subst={'RESEXP': spec.resexp})
        
        code = spec.join.get_code(spec.params, code,
                                  augmented=self.augmented)
        
        code = L.pc('''
            SPEC_STR
            result = set()
            COMPUTE
            return result
            ''', subst={'SPEC_STR': L.Str(s=str(self.spec)),
                        '<c>COMPUTE': code})
        
        code = L.plainfuncdef(L.N.queryfunc(self.name), spec.params, code)
        
        if self.need_func:
            node = node._replace(body=code + node.body)
        
        return node
    
    def visit_Comp(self, node):
        node = self.generic_visit(node)
        
        if node != self.comp:
            return node
        
        self.need_func = True
        
        call = L.pe('QFUN(__ARGS)',
                    subst={'QFUN': L.ln(L.N.queryfunc(self.name))})
        
        call = call._replace(args=tuple(L.ln(p)
                                        for p in self.comp.params))
        
        return call
    
    def visit_For(self, node):
        # Recurse only after we've handled the potential special case.
        
        if node.iter != self.comp:
            return self.generic_visit(node)
        
        spec = self.spec
        
        special_case = (
            node.orelse == () and
            spec.is_duplicate_safe and
            L.is_vartuple(node.target) and
            L.is_vartuple(spec.resexp) and
            (L.get_vartuple(node.target) == L.get_vartuple(spec.resexp) or
             (L.is_name(node.target) and L.get_name(node.target) == '_'))
        )
        if special_case:
            code = ()
            code += (L.Comment('Iterate ' + str(spec)),)
            code += spec.join.get_code(spec.params, node.body,
                                       augmented=self.augmented)
            return self.visit(code)
        else:
            return self.generic_visit(node)


class SubqueryArityFinder(L.NodeVisitor):
    
    """Determine if all occurrences of a comprehension are as a
    subquery with an arity consistent with the result expression.
    """
    
    class Failure(BaseException):
        pass
    
    def __init__(self, comp):
        super().__init__()
        self.comp = comp
    
    def process(self, tree):
        # Result value:
        #   False: non-subquery occurrence found, or subquery
        #     occurrences with inconsistent arity
        #   integer: subquery occurrences only, consistent arity
        
        if isinstance(self.comp.resexp, L.Tuple):
            self.arity = len(self.comp.resexp.elts)
        else:
            self.arity = 1
        
        try:
            super().process(tree)
        except self.Failure:
            self.arity = False
        
        return self.arity
    
    def visit_Comp(self, node):
        if node == self.comp:
            raise self.Failure
        
        self.generic_visit(node)
    
    def visit_Enumerator(self, node):
        if node.iter == self.comp:
            if not L.is_vartuple(node.target):
                raise self.Failure
            arity = len(L.get_vartuple(node.target))
            if self.arity != arity:
                raise self.Failure
            return
        
        self.generic_visit(node)


def get_subquery_demnames(spec):
    """For each subquery in a comp, construct an invariant definition
    for its U-set, formed as the conjunction of the enumerators to the
    left of the subquery's occurrence. Each parameter of the subquery
    must be an enumvar in one of these clauses. Return a list of pairs
    of a demand name of a subquery and its invariant (comp spec).
    """
    clauses = spec.join.clauses
    clauses = [cl for cl in clauses if cl.kind is cl.KIND_ENUM]
    result = []
    
    for i, cl in enumerate(clauses):
        if cl.has_demand:
            # Grab clauses to the left of this one.
            # If they too are demand clauses, unwrap them to get
            # the underlying clause.
            demclauses = clauses[:i]
            for i, demcl in enumerate(demclauses):
                if demcl.has_demand:
                    demclauses[i] = demcl.cl
            
            # Make sure the demand parameters are all bound in clauses
            # to the left of here.
            boundvars = set(v for demcl in demclauses for v in demcl.enumvars)
            unboundparams = set(cl.demparams) - boundvars
            assert len(unboundparams) == 0, \
                'Subquery parameter(s) {} not bound in clause to left ' \
                'of occurrence'.format(unboundparams)
            # Construct the invariant.
            new_join = Join(demclauses, spec.join.factory, None)
            new_spec = CompSpec(new_join, L.tuplify(cl.demparams), ())
            result.append((cl.demname, new_spec))
    
    return result


def make_inccomp(tree, manager, comp, name, *,
                 force_uset=False, outsideinvs=()):
    """Make the IncComp structure describing how to incrementalize
    a comprehension.
    """
    get = manager.options.get_queryopt
    uset_mode = get(comp, 'uset_mode')
    explicit = get(comp, 'uset_params')
    maint_impl = get(comp, 'maint_impl')
    eager_demand_params = get(comp, 'eager_demand_params')
    
    no_rc = get(comp, 'no_rc')
    rc_elim = manager.options.get_opt('rc_elim')
    # 'rc_elim' must be enabled to do elimination,
    # even when 'no_rc' is set on the individual query.
    if rc_elim:
        if no_rc:
            rc = 'no'
        else:
            rc = 'safe'
    else:
        rc = 'yes'
    
    selfjoin_strat = manager.options.get_opt('selfjoin_strat')
    
    can_flatten = (isinstance(comp.resexp, L.Tuple) and
                   SubqueryArityFinder.run(tree, comp))
    spec = CompSpec.from_comp(comp, manager.factory)
    uset_params = get_uset_params(spec, uset_mode, explicit)
    spec = spec.with_uset(L.N.uset(name), uset_params,
                          force=force_uset)
    spec = spec.without_params(flat=can_flatten)
    use_uset = len(uset_params) > 0 or force_uset
    
    uset_lru = get(comp, 'uset_lru')
    if uset_lru is None:
        uset_lru = manager.options.get_opt('default_uset_lru')
    
    return IncComp(comp, spec, name, use_uset, L.N.uset(name),
                   uset_params, rc, selfjoin_strat, maint_impl,
                   outsideinvs, uset_lru, eager_demand_params)

def inc_relcomp_helper(tree, manager, inccomp):
    """Incrementalize a comprehension based on an IncComp structure.
    Also return maintenance comprehensions.
    """
    if manager.options.get_opt('verbose'):
        s = ('Incrementalizing ' + inccomp.name + ': ').ljust(45)
        s += L.ts(inccomp.comp)
        print(s)
    
    # FIXME: Is the below demand code correct when the inner query's
    # demand invariant must be reference-counted? Given that change
    # tracking doesn't handle reference counting?
    
    # Create invariants for demand sets for demand-driven subqueries.
    # This only fires if we have subqueries with demand and this outer
    # query is being transformed WITHOUT filtering. If we are being
    # transformed WITH filtering, the inner queries would have been
    # rewritten without demand first; see demand/demtrans.py.
    deminvs = get_subquery_demnames(inccomp.spec)
    # Incrementalize them. Use a delta-set for deferring the propagation
    # of demand until after the inner query's maintenance code already
    # runs. (The inner query has already been incrementalized.)
    for demname, demspec in deminvs:
        # Hack: OuterDemandMaintainer should be refactored to move
        # to here, to avoid this import.
        from incoq.demand.demtrans import OuterDemandMaintainer
        
        # Determine dependencies of demand invariant.
        at_rels = set(e.enumrel for e in demspec.join.clauses)
        
        deltaname = L.N.deltaset(demname)
        demcomp = demspec.to_comp({})
        # Add delta maintenance code as per the invariant.
        tree = inc_changetrack(tree, manager, demcomp, deltaname)
        # Add code (outside all other maintenance) to propagate
        # the delta changes to the actual inner query demand function.
        tree = OuterDemandMaintainer.run(
                    tree, manager, deltaname,
                    demname, at_rels,
                    L.get_vartuple(demcomp.resexp),
                    None)
    
    # Unwrap the demand clauses in the comp now that we've handled them.
    spec = inccomp.spec
    new_clauses = []
    for cl in spec.join.clauses:
        if cl.has_demand:
            cl = cl.cl
        new_clauses.append(cl)
    new_spec = spec._replace(join=spec.join._replace(clauses=new_clauses))
    inccomp.spec = new_spec
    
    tree = CompReplacer.run(tree, manager, inccomp)
    tree, comps = RelcompMaintainer.run(tree, manager, inccomp)
    
    # If this was an original query, register it with the manager.
    if 'in_original' in inccomp.comp.options:
        manager.original_queryinvs.add(inccomp.name)
    
    # Add calls to the query function around uset param updates,
    # if requested.
    from incoq.compiler.central.rewritings import EagerDemandRewriter
    for param in inccomp.eager_demand_params:
        tree = EagerDemandRewriter.run(tree, param, inccomp.name,
                                       inccomp.uset_params)
    
    return tree, comps

def inc_relcomp(tree, manager, comp, name, *, outsideinvs=()):
    """Incrementalize a comprehension."""
    inccomp = make_inccomp(tree, manager, comp, name, outsideinvs=outsideinvs)
    tree, _comps = inc_relcomp_helper(tree, manager, inccomp)
    return tree

def inc_changetrack(tree, manager, comp, name):
    """Generate change-tracking code."""
    inccomp = make_inccomp(tree, manager, comp, name)
    inccomp.change_tracker = True
    tree, _comps = inc_relcomp_helper(tree, manager, inccomp)
    return tree


def impl_auxonly_relcomp(tree, manager, comp, name):
    if manager.options.get_opt('verbose'):
        s = ('Auxonly ' + name + ': ').ljust(45)
        s += L.ts(comp)
        print(s)
    
    augmented = manager.options.get_opt('selfjoin_strat') == 'aug'
    
    tree = AuxonlyTransformer.run(tree, manager, comp, name,
                                  augmented=augmented)
    return tree


def patternize_comp(comp, factory):
    """Patternize a comprehension."""
    spec = CompSpec.from_comp(comp, factory)
    spec = spec.to_pattern()
    return spec.to_comp(comp.options)

def depatternize_comp(comp, factory):
    """Depatternize a comprehension."""
    spec = CompSpec.from_comp(comp, factory)
    spec = spec.to_nonpattern()
    return spec.to_comp(comp.options)

def patternize_all(tree, factory):
    """Patternize all comps in the program."""
    class Patternizer(L.QueryMapper):
        def map_Comp(self, node):
            return patternize_comp(node, factory)
    
    return Patternizer.run(tree)

def depatternize_all(tree, factory):
    """Depatternize all (valid) comps in the program."""
    class Depatternizer(L.QueryMapper):
        ignore_invalid = True
        def map_Comp(self, node):
            return depatternize_comp(node, factory)
    
    return Depatternizer.run(tree)


def comp_inc_needs_dem(manager, comp):
    """Given a Comp node, return whether demand is required for
    incrementalization.
    """
    spec = CompSpec.from_comp(comp, manager.factory)
    return spec.join.has_demand


def comp_isvalid(manager, comp):
    """Return whether a Comp node satisfies the syntactic requirements
    of a relational comprehension.
    """
    try:
        CompSpec.from_comp(comp, manager.factory)
    except TypeError:
        return False
    return True


def split_eqwild_clauses(manager, comp):
    """Return a new comprehension that does not use equalities
    or wildcards. Form it by rewriting clauses that have these
    features into clauses over new one-clause subcomprehensions.
    """
    spec = CompSpec.from_comp(comp, manager.factory)
    new_clasts = []
    for cl in spec.join.clauses:
        if cl.has_wildcards or cl.has_equalities:
            # Come up with new variable names for the new sub-
            # comprehension, including for its wildcard components.
            prefix = manager.namegen.next_prefix()
            nums = (str(i) for i in itertools.count(1))
            new_vars = [prefix + v for v in cl.enumvars]
            new_lhs = tuple((prefix + 'w' + next(nums)
                             if v == '_' else prefix + v)
                            for v in cl.enumlhs)
            
            # Generate the AST for the new subcomprehension.
            clast = cl.to_AST()
            subcomp_clast = clast._replace(target=L.tuplify(
                                           new_lhs, lval=True))
            subcomp_resexp = L.tuplify(new_vars)
            subcomp = L.Comp(subcomp_resexp, (subcomp_clast,), (), {})
            
            # Generate new clause for outer comprehension.
            new_clast = clast._replace(target=L.tuplify(
                                       cl.enumvars, lval=True),
                                       iter=subcomp)
            new_clasts.append(new_clast)
        else:
            new_clasts.append(cl.to_AST())
    return comp._replace(clauses=tuple(new_clasts))
