"""Demand-driven incrementalization transformation."""


__all__ = [
    'deminc_relcomp',
]


from operator import attrgetter

import oinc.incast as L
from oinc.comp import (make_inccomp, inc_relcomp_helper,
                       inc_relcomp, inc_changetrack)

from .demclause import DemClause
from .tags import (make_structures, filter_comps,
                   structures_to_comps, uset_to_comp)


class OuterDemandMaintainer(L.OuterMaintTransformer):
    
    """Insert code after an update to read from a demand delta set
    and call the demand or undemand function for each element.
    """
    
    def __init__(self, manager, delta_name, demname, at_rels, projvars,
                 outsideinvs):
        super().__init__(outsideinvs)
        self.manager = manager
        self.delta_name = delta_name
        self.demname = demname
        self.at_rels = at_rels
        self.projvars = projvars
    
    def visit_SetUpdate(self, node):
        rel = L.get_name(node.target)
        if rel not in self.at_rels:
            return
        
        # New code gets inserted after the update.
        # This is true even if the update was a removal.
        # It shouldn't matter where we do the U-set update,
        # so long as the invariants are properly maintained
        # at the time.
        
        prefix = self.manager.namegen.next_prefix()
        vars = [prefix + v for v in self.projvars]
        
        if node.op == 'add':
            funcname = L.N.demfunc(self.demname)
        else:
            funcname = L.N.undemfunc(self.demname)
        
        call_func = L.Call(L.ln(funcname),
                              tuple(L.ln(v) for v in vars),
                              (), None, None)
        postcode = L.pc('''
            for S_PROJVARS in DELTA.elements():
                CALL_FUNC
            DELTA.clear()
            ''', subst={'S_PROJVARS': L.tuplify(vars, lval=True),
                        'DELTA': self.delta_name,
                        'CALL_FUNC': call_func})
        
        return self.with_outer_maint(node, funcname, L.ts(node),
                                     (), postcode)


def deminc_relcomp(tree, manager, comp, compname):
    """Incrementalize a relational comprehension, add appropriate
    incrementalized demand structures, and rewrite the maint comps
    to use these structures.
    """
    verbose = manager.options.get_opt('verbose')
    use_tag_checks = manager.options.get_opt('tag_checks')
    factory = manager.factory
    
    force_uset = manager.options.get_queryopt(comp, 'uset_force')
    if force_uset is None:
        force_uset = manager.options.get_opt('default_uset_force')
    
    subdem_tags = manager.options.get_opt('subdem_tags')
    
    # Get the CompSpec and inc info of the original comprehension.
    inccomp = make_inccomp(tree, manager, comp, compname,
                           force_uset=force_uset)
    spec = inccomp.spec
    augmented = inccomp.selfjoin == 'aug'
    
    # Make tags/filters/usets structures.
    ds = make_structures(spec.join.clauses, compname,
                         singletag=manager.options.get_opt('single_tag'),
                         subdem_tags=subdem_tags)
    if verbose:
        print('  Tags/filters/usets: ' + ' ' * 31 +
              ', '.join(s.name for s in ds.structs))
    
    # Eliminate Demand from clauses.
    new_clauses = []
    for cl in spec.join.clauses:
        if isinstance(cl, DemClause):
            new_clauses.append(cl.cl)
        else:
            new_clauses.append(cl)
    inccomp.spec = spec = spec._replace(join=spec.join._replace(
                                                clauses=new_clauses))
    
    # Incrementalize query comp.
    # (Since we've unwrapped demand clauses, the logic for defining
    # inner queries' U-sets for if filtering weren't used won't fire.)
    tree, maintcomps = inc_relcomp_helper(tree, manager, inccomp,
                                          instrument=False)
    
    # Rewrite maintcomps to use filters. Prune structures.
    tree, ds = filter_comps(tree, factory, ds, maintcomps,
                            use_tag_checks,
                            augmented=augmented, subdem_tags=subdem_tags)
    
    manager.stats['dem structs'] += len(ds.structs)
    
    # Incrementalize tags and filters.
    demcomps = structures_to_comps(ds, factory)
    for name, comp in demcomps:
        # When using augmented maintenance code, since the query
        # maintenance goes before an addition and after a removal,
        # make sure the demand invariant maintenance still comes
        # before and after that query maintenance respectively.
        outsideinvs = [compname] if augmented else []
        tree = inc_relcomp(tree, manager, comp, name,
                           outsideinvs=outsideinvs)
    
    # Take care of usets.
    usets = sorted(ds.usets, key=attrgetter('i'))
    
    for uset in usets:
        
        at_rels = set(e.enumrel for i, e in enumerate(spec.join.clauses)
                                if i < uset.i)
        
        # Maintain U-set change set.
        # FIXME: The delta set name should probably be freshly generated
        # for this comprehension, so as to ensure it does not interfere
        # with another delta set for a different use of the same demand
        # function (i.e. same nested query) in a different occurrence
        # (possibly even within this same outer query?).
        demname = uset.name
        deltaname = L.N.deltaset(demname)
        
        uset_comp = uset_to_comp(ds, uset, factory, spec.join.clauses[0])
        tree = inc_changetrack(tree, manager, uset_comp, deltaname)
        
        tree = OuterDemandMaintainer.run(
                    tree, manager, deltaname,
                    demname, at_rels,
                    L.get_vartuple(uset_comp.resexp),
                    None)
    
    return tree
