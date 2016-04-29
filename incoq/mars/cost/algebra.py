"""Cost algebra, simplification, normalization."""


__all__ = [
    'ImgkeySubstitutor',
    'BasicSimplifier',
]


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
