"""Cost algebra, simplification, normalization."""


__all__ = [
    'ImgkeySubstitutor',
    'normalize',
]


from itertools import chain, product
from collections import Counter

from incoq.util.collections import OrderedSet

from .costs import *


class ImgkeySubstitutor(CostTransformer):
    
    """Apply a substitution to the keys of definite image-set costs.
    Use None in the mapping to replace any definite image-set costs that
    uses that key with its corresponding indefinite image-set cost.
    
    subst may also be a callable.
    """
    
    def __init__(self, subst):
        super().__init__()
        self.subst = subst
    
    def visit_DefImgset(self, cost):
        new_key = []
        for k in cost.key:
            try:
                new_k = self.subst(k)
            except TypeError:
                new_k = self.subst.get(k, k)
            new_key.append(new_k)
        
        if None not in new_key:
            return cost._replace(key=new_key)
        else:
            return cost.to_indef()


def trivial_simplify(cost):
    """For Sum and Min cost terms, rewrite them to eliminate duplicate
    entries. For Product and Sum, eliminate unit cost entries. Other
    costs are returned verbatim.
    """
    if not isinstance(cost, (Product, Sum, Min)):
        return cost
    terms = cost.terms
    
    if isinstance(cost, (Product, Sum)):
        terms = [t for t in terms if t != Unit()]
    
    if isinstance(cost, (Sum, Min)):
        terms = OrderedSet(terms)
    
    cost = cost._replace(terms=terms)
    return cost


class TrivialSimplifier(CostTransformer):
    
    """Return an algebraically equivalent cost tree that is either
    simpler than this one or the same as this one, applying
    trivial_simplify() to each term.
    """
    
    def helper(self, cost):
        terms = [self.visit(t) for t in cost.terms]
        cost = cost._replace(terms=terms)
        
        cost = trivial_simplify(cost)
        
        return cost
    
    visit_Product = helper
    visit_Sum = helper
    visit_Min = helper


# A factor index is a mapping whose keys are Products, and whose values
# are themselves mappings from each term of the Product to the number of
# occurrences it has in that Product. For instance, the factor index for
#
#     p1 = Product([Name('A'), Name('A'), Name('B')])
#     p2 = Product([Name('B'), Unit()])
#
# is
#
#     {p1: {Name('A'): 2, Name('B'): 1},
#      p2: {Name('B'): 1, Unit(): 1}}.
#
# The below functions take a factor_index optional argument to avoid
# recomputing the factor index when a suitable one is already available.

def build_factor_index(prods):
    """Return a new factor index covering the given list of products."""
    assert all(isinstance(p, Product) for p in prods)
    result = {}
    for p in prods:
        # The same Product may appear multiple times in prods;
        # this is fine.
        result[p] = Counter(p.terms)
    return result


# A product p1 dominates another product p2 if every term in p2
# appears at least that many times in p1, not counting Unit terms.
# The domination relation is a partial order.

def product_dominates(prod1, prod2, factor_index=None):
    """Return whether Product prod1 dominates Product prod2."""
    if factor_index is None:
        factor_index = build_factor_index([prod1, prod2])
    
    c1 = factor_index[prod1]
    c2 = factor_index[prod2]
    return all(c1[t] >= c2[t]
               for t in c2.keys() if t != Unit())


def all_products_dominated(prods1, prods2, factor_index=None):
    """Return True if for every Product in prods1, there is some
    Product in prods2 that dominates it.
    """
    allprods = list(chain(prods1, prods2))
    assert all(isinstance(p, Product) for p in allprods)
    
    if factor_index is None:
        factor_index = build_factor_index(allprods)
    
    # Do a pairwise comparison.
    for p1 in prods1:
        for p2 in prods2:
            if product_dominates(p2, p1, factor_index):
                break
        else:
            return False
    return True


# The simplify functions remove terms that are redundant because they
# dominate, or are dominated by, other terms. They subsume the actions
# of trivial_simplify().
#
# The simplify functions are coded in a way that accounts for the case
# that two distinct terms can dominate each other (i.e., that the
# domination relation is a preorder). This may be useful in the future
# if we pass in user-defined rules for deciding one term dominates
# another.

def simplify_sum_of_products(sumcost):
    """For a Sum of Products, return a version of this cost where
    Products that are dominated by other Products are removed.
    """
    assert isinstance(sumcost, Sum)
    assert all(isinstance(p, Product) for p in sumcost.terms)
    
    sumcost = trivial_simplify(sumcost)
    terms = sumcost.terms
    factor_index = build_factor_index(terms)
    
    # If two terms dominate each other (i.e., they are the same term),
    # we don't want to remove both of them. We'll walk from right to
    # left, eliminating terms using any other term that has not already
    # been eliminated.
    new_terms = []
    available_terms = set(terms)
    for prod in reversed(list(terms)):
        available_terms.remove(prod)
        if all_products_dominated([prod], available_terms,
                                  factor_index):
            # Remove it.
            pass
        else:
            # Keep it, and add it back into the pool of available terms
            # for dominating other terms.
            new_terms.append(prod)
            available_terms.add(prod)
    new_terms.reverse()
    
    return sumcost._replace(terms=new_terms)


