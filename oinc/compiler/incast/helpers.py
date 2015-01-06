"""Utility functions for specific AST construction and pattern-matching
operations.
"""


__all__ = [
    'ln',
    'sn',
    'dn',
    'tuplify',
    'cmp',
    'cmpin',
    'cmpnotin',
    'cmpeq',
    'cmpnoteq',
    'plainfuncdef',
    'get_plainfuncdef',
    'is_plainfuncdef',
    
    'get_varassign',
    'is_varassign',
    'get_vartuple',
    'is_vartuple',
    'get_name',
    'is_name',
    'get_cmp',
    'is_cmp',
    'get_vareqcmp',
    'is_vareqcmp',
    'get_singletonset',
    'is_singletonset',
    'get_singadd',
    'is_singadd',
    'get_singsub',
    'is_singsub',
    'get_namematch',
    'is_namematch',
    'get_namesmlookup',
    'is_namesmlookup',
    'get_attrassign',
    'is_attrassign',
    'get_delattr',
    'is_delattr',
    'get_mapassign',
    'is_mapassign',
    'get_delmap',
    'is_delmap',
    'get_importstar',
    'is_importstar',
    'get_setunion',
    'is_setunion',
    'get_plaincall',
    'is_plaincall',
]


from functools import partial, wraps
from iast import trim
from simplestruct.type import checktype, checktype_seq

from .nodes import *
from .structconv import NodeVisitor


# Construction helpers.


def ln(id):
    checktype(id, str)
    return Name(id, Load())

def sn(id):
    checktype(id, str)
    return Name(id, Store())

def dn(id):
    checktype(id, str)
    return Name(id, Del())


def tuplify(components, lval=False):
    """Wrap a sequence of components in a Tuple node.
    
    Each component may be either an AST expression node or an
    identifier that gets preprocessed into a Name node.
    
    The Tuple and Name nodes are created with Load context if lval is
    False and Store context if lval is True.
    
    If there is exactly one component, it is returned rather than
    a singleton Tuple wrapping it.
    
    If there are zero components, then an empty Tuple is returned if
    lval is False and a wildcard Name is returned if lval is True.
    (This is because an empty Tuple is syntactically invalid in Store
    context, e.g. "for () in S" is not allowed.)
    """
    ctxcls = Store if lval else Load
    
    orig, components = components, []
    for comp in orig:
        if isinstance(comp, str):
            components.append(Name(comp, ctxcls()))
        else:
            components.append(comp)
    components = tuple(components)
    checktype_seq(components, AST)
    
    if len(components) == 0 and lval:
        return Name('_', Store())
    elif len(components) == 1:
        return components[0]
    else:
        return Tuple(components, ctxcls())


def cmp(left, op, right):
    """Comparison with only two operands."""
    checktype(left, AST)
    checktype(op, AST)
    checktype(right, AST)
    
    return Compare(left, (op,), (right,))

def cmp_(left, right, op_kind):
    """Helper for cmp*."""
    return cmp(left, op_kind(), right)

cmpin = partial(cmp_, op_kind=In)
cmpnotin = partial(cmp_, op_kind=NotIn)
cmpeq = partial(cmp_, op_kind=Eq)
cmpnoteq = partial(cmp_, op_kind=NotEq)

def plainfuncdef(name, argnames, body):
    """FunctionDef with no fancy arguments. Wrapped in a tuple
    (i.e., code, not stmt).
    """
    processed_args = tuple(arg(a, None) for a in argnames)
    processed_arguments = arguments(processed_args, None, (),
                                    (), None, ())
    funcdef = FunctionDef(name, processed_arguments, body, (), None)
    return (funcdef,)

def get_plainfuncdef(func):
    """Return the name, tuple of arg names, and body of a plain
    function definition.
    """
    if not is_plainfuncdef(func):
        raise TypeError
    
    args = tuple(a.arg for a in func.args.args)
    return (func.name, args, func.body)

def is_plainfuncdef(func):
    """Returns True if the function has no fancy arguments.
    (Note that func is a FunctionDef statement, not code.
    """
    checktype(func, FunctionDef)
    plain_args = tuple(arg(a.arg, None) for a in func.args.args)
    plain_arguments = arguments(plain_args, None, (),
                                (), None, ())
    return func.args == plain_arguments


# Pattern helpers.


