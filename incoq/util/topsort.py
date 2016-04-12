"""Topological sort routine."""


__all__ = [
    'topsort',
    'get_cycle',
]

from .collections import OrderedSetDict, OrderedSet


def topsort_helper(nodes, edges):
    """Run topsort and return a triple of
    
        1) the nodes popped in order,
        
        2) the nodes and 3) edges of the remaining graph at the time
           no more roots were available.
    
    If an ordering was in fact found, (2) and (3) will be empty.
    
    The return value is deterministic even when multiple orders are
    possible.
    """
    eout = OrderedSetDict()
    ein = OrderedSetDict()
    for x, y in edges:
        assert x in nodes and y in nodes, \
            'Edge ({}, {}) uses invalid node'.format(x, y)
        eout[x].add(y)
        ein[y].add(x)
    remaining_nodes = OrderedSet(nodes)
    remaining_edges = OrderedSet(edges)
    
    result = []
    roots = OrderedSet(n for n in nodes if len(ein[n]) == 0)
    while len(roots) > 0:
        # Pop front.
        x = next(iter(roots))
        roots.discard(x)
        
        result.append(x)
        remaining_nodes.remove(x)
        if x in eout:
            succs = eout.pop(x)
            for y in succs:
                ein[y].remove(x)
                remaining_edges.remove((x, y))
                if len(ein[y]) == 0:
                    roots.add(y)
    
    return result, remaining_nodes, remaining_edges

def topsort(nodes, edges):
    """Given a graph, return a topological ordering of the nodes,
    or None if there is a cycle.
    """
    order, rem_nodes, _rem_edges = topsort_helper(nodes, edges)
    if len(rem_nodes) > 0:
        return None
    else:
        return order

def get_cycle(nodes, edges):
    """Return a cycle in the graph if one exists, or None otherwise."""
    _order, rem_nodes, rem_edges = topsort_helper(nodes, edges)
    if len(rem_nodes) == 0:
        return None
    
    ein = OrderedSetDict()
    for x, y in rem_edges:
        ein[y].add(x)
    
    # Choose an arbitrary node, and follow its in-edges until we hit
    # the same node twice. This is guaranteed to happen since topsort
    # already popped the roots away.
    node = next(iter(rem_nodes))
    stack = [node]
    stackset = set(stack)
    ans = []
    while True:
        top = stack[-1]
        pred = next(iter(ein[top]))
        if pred in stackset:
            ans.append(pred)
            while stack[-1] != pred:
                ans.append(stack.pop())
            break
        else:
            stack.append(pred)
            stackset.add(pred)
    
    return ans
