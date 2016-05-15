"""Base tools for manipulating IncAST trees."""


__all__ = [
    'literal_unparse',
    'IdentFinder',
    'BindingFinder',
    'Templater',
    'MacroExpander',
    'tree_size',
    'rewrite_comp',
]


from functools import partial
from numbers import Number

from incoq.util.collections import OrderedSet, frozendict

from . import nodes as L


def literal_unparse(value):
    """Given a value, return its unparsed AST representation. The value
    may consist of lists, sets, dictionaries, tuples, frozensets,
    frozendicts, numbers, strings, and singletons (True/False/None).
    Frozendicts and frozensets are converted to dicts and sets, even
    when the resulting value would not be nestable due to unhashability.
    """
    un = literal_unparse
    if isinstance(value, list):
        tree = L.List([un(e) for e in value])
    elif isinstance(value, (set, frozenset)):
        tree = L.Set([un(e) for e in value])
    elif isinstance(value, (dict, frozendict)):
        items = value.items()
        tree = L.Dict([un(k) for k, _v in items],
                      [un(v) for _k, v in items])
    elif isinstance(value, tuple):
        tree = L.Tuple([un(e) for e in value])
    elif isinstance(value, str):
        tree = L.Str(value)
    elif value is True or value is False or value is None:
        # Must use identity comparison because 1 == True but 1 is not True.
        tree = L.NameConstant(value)
    elif isinstance(value, Number):
        # Must be last because True/False are numbers.
        tree = L.Num(value)
    return tree


class IdentFinder(L.NodeVisitor):
    
    """Return an OrderedSet of all identifiers in the specified
    contexts.
    """
    
    fun_ctxs = ('Fun.name', 'Call.func')
    query_ctxs = ('Query.name', 'ResetDemand.names')
    rel_ctxs = ('RelUpdate.rel', 'RelClear.rel', 'RelMember.rel')
    
    @classmethod
    def find_functions(cls, tree):
        return cls().run(tree, contexts=cls.fun_ctxs)
    
    @classmethod
    def find_vars(cls, tree):
        ctxs = (cls.fun_ctxs + cls.query_ctxs)
        return cls().run(tree, contexts=ctxs, invert=True)
    
    @classmethod
    def find_non_rel_uses(cls, tree):
        ctxs = (cls.fun_ctxs + cls.query_ctxs + cls.rel_ctxs)
        return cls().run(tree, contexts=ctxs, invert=True)
    
    def __init__(self, contexts=None, invert=False):
        if contexts is not None:
            for c in contexts:
                node_name, field_name = c.split('.')
                if not field_name in L.ident_fields.get(node_name, []):
                    raise ValueError('Unknown identifier context "{}"'
                                     .format(c))
        
        self.contexts = contexts
        """Collection of contexts to include/exclude. Each context is
        a string of the form '<node type name>.<field name>'. A value
        of None is equivalent to specifying all contexts.
        """
        self.invert = bool(invert)
        """If True, find identifiers that occur in any context besides
        the ones given.
        """
    
    def process(self, tree):
        self.names = OrderedSet()
        super().process(tree)
        return self.names
    
    def generic_visit(self, node):
        super().generic_visit(node)
        clsname = node.__class__.__name__
        id_fields = L.ident_fields.get(clsname, [])
        for f in id_fields:
            inctx = (self.contexts is None or
                     clsname + '.' + f in self.contexts)
            if inctx != self.invert:
                # Normalize for either one id or a sequence of ids.
                ids = getattr(node, f)
                if isinstance(ids, str):
                    ids = [ids]
                if ids is not None:
                    self.names.update(ids)


class BindingFinder(L.NodeVisitor):
    
    """Return names of variables that appear in a binding context, i.e.,
    that would have a Store context in Python's AST.
    """
    
    def process(self, tree):
        self.vars = OrderedSet()
        self.write_ctx = False
        super().process(tree)
        return self.vars
    
    def visit_Fun(self, node):
        self.vars.update(node.args)
        self.generic_visit(node)
    
    def visit_For(self, node):
        self.vars.add(node.target)
        self.generic_visit(node)
    
    def visit_DecompFor(self, node):
        self.vars.update(node.vars)
        self.generic_visit(node)
    
    def visit_Assign(self, node):
        self.vars.add(node.target)
        self.generic_visit(node)
    
    def visit_DecompAssign(self, node):
        self.vars.update(node.vars)
        self.generic_visit(node)


