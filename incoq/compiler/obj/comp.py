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
    'ObjRelations',
    
    'ReplaceableRewriter',
    'flatten_replaceables',
    'flatten_memberships',
    'flatten_all_comps',
    
    'define_obj_relations',
    
    'rewrite_aggregates',
]


from simplestruct import Struct, Field, TypedField

from incoq.util.collections import OrderedSet
from incoq.compiler.incast import L
from incoq.compiler.type import T
from incoq.compiler.symbol import S, N


class ObjRelations(Struct):
    
    M = TypedField(bool)
    Fs = TypedField(str, seq=True)
    MAP = TypedField(bool)
    TUPs = TypedField(int, seq=True)
    
    @classmethod
    def empty(cls):
        """Return an empty ObjRelations."""
        return ObjRelations(False, [], False, [])
    
    def union(self, other):
        """Return an ObjRelations value that combines this one with
        another.
        """
        M = self.M or other.M
        Fs = OrderedSet(self.Fs + other.Fs)
        MAP = self.MAP or other.MAP
        TUPs = OrderedSet(self.TUPs + other.TUPs)
        return ObjRelations(M, Fs, MAP, TUPs)

class MutableObjRelations(Struct):
    _immutable = False
    
    M = Field()
    Fs = Field()
    MAP = Field()
    TUPs = Field()
    
    @classmethod
    def empty(cls):
        return MutableObjRelations(False, [], False, [])


