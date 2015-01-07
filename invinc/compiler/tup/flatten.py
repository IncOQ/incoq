"""Flatten relations that have a nested tuple structure."""


__all__ = [
    'flatten_relations',
]


import invinc.compiler.incast as L


def tuptree_to_type(node):
    """Given a tuple tree of variables, return the type structure."""
    if isinstance(node, L.Tuple):
        return ('<T>',) + tuple(tuptree_to_type(elt)
                                for elt in node.elts)
    elif isinstance(node, L.Name):
        return node.id
    else:
        assert()


def tuptype_leaves(tuptype):
    """Given a tuple tree type (in the form of the domain types for
    relations), return a list of paths to leaf components, i.e.
    non-tuple components. Each path is itself a sequence of indices,
    such that subscripting with each index in turn brings us from the
    root tuple value to the leaf value.
    """
    leaves = []
    
    def process(t, path):
        if isinstance(t, tuple) and t[0] == '<T>':
            for i, elt in enumerate(t[1:]):
                process(elt, path + (i,))
        else:
            leaves.append(path)
    
    process(tuptype, ())
    return leaves


def make_flattup_code(tuptype, in_node, out_node, tempvar):
    """Given a tuple tree type, make code to take the tuple given by the
    expression in_node and store the flattened form in the tuple given
    by out_node.
    """
    def leaf_to_expr(root, path):
        """Turn a leaf path into a series of subscript expressions
        that obtain the leaf value from the root value.
        """
        node = root
        for i in path:
            node = L.Subscript(node, L.Index(L.Num(i)), L.Load())
        return node
    
    leaves = tuptype_leaves(tuptype)
    code = ()
    
    # If in_expr is just a variable name, use it as is.
    # Otherwise store it in a temporary variable to avoid redundant
    # evaluation of in_expr.
    if isinstance(in_node, L.Name):
        root_node = in_node
    else:
        rootname = tempvar
        code += L.pc('''
            ROOT = IN_NODE
            ''', subst={'IN_NODE': in_node,
                        'ROOT': L.sn(rootname)})
        root_node = L.ln(rootname)
    
    flattuple_expr = L.Tuple(tuple(leaf_to_expr(root_node, leaf)
                                   for leaf in leaves),
                             L.Load())
    code += L.pc('''
        OUT_NODE = FLATTUP
        ''', subst={'FLATTUP': flattuple_expr,
                    'OUT_NODE': out_node})
    
    return code


class UpdateFlattener(L.NodeTransformer):
    
    """Rewrite updates to the given set to use the flattened form."""
    
    def __init__(self, rel, tuptype, namegen):
        super().__init__()
        self.rel = rel
        self.tuptype = tuptype
        self.namegen = namegen
    
    def visit_SetUpdate(self, node):
        if not (isinstance(node.target, L.Name) and
                node.target.id == self.rel):
            return
        
        fresh = next(self.namegen)
        tvar = '_t' + fresh
        ftvar = '_ft' + fresh
        code = make_flattup_code(self.tuptype, node.elem,
                                 L.sn(ftvar), tvar)
        update = node._replace(elem=L.ln(ftvar))
        return code + (update,)


def get_clause_vars(enum_node, tuptype):
    """Given a clause and tuple tree type, return a list of the
    variables or wildcards used on the tuple tree on the LHS.
    The LHS must exactly match the structure of the type.
    """
    vars = []
    
    def process(node, t):
        if isinstance(t, tuple) and t[0] == '<T>':
            assert (isinstance(node, L.Tuple) and
                    len(node.elts) == len(t) - 1)
            for n, t2 in zip(node.elts, t[1:]):
                process(n, t2)
        else:
            assert isinstance(node, L.Name)
            vars.append(node.id)
    
    process(enum_node.target, tuptype)
    return vars


class ClauseFlattener(L.NodeTransformer):
    
    """Rewrite all clauses over the given relation to use the flattened
    form of its type. This requires that the tuple tree structure of
    the clauses exactly matches that of the type. In particular,
    variables that summarize tuple components in the type are not
    allowed.
    """
    
    def __init__(self, rel, tuptype):
        super().__init__()
        self.rel = rel
        self.tuptype = tuptype
    
    def visit_Enumerator(self, node):
        node = self.generic_visit(node)
        
        if not (isinstance(node.iter, L.Name) and
                node.iter.id == self.rel):
            return
        
        vars = get_clause_vars(node, self.tuptype)
        new_lhs = L.tuplify(vars, lval=True)
        return node._replace(target=new_lhs)


class ReltypeGetter(L.NodeVisitor):
    
    """Gets type information for a given relation based on enumerators
    over it. All the enumerators over it must have the exact same tuple
    structure. The type must not be a singleton tuple, but it can be
    a singular non-tuple value. If there are no enumerators over it,
    a singular non-tuple value type is returned.
    """
    
    def __init__(self, rel):
        super().__init__()
        self.rel = rel
    
    def process(self, tree):
        self.tuptype = None
        super().process(tree)
        
        if self.tuptype is None:
            self.tuptype = '_'
        if isinstance(self.tuptype, tuple) and self.tuptype[0] == '<T>':
            assert len(self.tuptype) > 2, \
               'Type of {} is singleton tuple'.format(self.rel)
        return self.tuptype
    
    def visit_Enumerator(self, node):
        self.generic_visit(node)
        
        if not (isinstance(node.iter, L.Name) and
                node.iter.id == self.rel):
            return
        
        tuptype = tuptree_to_type(node.target)
        if self.tuptype is None:
            self.tuptype = tuptype
        else:
            assert self.tuptype == tuptype


def flatten_relations(tree, rels, namegen):
    """Return a modified tree where the structure of the given relations
    is flattened.
    
    This only works when the relation is only read via comprehension
    enumerators. Each clause over the relation must use a tuple
    structure that exactly matches the relation's type information.
    """
    for rel in rels:
        tuptype = ReltypeGetter.run(tree, rel)
        # Skip if tuptype is just a variable with no tuple.
        if not (isinstance(tuptype, tuple) and tuptype[0] == '<T>'):
            continue
        tree = ClauseFlattener.run(tree, rel, tuptype)
        tree = UpdateFlattener.run(tree, rel, tuptype, namegen)
    return tree
