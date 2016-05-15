"""Conversion between IncAST nodes and Python nodes."""


__all__ = [
    'IncASTConversionError',
    'import_incast',
    'export_incast',
    'Parser',
]


import keyword

from incoq.util.misc import new_namespace

from . import nodes as _nodes
from . import tools as _tools
from . import pynodes as P

L = new_namespace(_nodes, _tools)


class IncASTConversionError(Exception):
    pass
# Alias.
ASTErr = IncASTConversionError


def is_valid_identifier(s):
    return s.isidentifier() and not keyword.iskeyword(s)


# Trivial nodes are nodes that exist in both languages and whose
# translation is simply to map the conversion function to each of
# the node's children.
trivial_nodes = [
    'Module',
    
    'Import', 'ImportFrom',
    
    'Raise', 'Try',
    'Global',
    
    'Return', 'If', 'Expr', 'Pass', 'Break', 'Continue',
    
    'UnaryOp', 'BoolOp', 'BinOp', 'IfExp',
    'Num', 'Str', 'NameConstant', 'Set', 'Dict',
    'ListComp',
    
    'comprehension', 'ExceptHandler', 'alias',
    
    'And', 'Or',
    'Add', 'Sub', 'Mult', 'Div', 'Mod', 'Pow', 'LShift',
    'RShift', 'BitOr', 'BitXor', 'BitAnd', 'FloorDiv',
    'Invert', 'Not', 'UAdd', 'USub',
    'Eq', 'NotEq', 'Lt', 'LtE', 'Gt', 'GtE', 'Is', 'IsNot', 'In', 'NotIn'
]


# Note L.NodeVisitor == P.NodeVisitor.
class NodeMapper(L.NodeVisitor):
    
    """Mixin for conversion of trivial nodes."""
    
    target_lang = None
    
    def seq_visit(self, seq):
        # Map to each element.
        return tuple(self.visit(item) for item in seq)
    
    def trivial_helper(self, node):
        cls = getattr(self.target_lang, type(node).__name__)
        assert cls._fields == node._fields
        children = tuple(self.visit(getattr(node, field))
                         for field in node._fields)
        return cls(*children)


