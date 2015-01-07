"""Features for simplifying costs based on user-supplied
additional information.
"""


__all__ = [
    'add_domain_names',
    'reinterpret_cost',
]


from functools import partial

from invinc.util.unify import unify
import invinc.compiler.incast as L
from invinc.compiler.set import Mask
from invinc.compiler.comp import CompSpec
from invinc.compiler.aggr import AggrSpec

from .cost import *


def make_dompath_eqs(subst, roots=None):
    """Given a domain substitution, make equations for domain path
    specifiers that begin with one of the names in roots. If roots
    is None do it for all keys in the substitution.
    """
    eqs = []
    
    def make(var, rhs):
        if not (isinstance(rhs, tuple) and rhs[0] == '<T>'):
            eq = (var, rhs)
            eqs.append(eq)
            return
        parts = rhs[1:]
        
        subvars = [var + '.' + str(i)
                   for i in range(1, len(parts) + 1)]
        eq = (var, tuple(['<T>'] + subvars))
        eqs.append(eq)
        
        for s, p in zip(subvars, parts):
            make(s, p)
    
    for k, v in subst.items():
        if roots is None or k in roots:
            make(k, v)
    
    return eqs

def add_domain_names(subst, domainnames, roots=None):
    """Given a domain substitution and a mapping from domain paths to
    names of primitive domains, produce the augmented substitution.
    """
    subst_eqs = list(subst.items())
    dompath_eqs = make_dompath_eqs(subst, roots)
    domainname_eqs = [(k, (v,)) for k, v in domainnames.items()]
    new_eqs = subst_eqs + dompath_eqs + domainname_eqs
    new_subst = unify(new_eqs)
    return new_subst


def split_resexp_vars(resexp, mask):
    """Given a result expression of a comprehension and a mask over
    the comprehension result, determine which variables appearing in
    the result expression are bound and unbound. Return the set of
    bounds and unbounds respectively.
    
    A variable is considered bound if it occurs somewhere within any
    subexpression corresponding to a bound part of the mask, where this
    subexpression is injective. Otherwise it is unbound.
    
    For example, if the result expression is ((x, y), z) and the mask
    if 'bu', then x and y are bound and z is unbound. However, if the
    result expression were (x + y, z) then they would all be unbound.
    
    E.g., if the result expression is ((x, y), z) and the mask is
    'bu', then x and y are bound. But if the result expression is
    (x + y, z), then no variables are bound.
    """
    find = partial(L.VarsFinder.run, ignore_functions=True)
    boundvars = set()
    unboundvars = set()
    
    if isinstance(resexp, L.Tuple):
        boundexps, unboundexps, _ = mask.split_vars(resexp.elts)
        # Determine bound vars.
        for e in boundexps:
            # Injective expressions include simple variable names and
            # tuple trees of variable names.
            if L.is_injective(e):
                boundvars.update(find(e))
        # Determine unbound vars.
        for e in unboundexps:
            unboundvars.update(find(e))
        unboundvars.difference_update(boundvars)
    
    else:
        # Special case: If the result expression is not a tuple,
        # then the mask is either a single bound or single unbound.
        if mask == Mask('b'):
            boundvars = find(resexp)
        elif mask == Mask.U or mask == Mask('w'):
            unboundvars = find(resexp)
        else:
            assert()
    
    return boundvars, unboundvars

