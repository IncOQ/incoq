"""Definitions of cost terms and framework for manipulation."""


__all__ = [
    'Cost',
    'UnknownCost',
    'UnitCost',
    'NameCost',
    'IndefImgsetCost',
    'DefImgsetCost',
    'ProductCost',
    'SumCost',
    'MinCost',
    
    'BaseCostVisitor',
    'CostVisitor',
    'CostTransformer',
    
    'PrettyPrinter',
    'CostSubstitutor',
    'ImgkeySubstitutor',
    'Simplifier',
    'normalize',
]

from itertools import product, chain, groupby
from collections import Counter

from simplestruct import Struct, TypedField

from util.collections import OrderedSet
from oinc.set import Mask


class Cost(Struct):
    """An asymptotic cost term."""

class UnknownCost(Cost):
    
    def __str__(self):
        return '?'

class UnitCost(Cost):
    
    def __str__(self):
        return '1'

class NameCost(Cost):
    name = TypedField(str)
    
    def __str__(self):
        return self.name

class IndefImgsetCost(Cost):
    rel = TypedField(str)
    mask = TypedField(Mask)
    
    def __str__(self):
        return self.rel + '_' + str(self.mask)

class DefImgsetCost(Cost):
    rel = TypedField(str)
    mask = TypedField(Mask)
    key = TypedField(str, seq=True)
    
    def __str__(self):
        return '{}_{}[{}]'.format(self.rel, self.mask,
                                  ', '.join(self.key))
    
    def to_indef(self):
        """Return the indefinite image set cost that generalizes
        this cost.
        """
        return IndefImgsetCost(self.rel, self.mask)

class ProductCost(Cost):
    
    terms = TypedField(Cost, seq=True)
    
    @classmethod
    def from_products(cls, costs):
        """Form as the concatenation of other ProductCosts."""
        assert all(isinstance(c, ProductCost) for c in costs)
        return ProductCost(tuple(chain.from_iterable(c.terms for c in costs)))
    
    def __str__(self):
        return '(' + '*'.join(str(t) for t in self.terms) + ')'

class SumCost(Cost):
    
    terms = TypedField(Cost, seq=True)
    
    @classmethod
    def from_sums(cls, costs):
        """Form as the concatenation of other SumCosts."""
        assert all(isinstance(c, SumCost) for c in costs)
        return SumCost(tuple(chain.from_iterable(c.terms for c in costs)))
    
    def __str__(self):
        return '(' + ' + '.join(str(s) for s in self.terms) + ')'

class MinCost(Cost):
    
    terms = TypedField(Cost, seq=True)
    
    @classmethod
    def from_mins(cls, costs):
        """Form as the concatenation of other MinCosts."""
        assert all(isinstance(c, MinCost) for c in costs)
        return MinCost(tuple(chain.from_iterable(c.terms for c in costs)))
    
    def __str__(self):
        return 'min(' + ', '.join(str(s) for s in self.terms) + ')'


class BaseCostVisitor:
    
    """Visitor for costs, analogous to NodeVisitor."""
    
    # We don't use a generic_visit() method because there are only
    # a few types of Cost nodes, and that would require a common
    # list of subterms a la '_fields' for AST nodes. Instead we give
    # visit_ handlers for each kind of cost.
    #
    # To avoid an accidental inconsistency if a new cost type is added
    # but a new handler is not defined, we separate BaseCostVisitor
    # from CostVisitor so that CostTransformer is forced to explicitly
    # provide its own handlers.
    
    @classmethod
    def run(cls, tree, *args, **kargs):
        visitor = cls(*args, **kargs)
        result = visitor.process(tree)
        return result
    
    def process(self, tree):
        result = self.visit(tree)
        return result
    
    def visit(self, cost):
        assert isinstance(cost, Cost)
        method = 'visit_' + cost.__class__.__name__
        visitor = getattr(self, method)
        result = visitor(cost)
        return result

class CostVisitor(BaseCostVisitor):
    
    def do_nothing(self, cost):
        return
    
    visit_UnknownCost = do_nothing
    visit_UnitCost = do_nothing
    visit_NameCost = do_nothing
    visit_IndefImgsetCost = do_nothing
    visit_DefImgsetCost = do_nothing
    
    def do_termlist(self, cost):
        for c in cost.terms:
            self.visit(c)
    
    visit_ProductCost = do_termlist
    visit_SumCost = do_termlist
    visit_MinCost = do_termlist

class CostTransformer(BaseCostVisitor):
    
    """Transformer for costs. Like NodeTransformer, use None to indicate
    no change, and in a sequence return () to indicate removal of this
    term.
    """
    
    def visit(self, cost):
        result = super().visit(cost)
        if result is None:
            result = cost
        return result
    
    def do_nothing(self, cost):
        return cost
    
    visit_UnknownCost = do_nothing
    visit_UnitCost = do_nothing
    visit_NameCost = do_nothing
    visit_IndefImgsetCost = do_nothing
    visit_DefImgsetCost = do_nothing
    
    def do_termlist(self, cost):
        changed = False
        new_terms = []
        
        for c in cost.terms:
            result = self.visit(c)
            if result is None:
                result = c
            if result is not c:
                changed = True
            if isinstance(result, (tuple, list)):
                new_terms.extend(result)
            else:
                new_terms.append(result)
        
        if changed:
            return cost._replace(terms=new_terms)
        else:
            return cost
    
    visit_ProductCost = do_termlist
    visit_SumCost = do_termlist
    visit_MinCost = do_termlist


