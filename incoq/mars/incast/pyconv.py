"""Conversion between IncAST nodes and Python nodes."""


__all__ = [
    'import_incast',
    'export_incast',
    'Parser',
]


from . import nodes as L
from . import pynodes as P


# Trivial nodes are nodes that exist in both languages and whose
# translation is simply to map the conversion function to each of
# the node's children.
trivial_nodes = [
    'Return', 'If', 'Expr', 'Pass', 'Break', 'Continue',
    
    'UnaryOp', 'BoolOp', 'BinOp', 'IfExp',
    'Num', 'Str', 'NameConstant', 'Name', 'Tuple', 'Attribute',
    
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
    
    def trivial_handler(self, node):
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
        raise ValueError('Invalid node for IncAST: ' +
                         node.__class__.__name__)
    
    def match_vars(self, node):
        """Turn a variable or tuple of variables, all of which
        are in Store context, into a list of identifiers.
        """
        if isinstance(node, P.Name):
            names = [node]
        elif isinstance(node, P.Tuple):
            if not isinstance(node.ctx, P.Store):
                raise TypeError('Vars list not in Store context')
            if not all(isinstance(item, P.Name) for item in node.elts):
                raise TypeError('Vars list contains non-variables')
            names = node.elts
        else:
            raise TypeError('Invalid node where vars list expected: ' +
                            node.__class__.__name__)
        
        if not all(isinstance(name.ctx, P.Store) for name in names):
                raise TypeError('Vars list contains variable not '
                                'in Store context')
        
        return [name.id for name in names]
    
    # Visitors for trivial nodes are auto-generated below
    # the class definition.
    
    def visit_Module(self, node):
        if not all(isinstance(stmt, P.FunctionDef) for stmt in node.body):
            raise TypeError('IncAST only allows function definitions at '
                            'the top level')
        return L.Module(self.visit(node.body))
    
    def visit_FunctionDef(self, node):
        if (len(self._visit_stack) > 1 and
            not isinstance(self._visit_stack[-2], P.Module)):
            raise TypeError('IncAST does not allow non-top-level functions')
        
        a = node.args
        if not (a.vararg is a.kwarg is None and
                a.kwonlyargs == a.kw_defaults == a.defaults and
                all(a2.annotation is None for a2 in a.args)):
            raise TypeError('IncAST does not allow functions with '
                            'default args, keyword-only args, '
                            '*args, or **kwargs')
        args = [a2.arg for a2 in a.args]
        return L.fun(node.name, args, self.visit(node.body))
    
    def visit_Assign(self, node):
        if len(node.targets) != 1:
            raise TypeError('IncAST does not allow multiple assignment')
        vars = self.match_vars(node.targets[0])
        return L.Assign(vars, self.visit(node.value))
    
    def visit_For(self, node):
        if len(node.orelse) > 0:
            raise TypeError('IncAST does not allow else clauses in loops')
        vars = self.match_vars(node.target)
        return L.For(vars,
                     self.visit(node.iter),
                     self.visit(node.body))
    
    def visit_While(self, node):
        if len(node.orelse) > 0:
            raise TypeError('IncAST does not allow else clauses in loops')
        return L.While(self.visit(node.test),
                       self.visit(node.body))
    
    def visit_SetComp(self, node):
        clauses = []
        for gen in node.generators:
            vars = self.match_vars(gen.target)
            iter = self.visit(gen.iter)
            if not isinstance(iter, L.Name):
                raise TypeError('IncAST membership clauses must have '
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
            raise TypeError('IncAST does not allow multiple comparisons')
        return L.Compare(self.visit(node.left),
                         self.visit(node.ops[0]),
                         self.visit(node.comparators[0]))
    
    def visit_Call(self, node):
        if not (len(node.keywords) == 0 and
                node.starargs is node.kwargs is None):
            raise TypeError('IncAST does not allow keyword args, '
                            '*args, or **kwargs')
        return L.GeneralCall(self.visit(node.func),
                             self.visit(node.args))
    
    def visit_Load(self, node):
        return L.Read()
    
    def visit_Store(self, node):
        return L.Write()
    
    def visit_Del(self, node):
        return L.Write()

for name in trivial_nodes:
    setattr(IncLangNodeImporter, 'visit_' + name,
            IncLangNodeImporter.trivial_handler)


class CallSimplifier(L.NodeTransformer):
    
    """Replaces GeneralCall nodes with Call nodes. Fails if this
    isn't possible.
    """
    
    def visit_GeneralCall(self, node):
        node = self.generic_visit(node)
        
        if not isinstance(node.func, L.Name):
            raise TypeError('IncAST function calls must be directly '
                            'by function name')
        return L.Call(node.func.id, node.args)


def import_incast(tree):
    """Convert a Python tree to an IncAST tree."""
    tree = IncLangNodeImporter.run(tree)
    tree = CallSimplifier.run(tree)
    return tree


class IncLangNodeExporter(NodeMapper):
    
    """Constructs a parallel tree of Python nodes given a tree of
    IncAST nodes.
    """
    
    # Not all IncAST nodes should appear in complete programs.
    # But we still need to be able to convert every node into
    # Python, in order to unparse them (e.g. for debugging).
    
    target_lang = P
    
    def generic_visit(self, node):
        raise ValueError('Invalid node to export from IncAST: ' +
                         node.__class__.__name__)
    
    def name_handler(self, name):
        """Turn an identifier string into a Name in Load context."""
        return P.Name(name, P.Load())
    
    def vars_handler(self, vars):
        """Turn a list of variables into a Name node or a Tuple
        of Name nodes, all in Store context.
        """
        assert len(vars) > 0
        if len(vars) == 1:
            node = P.Name(vars[0], P.Store())
        else:
            node = P.Tuple([P.Name(var, P.Store()) for var in vars],
                           P.Store())
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
    
#    def visit_Comment(self, node):
#        pass
    
    def visit_For(self, node):
        target = self.vars_handler(node.vars)
        return P.For(target, self.visit(node.iter),
                     self.visit(node.body), [])
    
    def visit_While(self, node):
        return P.While(self.visit(node.test),
                       self.visit(node.body), [])
    
    def visit_Assign(self, node):
        target = self.vars_handler(node.vars)
        return P.Assign([target], self.visit(node.value))
    
    def visit_Compare(self, node):
        return P.Compare(self.visit(node.left),
                         [self.visit(node.op)],
                         [self.visit(node.right)])
    
    def visit_GeneralCall(self, node):
        return P.Call(self.visit(node.func),
                      self.visit(node.args),
                      [], None, None)
    
    def visit_Call(self, node):
        return P.Call(self.name_handler(node.func),
                      self.visit(node.args),
                      [], None, None)
    
    def visit_Comp(self, node):
        assert (len(node.clauses) > 0 and
                isinstance(node.clauses[0], L.Member))
        generators = []
        for clause in node.clauses:
            if isinstance(clause, L.Member):
                target = self.vars_handler(clause.vars)
                gen = P.comprehension(target,
                                      self.name_handler(clause.rel), [])
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
        target = self.vars_handler(node.vars)
        return P.comprehension(target, self.name_handler(node.rel), [])
    
    def visit_Cond(self, node):
        return self.visit(node.cond)
    
    def visit_Read(self, node):
        return P.Load()
    
    def visit_Write(self, node):
        # We don't know whether this is Store or Del context,
        # so just set it to Load so it's explicitly invalid.
        return P.Load()

for name in trivial_nodes:
    setattr(IncLangNodeExporter, 'visit_' + name,
            IncLangNodeExporter.trivial_handler)


def export_incast(tree):
    """Convert an IncAST tree to a Python tree. Expression contexts
    are all set to Load.
    """
    tree = IncLangNodeExporter.run(tree)
    return tree


class Parser(P.Parser):
    
    """Parser for IncAST based on the one for Python and the
    import/export functions.
    """
    
    @classmethod
    def action(cls, *args, **kargs):
        tree = super().action(*args, **kargs)
        tree = import_incast(tree)
        return tree
    
    @classmethod
    def unaction(cls, tree):
        tree = export_incast(tree)
        return super().unaction(tree)