def simplify_min_of_sums(mincost):
    """For a Min of Sums of Products, return a version of this cost
    where Sums that dominate other Sums are removed.
    """
    assert isinstance(mincost, Min)
    assert all(isinstance(s, Sum) for s in mincost.terms)
    assert all(isinstance(p, Product)
               for s in mincost.terms for p in s.terms)
    
    mincost = trivial_simplify(mincost)
    terms = mincost.terms
    factor_index = build_factor_index([p for s in terms for p in s.terms])
    
    new_terms = []
    available_terms = set(terms)
    for sum in reversed(list(terms)):
        available_terms.remove(sum)
        for other_sum in available_terms:
            if all_products_dominated(other_sum.terms, sum.terms,
                                      factor_index):
                break
        else:
            new_terms.append(sum)
            available_terms.add(sum)
    new_terms.reverse()
    
    return mincost._replace(terms=new_terms)


def multiply_sums_of_products(sums):
    """Given a list of Sums of Products, produce their overall product
    in Sum-of-Product form. The terms of the Sum are simplified, but
    the Sum itself might not be.
    """
    assert all(isinstance(s, Sum) for s in sums)
    assert all(isinstance(p, Product) for s in sums for p in s.terms)
    
    product_lists = [s.terms for s in sums]
    new_terms = []
    # Generate all combinations.
    for comb in product(*product_lists):
        nt = Product(list(chain.from_iterable(c.terms for c in comb)))
        nt = trivial_simplify(nt)
        new_terms.append(nt)
    
    return Sum(new_terms)


# A cost is in normalized form if it is a Min of Sums of Products of
# other kinds of terms.

class Normalizer(CostTransformer):
    
    """Rewrite a cost in normalized form."""
    
    # Each recursive call returns a normalized cost that has already
    # been simplified. The visitors combine these normalized costs
    # together.
    
    def wrapper_helper(self, cost):
        """Return the normalized cost for a simple term."""
        return Min([Sum([Product([cost])])])
    
    visit_Unknown = wrapper_helper
    visit_Unit = wrapper_helper
    visit_Name = wrapper_helper
    visit_IndefImgset = wrapper_helper
    visit_DefImgset = wrapper_helper
    
    def visit_Product(self, cost):
        # Recurse, putting us in the form of a Product of normalized
        # costs.
        cost = super().visit_Product(cost)
        
        # Distribute the multiplication over all arguments to the Mins,
        # obtaining one top-level Min.
        sum_lists = [m.terms for m in cost.terms]
        new_terms = []
        for comb in product(*sum_lists):
            term = multiply_sums_of_products(comb)
            term = simplify_sum_of_products(term)
            new_terms.append(term)
        
        cost = Min(new_terms)
        cost = simplify_min_of_sums(cost)
        return cost
    
    def visit_Sum(self, cost):
        # Recurse to get a Sum of normalized costs.
        cost = super().visit_Sum(cost)
        
        # Choose all possible combinations of arguments to the Mins,
        # and take the Sums of those combinations. Pick the Min of that.
        sum_lists = [m.terms for m in cost.terms]
        new_terms = []
        for comb in product(*sum_lists):
            term = Sum(list(chain.from_iterable([s.terms for s in comb])))
            term = simplify_sum_of_products(term)
            new_terms.append(term)
        
        cost = Min(new_terms)
        cost = simplify_min_of_sums(cost)
        return cost
    
    def visit_Min(self, cost):
        # Recurse to get a Min of normalized costs.
        cost = super().visit_Min(cost)
        
        # Flatten the argument Mins together.
        sum_lists = [m.terms for m in cost.terms]
        cost = Min(list(chain.from_iterable(sum_lists)))
        cost = simplify_min_of_sums(cost)
        return cost


class Unwrapper(CostTransformer):
    
    """Get rid of superfluous nodes -- Products, Sums, and Mins that
     have zero or one arguments.
     """
    
    def helper(self, cost):
        terms = [self.visit(t) for t in cost.terms]
        cost = cost._replace(terms=terms)
        
        if len(cost.terms) == 0:
            return Unit()
        elif len(cost.terms) == 1:
            return cost.terms[0]
        else:
            return cost
    
    visit_Product = helper
    visit_Sum = helper
    visit_Min = helper


def normalize(cost):
    cost = Normalizer.run(cost)
    cost = Unwrapper.run(cost)
    return cost