class IncLangNodeImporter(NodeMapper, P.AdvNodeVisitor):
    
    """Constructs a parallel tree of IncAST nodes given a tree of Python
    nodes. Fails if there are constructs that have no equivalent IncAST
    representation.
    """
    
    target_lang = L
    
    # AdvNodeVisitor refines NodeVisitor, which NodeMapper extends.
    # We need to override seq_visit to accommodate AdvNodeVisitor's
    # need to track the _index argument for the visit stack.
    def seq_visit(self, seq):
        return tuple(self.visit(item, _index=i)
                     for i, item in enumerate(seq))
    
    def generic_visit(self, node):
        raise ASTErr('Invalid node for IncAST: ' +
                     node.__class__.__name__)
    
    def match_store_vars(self, node):
        """Turn a tuple of variables into a list of identifiers. An
        empty list is considered as an empty tuple (since Python grammar
        does not allow us to write () = ...).
        """
        if isinstance(node, P.Tuple):
            if not all(isinstance(item, P.Name) for item in node.elts):
                raise ASTErr('Vars list contains non-variables')
            names = node.elts
        elif isinstance(node, P.List) and len(node.elts) == 0:
            names = []
        else:
            raise ASTErr('Invalid node where vars list expected: ' +
                         node.__class__.__name__)
        
        return [name.id for name in names]
    
    def match_dictlookup(self, node):
        """Turn a lookup expression M[k] into a pair of expression M
        and expression k.
        """
        if not isinstance(node, P.Subscript):
            raise ASTErr('Invalid node where dict lookup expected: ' +
                         node.__class__.__name__)
        if not isinstance(node.slice, P.Index):
            raise ASTErr('Invalid node where dict lookup key expected: ' +
                         node.__class__.__name__)
        return node.value, node.slice.value
    
    def match_attribute(self, node):
        """Turn an expression o.f into a pair of expression o and
        identifier f. Note that the given expression may be a chain of
        field retrievals, in which case only the outermost retrieval is
        matched; the rest are included in o.
        """
        if not isinstance(node, P.Attribute):
            raise ASTErr('Invalid node where attribute expected: ' +
                         node.__class__.__name__)
        return node.value, node.attr
    
    # Visitors for trivial nodes are auto-generated below
    # the class definition.
    
    def visit_FunctionDef(self, node):
        a = node.args
        if not (a.vararg is a.kwarg is None and
                a.kwonlyargs == a.kw_defaults == a.defaults == () and
                all(a2.annotation is None for a2 in a.args)):
            raise ASTErr('IncAST does not allow functions with '
                         'default args, keyword-only args, '
                         '*args, **kwargs, or annotations')
        if not (node.decorator_list == () and node.returns is None):
            raise ASTErr('IncAST does not allow functions with '
                         'decorators or annotations')
        args = [a2.arg for a2 in a.args]
        return L.Fun(node.name, args, self.visit(node.body))
    
    def visit_ClassDef(self, node):
        if not (node.starargs is node.kwargs is None and
                node.keywords == node.decorator_list == ()):
            raise ASTErr('IncAST does not allow classes with '
                         'keywords in the bases list, or with '
                         'decorators')
        return L.Class(node.name, self.visit(node.bases),
                       self.visit(node.body))
    
    def visit_Delete(self, node):
        if len(node.targets) != 1:
            raise ASTErr('IncAST does not allow multiple deletion')
        target = node.targets[0]
        
        result = None
        
        # Dictionary deletion.
        if result is None:
            try:
                dict, key = self.match_dictlookup(target)
                result = L.DictDelete(self.visit(dict), self.visit(key))
            except ASTErr:
                pass
        
        # Attribute deletion.
        if result is None:
            try:
                obj, attr = self.match_attribute(target)
                result = L.AttrDelete(self.visit(obj), attr)
            except ASTErr:
                pass
        
        if result is None:
            raise ASTErr('IncAST deletion does not fit '
                         'allowed forms') from None
        
        return result
    
    def visit_Assign(self, node):
        if len(node.targets) != 1:
            raise ASTErr('IncAST does not allow multiple assignment')
        target = node.targets[0]
        value = self.visit(node.value)
        
        result = None
        
        # Simple variable assignment.
        if isinstance(target, P.Name):
            result = L.Assign(target.id, value)
        
        # Decomposing tuple assignment.
        if result is None:
            try:
                vars = self.match_store_vars(target)
                result = L.DecompAssign(vars, value)
            except ASTErr:
                pass
        
        # Dictionary assignment.
        if result is None:
            try:
                dict, key = self.match_dictlookup(target)
                result = L.DictAssign(self.visit(dict), self.visit(key),
                                      value)
            except ASTErr:
                pass
        
        # Attribute assignment.
        if result is None:
            try:
                obj, attr = self.match_attribute(target)
                result = L.AttrAssign(self.visit(obj), attr, value)
            except ASTErr:
                pass
        
        if result is None:
            raise ASTErr('IncAST assignment does not fit '
                         'allowed forms') from None
        
        return result
    
    def visit_For(self, node):
        if len(node.orelse) > 0:
            raise ASTErr('IncAST does not allow else clauses in loops')
        iter = self.visit(node.iter)
        body = self.visit(node.body)
        if isinstance(node.target, P.Name):
            result = L.For(node.target.id, iter, body)
        else:
            try:
                vars = self.match_store_vars(node.target)
                result = L.DecompFor(vars, iter, body)
            except ASTErr:
                raise ASTErr('Invalid left-hand side of For loop') from None
        return result
    
    def visit_While(self, node):
        if len(node.orelse) > 0:
            raise ASTErr('IncAST does not allow else clauses in loops')
        return L.While(self.visit(node.test),
                       self.visit(node.body))
    
    def visit_Assert(self, node):
        if node.msg is not None:
            raise ASTErr('IncAST does not allow msg for assert')
        return L.Assert(self.visit(node.test))
    
    def visit_SetComp(self, node):
        clauses = []
        for gen in node.generators:
            new_clauses = self.comprehension_helper(gen)
            clauses.extend(new_clauses)
        return L.Comp(self.visit(node.elt), clauses)
    
    def member_clause_helper(self, target, iter):
        # iter is already converted to IncAST nodes, but target is not.
        # This facilitates recursion (for clause types that wrap other
        # clauses) without assuming anything about the structure of the
        # lhs.
        
        # for x1, ..., xn in REL(R)
        if (isinstance(iter, L.GeneralCall) and
            isinstance(iter.func, L.Name) and
            iter.func.id == 'REL'):
            vars = self.match_store_vars(target)
            if not (len(iter.args) == 1 and
                    isinstance(iter.args[0], L.Name)):
                raise ASTErr('Invalid REL clause')
            rel = iter.args[0].id
            member = L.RelMember(vars, rel)
        
        # for x1, ..., xn in SING(e)
        elif (isinstance(iter, L.GeneralCall) and
              isinstance(iter.func, L.Name) and
              iter.func.id == 'SING'):
            vars = self.match_store_vars(target)
            if not len(iter.args) == 1:
                raise ASTErr('Invalid SING clause')
            value = iter.args[0]
            member = L.SingMember(vars, value)
        
        # for x1, ..., xn in WITHOUT(R, e)
        elif (isinstance(iter, L.GeneralCall) and
              isinstance(iter.func, L.Name) and
              iter.func.id == 'WITHOUT'):
            if not len(iter.args) == 2:
                raise ASTErr('Invalid WITHOUT clause')
            value = iter.args[1]
            cl = self.member_clause_helper(target, iter.args[0])
            member = L.WithoutMember(cl, value)
        
        # for x1, ..., xn in VARS(e)
        elif (isinstance(iter, L.GeneralCall) and
              isinstance(iter.func, L.Name) and
              iter.func.id == 'VARS'):
            vars = self.match_store_vars(target)
            if not len(iter.args) == 1:
                raise ASTErr('Invalid VARS clause')
            value = iter.args[0]
            member = L.VarsMember(vars, value)
        
        # for x1, ..., xn in SETFROMMAP(R, M, mask)
        elif (isinstance(iter, L.GeneralCall) and
              isinstance(iter.func, L.Name) and
              iter.func.id == 'SETFROMMAP'):
            vars = self.match_store_vars(target)
            if not (len(iter.args) == 3 and
                    isinstance(iter.args[0], L.Name) and
                    isinstance(iter.args[1], L.Name) and
                    isinstance(iter.args[2], L.Str)):
                raise ASTErr('Invalid SETFROMMAP clause')
            rel = iter.args[0].id
            map = iter.args[1].id
            mask = L.mask(iter.args[2].s)
            member = L.SetFromMapMember(vars, rel, map, mask)
        
        # for x, y in M()
        elif (isinstance(iter, L.GeneralCall) and
              isinstance(iter.func, L.Name) and
              iter.func.id == 'M'):
            vars = self.match_store_vars(target)
            if not (len(iter.args) == 0 and
                    len(vars) == 2):
                raise ASTErr('Invalid M clause')
            set_, elem = vars
            member = L.MMember(set_, elem)
        
        # for x, y in F(attr)
        elif (isinstance(iter, L.GeneralCall) and
              isinstance(iter.func, L.Name) and
              iter.func.id == 'F'):
            vars = self.match_store_vars(target)
            if not (len(iter.args) == 1 and
                    isinstance(iter.args[0], L.Name) and
                    len(vars) == 2):
                raise ASTErr('Invalid F clause')
            attr = iter.args[0].id
            obj, value = vars
            member = L.FMember(obj, value, attr)
        
        # for m, k, v in MAP()
        elif (isinstance(iter, L.GeneralCall) and
              isinstance(iter.func, L.Name) and
              iter.func.id == 'MAP'):
            vars = self.match_store_vars(target)
            if not (len(iter.args) == 0 and
                    len(vars) == 3):
                raise ASTErr('Invalid MAP clause')
            map, key, value = vars
            member = L.MAPMember(map, key, value)
        
        # for t, x1, ..., xn in TUP()
        elif (isinstance(iter, L.GeneralCall) and
              isinstance(iter.func, L.Name) and
              iter.func.id == 'TUP'):
            vars = self.match_store_vars(target)
            if not (len(iter.args) == 0 and
                    len(vars) >= 1):
                raise ASTErr('Invalid TUP clause')
            tup, *elts = vars
            member = L.TUPMember(tup, elts)
        
        # General case.
        else:
            target = self.visit(target)
            member = L.Member(target, iter)
        
        return member
    
    def comprehension_helper(self, node):
        # Switch on iter to determine what kind of membership clause
        # to produce.
        assert isinstance(node, P.comprehension)
        iter = self.visit(node.iter)
        member = self.member_clause_helper(node.target, iter)
        conds = [L.Cond(self.visit(c)) for c in node.ifs]
        return [member] + conds
    
    def visit_Compare(self, node):
        # Comparisons must involve exactly two terms and one operator.
        if not (len(node.ops) == len(node.comparators) == 1):
            raise ASTErr('IncAST does not allow multiple comparisons')
        return L.Compare(self.visit(node.left),
                         self.visit(node.ops[0]),
                         self.visit(node.comparators[0]))
    
    def visit_Call(self, node):
        if not (len(node.keywords) == 0 and
                node.starargs is node.kwargs is None):
            raise ASTErr('IncAST does not allow keyword args, '
                         '*args, or **kwargs')
        return L.GeneralCall(self.visit(node.func),
                             self.visit(node.args))
    
    def visit_Attribute(self, node):
        return L.Attribute(self.visit(node.value),
                           node.attr)
    
    def visit_Subscript(self, node):
        if not isinstance(node.slice, P.Index):
            raise ASTErr('IncAST does not allow complex dict indexing')
        return L.DictLookup(self.visit(node.value),
                            self.visit(node.slice.value),
                            None)
    
    def visit_Name(self, node):
        return L.Name(node.id)
    
    def visit_List(self, node):
        return L.List(self.visit(node.elts))
    
    def visit_Tuple(self, node):
        return L.Tuple(self.visit(node.elts))

