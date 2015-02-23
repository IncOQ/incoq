"""Type analysis."""


__all__ = [
    'FrozenDictField',
    
    'Type',
    'toptype',
    'bottomtype',
    'PrimitiveType',
    'booltype',
    'numbertype',
    'strtype',
    'SeqType',
    'TupleType',
    'ListType',
    'SetType',
    'DictType',
    'ObjType',
    
    'eval_typestr',
    
    'TypedUnparser',
    'unparse_structast_typed',
    'TypeAnnotator',
    
    'analyze_types',
]


from numbers import Number
from simplestruct import Struct, Field, TypedField

from invinc.util.collections import frozendict

from .nodes import expr, Not, Index, Num
from .structconv import AdvNodeTransformer, Unparser, export_structast


class FrozenDictField(TypedField):
    
    """Field for frozendicts, with coercion from ordinary dicts."""
    
    def __init__(self, keytype=None, valuetype=None):
        super().__init__(frozendict)
        self.keytype = keytype
        self.valuetype = valuetype
    
    def copy(self):
        return type(self)(self.keytype, self.valuetype)
    
    def check(self, inst, value):
        if (self.keytype is not None and
            not all(isinstance(k, self.keytype) for k in value.keys())):
            raise TypeError('Key with bad type')
        if (self.valuetype is not None and
            not all(isinstance(v, self.valuetype) for v in value.values())):
            raise TypeError('Value with bad type')
    
    def normalize(self, inst, value):
        if not isinstance(value, frozendict):
            return frozendict(value)
        return value


class Type(Struct):
    
    def unify(self, *others):
        """Unify this type with one or more others, returning
        a new type.
        """
        t = self
        for o in others:
            t = t.unify_one(o)
        return t
    
    def unify_one(self, other):
        if self == toptype:
            return other
        elif other == toptype:
            return self
        elif self == other:
            return self
        else:
            return self.unify_helper(other)
    
    def unify_helper(self, other):
        return bottomtype

class TopTypeClass(Type):
    """No type info."""
    
    singleton = None
    
    def __new__(cls):
        if cls.singleton is None:
            cls.singleton = super().__new__(cls)
        return cls.singleton
    
    def __str__(self):
        return 'Top'
toptype = TopTypeClass()

class BottomTypeClass(Type):
    """Conflicting type info."""
    
    singleton = None
    
    def __new__(cls):
        if cls.singleton is None:
            cls.singleton = super().__new__(cls)
        return cls.singleton
    
    def __str__(self):
        return 'Bottom'
bottomtype = BottomTypeClass()

class PrimitiveType(Type):
    t = TypedField(type)
    
    def __str__(self):
        return self.t.__name__
booltype = PrimitiveType(bool)
numbertype = PrimitiveType(Number)
strtype = PrimitiveType(str)

class TupleType(Type):
    ets = TypedField(Type, seq=True)
    
    def __str__(self):
        return '(' + ', '.join(str(et) for et in self.ets) + ')'
    
    def unify_helper(self, other):
        if type(self) == type(other) and len(self.ets) == len(other.ets):
            return TupleType([e1.unify(e2)
                              for e1, e2 in zip(self.ets, other.ets)])
        else:
            return bottomtype

class SeqType(Type):
    et = TypedField(Type)
    brackets = '??'
    
    def __str__(self):
        return self.brackets[0] + str(self.et) + self.brackets[1]
    
    def unify_helper(self, other):
        if type(self) == type(other):
            et = self.et.unify(other.et)
            return self._replace(et=et)
        else:
            return bottomtype

class ListType(SeqType):
    _inherit_fields = True
    brackets = '[]'

class SetType(SeqType):
    _inherit_fields = True
    brackets = '{}'

class DictType(Type):
    kt = TypedField(Type)
    vt = TypedField(Type)
    
    def __str__(self): 
        return '{' + str(self.kt) + ': ' + str(self.vt) + '}'
    
    def unify_helper(self, other):
        if type(self) == type(other):
            kt = self.kt.unify(other.kt)
            vt = self.vt.unify(other.vt)
            return self._replace(kt=kt, vt=vt)
        else:
            return bottomtype

class ObjType(Type):
    name = TypedField(str)
    
    def __str__(self):
        return self.name


def eval_typestr(s):
    """eval() a string representing a type expression."""
    ns = {k: v for k, v in globals().items()
               if isinstance(v, Type) or
                  (isinstance(v, type) and issubclass(v, Type))}
    return eval(s, ns)


class TypedUnparser(Unparser):
    
    """Unparser that includes type information for all expression
    nodes.
    """
    
    def dispatch(self, tree):
        show_type = isinstance(tree, expr) and tree.type is not None
        
        if show_type:
            self.write('(')
        super().dispatch(tree)
        if show_type:
            self.write(' : ' + str(tree.type) + ')')

