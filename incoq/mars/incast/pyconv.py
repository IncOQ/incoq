"""Conversion between IncAST nodes and Python nodes."""


__all__ = [
    'IncASTConversionError',
    'import_incast',
    'export_incast',
    'Parser',
]


from incoq.util.misc import new_namespace

from . import nodes as _nodes
from . import tools as _tools
from . import pynodes as P

L = new_namespace(_nodes, _tools)


class IncASTConversionError(Exception):
    pass
# Alias.
ASTErr = IncASTConversionError


# Trivial nodes are nodes that exist in both languages and whose
# translation is simply to map the conversion function to each of
# the node's children.
trivial_nodes = [
    'Return', 'If', 'Expr', 'Pass', 'Break', 'Continue',
    
    'UnaryOp', 'BoolOp', 'BinOp', 'IfExp',
    'Num', 'Str', 'NameConstant',
    
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
    
    def match_vars(self, node):
        """Turn a variable or tuple of variables into a list of
        identifiers.
        """
        if isinstance(node, P.Name):
            names = [node]
        elif isinstance(node, P.Tuple):
            if not all(isinstance(item, P.Name) for item in node.elts):
                raise ASTErr('Vars list contains non-variables')
            names = node.elts
        else:
            raise ASTErr('Invalid node where vars list expected: ' +
                         node.__class__.__name__)
        
        return [name.id for name in names]
    
    def match_maplookup(self, node):
        """Turn a lookup expression M[k] into a pair of identifier M
        and expression k.
        """
        if not isinstance(node, P.Subscript):
            raise ASTErr('Invalid node where map lookup expected: ' +
                         node.__class__.__name__)
        if not isinstance(node.value, P.Name):
            raise ASTErr('Invalid node where map identifier expected: ' +
                         node.__class__.__name__)
        if not isinstance(node.slice, P.Index):
            raise ASTErr('Invalid node where map lookup index expected: ' +
                         node.__class__.__name__)
        return node.value.id, node.slice.value
    
    # Visitors for trivial nodes are auto-generated below
    # the class definition.
    
    def visit_Module(self, node):
        if not all(isinstance(stmt, P.FunctionDef) for stmt in node.body):
            raise ASTErr('IncAST only allows function definitions at '
                         'the top level')
        return L.Module(self.visit(node.body))
    
    def visit_FunctionDef(self, node):
        if (len(self._visit_stack) >= 3 and
            not isinstance(self._visit_stack[-3], P.Module)):
            raise ASTErr('IncAST does not allow non-top-level functions')
        
        a = node.args
        if not (a.vararg is a.kwarg is None and
                a.kwonlyargs == a.kw_defaults == a.defaults and
                all(a2.annotation is None for a2 in a.args)):
            raise ASTErr('IncAST does not allow functions with '
                         'default args, keyword-only args, '
                         '*args, or **kwargs')
        args = [a2.arg for a2 in a.args]
        return L.fun(node.name, args, self.visit(node.body))
    
    def visit_Delete(self, node):
        if len(node.targets) != 1:
            raise ASTErr('IncAST does not allow multiple deletion')
        map, key = self.match_maplookup(node.targets[0])
        return L.MapDelete(map, self.visit(key))
    
    def visit_Assign(self, node):
        if len(node.targets) != 1:
            raise ASTErr('IncAST does not allow multiple assignment')
        try:
            vars = self.match_vars(node.targets[0])
            result = L.Assign(vars, self.visit(node.value))
        except ASTErr:
            try:
                map, key = self.match_maplookup(node.targets[0])
                result = L.MapAssign(map, self.visit(key),
                                     self.visit(node.value))
            except ASTErr:
                raise ASTErr('IncAST assignment does not fit '
                             'allowed forms') from None
        return result
    
    def visit_For(self, node):
        if len(node.orelse) > 0:
            raise ASTErr('IncAST does not allow else clauses in loops')
        vars = self.match_vars(node.target)
        return L.For(vars,
                     self.visit(node.iter),
                     self.visit(node.body))
    
    def visit_While(self, node):
        if len(node.orelse) > 0:
            raise ASTErr('IncAST does not allow else clauses in loops')
        return L.While(self.visit(node.test),
                       self.visit(node.body))
    
    def visit_SetComp(self, node):
        clauses = []
        for gen in node.generators:
            vars = self.match_vars(gen.target)
            iter = self.visit(gen.iter)
            if not isinstance(iter, L.Name):
                raise ASTErr('IncAST membership clauses must have '
                             'variables on right-hand side; got ' +
                             iter.__class__.__name__)
            rel = iter.id
            member = L.Member(vars, rel)
            conds = [L.Cond(self.visit(if_)) for if_ in gen.ifs]
            clauses.append(member)
            clauses.extend(conds)
        return L.Comp(self.visit(node.elt), clauses)
    
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
            raise ASTErr('IncAST does not allow complex map indexing')
        return L.MapLookup(self.visit(node.value),
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
    
    def handle_fs_COMMENT(self, _func, text):
        if not isinstance(text, L.Str):
            raise ASTErr('Comment argument must be string literal')
        return L.Comment(text.s)
    
    def handle_ms_add(self, _func, set_, elem):
        return L.SetUpdate(set_, L.SetAdd(), elem)
    
    def handle_ms_remove(self, _func, set_, elem):
        return L.SetUpdate(set_, L.SetRemove(), elem)
    
    def handle_ms_reladd(self, _func, rel, elem):
        if not isinstance(rel, L.Name):
            raise ASTErr('Cannot apply reladd operation to '
                         '{} node'.format(rel.__class__.__name__))
        return L.RelUpdate(rel.id, L.SetAdd(), elem)
    
    def handle_ms_relremove(self, _func, rel, elem):
        if not isinstance(rel, L.Name):
            raise ASTErr('Cannot apply relremove operation to '
                         '{} node'.format(rel.__class__.__name__))
        return L.RelUpdate(rel.id, L.SetRemove(), elem)
    
    def handle_me_get(self, _func, map, key, default):
        return L.MapLookup(map, key, default)
    
    def handle_me_imgset(self, _func, rel, maskstr, bounds):
        if not isinstance(rel, L.Name):
            raise ASTErr('Cannot apply imgset operation to '
                         '{} node'.format(rel.__class__.__name__))
        rel = rel.id
        if not isinstance(maskstr, L.Str):
            raise ASTErr('imgset operation requires string literal '
                         'for mask')
        maskstr = maskstr.s
        try:
            mask = L.mask(maskstr)
        except ValueError:
            raise ASTErr('invalid mask string for imgset operation')
        if not (isinstance(bounds, L.Tuple) and
                all(isinstance(item, L.Name) for item in bounds.elts)):
            raise ASTErr('imgset operation requires tuple of bound '
                         'variable identifiers')
        bounds = [item.id for item in bounds.elts]
        return L.Imgset(rel, mask, bounds)


class CallSimplifier(L.NodeTransformer):
    
    """Replaces GeneralCall nodes with Call nodes. Fails if this
    isn't possible.
    """
    
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
    
    def visit_SetUpdate(self, node):
        node = self.generic_visit(node)
        
        op = {L.SetAdd: 'add',
              L.SetRemove: 'remove'}[node.op.__class__]
        return L.Expr(L.GeneralCall(L.Attribute(node.target, op),
                                    [node.value]))
    
    def visit_RelUpdate(self, node):
        node = self.generic_visit(node)
        
        op = {L.SetAdd: 'reladd',
              L.SetRemove: 'relremove'}[node.op.__class__]
        return L.Expr(L.GeneralCall(L.Attribute(L.Name(node.rel), op),
                                    [node.value]))
    
    def visit_Imgset(self, node):
        node = self.generic_visit(node)
        
        maskstr = L.Str(node.mask.m)
        idents = L.Tuple([L.Name(item) for item in node.bounds])
        return L.GeneralCall(L.Attribute(L.Name(node.rel), 'imgset'),
                             [maskstr, idents])


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
    
    def vars_helper(self, vars):
        """Turn a list of variables into a Name node or a Tuple
        of Name nodes, all in Load context.
        """
        assert len(vars) > 0
        if len(vars) == 1:
            node = P.Name(vars[0], P.Load())
        else:
            node = P.Tuple([P.Name(var, P.Load()) for var in vars],
                           P.Load())
        return node
    
    # Visitors for trivial nodes are auto-generated below
    # the class definition.
    
    def visit_Module(self, node):
        return P.Module(self.visit(node.decls))
    
    def visit_fun(self, node):
        args = P.arguments([P.arg(a, None) for a in node.args],
                           None, [], [], None, [])
        return P.FunctionDef(node.name, args, self.visit(node.body),
                             [], None)
    
    def visit_Comment(self, node):
        return P.Expr(P.Call(self.name_helper('COMMENT'),
                             [P.Str(node.text)],
                             [], None, None))
    
    def visit_For(self, node):
        target = self.vars_helper(node.vars)
        return P.For(target, self.visit(node.iter),
                     self.visit(node.body), [])
    
    def visit_While(self, node):
        return P.While(self.visit(node.test),
                       self.visit(node.body), [])
    
    def visit_Assign(self, node):
        target = self.vars_helper(node.vars)
        return P.Assign([target], self.visit(node.value))
    
    def visit_MapAssign(self, node):
        map = P.Name(node.map, P.Load())
        key = self.visit(node.key)
        value = self.visit(node.value)
        return P.Assign([P.Subscript(map, P.Index(key), P.Load())],
                        value)
    
    def visit_MapDelete(self, node):
        map = P.Name(node.map, P.Load())
        key = self.visit(node.key)
        return P.Delete([P.Subscript(map, P.Index(key), P.Load())])
    
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
    
    def visit_MapLookup(self, node):
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
    
    def visit_Comp(self, node):
        assert (len(node.clauses) > 0 and
                isinstance(node.clauses[0], L.Member))
        generators = []
        for clause in node.clauses:
            if isinstance(clause, L.Member):
                target = self.vars_helper(clause.vars)
                gen = P.comprehension(target,
                                      self.name_helper(clause.rel), [])
                generators.append(gen)
            elif isinstance(clause, L.Cond):
                last = generators[-1]
                new_ifs = last.ifs + (self.visit(clause.cond),)
                last = last._replace(ifs=new_ifs)
                generators[-1] = last
            else:
                assert()
        return P.SetComp(self.visit(node.resexp), generators)
    
    # Member and Cond are handled by the case for Comp, but these
    # cases are still needed to convert clauses in isolation.
    
    def visit_Member(self, node):
        target = self.vars_helper(node.vars)
        return P.comprehension(target, self.name_helper(node.rel), [])
    
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