for name in trivial_nodes:
    setattr(IncLangNodeImporter, 'visit_' + name,
            IncLangNodeImporter.trivial_helper)


class IncLangSpecialImporter(L.MacroExpander):
    
    """Expand macros, e.g. for nodes unique to IncAST or for
    multi-statement operations.
    """
    
    def assert_isname(self, nodes, op):
        for node in nodes:
            if not isinstance(node, L.Name):
                raise ASTErr('Cannot apply {} operation with '
                             '{} node'.format(op, node.__class__.__name__))
    
    def handle_fs_COMMENT(self, _func, text):
        if not isinstance(text, L.Str):
            raise ASTErr('Comment argument must be string literal')
        return L.Comment(text.s)
    
    def handle_fs_resetdemand(self, _func):
        return L.ResetDemand([])
    
    def handle_fs_resetdemandfor(self, _func, names):
        if not (isinstance(names, L.List) and
                all(isinstance(n, L.Str) for n in names.elts)):
            raise ASTErr('resetdemandfor() directive takes either no '
                         'arguments or a literal list of strings')
        return L.ResetDemand([n.s for n in names.elts])
    
    def handle_ms_add(self, _func, set_, elem):
        return L.SetUpdate(set_, L.SetAdd(), elem)
    
    def handle_ms_remove(self, _func, set_, elem):
        return L.SetUpdate(set_, L.SetRemove(), elem)
    
    def handle_ms_inccount(self, _func, set_, elem):
        return L.SetUpdate(set_, L.IncCount(), elem)
    
    def handle_ms_deccount(self, _func, set_, elem):
        return L.SetUpdate(set_, L.DecCount(), elem)
    
    def handle_ms_update(self, _func, set_, other):
        return L.SetBulkUpdate(set_, L.Union(), other)
    
    def handle_ms_intersection_update(self, _func, set_, other):
        return L.SetBulkUpdate(set_, L.Inter(), other)
    
    def handle_ms_difference_update(self, _func, set_, other):
        return L.SetBulkUpdate(set_, L.Diff(), other)
    
    def handle_ms_symmetric_difference_update(self, _func, set_, other):
        return L.SetBulkUpdate(set_, L.SymDiff(), other)
    
    def handle_ms_copy_update(self, _func, set_, other):
        return L.SetBulkUpdate(set_, L.Copy(), other)
    
    def handle_ms_clear(self, _func, set_):
        return L.SetClear(set_)
    
    def handle_ms_reladd(self, _func, rel, elem):
        self.assert_isname([rel, elem], 'reladd')
        return L.RelUpdate(rel.id, L.SetAdd(), elem.id)
    
    def handle_ms_relremove(self, _func, rel, elem):
        self.assert_isname([rel, elem], 'relremove')
        return L.RelUpdate(rel.id, L.SetRemove(), elem.id)
    
    def handle_ms_relinccount(self, _func, rel, elem):
        self.assert_isname([rel, elem], 'relinccount')
        return L.RelUpdate(rel.id, L.IncCount(), elem.id)
    
    def handle_ms_reldeccount(self, _func, rel, elem):
        self.assert_isname([rel, elem], 'reldeccount')
        return L.RelUpdate(rel.id, L.DecCount(), elem.id)
    
    def handle_ms_relclear(self, _func, rel):
        self.assert_isname([rel], 'relclear')
        return L.RelClear(rel.id)
    
    def handle_ms_dictcopy_update(self, _func, target, other):
        return L.DictBulkUpdate(target, L.DictCopy(), other)
    
    def handle_ms_dictclear(self, _func, target):
        return L.DictClear(target)
    
    def handle_ms_mapassign(self, _func, map, key, value):
        self.assert_isname([map, key, value], 'mapassign')
        return L.MapAssign(map.id, key.id, value.id)
    
    def handle_ms_mapdelete(self, _func, map, key):
        self.assert_isname([map, key], 'mapdelete')
        return L.MapDelete(map.id, key.id)
    
    def handle_ms_mapclear(self, _func, map):
        self.assert_isname([map], 'mapclear')
        return L.MapClear(map.id)
    
    def handle_fe_index(self, _func, value, index):
        return L.Subscript(value, index)
    
    def handle_me_get(self, _func, dict, key, default):
        return L.DictLookup(dict, key, default)
    
    def handle_fe_FIRSTTHEN(self, _func, first, then):
        return L.FirstThen(first, then)
    
    def handle_me_imglookup(self, _func, set, maskstr, bounds):
        if not isinstance(maskstr, L.Str):
            raise ASTErr('imglookup operation requires string literal '
                         'for mask')
        maskstr = maskstr.s
        try:
            mask = L.mask(maskstr)
        except ValueError:
            raise ASTErr('Invalid mask string for imglookup operation')
        if not (isinstance(bounds, L.Tuple) and
                all(isinstance(item, L.Name) for item in bounds.elts)):
            raise ASTErr('imglookup operation requires tuple of bound '
                         'variable identifiers')
        bounds = [item.id for item in bounds.elts]
        return L.ImgLookup(set, mask, bounds)
    
    def handle_me_setfrommap(self, _func, map, maskstr):
        if not isinstance(maskstr, L.Str):
            raise ASTErr('setfrommap operation requires string literal '
                         'for mask')
        maskstr = maskstr.s
        try:
            mask = L.mask(maskstr)
        except ValueError:
            raise ASTErr('Invalid mask string for setfrommap operation')
        return L.SetFromMap(map, mask)
    
    def handle_fe_unwrap(self, _func, set_):
        return L.Unwrap(set_)
    
    def handle_fe_wrap(self, _func, set_):
        return L.Wrap(set_)
    
    def handle_fe_isset(self, _func, value):
        return L.IsSet(value)
    
    def handle_fe_hasfield(self, _func, value, attr):
        if not isinstance(attr, L.Str):
            raise ASTErr('hasfield requires string literal for second arg')
        return L.HasField(value, attr.s)
    
    def handle_fe_ismap(self, _func, value):
        return L.IsMap(value)
    
    def handle_fe_hasarity(self, _func, value, arity):
        if not isinstance(arity, L.Num):
            raise ASTErr('hasarity requires integer literal for second arg')
        return L.HasArity(value, arity.n)
    
    def handle_me_getcount(self, _func, set_, elem):
        return L.BinOp(set_, L.GetCount(), elem)
    
    def handle_fe_QUERY(self, _func, name, query, ann=None):
        if not (isinstance(name, L.Str) and
                is_valid_identifier(name.s)):
            raise ASTErr('QUERY annotation first argument must be a '
                         'string literal containing a valid identifier')
        if ann is not None:
            ann = L.frozen_literal_eval(ann)
        return L.Query(name.s, query, ann)
    
    def aggr_helper(self, _func, value, params=None, restr=None):
        op = {'count': L.Count(),
              'sum': L.Sum(),
              'min': L.Min(),
              'max': L.Max()}[_func]
        
        if params is None and restr is None:
            return L.Aggr(op, value)
        else:
            if not (isinstance(params, L.Tuple) and
                    all(isinstance(p, L.Name) for p in params.elts)):
                raise ASTErr('Bad parameter list for AggrRestr')
            params = [p.id for p in params.elts]
            return L.AggrRestr(op, value, params, restr)
    
    handle_fe_count = aggr_helper
    handle_fe_sum = aggr_helper
    handle_fe_min = aggr_helper
    handle_fe_max = aggr_helper