class ReplaceableRewriterBase(L.NodeTransformer):
    
    """Rewrite replaceable expressions. Return a pair of the modified
    tree and two sequences of new clauses to insert before and after
    the occurrence of this AST's clause.
    
    It is intended that the same instance of this transformer be reused
    for each part of a comprehension. A new variable and clause will
    not be emitted if a replaceable expression has already been seen
    in a prior run.
    
    The objrels attribute tracks all object relations that have been
    observed to be needed.
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
        
        self.objrels = MutableObjRelations.empty()
        """MutableObjRelations representing what relations are needed."""
    
    def process(self, tree):
        self.before_clauses = []
        self.after_clauses = []
        tree = super().process(tree)
        return tree, self.before_clauses, self.after_clauses
    
    # Don't rewrite subqueries.
    def visit_Comp(self, node):
        return node
    
    # The helpers break apart the replaceable node, insert the
    # new clause, update objrels, and return the replacement variable
    # name.
    #
    # Attribute and DictLookup insert the clause to the before list,
    # Tuple to the after list.
    
    def Attribute_helper(self, node):
        if not isinstance(node.value, L.Name):
            raise L.ProgramError('Non-simple field retrieval: {}'
                                 .format(node))
        obj = node.value.id
        attr = node.attr
        
        name = self.field_namer(obj, attr)
        clause = L.FMember(obj, name, node.attr)
        self.objrels.Fs.append(attr)
        self.before_clauses.append(clause)
        return name
    
    def DictLookup_helper(self, node):
        if not (isinstance(node.value, L.Name) and
                isinstance(node.key, L.Name) and
                node.default is None):
            raise L.ProgramError('Non-simple map lookup: {}'.format(node))
        map = node.value.id
        key = node.key.id
        
        name = self.map_namer(map, key)
        clause = L.MAPMember(map, key, name)
        self.objrels.MAP |= True
        self.before_clauses.append(clause)
        return name
    
    def Tuple_helper(self, node):
        if not L.is_tuple_of_names(node):
            raise L.ProgramError('Non-simple tuple expression: {}'
                                 .format(node))
        elts = L.detuplify(node)
        
        name = self.tuple_namer(elts)
        clause = L.TUPMember(name, elts)
        self.objrels.TUPs.append(len(elts))
        self.after_clauses.insert(0, clause)
        return name
    
    def replaceable_helper(self, node):
        if node in self.cache:
            return L.Name(self.cache[node])
        orig_node = node
        
        node = self.generic_visit(node)
        
        helper = {L.Attribute: self.Attribute_helper,
                  L.DictLookup: self.DictLookup_helper,
                  L.Tuple: self.Tuple_helper}[node.__class__]
        new_name = helper(node)
        
        self.cache[orig_node] = new_name
        return L.Name(new_name)
    
    visit_Attribute = replaceable_helper
    visit_DictLookup = replaceable_helper
    visit_Tuple = replaceable_helper


class ReplaceableRewriter(ReplaceableRewriterBase):
    
    """Extension of ReplaceableRewriterBase that adds the behavior of
    not rewriting tuples in condition and result expressions.
    """
    
    def __init__(self, *args):
        super().__init__(*args)
        self.rewrite_tuples = True
        """Used to disable tuple rewriting for condition/result
        expressions.
        """
    
    def is_member(self, node):
        """Return True if this is a membership clause."""
        return (isinstance(node, L.clause) and
                not isinstance(node, L.Cond))
    
    def process(self, tree):
        # Enable/disable tuple rewriting depending on whether we're
        # called on a membership clause.
        self.rewrite_tuples = self.is_member(tree)
        return super().process(tree)
    
    def visit_Tuple(self, node):
        if self.rewrite_tuples:
            return self.replaceable_helper(node)
        else:
            # Make sure to rewrite non-tuple replaceables below us.
            return self.generic_visit(node)


def flatten_replaceables(comp):
    """Transform the comprehension to rewrite replaceables and add new
    clauses for them. Also return an ObjRelations indicating what object
    relations are needed.
    """
    field_namer = lambda obj, attr: obj + '_' + attr
    map_namer = lambda map, key: map + '_' + key
    tuple_namer = lambda elts: 't_' + '_'.join(elts)
    
    rewriter = ReplaceableRewriter(field_namer, map_namer, tuple_namer)
    tree = L.rewrite_comp(comp, rewriter.process)
    
    # Go from MutableObjRelations to an immutable one.
    objrels = ObjRelations(*rewriter.objrels)
    
    return tree, objrels


def flatten_memberships(comp):
    """Transform the comprehension to rewrite set memberships (Member
    nodes) as MMember clauses. Return an ObjRelations indicating whether
    an M set is needed.
    """
    M = False
    def process(clause):
        nonlocal M
        if isinstance(clause, L.Member):
            # MMember.
            if (isinstance(clause.target, L.Name) and
                isinstance(clause.iter, L.Name)):
                set_ = clause.iter.id
                elem = clause.target.id
                M = True
                clause = L.MMember(set_, elem)
            
            # Subquery clause, leave as Member for now.
            elif (isinstance(clause.target, L.Name) and
                  isinstance(clause.iter, L.Unwrap)):
                pass
            
            else:
                raise L.ProgramError('Cannot flatten Member clause: {}'
                                     .format(clause))
            
        
        return clause, [], []
    
    tree = L.rewrite_comp(comp, process)
    objrels = ObjRelations(M, [], False, [])
    return tree, objrels


def flatten_all_comps(tree, symtab):
    """Flatten all comprehension queries with non-Normal impl. Also
    tuplify their result expression and wrap with a call to unwrap().
    Return the transformed tree and an ObjRelations indicating what new
    relations are needed.
    """
    objrels = ObjRelations.empty()
    
    flattened_queries = set()
    
    class FlattenRewriter(S.QueryRewriter):
        
        def visit_Query(self, node):
            node = super().visit_Query(node)
            # Add an Unwrap node.
            if node.name in flattened_queries:
                node = L.Unwrap(node)
            return node
        
        def rewrite_comp(self, symbol, name, comp):
            nonlocal objrels
            flattened_queries.add(name)
            
            comp, objrels1 = flatten_replaceables(comp)
            comp, objrels2 = flatten_memberships(comp)
            objrels = objrels.union(objrels1).union(objrels2)
            
            # Wrap result expression.
            comp = comp._replace(resexp=L.Tuple([comp.resexp]))
            t = symbol.type
            t = t.join(T.Set(T.Bottom))
            assert t.issmaller(T.Set(T.Top))
            symbol.type = T.Set(T.Tuple([t.elt]))
            
            return comp
    
    tree = FlattenRewriter.run(tree, symtab)
    return tree, objrels


def define_obj_relations(symtab, objrels):
    """Define object relations in the symbol table."""
    pairset = T.Set(T.Tuple([T.Top, T.Top]))
    tripleset = T.Set(T.Tuple([T.Top, T.Top, T.Top]))
    if objrels.M:
        symtab.define_relation(N.M, type=pairset)
    for attr in objrels.Fs:
        symtab.define_relation(N.F(attr), type=pairset)
    if objrels.MAP:
        symtab.define_relation(N.MAP, type=pairset)
    for arity in objrels.TUPs:
        t = T.Set(T.Tuple([T.Top] * (arity + 1)))
        symtab.define_relation(N.TUP(arity), type=t)


def rewrite_aggregates(tree, symtab):
    """Rewrite all incrementalizable aggregate queries whose operand is
    not a relation or a subquery, such that the operand is now a
    comprehension subquery.
    """
    class Rewriter(S.QueryRewriter):
        def rewrite_aggr(self, symbol, name, expr):
            operand = expr.value
            
            if (isinstance(operand, L.Name) and
                operand.id in symtab.get_relations()):
                return
            if isinstance(operand, L.Query):
                return
            
            oper_name = symbol.name + '_oper'
            elem = next(symtab.fresh_names.vars)
            t_oper = symtab.analyze_expr_type(operand)
            # We're tolerant of type misinformation here, since our object
            # type inference isn't in place at the moment.
            if not t_oper.issmaller(T.Set(T.Top)):
                t_oper = T.Set(T.Top)
            
            comp = L.Comp(L.Name(elem), [L.Member(L.Name(elem), operand)])
            oper_query = L.Query(oper_name, comp, None)
            symtab.define_query(oper_name, node=comp, type=t_oper,
                                impl=symbol.impl)
            expr = expr._replace(value=oper_query)
            return expr
    
    tree = Rewriter.run(tree, symtab)
    return tree
