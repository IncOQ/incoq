"""Type analysis."""


__all__ = [
    'TypedUnparser',
    'unparse_structast_typed',
    'TypeAnnotator',
]


from numbers import Number

from invinc.util.collections import frozendict

from .nodes import expr, Not
from .structconv import AdvNodeTransformer, Unparser, export_structast


def strtype(t):
    if t is None:
        return 'None'
    elif isinstance(t, type):
        return t.__name__
    elif isinstance(t, tuple):
        if t[0] is object:
            return '{' + ', '.join('{}: {}'.format(attr, strtype(attrtype))
                                   for attr, attrtype in t[1].items()) + '}'
        else:
            return '(' + ', '.join(strtype(t2) for t2 in t) + ')'
    else:
        assert()

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
            self.write(' : ' + strtype(tree.type) + ')')

def unparse_structast_typed(tree):
    """As structconv.unparse_structast(), but with type info."""
    return TypedUnparser.to_source(tree)


def typeof(exprs):
    """Given a sequence of expressions, return their common type
    or None if they are heterogenously typed.
    """
    assert len(exprs) > 0
    t = exprs[0].type
    if not all(e.type == t for e in exprs):
        t = None
    return t

def picktype(t1, t2):
    """If two types are equal, return the type. If one is None,
    return the other. If they disagree and are both non-None,
    return None.
    
    For composite types, if they agree on the functor symbol
    (first tuple component), return the type obtained by applying
    this rule to each component.
    """
    if t1 == t2:
        return t1
    elif t1 is None:
        return t2
    elif t2 is None:
        return t1
    elif isinstance(t1, tuple) and isinstance(t2, tuple) and t1[0] == t2[0]:
        assert len(t1) == len(t2)
        return (t1[0],) + tuple(picktype(u1, u2) for u1, u2 in zip(t1, t2))
    else:
        return None

