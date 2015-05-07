"""Implementation of the unification algorithm.

Variable names are represented as strings. Wildcards are the string '_'.
Constants and complex terms are represented as tuple trees. The first
component of the tuple is a string identifying its functor symbol.
The remaining components are the subterms -- either other tuples or else
variable name strings.

    f(x, y)     -->   ('f', 'x', 'y')
    f(g(x), y)  -->   ('f', ('g', 'x'), 'y')
    c           -->   ('c',)

A substitution is represented as a dictionary from variable name to
a term. No variable in the domain of this mapping is anywhere in the
range. A set of equations is represented as a list of pairs of terms.
"""


__all__ = [
    'unify',
]


class MatchFailure(Exception):
    """Raised in case matching fails, to terminate the recursive search."""

class OccursCheckFailure(Exception):
    """Raised if a recursive term is found."""


def apply_subst(term, subst):
    """Apply a substitution to a term."""
    if isinstance(term, str):
        if term == '_':
            return '_'
        else:
            return subst.get(term, term)
    elif isinstance(term, tuple):
        return tuple([term[0]] + [apply_subst(s, subst) for s in term[1:]]) 
    else:
        assert()

def occurs_check(var, term):
    """Raise OccursCheckFailure if var appears anywhere in term."""
    assert var != '_'
    if isinstance(term, str):
        if term == var:
            raise OccursCheckFailure
    elif isinstance(term, tuple):
        for s in term[1:]:
            occurs_check(var, s)
    else:
        assert()

def add_mapping(var, term, subst, eqs):
    """Update the given substitution and equations to account for a new
    mapping from var to term. Occurrences of var in subst and eqs are
    replaced with term, and the new entry is added to subst. May raise
    OccursCheckFailure.
    """
    assert isinstance(var, str)
    assert var != '_'
    assert isinstance(term, (str, tuple))
    
    # For each existing mapping, expand it based on this new mapping
    # and do an occurs check.
    for var2, term2 in subst.items():
        new_term2 = apply_subst(term2, {var: term})
        occurs_check(var2, new_term2)
        subst[var2] = new_term2
    
    subst[var] = term
    
    # Expand equations.
    for i, (left, right) in enumerate(eqs):
        eqs[i] = (apply_subst(left, {var: term}),
                  apply_subst(right, {var: term}))


def unify_terms(t1, t2, subst, eqs):
    """Attempt to unify t1 with t2, adding the resulting substitutions
    to the out-parameter subst dictionary. Also expand the supplied set
    of equations as well. If unification fails, raise MatchFailure.
    """
    # Skip the trivial case of equating a wildcard with anything.
    if t1 == '_' or t2 == '_':
        return
    
    # Skip the trivial case of equating a variable with itself.
    if isinstance(t1, str) and isinstance(t2, str) and t1 == t2:
        return
    
    # Flip tuple = var to its symmetric case.
    if isinstance(t1, tuple) and isinstance(t2, str):
        t1, t2 = t2, t1
    
    # Handle var = var or var = tuple.
    if isinstance(t1, str):
        add_mapping(t1, t2, subst, eqs)
    
    # Handle tuple = tuple.
    elif isinstance(t1, tuple) and isinstance(t2, tuple):
        # Different functors.
        if t1[0] != t2[0] or len(t1) != len(t2):
            raise MatchFailure
        
        # Recurse on subterms.
        for s1, s2 in zip(t1[1:], t2[1:]):
            # Apply the substitution to the terms in case there were any
            # new mappings introduced by previous steps of this loop.
            s1 = apply_subst(s1, subst)
            s2 = apply_subst(s2, subst)
            unify_terms(s1, s2, subst, eqs)
    
    else:
        assert()


def unify(eqs):
    """Run unification on a sequence of equations (pairs of terms)
    and return a substitution mapping, or None if the equations are
    not solvable.
    """
    eqs = list(eqs)
    subst = {}
    
    try:
        while len(eqs) > 0:
            left, right = eqs.pop()
            unify_terms(left, right, subst, eqs)
    
    except MatchFailure:
        return None
    
    return subst