class CallSimplifier(L.NodeTransformer):
    
    """Replaces GeneralCall nodes with Call nodes if possible."""
    
    def visit_GeneralCall(self, node):
        node = self.generic_visit(node)
        
        if isinstance(node.func, L.Name):
            node = L.Call(node.func.id, node.args)
        return node


def import_incast(tree):
    """Convert a Python tree to an IncAST tree."""
    tree = IncLangNodeImporter.run(tree)
    tree = IncLangSpecialImporter.run(tree)
    tree = CallSimplifier.run(tree)
    return tree


class IncLangSpecialExporter(L.NodeTransformer):
    
    """Export IncAST constructs, expressing them as IncAST nodes."""
    
    def visit_ResetDemand(self, node):
        if len(node.names) == 0:
            return L.Expr(L.GeneralCall(L.Name('resetdemand'), []))
        else:
            namelist = L.List([L.Str(n) for n in node.names])
            return L.Expr(L.GeneralCall(L.Name('resetdemandfor'),
                                        [namelist]))
    
    def visit_SetUpdate(self, node):
        node = self.generic_visit(node)
        
        op = {L.SetAdd: 'add',
              L.SetRemove: 'remove',
              L.IncCount: 'inccount',
              L.DecCount: 'deccount'}[node.op.__class__]
        return L.Expr(L.GeneralCall(L.Attribute(node.target, op),
                                    [node.value]))
    
    def visit_SetBulkUpdate(self, node):
        node = self.generic_visit(node)
        
        op = {L.Union: 'update',
              L.Inter: 'intersection_update',
              L.Diff: 'difference_update',
              L.SymDiff: 'symmetric_difference_update',
              L.Copy: 'copy_update'}[node.op.__class__]
        return L.Expr(L.GeneralCall(L.Attribute(node.target, op),
                                    [node.value]))
    
    def visit_SetClear(self, node):
        node = self.generic_visit(node)
        
        return L.Expr(L.GeneralCall(L.Attribute(node.target, 'clear'), [])) 
    
    def visit_RelUpdate(self, node):
        op = {L.SetAdd: 'reladd',
              L.SetRemove: 'relremove',
              L.IncCount: 'relinccount',
              L.DecCount: 'reldeccount'}[node.op.__class__]
        return L.Expr(L.GeneralCall(L.Attribute(L.Name(node.rel), op),
                                    [L.Name(node.elem)]))
    
    def visit_RelClear(self, node):
        return L.Expr(L.GeneralCall(L.Attribute(L.Name(node.rel),
                                                'relclear'),
                                    []))
    
    def visit_DictBulkUpdate(self, node):
        op = {L.DictCopy: 'dictcopy_update'}[node.op.__class__]
        return L.Expr(L.GeneralCall(L.Attribute(node.target, op),
                                    [node.value]))
    
    def visit_DictClear(self, node):
        node = self.generic_visit(node)
        func = L.Attribute(node.target, 'dictclear')
        return L.Expr(L.GeneralCall(func, []))
    
    def visit_MapAssign(self, node):
        func = L.Attribute(L.Name(node.map), 'mapassign')
        return L.Expr(L.GeneralCall(func, [L.Name(node.key),
                                           L.Name(node.value)]))
    
    def visit_MapDelete(self, node):
        func = L.Attribute(L.Name(node.map), 'mapdelete')
        return L.Expr(L.GeneralCall(func, [L.Name(node.key)]))
    
    def visit_MapClear(self, node):
        func = L.Attribute(L.Name(node.map), 'mapclear')
        return L.Expr(L.GeneralCall(func, []))
    
    def visit_BinOp(self, node):
        node = self.generic_visit(node)
        
        if isinstance(node.op, L.GetCount):
            return L.GeneralCall(L.Attribute(node.left, 'getcount'),
                                 [node.right])
        return node
    
    def visit_FirstThen(self, node):
        node = self.generic_visit(node)
        
        func = L.Name('FIRSTTHEN')
        return L.GeneralCall(func, [node.first, node.then])
    
    def visit_ImgLookup(self, node):
        node = self.generic_visit(node)
        
        maskstr = L.Str(node.mask.m)
        idents = L.Tuple([L.Name(item) for item in node.bounds])
        return L.GeneralCall(L.Attribute(node.set, 'imglookup'),
                             [maskstr, idents])
    
    def visit_SetFromMap(self, node):
        node = self.generic_visit(node)
        
        maskstr = L.Str(node.mask.m)
        return L.GeneralCall(L.Attribute(node.map, 'setfrommap'),
                             [maskstr])
    
    def visit_Unwrap(self, node):
        node = self.generic_visit(node)
        
        return L.Call('unwrap', [node.value])
    
    def visit_Wrap(self, node):
        node = self.generic_visit(node)
        
        return L.Call('wrap', [node.value])
    
    def visit_IsSet(self, node):
        node = self.generic_visit(node)
        
        return L.Call('isset', [node.value])
    
    def visit_HasField(self, node):
        node = self.generic_visit(node)
        
        return L.Call('hasfield', [node.value, L.Str(node.attr)])
    
    def visit_IsMap(self, node):
        node = self.generic_visit(node)
        
        return L.Call('ismap', [node.value])
    
    def visit_HasArity(self, node):
        node = self.generic_visit(node)
        
        return L.Call('hasarity', [node.value, L.Num(node.arity)])
    
    def visit_Aggr(self, node):
        node = self.generic_visit(node)
        
        op = {L.Count: 'count',
              L.Sum: 'sum',
              L.Min: 'min',
              L.Max: 'max'}[node.op.__class__]
        return L.Call(op, [node.value])
    
    def visit_AggrRestr(self, node):
        node = self.generic_visit(node)
        
        op = {L.Count: 'count',
              L.Sum: 'sum',
              L.Min: 'min',
              L.Max: 'max'}[node.op.__class__]
        params = L.Tuple([L.Name(p) for p in node.params])
        return L.Call(op, [node.value, params, node.restr])