def get_nondet_info(spec, bound_vars):
    """Given a comprehension and some bound variables, return
    information to help put a bound on the size of the part of
    the comprehension result that matches the bound variables.
    
    Specifically, we look at the non-determined variables. Choose
    a join order of the comprehension's clauses starting with the
    bound variables. For each clause in order, append to the result
    a triple of
    
        (iterated relation, mask, non-determined variables)
    
    where the non-determined variables are a subset of unbound vars
    in the clause that, together with the bound vars, functionally
    determine the remaining unbound vars in the clause. All the
    unbound variables in a clause become bound for future clauses.
    The mask is the lookup pattern that goes from the bound vars
    and determined unbound vars to the non-determined unbound vars.
    
    This goes on until all variables appearing in the comprehension
    result expression are bound.
    
    For each entry in the result, the newly introduced non-
    determined vars introduce a cost factor, and the overall
    comprehension's cost is bounded by the product of these factors.
    Each factor can itself be bounded in two ways. First, it can be
    considered recursively as an image set lookup over the iterated
    relation. Second, we can take all the membership constraints
    on the non-determined variables and use domain bounds for them.
    Assembling/minimizing these bounds is the caller's
    responsibility.
    """
    goal_vars = L.VarsFinder.run(spec.resexp, ignore_functions=True)
    bound_vars = set(bound_vars)
    result = []
    
    ordering = spec.join.get_ordering(bound_vars)
    for _i, cl, _bindenv in ordering:
        # Skip the remaining clauses if we bound all the
        # variables we need to.
        if bound_vars.issuperset(goal_vars):
            break
        # Ignore condition clauses and clauses that are not over
        # a relation.
        if cl.enumrel is None:
            continue
        
        det_vars = set(cl.get_determined_vars(bound_vars))
        nondet_vars = set(cl.enumvars) - bound_vars - det_vars
        
        # Special case for lower cost bounds: If we happen to be able
        # to span the goal vars by taking some but not all of the nondet
        # vars and no det vars, then do that instead.
        if (bound_vars | nondet_vars).issuperset(goal_vars):
            to_vars = goal_vars - bound_vars
            from_vars = bound_vars
        else:
            to_vars = nondet_vars
            from_vars = bound_vars
        wild_vars = set(cl.enumvars) - from_vars - to_vars
        
        mask = Mask.from_vars(cl.enumlhs, from_vars, wild_vars)
        
        result.append((cl.enumrel, mask, to_vars))
        
        bound_vars.update(cl.enumvars)
    
    return result


