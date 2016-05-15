"""Pre- and post-processings applied at the IncAST level."""


__all__ = [
    # Preprocessings are paired with their postprocessings,
    # and listed in order of their application, outermost-first.
    
    'preprocess_query_markings',
    
    'postprocess_firstthen',
    
    'preprocess_clauses',
    'postprocess_clauses',
    
    'disallow_features',
    
    'check_annotations',
    
    'rename_wildcards',
    
    # Main exports.
    'incast_preprocess',
    'incast_postprocess',
]


from incoq.util.collections import frozendict
from incoq.compiler.incast import L
from incoq.compiler.symbol import S


class QueryMarker(L.NodeTransformer):
    
    """Given a tree and a mapping from query expressions to query names,
    mark all occurrences of the query expressions in the tree, by
    wrapping them in a Query node. Expressions that are already the
    direct descendant of a Query node are not marked, but their
    subexpressions can be.
    
    In the case where some of the the given query expressions may
    contain others, these occurrences of inner query expressions must
    already be marked. For example, if the given expressions in the
    mapping are
    
        A(... B ...)
        B
    
    Then the occurrence of B in A must be marked (with no annotations),
    as in
    
        A(... QUERY(<name>, B) ...)
        B
    
    This is to ensure that the rule for A matches occurrences of its
    expression in the tree, after the subtrees of such occurrences
    have already been processed.
    
    If strict is True, raise ProgramError if any given query expression
    has no occurrence that can be marked.
    """
    
    def __init__(self, query_name_map, *, strict=False):
        super().__init__()
        self.query_name_map = query_name_map
        """Map from query AST to name."""
        self.strict = strict
        """Raise error if a query does not occur, or only occurs
        directly inside a Query node.
        """
    
    def process(self, tree):
        self.found = set()
        tree = super().process(tree)
        notfound = set(self.query_name_map.keys()) - self.found
        if self.strict and len(notfound) > 0:
            qstrs = [L.Parser.ts(query) for query in notfound]
            raise L.ProgramError('No matching occurrence for queries: {}'
                                 .format(', '.join(qstrs)))
        return tree
    
    def generic_visit(self, node):
        node = super().generic_visit(node)
        
        # Wrap in Query if it's one of the queries we're given.
        name = self.query_name_map.get(node, None)
        if name is not None:
            self.found.add(node)
            node = L.Query(name, node, None)
        
        return node
    
    def visit_Query(self, node):
        # Skip immediate child but recurse over its children.
        # This is one of the few cases where it's appropriate
        # for a visitor to call super().generic_visit().
        child = super().generic_visit(node.query)
        if child is not node.query:
            node = node._replace(query=child)
        return node


def preprocess_query_markings(tree, query_name_map):
    """Apply QueryMarker, taking care of the case where some of the
    given queries can be nested inside other ones.
    """
    # Form a new query name map where all proper subquery expressions
    # are marked. Do this by running QueryMarker on each query
    # expression in a topologically sorted order, with the substitutions
    # specified by the smaller expressions that have already been
    # processed. The topological order is obtained by sorting on tree
    # size.
    query_name_items = list(query_name_map.items())
    query_name_items.sort(key=L.tree_size)
    new_map = {}
    for query, name in query_name_items:
        new_query = QueryMarker.run(query, new_map)
        new_map[new_query] = name
    
    return QueryMarker.run(tree, new_map, strict=True)


class FirstThenExporter(L.NodeTransformer):
    
    """Expand FirstThen nodes using boolean operators."""
    
    def visit_FirstThen(self, node):
        node = self.generic_visit(node)
        
        first = L.BoolOp(L.Or(), [node.first, L.NameConstant(True)])
        return L.BoolOp(L.And(), [first, node.then])

postprocess_firstthen = FirstThenExporter.run


class ClauseImporter(L.NodeTransformer):
    
    """Rewrite Member clauses as SingMember and WithoutMember
    when applicable.
    """
    
    def visit_Member(self, node):
        # For clauses that wrap around another clause, like
        # WithoutMember, reorient the target and iter before recursing.
        handled = False
        
        # <target> in <expr> - {<elem>}
        if (isinstance(node.iter, L.BinOp) and
            isinstance(node.iter.op, L.Sub) and
            isinstance(node.iter.right, L.Set) and
            len(node.iter.right.elts) == 1):
            inner_clause = L.Member(node.target, node.iter.left)
            node = L.WithoutMember(inner_clause, node.iter.right.elts[0])
            handled = True
        
        node = self.generic_visit(node)
        if handled:
            return node
        
        # <vars> in {<elem>}
        if (L.is_tuple_of_names(node.target) and
            isinstance(node.iter, L.Set) and
            len(node.iter.elts) == 1):
            return L.SingMember(L.detuplify(node.target),
                                node.iter.elts[0])
        
        return node


class ClauseExporter(L.NodeTransformer):
    
    """Convert SingMember and WithoutMember into equivalent ordinary
    Member clauses.
    """
    
    def visit_SingMember(self, node):
        node = self.generic_visit(node)
        
        return L.Member(L.tuplify(node.vars),
                        L.Set([node.value]))
    
    def visit_WithoutMember(self, node):
        node = self.generic_visit(node)
        
        new_iter = L.BinOp(node.cl.iter, L.Sub(), L.Set([node.value]))
        return L.Member(node.cl.target, new_iter)
    
    def visit_VarsMember(self, node):
        node = self.generic_visit(node)
        
        return L.Member(L.tuplify(node.vars), node.iter)


preprocess_clauses = ClauseImporter.run
postprocess_clauses = ClauseExporter.run


class FeatureDisallower(L.NodeVisitor):
    
    """Fail if there are any GeneralCall nodes in the tree."""
    
    def visit_GeneralCall(self, node):
        raise TypeError('IncAST function calls must be directly '
                        'by function name')

disallow_features = FeatureDisallower.run


class AnnotationChecker(L.NodeVisitor):
    
    def visit_Query(self, node):
        self.generic_visit(node)
        if node.ann is not None:
            if not isinstance(node.ann, (dict, frozendict)):
                raise L.ProgramError('Query annotation must be a '
                                     'dictionary')
            for key in node.ann.keys():
                if key not in S.annotations:
                    raise L.ProgramError('Unknown annotation key "{}"'.
                                         format(key))

check_annotations = AnnotationChecker.run


def rename_wildcards(tree, fresh_vars):
    """Replace all wildcards ('_' identifiers) with fresh variable
    names.
    """
    class Trans(L.NodeTransformer):
        def visit_Name(self, node):
            if node.id == '_':
                node = node._replace(id=next(fresh_vars))
            return node
    
    return Trans.run(tree)


def incast_preprocess(tree, *, fresh_vars, query_name_map):
    """Preprocess an IncAST tree, returning the new tree."""
    # Mark query occurrences.
    tree = preprocess_query_markings(tree, query_name_map)
    
    # Import special clause forms besides relation clauses.
    tree = preprocess_clauses(tree)
    
    # Check to make sure certain general-case IncAST nodes
    # aren't used.
    ### Disabled at the moment.
#    disallow_features(tree)
    
    # Check to make sure annotations are well-formed.
    check_annotations(tree)
    
    tree = rename_wildcards(tree, fresh_vars)
    
    return tree


def incast_postprocess(tree):
    """Postprocess an IncAST tree, returning the new tree."""
    # Postprocess special clauses.
    tree = postprocess_clauses(tree)
    
    # Expand FirstThen nodes.
    tree = postprocess_firstthen(tree)
    
    return tree
