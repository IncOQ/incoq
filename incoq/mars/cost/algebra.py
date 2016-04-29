"""Cost algebra, simplification, normalization."""


__all__ = [
    'ImgkeySubstitutor',
    'BasicSimplifier',
]


from itertools import chain
from collections import Counter

from incoq.util.collections import OrderedSet

from .costs import *


class ImgkeySubstitutor(CostTransformer):
    
    """Apply a substitution to the keys of definite image-set costs.
    Use None in the mapping to replace any definite image-set costs that
    uses that key with its corresponding indefinite image-set cost.
    """
    
    def __init__(self, subst):
        super().__init__()
        self.subst = subst
    
    def visit_DefImgset(self, cost):
        new_key = tuple(self.subst.get(k, k) for k in cost.key)
        if None not in new_key:
            return cost._replace(key=new_key)
        else:
            return cost.to_indef()


class BasicSimplifier(CostTransformer):
    
    """Return an algebraically equivalent cost tree that is either
    simpler than this one or the same as this one.
    
    For sum and min cost terms, rewrite them to eliminate duplicate
    entries. For product and sum, eliminate unit cost entries.
    """
    
    def recurse_helper(self, cost):
        """Recurse over terms. Analogous to NodeVisitor.generic_visit()
        but for Product/Sum/Min only.
        """
        terms = [self.visit(t) for t in cost.terms]
        return cost._replace(terms=terms)
    
    def unique_helper(self, cost):
        """Eliminate duplicate terms."""
        terms = OrderedSet(cost.terms)
        return cost._replace(terms=terms)
    
    def elimunit_helper(self, cost):
        """Eliminate Unit terms."""
        terms = [t for t in cost.terms if t != Unit()]
        return cost._replace(terms=terms)
    
    def visit_Product(self, cost):
        cost = self.recurse_helper(cost)
        cost = self.elimunit_helper(cost)
        return cost
    
    def visit_Sum(self, cost):
        cost = self.recurse_helper(cost)
        cost = self.unique_helper(cost)
        cost = self.elimunit_helper(cost)
        return cost
    
    def visit_Min(self, cost):
        cost = self.recurse_helper(cost)
        cost = self.unique_helper(cost)
        return cost


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