class CostReinterpreter(CostTransformer):
    
    def __init__(self, invs,
                 domain_subst, domain_sizes, domain_costs,
                 *, strip_min=False):
        super().__init__()
        self.invs = invs
        self.domain_subst = domain_subst
        self.domain_sizes = domain_sizes
        self.domain_costs = domain_costs
        self.strip_min = strip_min
    
    def make_min(self, terms):
        """If strip_min is True, avoid generating MinCosts by
        trying to pick the best option statically. Arbitrarily
        commit to one if necessary. If strip_min is False, just
        emit a MinCost. terms may include None; these are ignored.
        If terms is empty (are all Nones), return the unit cost.
        """
        terms = [t for t in terms if t is not None]
        if len(terms) == 0:
            return UnitCost()
        
        if self.strip_min:
            cost = MinCost(terms)
            # The cost of normalization may be big enough that
            # it defeats the purpose of having strip_min in the
            # first place, but the hope is that these mins will
            # be rather small.
            cost = normalize(cost)
            if isinstance(cost, MinCost) and len(cost.terms) > 1:
                return cost.terms[0]
            else:
                return cost
        else:
            cost = MinCost(terms)
            # Simplify for the sake of trying to keep the
            # size of terms small.
            cost = Simplifier.run(cost)
            return cost
    
    def dompath_to_size(self, dompath):
        """Produce a cost for a dompath. First check to see if there's
        a specific cost override. If there isn't, then use a bound based
        on its domain type. If this type is itself a tuple (Cartesian
        product), recurse to get the sub-domain costs. If type
        information is unavailable for this type or one of the sub-
        types, return None.
        """
        # Use cost override if available.
        if dompath in self.domain_costs:
            return self.domain_costs[dompath]
        
        # Return None if type information is unavilable.
        if dompath not in self.domain_subst:
            return None
        dom = self.domain_subst[dompath]
        
        if isinstance(dom, tuple) and dom[0] == '<T>':
            # Cartesian product of sub-domain types.
            arity = len(dom) - 1
            subdoms = [dompath + '.' + str(i) for i in range(1, arity + 1)]
            subcosts = tuple(self.dompath_to_size(s) for s in subdoms)
            if any(c == None for c in subcosts):
                return None
            return ProductCost(subcosts)
        
        elif isinstance(dom, tuple) and len(dom) == 1:
            # Primitive domain type.
            # Check for a size for this domain.
            if dom[0] in self.domain_sizes:
                return self.domain_sizes[dom[0]]
            else:
                # Just use the name of the domain.
                return NameCost(dom[0])
        
        elif isinstance(dom, str):
            # Domain variable. We don't know what to make of it,
            # so just use its name.
            return NameCost(dom)
        
        else:
            assert()
    
    def dompaths_for_mask(self, dompath, mask):
        """For a given mask over a dompath, return the names of the
        sub-dompaths for the unbound components. If type information
        is not available for the given dompath or any needed sub-
        dompath, return None.
        """
        if dompath not in self.domain_subst:
            return None
        dom = self.domain_subst[dompath]
        
        subdoms = [dompath + '.' + str(i)
                   for i in range(1, len(mask) + 1)]
        _bounds, unbounds, _eqs = mask.split_vars(subdoms)
        
        # For a tuple, just return the subdoms for the unbound components.
        # If this isn't a tuple, then there must be at most one unbound
        # component, and its dompath is the same (not dompath.1).
        if isinstance(dom, tuple) and dom[0] == '<T>':
            result = unbounds
        else:
            if len(unbounds) == 0:
                result = ()
            else:
                assert len(unbounds) == 1
                result = (dompath,)
        
        if all(subdom in self.domain_subst for subdom in result):
            return result
        else:
            return None
    
    def nondet_cost_factor(self, subrel, submask, nondet, memconstrs):
        """Given an entry returned by get_nondet_info(), along with
        comprehension membership constraints, produce a cost factor
        based on two separate bits of information: the domain
        information for the new variables, and the cost of the clause
        image set lookup (recursively simplified).
        """
        # Get domain-based bound.
        # For each variable, gather all constraints on it, turn each
        # into a cost, and take the min of these costs. Multiply these
        # terms for each variable together.
        factors = []
        for v in nondet:
            containing = memconstrs[v]
            sizes = [self.dompath_to_size(dompath)
                     for dompath in containing]
            factor = self.make_min(sizes)
            factors.append(factor)
        domain_cost = ProductCost(factors)
        
        # Get lookup-based bound.
        # Create a name or image set cost for the iterated relation
        # and try to simplify recursively. 
        if all(c == 'u' for c in submask.parts):
            lookup_cost = NameCost(subrel)
        elif all(c != 'u' for c in submask.parts):
            lookup_cost = UnitCost()
        else:
            lookup_cost = IndefImgsetCost(subrel, submask)
        lookup_cost = self.visit(lookup_cost)
        # If recursing failed to simplify this cost to a term that
        # the user would understand -- specifically, if it is still
        # a name or image set cost whose iterated relation is *not*
        # in the domain substitution -- then don't use this cost
        # term at all. (This can happen if the relation is TUP, for
        # instance.)
        if ((isinstance(lookup_cost, NameCost) and
             lookup_cost.name not in self.domain_subst) or
            (isinstance(lookup_cost, (IndefImgsetCost, DefImgsetCost)) and
             lookup_cost.rel not in self.domain_subst)):
            cost = domain_cost
        else:
            cost = self.make_min((domain_cost, lookup_cost))
        
        return cost
    
    def assemble_nondet_cost(self, nondet_info, memconstrs):
        """Given the return data from get_nondet_info, assemble
        an overall cost for the comprehension based on the bound
        for each clause.
        """
        factors = []
        for subrel, submask, nondet in nondet_info:
            factor = self.nondet_cost_factor(subrel, submask, nondet,
                                             memconstrs)
            factors.append(factor)
        return ProductCost(factors)
    
    def visit_NameCost(self, cost):
        rel = cost.name
        
        inv_cost = None
        if rel in self.invs:
            spec = self.invs[rel].spec
            
            if isinstance(spec, CompSpec):
                info = get_nondet_info(spec, set())
                memconstrs = spec.get_membership_constraints()
                inv_cost = self.assemble_nondet_cost(info, memconstrs)
            
            elif isinstance(spec, AggrSpec):
                # Create an equivalent cost over the underlying operand
                # and process it instead.
                #
                # The number of entries in the aggregate relation is the
                # number of possible parameter values to the underlying
                # operand. Make a mask that projects out just the
                # parameters from this operand.
                mask = spec.relmask.make_param_proj_mask()
                inv_cost = IndefImgsetCost(spec.rel, mask)
                inv_cost = self.visit(cost)
            
            else:
                assert()
        
        # May return None.
        dom_cost = self.dompath_to_size(cost.name)
        
        cost = self.make_min((inv_cost, dom_cost))
        return cost
    
    def visit_IndefImgsetCost(self, cost):
        rel = cost.rel
        
        inv_cost = None
        if rel in self.invs:
            spec = self.invs[rel].spec
            
            if isinstance(spec, CompSpec):
                boundvars, _ = split_resexp_vars(spec.resexp, cost.mask)
                info = get_nondet_info(spec, boundvars)
                memconstrs = spec.get_membership_constraints()
                inv_cost = self.assemble_nondet_cost(info, memconstrs)
            
            elif isinstance(spec, AggrSpec):
                # As above for NameCost, but exclude the parameters that
                # are bound. First determine what parameters are bound
                # by the mask in this cost.
                vars = list(spec.params) + [object()] 
                bounds, _unbounds, _eqs = cost.mask.split_vars(vars)
                # Now modify the parameter projection mask to project
                # them away. 
                mask = spec.relmask.make_param_proj_mask()
                assert (len(spec.params) ==
                        len([True for p in mask.parts if p == 'u']))
                params = iter(spec.params)
                new_parts = []
                for part in mask.parts:
                    if part == 'u':
                        p = next(params)
                        if p in bounds:
                            new_parts.append('w')
                            continue
                    new_parts.append(part)
                
                new_mask = Mask(new_parts)
                inv_cost = IndefImgsetCost(spec.rel, new_mask)
                inv_cost = self.visit(inv_cost)
            
            else:
                assert()
        
        # Get the dompath for each unbound component and multiply
        # them together. If any domain is unknown, the whole cost
        # is left alone.
        dom_cost = None
        dompaths = self.dompaths_for_mask(rel, cost.mask)
        if dompaths is not None:
            factors = [self.dompath_to_size(s) for s in dompaths]
            # Check for None again since there could've been a
            # deeper nested dompath missing.
            if all(c is not None for c in factors):
                dom_cost = ProductCost(factors)
        
        cost = self.make_min((inv_cost, dom_cost))
        return cost
        
    visit_DefImgsetCost = visit_IndefImgsetCost


