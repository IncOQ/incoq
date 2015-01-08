"""Object-set comprehension translation."""


__all__ = [
    'flatten_comp',
    'unflatten_comp',
]


from invinc.util.collections import OrderedSet
import invinc.compiler.incast as L

from .pairrel import (make_mrel, is_mrel, get_menum, make_frel, get_fenum,
                      make_maprel, get_mapenum, is_specialrel)


class RetrievalReplacer(L.NodeTransformer):
    
    """Replace simple field and map retrieval expressions with a
    variable. A retrieval expression is simple if the object or map
    part of the expression is just a variable. Raise an error if any
    non-simple retrievals are encountered.
    
    Retrievals are processed inner-to-outer, so complex expressions
    like a.b[c.d].e can be handled, so long as they are built up using
    only variables and retrievals.
    
    The name of the replacement variable is given by the field_namer
    and map_namer functions.
    
    Two attributes, field_repls and map_repls, are made available for
    inspecting what replacements were performed. They are OrderedSets
    of triples where the first two components are the object/map and
    field/key respectively, and the third component is the replacement
    variable name. These attributes are cleared when process() is called
    again.
    """
    
    def __init__(self, field_namer, map_namer):
        super().__init__()
        self.field_namer = field_namer
        self.map_namer = map_namer
    
    def process(self, tree):
        self.field_repls = OrderedSet()
        self.map_repls = OrderedSet()
        tree = super().process(tree)
        return tree
    
    def visit_Attribute(self, node):
        node = self.generic_visit(node)
        
        if not isinstance(node.value, L.Name):
            raise L.ProgramError('Non-simple field retrieval', node=node)
        obj = node.value.id
        field = node.attr
        
        new_name = self.field_namer(obj, field)
        self.field_repls.add((obj, field, new_name))
        
        return L.Name(new_name, node.ctx)
    
    def visit_Subscript(self, node):
        node = self.generic_visit(node)
        
        if not (isinstance(node.value, L.Name) and
                isinstance(node.slice, L.Index) and
                isinstance(node.slice.value, L.Name)):
            raise L.ProgramError('Non-simple map retrieval', node=node)
        map = node.value.id
        key = node.slice.value.id
        
        new_name = self.map_namer(map, key)
        self.map_repls.add((map, key, new_name))
        
        return L.Name(new_name, node.ctx)

class RetrievalExpander(L.NodeTransformer):
    
    """Replace field and map replacement names with their corresponding
    retrieval expressions. Takes in mappings from replacement variable
    names to pairs of obj/map and field/key names. Expansion is
    recursive.
    """
    
    def __init__(self, field_exps, map_exps):
        super().__init__()
        self.field_exps = field_exps
        self.map_exps = map_exps
    
    def visit_Name(self, node):
        if node.id in self.field_exps:
            obj, field = self.field_exps[node.id]
            new_node = L.Attribute(L.ln(obj), field, node.ctx)
            new_node = self.generic_visit(new_node)
            return new_node
        
        elif node.id in self.map_exps:
            map, key = self.map_exps[node.id]
            new_node = L.Subscript(L.ln(map), L.Index(L.ln(key)), node.ctx)
            new_node = self.generic_visit(new_node)
            return new_node
        
        else:
            return node


def flatten_retrievals(comp):
    """Flatten the retrievals in a Comp node. Return a triple of the new
    Comp node, an OrderedSet of the fields seen, and a bool indicating
    whether a map was seen.
    
    Field and map clauses are introduced immediately to the left of their
    first use (or for the result expression, at the end of the clause
    list).
    """
    # For map_namer, add a little extra fluff to reduce the liklihood
    # of us inadvertently creating ambiguous names.
    field_namer = lambda obj, field: obj + '_' + field
    map_namer = lambda map, key: 'm_' + map + '_k_' + key
    replacer = RetrievalReplacer(field_namer, map_namer)
    
    seen_fields = OrderedSet()
    seen_map = False
    seen_field_repls = OrderedSet()
    seen_map_repls = OrderedSet()
    
    def process(expr):
        """Rewrite any retrievals in the given expression. Return a pair
        of the new expression, and a list of new clauses to be added
        for any retrievals not already seen.
        """
        nonlocal seen_map
        new_expr = replacer.process(expr)
        new_field_repls = replacer.field_repls - seen_field_repls
        new_map_repls = replacer.map_repls - seen_map_repls
        new_clauses = []
        
        for repl in new_field_repls:
            obj, field, value = repl
            seen_fields.add(field)
            seen_field_repls.add(repl)
            new_cl = L.Enumerator(L.tuplify((obj, value), lval=True),
                                  L.ln(make_frel(field)))
            new_clauses.append(new_cl)
        
        for repl in new_map_repls:
            map, key, value = repl
            seen_map = True
            seen_map_repls.add(repl)
            new_cl = L.Enumerator(L.tuplify((map, key, value), lval=True),
                                  L.ln(make_maprel()))
            new_clauses.append(new_cl)
        
        return new_expr, new_clauses
    
    new_comp = L.rewrite_compclauses(comp, process)
    
    return new_comp, seen_fields, seen_map