class TypeAnnotator(AdvNodeTransformer):
    
    """Add type information to all expression nodes where possible.
    
    First process the subtree. If all children are well-typed, try
    to type this node as well. Use None to indicate no type information
    or not-well-typed.
    """
    
    def __init__(self, annotations=None):
        super().__init__()
        if annotations is None:
            annotations = {}
        self.annotations = annotations
    
    # Expression and operands are bools.
    def visit_BoolOp(self, node, ctxtype=None):
        values = [self.visit(v, bool) for v in node.values]
        return node._replace(values=values, type=bool)
    
    # Expression and operands are numbers.
    def visit_BinOp(self, node, ctxtype=None):
        left = self.visit(node.left, Number)
        right = self.visit(node.right, Number)
        return node._replace(left=left, right=right, type=Number)
    
    # Boolean if "not", otherwise numerical.
    # Expression and operand are same type.
    def visit_UnaryOp(self, node, ctxtype=None):
        if isinstance(node.op, Not):
            t = bool
        else:
            t = Number
        operand = self.visit(node.operand, t)
        return node._replace(operand=operand, type=t)
    
    # No type info.
    def visit_Lambda(self, node, ctxtype=None):
        node = self.generic_visit(node)
        return node._replace(type=None)
    
    # Expression is the same as the type of the two branches,
    # or None if they disagree. No propagation is done between
    # the branches. The condition is a bool.
    def visit_IfExp(self, node, ctxtype=None):
        test = self.visit(node.test, bool)
        body = self.visit(node.body)
        orelse = self.visit(node.orelse)
        t = picktype(body.type, orelse.type)
        return node._replace(test=test, body=body, orelse=orelse, type=t)
    
    # A set literal has set type {E} where E is the type of all
    # the elements. E is None if the elements are heterogeneously
    # typed.
    #
    # The same pattern is applied analogously to other literals.
    #
    # Comprehensions have their collection type, except that
    # generators have no type.
    
    def visit_Dict(self, node, ctxtype=None):
        # Get the context key/value types and recurse.
        if isinstance(ctxtype, tuple) and ctxtype[0] is dict:
            _, ckt, cvt = ctxtype
        else:
            ckt = cvt = None
        keys = [self.visit(k, ckt) for k in node.keys]
        values = [self.visit(v, cvt) for v in node.values]
        # Get the actual inferred key/value types.
        t = (dict, typeof(keys), typeof(values))
        # Get agreed-upon type.
        t = picktype(ctxtype, t)
        return node._replace(keys=keys, values=values, type=t)
    
    def visit_Set(self, node, ctxtype=None):
        if isinstance(ctxtype, tuple) and ctxtype[0] is set:
            _, cet = ctxtype
        else:
            cet = None
        elts = [self.visit(e, cet) for e in node.elts]
        t = (set, typeof(elts))
        t = picktype(ctxtype, t)
        return node._replace(elts=elts, type=t)
    
    def visit_ListComp(self, node, ctxtype=None):
        if isinstance(ctxtype, tuple) and ctxtype[0] is list:
            _, cet = ctxtype
        else:
            cet = None
        elt = self.visit(node.elt, cet)
        generators = self.visit(node.generators)
        t = (list, elt.type)
        t = picktype(ctxtype, t)
        return node._replace(elt=elt, generators=generators, type=t)
    
    def visit_SetComp(self, node, ctxtype=None):
        if isinstance(ctxtype, tuple) and ctxtype[0] is set:
            _, cet = ctxtype
        else:
            cet = None
        elt = self.visit(node.elt, cet)
        generators = self.visit(node.generators)
        t = (set, elt.type)
        t = picktype(ctxtype, t)
        return node._replace(elt=elt, generators=generators, type=t)
    
    def visit_DictComp(self, node, ctxtype=None):
        if isinstance(ctxtype, tuple) and ctxtype[0] is dict:
            _, ckt, cvt = ctxtype
        else:
            ckt = cvt = None
        key = self.visit(node.key, ckt)
        value = self.visit(node.value, cvt)
        generators = self.visit(node.generators)
        t = (dict, key.type, value.type)
        t = picktype(ctxtype, t)
        return node._replace(key=key, value=value,
                             generators=generators, type=t)
    
    # No type info.
    def visit_GeneratorExp(self, node, ctxtype=None):
        node = self.generic_visit(node)
        return node._replace(type=None)
    
    def visit_Yield(self, node, ctxtype=None):
        node = self.generic_visit(node, ctxtype)
        return node._replace(type=node.value)
    
    def visit_YieldFrom(self, node, ctxtype=None):
        node = self.generic_visit(node, ctxtype)
        return node._replace(type=node.value)
    
    # Comparison operators have boolean type.
    def visit_Compare(self, node, ctxtype=None):
        ### TODO: Add context type passing based on what
        ### operator is used.
        node = self.generic_visit(node)
        t = picktype(ctxtype, bool)
        return node._replace(type=t)
    
    ### TODO: Special case
    def visit_Call(self, node, ctxtype=None):
        node = self.generic_visit(node)
        return node._replace(type=None)
    
    def visit_Num(self, node, ctxtype=None):
        t = picktype(ctxtype, Number)
        return node._replace(type=t)
    
    def visit_Str(self, node, ctxtype=None):
        node = self.generic_visit(node)
        t = picktype(ctxtype, str)
        return node._replace(type=t)
    
    # Untyped.
    def visit_Bytes(self, node, ctxtype=None):
        node = self.generic_visit(node)
        return node._replace(type=None)
    
    # True/False are booleans, None itself is untyped.
    def visit_NameConstant(self, node, ctxtype=None):
        node = self.generic_visit(node)
        if node.value in [True, False]:
            t = bool
        elif node.value is None:
            t = None
        else:
            assert()
        t = picktype(ctxtype, t)
        return node._replace(type=t)
    
    # Untyped.
    def visit_Ellipsis(self, node, ctxtype=None):
        node = self.generic_visit(node)
        return node._replace(type=None)
    
    def visit_Attribute(self, node, ctxtype=None):
        # We can't generate the object type from its attribute type,
        # so no context info to pass along.
        value = self.visit(node.value)
        vt = value.type
        if isinstance(vt, tuple) and vt[0] is object:
            t = vt[1].get(node.attr, None)
        else:
            t = None
        t = picktype(ctxtype, t)
        return node._replace(value=value, type=t)
    
    # Subscripting a list gives the element type, subscripting
    # a dict gives the value type, and anything else is unknown.
    def visit_Subscript(self, node, ctxtype=None):
        # We can't generate the list/dict type from its
        # element/value type, so no context info to pass along.
        value = self.visit(node.value)
        vt = value.type
        if isinstance(vt, tuple) and vt[0] is list:
            t = vt[1]
        elif isinstance(vt, tuple) and vt[0] is dict:
            t = vt[2]
        else:
            t = None
        t = picktype(t, ctxtype)
        return node._replace(value=value, type=t)
    
    def visit_Starred(self, node, ctxtype=None):
        node = self.generic_visit(node, ctxtype)
        return node._replace(type=node.value.type)
    
    def visit_Name(self, node, ctxtype=None):
        node = self.generic_visit(node)
        t = self.annotations.get(node.id, None)
        t = picktype(ctxtype, t)
        return node._replace(type=t)
    
    def visit_List(self, node, ctxtype=None):
        if isinstance(ctxtype, tuple) and ctxtype[0] is list:
            _, cet = ctxtype
        else:
            cet = None
        elts = [self.visit(e, cet) for e in node.elts]
        t = (list, typeof(elts))
        t = picktype(ctxtype, t)
        return node._replace(elts=elts, type=t)
    
    def visit_Tuple(self, node, ctxtype=None):
        if isinstance(ctxtype, tuple) and ctxtype[0] is tuple:
            _, cet = ctxtype
        else:
            cet = None
        elts = [self.visit(e, cet) for e in node.elts]
        t = (tuple,) + tuple(e.type for e in elts)
        t = picktype(ctxtype, t)
        return node._replace(elts=elts, type=t)