class IncLangNodeExporter(NodeMapper):
    
    """Constructs a parallel tree of Python nodes given a tree of
    IncAST nodes.
    """
    
    # Not all IncAST nodes should appear in complete programs.
    # But we still need to be able to convert every node into
    # Python, in order to unparse them (e.g. for debugging).
    
    target_lang = P
    
    def generic_visit(self, node):
        raise ASTErr('Invalid node to export from IncAST: ' +
                     node.__class__.__name__)
    
    def name_helper(self, name):
        """Turn an identifier string into a Name in Load context."""
        return P.Name(name, P.Load())
    
    def tuple_store_helper(self, vars):
        """Turn a list of variables into a Tuple of Name nodes,
        all in Load context. An empty list is turned into a unit
        List node ([]).
        """
        if len(vars) == 0:
            return P.List([], P.Load())
        else:
            return P.Tuple([P.Name(var, P.Load()) for var in vars],
                           P.Load())
    
    # Visitors for trivial nodes are auto-generated below
    # the class definition.
    
    def visit_Fun(self, node):
        args = P.arguments([P.arg(a, None) for a in node.args],
                           None, [], [], None, [])
        return P.FunctionDef(node.name, args, self.visit(node.body),
                             [], None)
    
    def visit_Class(self, node):
        return P.ClassDef(node.name, self.visit(node.bases), [],
                          None, None, self.visit(node.body), [])
    
    def visit_Comment(self, node):
        return P.Expr(P.Call(self.name_helper('COMMENT'),
                             [P.Str(node.text)],
                             [], None, None))
    
    def visit_Assert(self, node):
        return P.Assert(self.visit(node.test), None)
    
    def visit_For(self, node):
        target = self.name_helper(node.target)
        return P.For(target, self.visit(node.iter),
                     self.visit(node.body), [])
    
    def visit_DecompFor(self, node):
        target = self.tuple_store_helper(node.vars)
        return P.For(target, self.visit(node.iter),
                     self.visit(node.body), [])
    
    def visit_While(self, node):
        return P.While(self.visit(node.test),
                       self.visit(node.body), [])
    
    def visit_Assign(self, node):
        target = self.name_helper(node.target)
        return P.Assign([target], self.visit(node.value))
    
    def visit_DecompAssign(self, node):
        target = self.tuple_store_helper(node.vars)
        return P.Assign([target], self.visit(node.value))
    
    def visit_DictAssign(self, node):
        dict = self.visit(node.target)
        key = self.visit(node.key)
        value = self.visit(node.value)
        return P.Assign([P.Subscript(dict, P.Index(key), P.Load())],
                        value)
    
    def visit_DictDelete(self, node):
        dict = self.visit(node.target)
        key = self.visit(node.key)
        return P.Delete([P.Subscript(dict, P.Index(key), P.Load())])
    
    def visit_AttrAssign(self, node):
        obj = self.visit(node.obj)
        value = self.visit(node.value)
        return P.Assign([P.Attribute(obj, node.attr, P.Load())],
                        value)
    
    def visit_AttrDelete(self, node):
        obj = self.visit(node.obj)
        return P.Delete([P.Attribute(obj, node.attr, P.Load())])
    
    def visit_Compare(self, node):
        return P.Compare(self.visit(node.left),
                         [self.visit(node.op)],
                         [self.visit(node.right)])
    
    def visit_GeneralCall(self, node):
        return P.Call(self.visit(node.func),
                      self.visit(node.args),
                      [], None, None)
    
    def visit_Call(self, node):
        return P.Call(self.name_helper(node.func),
                      self.visit(node.args),
                      [], None, None)
    
    def visit_Name(self, node):
        return self.name_helper(node.id)
    
    def visit_List(self, node):
        return P.List(self.visit(node.elts), P.Load())
    
    def visit_Tuple(self, node):
        return P.Tuple(self.visit(node.elts), P.Load())
    
    def visit_Attribute(self, node):
        return P.Attribute(self.visit(node.value),
                           node.attr, P.Load())
    
    def visit_Subscript(self, node):
        return P.Call(P.Name('index', P.Load()),
                      [self.visit(node.value),
                       self.visit(node.index)],
                      [], None, None)
    
    def visit_DictLookup(self, node):
        if node.default is None:
            return P.Subscript(self.visit(node.value),
                               P.Index(self.visit(node.key)),
                               P.Load())
        else:
            return P.Call(P.Attribute(self.visit(node.value),
                                      'get', P.Load()),
                          [self.visit(node.key),
                           self.visit(node.default)],
                          [], None, None)
    
    def visit_Query(self, node):
        args = [P.Str(node.name), self.visit(node.query)]
        if node.ann is not None:
            ann = L.literal_unparse(node.ann)
            ann = self.visit(ann)
            args.append(ann)
        
        return P.Call(self.name_helper('QUERY'), args,
                      [], None, None)
    
    def visit_Comp(self, node):
        generators = []
        for cl in node.clauses:
            cl = self.visit(cl)
            if isinstance(cl, P.comprehension):
                generators.append(cl)
            elif isinstance(cl, P.expr):
                if len(generators) == 0:
                    break
                last = generators[-1]
                new_ifs = last.ifs + (cl,)
                last = last._replace(ifs=new_ifs)
                generators[-1] = last
            else:
                assert()
        if len(generators) == 0:
            raise ASTErr('Comprehension has no clauses, or first clause '
                         'is a condition')
        return P.SetComp(self.visit(node.resexp), generators)
    
    def visit_Member(self, node):
        return P.comprehension(self.visit(node.target),
                               self.visit(node.iter), [])
    
    def visit_RelMember(self, node):
        return P.comprehension(self.tuple_store_helper(node.vars),
                               P.Call(P.Name('REL', P.Load()),
                                      [self.name_helper(node.rel)],
                                      [], None, None), [])
    
    def visit_SingMember(self, node):
        return P.comprehension(self.tuple_store_helper(node.vars),
                               P.Call(P.Name('SING', P.Load()),
                                      [self.visit(node.value)],
                                      [], None, None), [])
    
    def visit_WithoutMember(self, node):
        cl = self.visit(node.cl)
        value = self.visit(node.value)
        iter = P.Call(P.Name('WITHOUT', P.Load()),
                      [cl.iter, value],
                      [], None, None)
        return P.comprehension(cl.target, iter, [])
    
    def visit_VarsMember(self, node):
        return P.comprehension(self.tuple_store_helper(node.vars),
                               P.Call(P.Name('VARS', P.Load()),
                                      [self.visit(node.iter)],
                                      [], None, None), [])
    
    def visit_SetFromMapMember(self, node):
        return P.comprehension(self.tuple_store_helper(node.vars),
                               P.Call(P.Name('SETFROMMAP', P.Load()),
                                      [self.name_helper(node.rel),
                                       self.name_helper(node.map),
                                       P.Str(node.mask.m)],
                                      [], None, None), [])
    
    def visit_MMember(self, node):
        vars = self.tuple_store_helper([node.set, node.elem])
        return P.comprehension(vars, P.Call(P.Name('M', P.Load()),
                                            [], [], None, None), [])
    
    def visit_FMember(self, node):
        vars = self.tuple_store_helper([node.obj, node.value])
        return P.comprehension(vars, P.Call(P.Name('F', P.Load()),
                                            [P.Name(node.attr, P.Load())],
                                            [], None, None), [])
    
    def visit_MAPMember(self, node):
        vars = self.tuple_store_helper([node.map, node.key, node.value])
        return P.comprehension(vars, P.Call(P.Name('MAP', P.Load()),
                                            [], [], None, None), [])
    
    def visit_TUPMember(self, node):
        vars = self.tuple_store_helper((node.tup,) + node.elts)
        return P.comprehension(vars, P.Call(P.Name('TUP', P.Load()),
                                            [], [], None, None), [])
    
    def visit_Cond(self, node):
        return self.visit(node.cond)
    
    # Mask is handled by nodes that use it.
    
    def visit_mask(self, node):
        return P.Str('<Mask: {}>'.format(node.m))
    
    # Convert op nodes that have no corresponding Python node
    # into their string representations. This enables them to
    # be unparsed when they appear in isolation. The other case,
    # when they appear as part of an actual operation, is handled
    # by the logic for the operation.
    
    def op_helper(self, node):
        return P.Str('<' + node.__class__.__name__ + '>')
    
    visit_SetAdd = op_helper
    visit_SetRemove = op_helper

for name in trivial_nodes:
    setattr(IncLangNodeExporter, 'visit_' + name,
            IncLangNodeExporter.trivial_helper)


def export_incast(tree):
    """Convert an IncAST tree to a Python tree. All expression
    nodes are given Load context."""
    tree = IncLangSpecialExporter.run(tree)
    tree = IncLangNodeExporter.run(tree)
    return tree


class Parser(P.Parser):
    
    """Parser for IncAST based on the one for Python and the
    import/export functions.
    """
    
    @classmethod
    def action(cls, *args, subst=None, **kargs):
        tree = super().action(*args, **kargs)
        tree = import_incast(tree)
        if subst is not None:
            tree = L.Templater.run(tree, subst)
        return tree
    
    @classmethod
    def unaction(cls, tree):
        tree = export_incast(tree)
        return super().unaction(tree)