def isify(func):
    """Autogenerate the "is_" functions."""
    @wraps(func)
    def f(node):
        try:
            func(node)
            return True
        except TypeError:
            return False
    
    f.__doc__ = trim(
        """
        Returns True if node fits the form matched by {},
        False otherwise.
        """.format(func.__name__))
    
    return f

def get_varassign(node):
    """Match an Assign node of form
    
        <Name> = <value>
    
    and return Name.id and value.
    """
    checktype(node, AST)
    
    if (isinstance(node, Assign) and
        len(node.targets) == 1 and
        isinstance(node.targets[0], Name)):
        return node.targets[0].id, node.value
    
    from . import ts
    raise TypeError('get_varassign failed: ' + ts(node))

is_varassign = isify(get_varassign)

def get_vartuple(node):
    """Match a Name or Tuple of Names and return a tuple of the
    identifiers.
    """
    checktype(node, AST)
    
    if isinstance(node, Name):
        return (node.id,)
    elif (isinstance(node, Tuple) and
          all(isinstance(item, Name) for item in node.elts)):
        return tuple(item.id for item in node.elts)
    
    from . import ts
    raise TypeError('get_vartuple failed: ' + ts(node))

is_vartuple = isify(get_vartuple)

def get_name(node):
    """Match a Name node and return the identifier."""
    checktype(node, AST)
    
    if isinstance(node, Name):
        return node.id
    
    from . import ts
    raise TypeError('get_name failed: ' + ts(node))

is_name = isify(get_name)

def get_cmp(node):
    """Match a Compare node of two operands, and return a triple
    of the first operand, the operation, and the second operand.
    """
    checktype(node, AST)
    
    if (isinstance(node, Compare) and
        len(node.ops) == len(node.comparators) == 1):
        return node.left, node.ops[0], node.comparators[0]
    
    from . import ts
    raise TypeError('get_cmp failed: ' + ts(node))

is_cmp = isify(get_cmp)

def get_vareqcmp(node):
    """Match a Compare node of form
    
        <Name 1> == <Name 2> == ... == <Name n>
    
    and return a tuple of the identifiers.
    """
    checktype(node, AST)
    
    if (isinstance(node, Compare) and
        all(isinstance(op, Eq) for op in node.ops) and
        isinstance(node.left, Name) and
        all(isinstance(c, Name) for c in node.comparators)):
        return (node.left.id,) + tuple(c.id for c in node.comparators)
    
    from . import ts
    raise TypeError('get_vareqcmp failed: ' + ts(node))

is_vareqcmp = isify(get_vareqcmp)

def get_singletonset(node):
    """Match a singleton set, i.e.
    
        {val}
    
    and return val.
    """
    checktype(node, AST)
    
    if isinstance(node, Set) and len(node.elts) == 1:
        return node.elts[0]
    
    from . import ts
    raise TypeError('get_singletonset failed: ' + ts(node))

is_singletonset = isify(get_singletonset)

def get_singadd(node):
    """Match a singleton set added to an expression, i.e.
    
        <expr1> + {<expr2>}
    
    and return the two expressions.
    """
    checktype(node, AST)
    
    if (isinstance(node, BinOp) and
        isinstance(node.op, Add) and
        isinstance(node.right, Set) and
        len(node.right.elts) == 1):
        return node.left, node.right.elts[0]
    
    from . import ts
    raise TypeError('get_singsub failed: ' + ts(node))

is_singadd = isify(get_singadd)

def get_singsub(node):
    """Match a singleton set subtracted from an expression, i.e.
    
        <expr1> - {<expr2>}
    
    and return the two expressions.
    """
    checktype(node, AST)
    
    if (isinstance(node, BinOp) and
        isinstance(node.op, Sub) and
        isinstance(node.right, Set) and
        len(node.right.elts) == 1):
        return node.left, node.right.elts[0]
    
    from . import ts
    raise TypeError('get_singsub failed: ' + ts(node))

is_singsub = isify(get_singsub)

def get_namematch(node):
    """Match a SetMatch over a Name, and return a triple of the name,
    mask, and key.
    """
    checktype(node, SetMatch)
    
    if isinstance(node.target, Name):
        return (node.target.id, node.mask, node.key)
    
    from . import ts
    raise TypeError('get_namematch failed: ' + ts(node))

is_namematch = isify(get_namematch)

