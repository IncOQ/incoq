"""Wrap gendb to provide an easy interface for generating pairs
with degree restrictions.
"""


__all__ = [
    'gen_pairs',
    'gen_pairs_with_inverse',
    'steal_edges',
    'print_pairinfo',
    'print_deginfo',
]


#QUIET = False
QUIET = True


import sys
import os
from random import shuffle, randrange, choice

from gendb.gen import Domain, Relation, Database


def gen_pairs(A, B, outdegree):
    """Return a list of pairs (a, b) where a and b are drawn
    from the domains A and B respectively. A and B must be
    sequences. The outdegree is passed to gendb as a constraint.
    """
    nA = len(A)
    nB = len(B)
    
    # Gendb likes to call sys.exit() on error conditions,
    # and flood stdout with status updates. Let's make it
    # play nicely.
    try:
        if QUIET:
            old_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')
        
        DA = Domain(1, nA)
        DB = Domain(1, nB)
        R = Relation('R', DA, DB)
        R.Set_Max_Constr4(1, 2, outdegree)
        DB = Database('DB')
        DB.Add_Relations(R)
        DB.Generate()
    except SystemExit as exc:
        raise ValueError('Gendb error') from exc
    finally:
        if QUIET:
            sys.stdout.close()
            sys.stdout = old_stdout
    
    result = [(A[i-1], B[j-1]) for i, j in R.rel_content]
    return result


def gen_pairs_with_inverse(A, B, outdegree, req_inv=None, max_tries=5):
    """As above, but also identify elements from B that have an
    ideal indegree of (|A| * outdegree / |B|). Return the resulting
    relation, along with a list of all elements from B ordered by
    their proximity to the ideal indegree.
    
    If req_inv is an integer, at least this many elements from B must
    have the ideal indegree. If such a configuration can't be found
    after max_tries many attempts, ValueError is raised.
    """
    R = None
    Blist = None
    n_perfect = None
    
    def try_it():
        nonlocal R, Blist, n_perfect
        R = gen_pairs(A, B, outdegree)
        R_indegs = {}
        for _x, y in R:
            R_indegs[y] = R_indegs.get(y, 0) + 1
        
        Blist = list(B)
        shuffle(Blist)
        Blist.sort(key=lambda b: abs(R_indegs[b] - outdegree))
        n_perfect = sum(1 for b in B if R_indegs[b] == outdegree)
    
    if req_inv is None:
        try_it()
        return R, Blist
    
    else:
        tries = 0
        best = 0
        while tries < max_tries:
            try_it()
            if n_perfect >= req_inv:
                return R, Blist
            tries += 1
            best = max(best, n_perfect)
        else:
            raise ValueError('Failed to generate enough elements with '
                             'desired in-degree (best: {}/{})'.format(
                             best, req_inv))


def steal_edges(A, R, chosen, n):
    """Make a modified version of R in which additional chosen values
    from the A domain are padded with additional outgoing edges, stolen
    from other values in (A - chosen). Return the modified R.
    """
    R = set(R)
    
    R_out = {}
    for x, y in R:
        R_out.setdefault(x, set()).add(y)
    
    for a in chosen:
        an = len(R_out.setdefault(a, set()))
        if an > n:
            raise ValueError('Value already has too many outgoing edges')
        if an < n:
            # Grab more edges.
            # Shuffle the edges. Note that it's more likely that we'll
            # grab an edge from a node with above-average outdegree.
            Rlist = list(R)
            shuffle(Rlist)
            for x, y in Rlist:
                # Don't steal from other chosen values.
                if x in chosen:
                    continue
                # Can't steal if we already have it.
                if y in R_out[a]:
                    continue
                # Move edge from x->y to a->y.
                R.remove((x, y))
                R_out[x].remove(y)
                R.add((a, y))
                R_out[a].add(y)
                if len(R_out[a]) == n:
                    break
            else:
                raise ValueError('Failed to steal enough edges')
    
    return R


def move_edge(R, R_set, B):
    """Given R as a list and set, and domain B, choose an edge
    (x, y) to remove and a new one (x, z) to add in its place.
    R and R_set are modified in-place. Return (x, y, z).
    """
    i = randrange(len(R))
    x, y = R[i]
    z = y
    while (x, z) in R_set:
        z = choice(B)
    R[i] = (x, z)
    R_set.remove((x, y))
    R_set.add((x, z))
    return (x, y, z)


def print_pairinfo(R):
    """Print min/max out/in degree info for a pair relation."""
    R_out = {}
    R_in = {}
    for x, y in R:
        R_out.setdefault(x, set()).add(y)
        R_in.setdefault(y, set()).add(x)
    
    print('Min/max out-degrees:  {}  -  {}'.format(
          min(len(s) for s in R_out.values()),
          max(len(s) for s in R_out.values())))
    print('Min/max in-degrees:  {}  -  {}'.format(
          min(len(s) for s in R_in.values()),
          max(len(s) for s in R_in.values())))

def print_deginfo(R, bs):
    """Print in-degree info for the given elements of B."""
    R_in = {}
    for _, y in R:
        R_in[y] = R_in.get(y, 0) + 1
    print([R_in[b] for b in bs])