class Templater(L.NodeTransformer):
    
    """Transformer for instantiating placeholders with different names
    or arbitrary code. Analogous to iast.python.python34.Templater.
    
    The templater takes in a mapping whose keys are strings.
    The following kinds of entries are recognized:
    
        IDENT -> EXPR
          Replace Name nodes having IDENT as their id with an
          arbitrary expression AST.
        
        IDENT1 -> IDENT2
          Replace all occurrences of IDENT1 with IDENT2. This includes
          non-Name occurrences such as attribute identifiers, function
          identifiers, and relation operations.
        
        <c>IDENT -> CODE
          Replace all occurrences of Expr nodes directly containing
          a Name node having IDENT as its id, with the statement or
          sequence of statements CODE.
    
    Template substitution is not recursive, i.e., replacement code
    is used as-is.
    """
    
    def __init__(self, subst):
        super().__init__()
        # Split subst into different mappings for each form of rule.
        self.name_subst = {}
        self.ident_subst = {}
        self.code_subst = {}
        for k, v in subst.items():
            if k.startswith('<c>'):
                suffix = k[len('<c>'):]
                self.code_subst[suffix] = v
            elif isinstance(v, str):
                self.ident_subst[k] = v
            elif isinstance(v, L.expr):
                self.name_subst[k] = v
            else:
                raise TypeError('Bad template mapping: {} -> {}'.format(
                                k, v))
    
    def ident_helper(self, node, field):
        """Apply ident_subst to the given field of the given node,
        where the field is an identifier or sequence of identifiers,
        and return the (possibly new) node.
        """ 
        old = getattr(node, field)
        if isinstance(old, tuple):
            new = tuple(self.ident_subst.get(v, v) for v in old)
        elif isinstance(old, str):
            new = self.ident_subst.get(old, old)
        else:
            assert()
        if new != old:
            node = node._replace(**{field: new})
        return node
    
    def generic_visit(self, node):
        node = super().generic_visit(node)
        id_fields = L.ident_fields.get(node.__class__.__name__, [])
        for f in id_fields:
            node = self.ident_helper(node, f)
        return node
    
    def visit_Name(self, node):
        # Name rule.
        if node.id in self.name_subst:
            node = self.name_subst[node.id]
        # Identifier rule.
        elif node.id in self.ident_subst:
            node = node._replace(id=self.ident_subst[node.id])
        return node
    
    def visit_Expr(self, node):
        # Code rules ("<c>Foo") take precedence over name and
        # identifier rules ("Foo"), so check this case before
        # we recurse.
        if (isinstance(node.value, L.Name) and
            node.value.id in self.code_subst):
            node = self.code_subst[node.value.id]
        else:
            node = self.generic_visit(node)
        return node