def get_namesmlookup(node):
    """Match a SMLookup node over a name, and return a triple of the
    name, mask, and key.
    """
    checktype(node, SMLookup)
    
    if isinstance(node.target, Name):
        return (node.target.id, node.mask, node.key)
    
    from . import ts
    raise TypeError('get_namesmlookup failed: ' + ts(node))

is_namesmlookup = isify(get_namesmlookup)

def get_attrassign(node):
    """Match an Assign node of form
    
        <alpha>.<attr> = <value>
    
    and returns alpha, attr, and value.
    """
    checktype(node, AST)
    
    if (isinstance(node, Assign) and
        len(node.targets) == 1 and
        isinstance(node.targets[0], Attribute)):
        return node.targets[0].value, node.targets[0].attr, node.value
    
    from . import ts
    raise TypeError('get_attrassign failed: ' + ts(node))

is_attrassign = isify(get_attrassign)

def get_delattr(node):
    """Match a Delete node of form
    
        del <alpha>.<attr>
    
    and return alpha and attr.
    """
    checktype(node, AST)
    
    if (isinstance(node, Delete) and
        len(node.targets) == 1 and
        isinstance(node.targets[0], Attribute)):
        return node.targets[0].value, node.targets[0].attr
    
    from . import ts
    raise TypeError('get_delattr failed: ' + ts(node))

is_delattr = isify(get_delattr)

def get_mapassign(node):
    """Match an Assign node of form
    
        <alpha>[<beta>] = <value>
    
    and returns alpha, beta, and value.
    """
    checktype(node, AST)
    
    if (isinstance(node, Assign) and
        len(node.targets) == 1 and
        isinstance(node.targets[0], Subscript) and
        isinstance(node.targets[0].slice, Index)):
        return node.targets[0].value, node.targets[0].slice.value, node.value
    
    from . import ts
    raise TypeError('get_mapassign failed: ' + ts(node))

is_mapassign = isify(get_mapassign)

def get_delmap(node):
    """Match a Delete node of form
    
        del <alpha>[<beta>]
    
    and return alpha and beta.
    """
    checktype(node, AST)
    
    if (isinstance(node, Delete) and
        len(node.targets) == 1 and
        isinstance(node.targets[0], Subscript) and
        isinstance(node.targets[0].slice, Index)):
        return node.targets[0].value, node.targets[0].slice.value
    
    from . import ts
    raise TypeError('get_delmap failed: ' + ts(node))

is_delmap = isify(get_delmap)

def get_importstar(node):
    """Match an import statement of form
    
        from <mod> import *
    
    and return mod.
    """
    checktype(node, AST)
    
    if (isinstance(node, ImportFrom) and
        len(node.names) == 1 and
        node.names[0].name == '*' and
        node.level == 0):
        return node.module
    
    from . import ts
    raise TypeError('get_importstar failed: ' + ts(node))

is_importstar = isify(get_importstar)

def get_setunion(node):
    """Match a union of set literals, set comprehensions, and names,
    and return a tuple of the individual set expression ASTs.
    """
    checktype(node, AST)
    
    class Flattener(NodeVisitor):
        
        # BinOp nodes are tree-structured. Flatten the tree.
        
        class Failure(BaseException):
            pass
        
        def process(self, tree):
            self.parts = []
            super().process(tree)
            return tuple(self.parts)
        
        def visit_BinOp(self, node):
            if not isinstance(node.op, BitOr):
                raise self.Failure
            self.visit(node.left)
            self.visit(node.right)
        
        def generic_visit(self, node):
            # Don't recurse. Just add this node as an operand.
            self.parts.append(node)
    
    try:
        parts = Flattener.run(node)
        if all(isinstance(p, (Set, Comp, Name))
               for p in parts):
            return parts
    except Flattener.Failure:
        pass
    
    from . import ts
    raise TypeError('get_setunion failed: ' + ts(node))

is_setunion = isify(get_setunion)

def get_plaincall(node):
    """Match a call of a Name node with only positional arguments.
    Return the function name and a tuple of the argument expressions.
    """
    checktype(node, AST)
    
    if (isinstance(node, Call) and
        isinstance(node.func, Name) and
        node.keywords == () and
        node.starargs is None and
        node.kwargs is None):
        return node.func.id, node.args
    
    from . import ts
    raise TypeError('get_importstar failed: ' + ts(node))

is_plaincall = isify(get_plaincall)