def unflatten_retrievals(comp):
    """Unflatten the retrievals of a Comp. Eliminate field and map
    enumerators and expand replacement variables to retrievals.
    """
    def unwrap(node):
        assert isinstance(node, L.Name)
        return node.id
    
    # Remove field and map clauses and record replacement info.
    field_exps = {}
    map_exps = {}
    new_clauses = []
    for cl in comp.clauses:
        as_field = get_fenum(cl)
        as_map = get_mapenum(cl)
        
        if as_field is not None:
            obj, value, field = as_field
            # Since no expansions have been done yet, we know that field
            # and map clauses just have variables on the lhs.
            obj, value = unwrap(obj), unwrap(value)
            field_exps[value] = (obj, field)
        
        elif as_map is not None:
            map, key, value = as_map
            map, key, value = unwrap(map), unwrap(key), unwrap(value)
            map_exps[value] = (map, key)
        
        else:
            new_clauses.append(cl)
    
    # Apply replacements to the comprehension.
    expander = RetrievalExpander(field_exps, map_exps)
    new_comp = comp._replace(clauses=tuple(new_clauses))
    new_comp = expander.process(new_comp)
    
    return new_comp


def flatten_set_clause(cl, input_rels):
    """Turn a membership clause that is not over a comprehension,
    special relation, or input relation, into a clause over the M-set.
    Return a pair of the (possibly unchanged) clause and a bool
    indicating whether or not the change was done.
    
    This also works on condition clauses that express membership
    constraints. The rewritten clause is still a condition clause.
    """
    def should_trans(rhs):
        return (not isinstance(rhs, L.Comp) and
                not (isinstance(rhs, L.Name) and
                     (is_specialrel(rhs.id) or rhs.id in input_rels)))
    
    # Enumerator case.
    if isinstance(cl, L.Enumerator) and should_trans(cl.iter):
        item = cl.target
        cont = cl.iter
        cont = L.ContextSetter.run(cont, L.Store)
        new_cl = L.Enumerator(L.tuplify((cont, item), lval=True),
                              L.ln(make_mrel()))
        return new_cl, True
    
    # Condition case.
    if isinstance(cl, L.expr) and L.is_cmp(cl):
        item, op, cont = L.get_cmp(cl)
        if isinstance(op, L.In) and should_trans(cont):
            new_cl = L.cmp(L.tuplify((cont, item)),
                           L.In(),
                           L.ln(make_mrel()))
            return new_cl, True
    
    return cl, False

def unflatten_set_clause(cl):
    """Opposite of above. Unflatten clauses over the M-set. Works for
    both enumerators and conditions. Returns the (possibly unchanged)
    clause.
    """
    # Enumerator case.
    if isinstance(cl, L.Enumerator):
        res = get_menum(cl)
        if res is None:
            return cl
        cont, item = res
        
        cont = L.ContextSetter.run(cont, L.Load)
        new_cl = L.Enumerator(item, cont)
        return new_cl
    
    # Condition case.
    if isinstance(cl, L.expr) and L.is_cmp(cl):
        lhs, op, rhs = L.get_cmp(cl)
        if not (isinstance(op, L.In) and
                isinstance(lhs, L.Tuple) and len(lhs.elts) == 2 and
                L.is_name(rhs) and is_mrel(L.get_name(rhs))):
            return cl
        cont, item = lhs.elts
        new_cl = L.cmp(item, L.In(), cont)
        return new_cl
    
    return cl


def flatten_sets(comp, input_rels):
    """Flatten the set iterations in a Comp node. Return a pair of the
    new comp and a bool indicating whether or not the M-set was used.
    (As a practical matter, this should generally be True.) Enumerators
    over pair relations, input relations, and other comprehensions are
    not affected.
    """
    use_mset = False
    
    def process(cl):
        nonlocal use_mset
        new_cl, new_use_mset = flatten_set_clause(cl, input_rels)
        use_mset |= new_use_mset
        return new_cl, []
    
    new_comp = L.rewrite_compclauses(comp, process, resexp=False)
    
    return new_comp, use_mset

def unflatten_sets(comp):
    """Unflatten _M enumerators."""
    new_clauses = tuple(unflatten_set_clause(cl) for cl in comp.clauses)
    return comp._replace(clauses=new_clauses)


def flatten_comp(comp, input_rels):
    """Flatten away objects and nested sets. Return a tuple of the new
    comp, a boolean indicating whether the M-set is used (in practice,
    always True), an OrderedSet of the fields replaced, and a boolean
    indicating whether a map retrieval is used.
    """
    comp, fields, use_map = flatten_retrievals(comp)
    comp, use_mset = flatten_sets(comp, input_rels)
    return comp, use_mset, fields, use_map

def unflatten_comp(comp):
    """Unflatten a relational comprehension back to the object domain."""
    comp = unflatten_sets(comp)
    comp = unflatten_retrievals(comp)
    return comp
