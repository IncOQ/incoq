"""Comprehension flattening and unflattening.

The steps for flattening are as follows.

    1) Rewrite all "replaceable" expressions. Replaceable expressions
       include:
       
           - field retrievals o.f
           - map lookups m[k]
           - tuple expressions (v1, ..., vk)
        
        where o, m, k, and v1..vk are all variables or smaller
        replaceable expressions.
        
        For each unique replaceable expression appearing in the
        comprehension, a fresh variable v is introduced. All occurrences
        of that particular expression are replaced by v, and a new
        clause is added to bind v. The clause is inserted to the left
        of the clause containing the first occurrence.
    
    2) Replace each membership clause that was in the comprehension
       prior to step (1) with a RelMember clause.

Flattening will fail in step (1) if there is a field retrieval, map
retrieval, or tuple expression that does not fit the form above, or if
there is a membership clause that does not fit the form of RelMember.
"""


__all__ = [
    'ReplaceableRewriter',
]


from incoq.util.collections import OrderedSet
from incoq.mars.incast import L


class ReplaceableRewriter(L.NodeTransformer):
    
    """Rewrite replaceable expressions. Return a pair of the modified
    tree and a sequence of new clauses to insert prior to this AST.
    
    It is intended that the same instance of this transformer be reused
    for each part of a comprehension. A new variable and clause will
    not be emitted if a replaceable expression has already been seen
    in a prior run.
    """
    
    # Make sure to handle replaceables in a post-recursive manner, so
    # inner expressions are replaced first.
    
    def __init__(self, field_namer, map_namer, tuple_namer):
        super().__init__()
        self.field_namer = field_namer
        self.map_namer = map_namer
        self.tuple_namer = tuple_namer
        self.cache = {}
        """Map from replaceable expression to its replacement variable."""
    
    def process(self, tree):
        self.new_clauses = []
        tree = super().process(tree)
        return tree, self.new_clauses
    
    # The helpers break apart the replaceable node, and return a pair
    # of the replacement variable name and the new clause.
    
    def Attribute_helper(self, node):
        if not isinstance(node.value, L.Name):
            raise L.ProgramError('Non-simple field retrieval: {}'
                                 .format(node))
        obj = node.value.id
        attr = node.attr
        
        name = self.field_namer(obj, attr)
        clause = L.FMember(obj, name, node.attr)
        return name, clause
    
    def DictLookup_helper(self, node):
        if not (isinstance(node.value, L.Name) and
                isinstance(node.key, L.Name) and
                node.default is None):
            raise L.ProgramError('Non-simple map lookup: {}'.format(node))
        map = node.value.id
        key = node.key.id
        
        name = self.map_namer(map, key)
        clause = L.MAPMember(map, key, name)
        return name, clause
    
    def Tuple_helper(self, node):
        if not L.is_tuple_of_names(node):
            return L.ProgramError('Non-simple tuple expression: {}'
                                  .format(node))
        elts = L.detuplify(node)
        
        name = self.tuple_namer(elts)
        clause = L.TUPMember(name, elts)
        return name, clause
    
    def replaceable_helper(self, node):
        if node in self.cache:
            return L.Name(self.cache[node])
        orig_node = node
        
        node = self.generic_visit(node)
        
        helper = {L.Attribute: self.Attribute_helper,
                  L.DictLookup: self.DictLookup_helper,
                  L.Tuple: self.Tuple_helper}[node.__class__]
        new_name, new_clause = helper(node)
        
        self.new_clauses.append(new_clause)
        self.cache[orig_node] = new_name
        return L.Name(new_name)
    
    visit_Attribute = replaceable_helper
    visit_DictLookup = replaceable_helper
    visit_Tuple = replaceable_helper