class PrettyPrinter(CostVisitor):
    
    def helper(self, cost):
        return str(cost)
    
    visit_UnknownCost = helper
    visit_UnitCost = helper
    visit_NameCost = helper
    visit_IndefImgsetCost = helper
    visit_DefImgsetCost = helper
    
    def visit_ProductCost(self, cost):
        termstrs = []
        
        # Sort terms by string representation first, then group.
        # Each repetition of the same term is coalesced into a power.
        terms = list(cost.terms)
        terms.sort(key=lambda t: str(t).lower())
        for key, group in groupby(terms):
            n = len(list(group))
            s = self.visit(key)
            if n == 1:
                termstrs.append(s)
            else:
                termstrs.append(s + '^' + str(n))
        
        return '(' + '*'.join(termstrs) + ')'
    
    def visit_SumCost(self, cost):
        return '(' + ' + '.join(self.visit(t) for t in cost.terms) + ')'
    
    def visit_MinCost(self, cost):
        return 'min(' + ', '.join(self.visit(t) for t in cost.terms) + ')'


class CostSubstitutor(CostTransformer):
    
    """Apply a substitution to replace some costs with others.
    Mainly intended to help simplify costs by replacing name or
    image set costs with unit costs or other names.
    
    If subsume_maps is True, indefinite image set costs in the
    substitution map will also match their definite image set cost
    versions.
    """
    
    def __init__(self, subst, *, subsume_maps=False):
        super().__init__()
        self.subst = subst
        self.subsume_maps = subsume_maps
    
    def visit(self, cost):
        if cost in self.subst:
            return self.subst[cost]
        else:
            return super().visit(cost)
    
    def visit_DefImgsetCost(self, cost):
        if self.subsume_maps:
            indef = cost.to_indef()
            if indef in self.subst:
                return self.subst[indef]
        return cost


class ImgkeySubstitutor(CostTransformer):
    
    """Apply a substitution to imageset keys. Use None in the mapping
    to replace definite imagesets with indefinite ones.
    """
    
    def __init__(self, subst):
        super().__init__()
        self.subst = subst
    
    def visit_DefImgsetCost(self, cost):
        new_key = tuple(self.subst.get(k, k) for k in cost.key)
        if None not in new_key:
            return cost._replace(key=new_key)
        else:
            return cost.to_indef()


def without_duplicates(cost):
    """For a ProductCost, SumCost, or MinCost, return a version without
    repeated terms among the direct arguments.
    """
    assert isinstance(cost, (ProductCost, SumCost, MinCost))
    new_terms = OrderedSet(cost.terms)
    return cost._replace(terms=new_terms)

class Simplifier(CostTransformer):
    
    """Return an algebraically equivalent cost tree that is either
    simpler than this one or the same as this one.
    
    For sum and min cost terms, rewrite them to eliminate duplicate
    entries. For product and sum, eliminate unit cost entries.
    
    If unwrap is True, unwrap any costs that have only one subterm,
    or replace them with the unit cost if they have zero subterms.
    """
    
    def __init__(self, unwrap=True):
        super().__init__()
        self.unwrap = unwrap
    
    def recurse_helper(self, cost):
        terms = [self.visit(t) for t in cost.terms]
        return cost._replace(terms=terms)
    
    def unique_helper(self, cost):
        terms = OrderedSet(cost.terms)
        return cost._replace(terms=terms)
    
    def elimunit_helper(self, cost):
        terms = [t for t in cost.terms if t != UnitCost()]
        return cost._replace(terms=terms)
    
    def unwrap_helper(self, cost):
        if self.unwrap:
            if len(cost.terms) == 0:
                return UnitCost()
            elif len(cost.terms) == 1:
                return cost.terms[0]
        return cost
    
    def visit_ProductCost(self, cost):
        cost = self.recurse_helper(cost)
        cost = self.elimunit_helper(cost)
        cost = self.unwrap_helper(cost)
        return cost
    
    def visit_SumCost(self, cost):
        cost = self.recurse_helper(cost)
        cost = self.unique_helper(cost)
        cost = self.elimunit_helper(cost)
        cost = self.unwrap_helper(cost)
        return cost
    
    def visit_MinCost(self, cost):
        cost = self.recurse_helper(cost)
        cost = self.unique_helper(cost)
        cost = self.unwrap_helper(cost)
        return cost


def build_factor_counts(prods):
    """Given a list of product costs, build a map from each product
    to a counter. The counter itself is a map from each factor to
    the number of times it appears in that product.
    """
    assert all(isinstance(p, ProductCost) for p in prods)
    result = {}
    for p in prods:
        # If the same one is seen twice, it's previous entry will just
        # be overwritten with the same information.
        result[p] = Counter(p.terms)
    return result