class MacroExpander(L.PatternTransformer):
    
    """Transformer for expanding function/method call macros.
    Analogous to iast.python.python34.MacroProcessor.
    
    A call macro is a GeneralCall node that has one of the following
    forms:
    
        <func>(<args>)           (function macro)
        <recv>.<func>(<args>)    (method macro)
    
    where <func> is a Name node or identifier respectively, <recv>
    is an expression AST, and <args> is a list of argument expression
    ASTs. Each of these forms can be either an expression macro or a
    statement macro.
    
    A subclass of MacroExpander defines handler methods with the
    name format and signature
    
        handle_<form>_<func>(self, func, *args)
    
    <form> is one of the strings 'fe', 'fs', 'me', or 'ms' indicating
    whether the handler is for a function or method macro and for an
    expression or statement macro. <func> is the macro's name, i.e.
    the identifier that will be used to find occurrences of the macro.
    
    The handler is called with <func> as its first argument (so the
    same handler can service multiple macros). The remaining arguments
    are the ASTs corresponding to <recv> (for method macros only) and
    each argument in <args>. The handler returns the expression or
    statement AST to substitute for the occurrence of the macro.
    
    Nested macros are processed in a bottom-up order.
    """
    
    func_expr_pattern = L.GeneralCall(L.Name(L.PatVar('_func')),
                                      L.PatVar('_args'))
    
    meth_expr_pattern = L.GeneralCall(L.Attribute(L.PatVar('_recv'),
                                                  L.PatVar('_func')),
                                      L.PatVar('_args'))
    
    func_stmt_pattern = L.Expr(func_expr_pattern)
    
    meth_stmt_pattern = L.Expr(meth_expr_pattern)
    
    def dispatch(self, prefix, *, _recv=None,
                 _func, _args):
        """Dispatcher to a macro handler. prefix is one of the
        macro type strings ('fe', etc.). _recv is the AST of the
        receiver object in the case of method macros. _func is
        a string and _args is a sequence of ASTs.
        """
        handler = getattr(self, prefix + _func, None)
        # No change if pattern does not correspond to any macro.
        if handler is None:
            return
        
        if _recv is not None:
            _args = (_recv,) + _args
        
        return handler(_func, *_args)
    
    def __init__(self):
        super().__init__()
        self.rules = [
            (self.func_expr_pattern,
             partial(self.dispatch, prefix='handle_fe_')),
            (self.func_stmt_pattern,
             partial(self.dispatch, prefix='handle_fs_')),
            (self.meth_expr_pattern,
             partial(self.dispatch, prefix='handle_me_')),
            (self.meth_stmt_pattern,
             partial(self.dispatch, prefix='handle_ms_')),
        ]


class Counter(L.NodeVisitor):
    
    def process(self, tree):
        self.count = 0
        super().process(tree)
        return self.count
    
    def generic_visit(self, node):
        super().generic_visit(node)
        self.count += 1

def tree_size(tree):
    """Return the number of nodes in an AST."""
    return Counter.run(tree)


def rewrite_comp(comp, rewriter, *,
                 member_only=False, recursive=False,
                 resexp=True):
    """Helper for rewriting a Comp node. Rewriter is applied to each
    clause in turn and then to the result expression. Each time it
    is applied to a clause, it returns a triple of the replacement
    clause's AST, and two lists of new clauses to be inserted
    respectively before and after this clause. When it is applied to
    the result expression, the return value is the same, except it is
    an expression AST and the two clause lists are both appended to
    the end of the comprehension's clause list.
    
    If member_only is True, only membership clauses will be processed,
    not condition clauses or the result expression. Separately, if
    resexp is False, the result expression will not be processed.
    
    If recursive is True, the rewriter will also be called on the newly
    inserted clauses as well.
    
    The rewriter may return None to indicate no change.
    """
    assert isinstance(comp, L.Comp)
    
    # Wrap rewriter to handle None case.
    orig_rewriter = rewriter
    def rewriter(clause):
        result = orig_rewriter(clause)
        if result is None:
            return clause, [], []
        else:
            return result
    
    # Use a recursive function to easily handle recursive=True case.
    def process(clauses):
        result = []
        
        for cl in clauses:
            if member_only and isinstance(cl, L.Cond):
                result.append(cl)
                continue
            
            clause, before_clauses, after_clauses = rewriter(cl)
            
            if recursive:
                before_clauses = process(before_clauses)
                after_clauses = process(after_clauses)
            
            clauses = before_clauses + [clause] + after_clauses
            result.extend(clauses)
        
        return result
    
    new_clauses = process(comp.clauses)
    
    # Handle result expression.
    if member_only or not resexp:
        new_resexp = comp.resexp
    else:
        new_resexp, before_clauses, after_clauses = rewriter(comp.resexp)
        inserted_clauses = before_clauses + after_clauses
        if recursive:
            inserted_clauses = process(inserted_clauses)
        new_clauses.extend(inserted_clauses)
    
    return comp._replace(resexp=new_resexp, clauses=new_clauses)