def reinterpret_cost(cost, *, invs,
                     domain_subst, domain_sizes, domain_costs,
                     domain_names):
    """Obtain a simplified cost using substitution rules for costs
    and domains.
    
    For convenience, the following shorthands are recognized for
    domain_sizes and domain_costs:
    
        - a value that is a string is interpreted as a name cost
        
        - a value that is the number 1 is interpreted as the unit cost
    
#    For convenience, the following shorthands are recognized for
#    cost_rules:
#    
#        - a key that is a string with one word is interpreted as
#          a relation name or domain
#        
#        - a key that is a string with two words (separated by
#          whitespace) is interpreted as an imageset cost
#        
#        - a value that is a string is interpreted as a name cost
#        
#        - a value that is the number 1 is interpreted as a unit cost
    """
#    def keyexp(k):
#        if isinstance(k, str):
#            words = k.split()
#            if len(words) == 1:
#                k = NameCost(words[0])
#            elif len(words) == 2:
#                k = IndefImgsetCost(words[0], Mask(words[1]))
#            else:
#                assert()
#        return k
    
    def valexp(v):
        if isinstance(v, str):
            v = NameCost(v)
        elif v == 1:
            v = UnitCost()
        return v
    
    # Expand shorthands.
    domain_sizes = {k: valexp(v) for k, v in domain_sizes.items()}
    domain_costs = {k: valexp(v) for k, v in domain_costs.items()}
    
    domain_subst = add_domain_names(domain_subst, domain_names)
    
    # Now apply domain expansions for remaining name costs.
    new_cost = CostReinterpreter.run(cost, invs, domain_subst,
                                     domain_sizes, domain_costs,
                                     strip_min=False)
    
    return new_cost