def all_products_dominated(prods1, prods2, factorcounts=None):
    """Return True if for every product cost in prods1, there is some
    product cost in prods2 that dominates it.
    
    If factorcounts is not given, it will be computed from scratch.
    """
    allprods = list(chain(prods1, prods2))
    assert all(isinstance(p, ProductCost) for p in allprods)
    
    if factorcounts is None:
        factorcounts = build_factor_counts(allprods)
    
    # Do a pairwise comparison.
    for p1 in prods1:
        c1 = factorcounts[p1]
        for p2 in prods2:
            c2 = factorcounts[p2]
            # t1 is dominated if for each of its factors,
            # t2 has at least that many occurrences of the factor.
            if all(c2[f] >= c1[f] for f in c1.keys()):
                break
        else:
            return False
    return True

def simplify_sum_of_products(sumcost):
    """For a sum of products, return a version of this cost where
    products that are dominated by other products are removed.
    """
    assert isinstance(sumcost, SumCost)
    assert all(isinstance(p, ProductCost) for p in sumcost.terms)
    
    # A naive approach only keeps terms that are not dominated by any
    # other term. This would incorrectly remove two terms that are
    # domianted only by each other. Once a term is dominated, we remove
    # it from the set so it can't be used to dominate anything else.
    
    terms = list(OrderedSet(sumcost.terms))
    factorcounts = build_factor_counts(terms)
    
    # Go right-to-left so that we keep the left occurrence of tied terms.
    for prod in reversed(list(terms)):
        rest = OrderedSet(terms) - {prod}
        if all_products_dominated([prod], rest, factorcounts):
            terms.remove(prod)
    
    return sumcost._replace(terms=terms)

def simplify_min_of_sums(mincost):
    """For a min of sums, return a version of this cost where
    sums that dominate other sums are removed.
    """
    assert isinstance(mincost, MinCost)
    terms = mincost.terms
    assert all(isinstance(s, SumCost)
               for s in terms)
    assert all(isinstance(p, ProductCost)
               for s in terms for p in s.terms)
    
    terms = list(OrderedSet(mincost.terms))
    factorcounts = build_factor_counts([p for s in terms for p in s.terms])
    
    for sum1 in reversed(list(terms)):
        rest = OrderedSet(terms) - {sum1}
        for sum2 in rest:
            if all_products_dominated(sum2.terms, sum1.terms, factorcounts):
                terms.remove(sum1)
                break
    
    return mincost._replace(terms=terms)

def multiply_sums_of_products(sums):
    """Given a list of sums of products, produce their overall product
    in sum-of-product form.
    """
    assert all(isinstance(s, SumCost)
               for s in sums)
    assert all(isinstance(p, ProductCost)
               for s in sums for p in s.terms)
    
    product_lists = [s.terms for s in sums]
    new_terms = []
    for comb in product(*product_lists):
        nt = ProductCost.from_products(comb)
        new_terms.append(nt)
    return SumCost(new_terms)

class Normalizer(CostTransformer):
    
    """Produces a cost in normalized form, where normalized means that
    it is a min of sums of products.
    """
    
    # Each recursive call returns a normalized cost. The visitors
    # combine normalized costs together.
    #
    # We simplify each complex term before returning it, in hopes
    # of avoiding an explosion in the size of intermediate terms.
    
    def wrapper_helper(self, cost):
        return MinCost((SumCost((ProductCost((cost,)),)),))
    
    visit_UnknownCost = wrapper_helper
    visit_UnitCost = wrapper_helper
    visit_NameCost = wrapper_helper
    visit_IndefImgsetCost = wrapper_helper
    visit_DefImgsetCost = wrapper_helper
    
    def visit_ProductCost(self, cost):
        cost = super().visit_ProductCost(cost)
        
        sum_lists = [m.terms for m in cost.terms]
        new_terms = []
        for comb in product(*sum_lists):
            term = multiply_sums_of_products(comb)
            term = simplify_sum_of_products(term)
            new_terms.append(term)
        
        cost = MinCost(new_terms)
        cost = Simplifier.run(cost, unwrap=False)
        cost = simplify_min_of_sums(cost)
        return cost
    
    def visit_SumCost(self, cost):
        cost = super().visit_SumCost(cost)
        
        sum_lists = [m.terms for m in cost.terms]
        new_terms = []
        for comb in product(*sum_lists):
            term = SumCost.from_sums(comb)
            term = simplify_sum_of_products(term)
            new_terms.append(term)
        
        cost = MinCost(new_terms)
        cost = Simplifier.run(cost, unwrap=False)
        cost = simplify_min_of_sums(cost)
        return cost
    
    def visit_MinCost(self, cost):
        cost = super().visit_MinCost(cost)
        cost = MinCost.from_mins(cost.terms)
        cost = Simplifier.run(cost, unwrap=False)
        cost = simplify_min_of_sums(cost)
        return cost

def normalize(cost):
    """Normalize and simplify a cost."""
    cost = Normalizer.run(cost)
    cost = Simplifier.run(cost)
    return cost