def unparse_structast_typed(tree):
    """As structconv.unparse_structast(), but with type info."""
    return TypedUnparser.to_source(tree)


class TypeAnnotator(AdvNodeTransformer):
    
    """Add type information to all expression nodes where possible."""
    
    def __init__(self, vartypes=None, objtypes=None):
        super().__init__()
        if vartypes is None:
            vartypes = {}
        self.vartypes = vartypes
        if objtypes is None:
            objtypes = {}
        self.objtypes = objtypes
    
    def process(self, tree):
        tree = super().process(tree)
        return tree, self.vartypes
    
    # Statements.
    
    def visit_Assign(self, node):
        value = self.visit(node.value)
        t = value.type
        targets = self.visit(node.targets, t)
        return node._replace(targets=targets, value=value)
    
    def visit_SetUpdate(self, node):
        elem = self.visit(node.elem)
        target = self.visit(node.target, SetType(elem.type))
        return node._replace(target=target, elem=elem)
    
    def visit_MacroSetUpdate(self, node):
        t = SetType(toptype)
        if node.other is None:
            other = None
        else:
            other = self.visit(node.other)
            t = t.unify(other.type)
        target = self.visit(node.target, t)
        return node._replace(target=target, other=other)
    
    visit_RCSetRefUpdate = visit_SetUpdate
    
    # Expressions.
    
    # Expression and operands are bools.
    def visit_BoolOp(self, node, ctxtype=toptype):
        values = [self.visit(v, booltype) for v in node.values]
        return node._replace(values=values, type=booltype)
    
    # Expression and operands are numbers.
    def visit_BinOp(self, node, ctxtype=toptype):
        left = self.visit(node.left, numbertype)
        right = self.visit(node.right, numbertype)
        return node._replace(left=left, right=right, type=numbertype)
    
    # Boolean if "not", otherwise numerical.
    # Expression and operand are same type.
    def visit_UnaryOp(self, node, ctxtype=toptype):
        if isinstance(node.op, Not):
            t = booltype
        else:
            t = numbertype
        operand = self.visit(node.operand, t)
        return node._replace(operand=operand, type=t)
    
    # No type info.
    def visit_Lambda(self, node, ctxtype=toptype):
        return self.generic_visit(node)
    
    # Expression is the same as the type of the two branches,
    # or None if they disagree. No propagation is done between
    # the branches. The condition is a bool.
    def visit_IfExp(self, node, ctxtype=toptype):
        test = self.visit(node.test, booltype)
        body = self.visit(node.body, ctxtype)
        orelse = self.visit(node.orelse, ctxtype)
        t = toptype.unify(body.type, orelse.type)
        return node._replace(test=test, body=body, orelse=orelse, type=t)
    
    # A set literal has set type {E} where E is the type of all
    # the elements. E is None if the elements are heterogeneously
    # typed.
    #
    # The same pattern is applied analogously to other literals.
    #
    # Comprehensions have their collection type, except that
    # generators have no type.
    
    def visit_Dict(self, node, ctxtype=toptype):
        # Get the context key/value types and recurse.
        ckt = cvt = toptype
        if isinstance(ctxtype, DictType):
            ckt, cvt = ctxtype
        keys = [self.visit(k, ckt) for k in node.keys]
        values = [self.visit(v, cvt) for v in node.values]
        # Get the actual inferred key/value types.
        t = DictType(ckt.unify(*(k.type for k in keys)),
                     cvt.unify(*(v.type for v in values)))
        t = t.unify(ctxtype)
        return node._replace(keys=keys, values=values, type=t)
    
    def seq_helper(self, node, ctxtype, seqtype):
        """Helper for homogenously typed sequences."""
        cet = toptype
        if isinstance(ctxtype, seqtype):
            cet, = ctxtype
        elts = [self.visit(e, cet) for e in node.elts]
        t = seqtype(cet.unify(*(e.type for e in elts)))
        t = t.unify(ctxtype)
        return node._replace(elts=elts, type=t)
    
    def visit_Set(self, node, ctxtype=toptype):
        return self.seq_helper(node, toptype, SetType)
    
    def seqcomp_helper(self, node, ctxtype, seqtype):
        """Helper for sequence comprehensions."""
        cet = toptype
        if isinstance(ctxtype, seqtype):
            cet, = ctxtype
        elt = self.visit(node.elt, cet)
        generators = self.visit(node.generators)
        t = seqtype(elt.type)
        t = t.unify(ctxtype)
        return node._replace(elt=elt, generators=generators, type=t)
    
    def visit_ListComp(self, node, ctxtype=toptype):
        return self.seqcomp_helper(node, ctxtype, ListType)
    
    def visit_SetComp(self, node, ctxtype=toptype):
        return self.seqcomp_helper(node, ctxtype, SetType)
    
    def visit_DictComp(self, node, ctxtype=toptype):
        ckt = cvt = toptype
        if isinstance(ctxtype, DictType):
            ckt, cvt = ctxtype
        key = self.visit(node.key, vkt)
        value = self.visit(node.value, cvt)
        generators = self.visit(node.generators)
        t = DictType(key.type, value.type)
        t = t.unify(ctxtype)
        return node._replace(key=key, value=value,
                             generators=generators, type=t)
    
    # No type info.
    def visit_GeneratorExp(self, node, ctxtype=toptype):
        return self.generic_visit(node)
    
    def visit_Yield(self, node, ctxtype=toptype):
        node = self.generic_visit(node, ctxtype)
        return node._replace(type=node.value.type)
    
    def visit_YieldFrom(self, node, ctxtype=toptype):
        node = self.generic_visit(node, ctxtype)
        return node._replace(type=node.value.type)
    
    # Comparison operators have boolean type.
    def visit_Compare(self, node, ctxtype=toptype):
        ### TODO: Add context type passing based on what
        ### operator is used.
        node = self.generic_visit(node)
        t = ctxtype.unify(booltype)
        return node._replace(type=t)
    
    ### TODO: Special case
    def visit_Call(self, node, ctxtype=toptype):
        node = self.generic_visit(node)
        return node._replace(type=toptype)
    
    def visit_Num(self, node, ctxtype=toptype):
        t = ctxtype.unify(numbertype)
        return node._replace(type=t)
    
    def visit_Str(self, node, ctxtype=toptype):
        t = ctxtype.unify(strtype)
        return node._replace(type=t)
    
    # Untyped.
    def visit_Bytes(self, node, ctxtype=toptype):
        return node
    
    # True/False are booleans, None itself is untyped.
    def visit_NameConstant(self, node, ctxtype=toptype):
        node = self.generic_visit(node)
        if node.value in [True, False]:
            t = booltype
        elif node.value is None:
            t = toptype
        else:
            assert()
        t = t.unify(ctxtype)
        return node._replace(type=t)
    
    # Untyped.
    def visit_Ellipsis(self, node, ctxtype=toptype):
        return self.generic_visit(node)
    
    # The object must either have top type or else have the type
    # of an object that defines the requested attribute.
    def visit_Attribute(self, node, ctxtype=toptype):
        ### TODO: Special cases for methods, e.g. ".elements()".
        
        # We can't generate the object type from its attribute type,
        # so no context info to pass along.
        value = self.visit(node.value)
        vt = value.type
        if vt is toptype:
            t = toptype
        elif isinstance(vt, ObjType):
            attrs = self.objtypes[vt.name]
            t = attrs.get(node.attr, bottomtype)
        else:
            t = bottomtype
        t = t.unify(ctxtype)
        return node._replace(value=value, type=t)
    
    # Subscripting a list or dict gives the element or value
    # type respectively. Subscripting a tuple where the index
    # is an integer constant gives the element type.
    # Subscripting top gives top. Anything else is bottom.
    def visit_Subscript(self, node, ctxtype=toptype):
        # We can't generate the list/dict type from its
        # element/value type, so no context info to pass along.
        value = self.visit(node.value)
        slice = self.visit(node.slice)
        vt = value.type
        if isinstance(vt, ListType):
            t = vt.et
        elif isinstance(vt, DictType):
            t = vt.vt
        elif isinstance(vt, TupleType):
            if isinstance(slice, Index) and isinstance(slice.value, Num):
                if 0 <= slice.value.n < len(vt.ets):
                    t = vt.ets[slice.value.n]
        elif vt is toptype:
            t = toptype
        else:
            t = bottomtype
        t = t.unify(ctxtype)
        return node._replace(value=value, slice=slice, type=t)
    
    def visit_Starred(self, node, ctxtype=toptype):
        node = self.generic_visit(node, ctxtype)
        return node._replace(type=node.value.type)
    
    def visit_Name(self, node, ctxtype=toptype):
        node = self.generic_visit(node)
        t = self.vartypes.get(node.id, toptype)
        t = t.unify(ctxtype)
        self.vartypes[node.id] = t
        return node._replace(type=t)
    
    def visit_List(self, node, ctxtype=toptype):
        return self.seq_helper(node, toptype, ListType)
    
    def visit_Tuple(self, node, ctxtype=toptype):
        # Can't use seq_helper() because tuples are
        # hetereogenously typed.
        nelems = len(node.elts)
        cets = [toptype] * nelems
        if isinstance(ctxtype, TupleType) and len(ctxtype.ets) == nelems:
            cets = ctxtype.ets
        elts = [self.visit(e, cet) for e, cet in zip(node.elts, cets)]
        t = TupleType([elt.type for elt in elts])
        t = t.unify(ctxtype)
        return node._replace(elts=elts, type=t)
    
    # IncAST nodes follow.
    
    def visit_IsEmpty(self, node, ctxtype=toptype):
        target = self.visit(node.target, SetType(toptype))
        t = ctxtype.unify(booltype)
        return node._replace(target=target, type=t)
    
    def visit_GetRef(self, node, ctxtype=toptype):
        target = self.visit(node.target, SetType(toptype))
        elem = self.visit(node.elem)
        t = ctxtype.unify(numbertype)
        return node._replace(target=target, elem=elem, type=t)
    
    def visit_Lookup(self, node, ctxtype=toptype):
        target = self.visit(node.target, DictType(toptype, ctxtype))
        key = self.visit(node.key)
        default = self.visit(node.default, ctxtype)
        t = ctxtype.unify(default.type)
        return node._replace(target=target, key=key, default=default, type=t)
    
    def visit_ImgLookup(self, node, ctxtype=toptype):
        t = ctxtype.unify(SetType(toptype))
        key = self.visit(node.key)
        target = self.visit(node.target, DictType(key.type, t))
        if (isinstance(target.type, DictType) and
            isinstance(target.type.vt, SetType)):
            t = t.unify(target.type.vt.et)
        return node._replace(target=target, key=key, type=t)
    
    visit_RCImgLookup = visit_ImgLookup
    
    def visit_SMLookup(self, node, ctxtype=toptype):
        t = ctxtype
        key = self.visit(node.key)
        target = self.visit(node.target, SetType(t))
        if (isinstance(target.type, DictType) and
            isinstance(target.type.vt, SetType)):
            t = t.unify(target.type.vt.et)
        return node._replace(target=target, key=key, type=t)
    
    def visit_DemQuery(self, node, ctxtype=toptype):
        args = self.visit(node.args)
        value = self.visit(node.value, ctxtype)
        t = ctxtype.unify(value.type)
        return node._replace(args=args, value=value, type=t)
    
    def visit_NoDemQuery(self, node, ctxtype=toptype):
        return self.generic_visit(node, ctxtype)
    
    def visit_Instr(self, node, ctxtype=toptype):
        value = self.visit(node.value, ctxtype)
        expvalue = self.visit(node.value, value.type)
        t = ctxtype.unify(value.type, expvalue.type)
        return node._replace(value=value, expvalue=expvalue, type=t)
        
    def visit_SetMatch(self, node, ctxtype=toptype):
        t = ctxtype.unify(SetType(toptype))
        key = self.visit(node.key)
        target = self.visit(node.target, t)
        return node._replace(target=target, key=key, type=t)
    
    def visit_DeltaMatch(self, node, ctxtype=toptype):
        t = ctxtype.unify(SetType(toptype))
        elem = self.visit(node.elem)
        target = self.visit(node.target, t)
        return node._replace(target=target, elem=elem, type=t)
    
    def visit_Enumerator(self, node, ctxtype=toptype):
        iter = self.visit(node.iter)
        it = iter.type
        tt = toptype
        if isinstance(it, SetType):
            tt = it.et
        target = self.visit(node.target, tt)
        return node._replace(target=target, iter=iter)
    
    def visit_Comp(self, node, ctxtype=toptype):
        cet = toptype
        if isinstance(ctxtype, SetType):
            cet, = ctxtype
        clauses = ()
        for cl in node.clauses:
            t = booltype if isinstance(cl, expr) else toptype
            cl = self.visit(cl, t)
            clauses += (cl,)
        resexp = self.visit(node.resexp, cet)
        t = ctxtype.unify(resexp.type)
        return node._replace(resexp=resexp, clauses=clauses, type=t)
    
    def visit_Aggregate(self, node, ctxtype=toptype):
        if node.op == 'count':
            t = numbertype
            at = toptype
        elif node.op == 'sum':
            t = at = numbertype
        elif node.op in ['min', 'max']:
            t = ctxtype
            at = SetType(t)
        else:
            assert()
        value = self.visit(node.value, at)
        t = t.unify(ctxtype)
        if node.op in ['min', 'max'] and isinstance(value.type, SetType):
            t = t.unify(value.type.et)
        return node._replace(value=value, type=t)

def analyze_types(tree, vartypes=None, objtypes=None):
    changed = True
    count = 0
    while changed and count < 10:
        oldtree = tree
        tree, vartypes = TypeAnnotator.run(tree, vartypes, objtypes)
        changed = oldtree != tree
        count += 1
    print('Iterated type analysis {} times'.format(count))
    return tree, vartypes
