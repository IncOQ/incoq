"""Pre- and post-processing rewritings."""


__all__ = [
    'ExpressionPreprocessor',
    'RuntimeImportPreprocessor',
    'MainCallRemover',
    'preprocess_vardecls',
    'SetUpdateImporter',
    'AttributeDisallower',
    'GeneralCallDisallower',
    'RelUpdateExporter',
    'postprocess_vardecls',
    'MainCallAdder',
    'RuntimeImportPostprocessor',
    'PassPostprocessor',
]


from incoq.util.seq import pairs
from incoq.util.collections import OrderedSet
from incoq.mars.incast import L, P


main_boilerplate_stmt = P.Parser.ps('''
    if __name__ == '__main__':
        main()
    ''')


class ExpressionPreprocessor(P.NodeTransformer):
    
    """Preprocessor for Python code that eliminates some features
    that can't be directly expressed in IncAST.
    """
    
    def visit_Assign(self, node):
        node = self.generic_visit(node)
        
        # Translate multiple assignments as a single statement
        # (e.g. "a = b = c") into sequential single assignments.
        if len(node.targets) > 1:
            stmts = []
            values = list(node.targets) + [node.value]
            for lhs, rhs in reversed(list(pairs(values))):
                rhs_load = P.ContextSetter.run(rhs, P.Load)
                stmts.append(P.Assign([lhs], rhs_load))
            node = stmts
        
        return node
    
    def visit_Compare(self, node):
        node = self.generic_visit(node)
        
        # Translate multiple comparisons into conjunctions of
        # each individual comparison.
        assert len(node.ops) == len(node.comparators) > 0
        if len(node.ops) > 1:
            conds = []
            values = [node.left] + list(node.comparators)
            for i in range(len(values) - 1):
                conds.append(P.Compare(values[i], [node.ops[i]],
                                       [values[i + 1]]))
            node = P.BoolOp(P.And(), conds)
        
        return node


class RuntimeImportPreprocessor(P.NodeTransformer):
    
    """Eliminate the runtime import statement and turn qualified
    names from the runtime into unqualified names, e.g.,
    
        incoq.mars.runtime.Set -> Set
    
    The recognized import forms are:
    
        import incoq.mars.runtime
        import incoq.mars.runtime as <alias>
        from incoq.mars.runtime import *
    
    If <alias> is used, the alias prefix is removed from qualified
    names.
    """
    
    def __init__(self):
        super().__init__()
        self.aliases = set()
    
    def visit_Import(self, node):
        pat = P.Import([P.alias('incoq.mars.runtime', P.PatVar('_ALIAS'))])
        match = P.match(pat, node)
        if match is None:
            return node
        
        if match['_ALIAS'] is not None:
            self.aliases.add(match['_ALIAS'])
        return []
    
    def visit_ImportFrom(self, node):
        pat = P.Parser.ps('from incoq.mars.runtime import *')
        if node != pat:
            return node
        
        return []
    
    def visit_Attribute(self, node):
        node = self.generic_visit(node)
        
        quals = []
        quals.append(P.Parser.pe('incoq.mars.runtime'))
        for alias in self.aliases:
            quals.append(P.Name(alias, P.Load()))
        
        for qual in quals:
            pat = P.Attribute(qual, P.PatVar('_ATTR'), P.Load())
            match = P.match(pat, node)
            if match is not None:
                break
        else:
            return node
        
        return P.Name(match['_ATTR'], P.Load())


class MainCallRemover(P.NodeTransformer):
    
    """Remove the specific code for calling main() when the
    program is executed directly.
    """
    
    def visit_Module(self, node):
        changed = False
        new_body = []
        for stmt in node.body:
            if stmt == main_boilerplate_stmt:
                changed = True
            else:
                new_body.append(stmt)
        if changed:
            node = node._replace(body=new_body)
        return node


def preprocess_vardecls(tree):
    """Eliminate global variable declarations of the form
    
        R = Set()
    
    and return a list of relations declared in this manner.
    """
    assert isinstance(tree, P.Module)
    pat = P.Assign([P.Name(P.PatVar('_REL'), P.Wildcard())],
                   P.Parser.pe('Set()'))
    
    rels = OrderedSet()
    body = []
    changed = False
    for stmt in tree.body:
        match = P.match(pat, stmt)
        if match is not None:
            rels.add(match['_REL'])
            changed = True
        else:
            body.append(stmt)
    
    if changed:
        tree = tree._replace(body=body)
    return tree, rels


class SetUpdateImporter(L.NodeTransformer):
    
    """Replace SetUpdate nodes on known relations variables with
    RelUpdate nodes.
    """
    
    def __init__(self, rels):
        super().__init__()
        self.rels = rels
    
    def visit_SetUpdate(self, node):
        if (isinstance(node.target, L.Name) and
            node.target.id in self.rels):
            return L.RelUpdate(node.target.id, node.op, node.value)
        return node


class AttributeDisallower(L.NodeVisitor):
    
    """Fail if there are any Attribute nodes in the tree."""
    
    def visit_Attribute(self, node):
        raise TypeError('IncAST does not allow attributes')


class GeneralCallDisallower(L.NodeVisitor):
    
    """Fail if there are any GeneralCall nodes in the tree."""
    
    def visit_GeneralCall(self, node):
        raise TypeError('IncAST function calls must be directly '
                        'by function name')


class RelUpdateExporter(L.NodeTransformer):
    
    def visit_RelUpdate(self, node):
        return L.SetUpdate(L.Name(node.rel), node.op, node.value)


def postprocess_vardecls(tree, rels, maps):
    """Prepend global variable declarations for the given relation
    names.
    """
    assert isinstance(tree, P.Module)
    header = ()
    header += tuple(P.Parser.ps('_REL = Set()', subst={'_REL': rel})
                    for rel in rels)
    header += tuple(P.Parser.ps('_MAP = Map()', subst={'_MAP': map})
                    for map in maps)
    tree = tree._replace(body=header + tree.body)
    return tree


class MainCallAdder(P.NodeTransformer):
    
    """Add boilerplate to call main(), if this function is present."""
    
    def process(self, tree):
        self.has_main = False
        tree = super().process(tree)
        return tree
    
    def visit_Module(self, node):
        node = self.generic_visit(node)
        
        if self.has_main:
            node = node._replace(body=node.body + (main_boilerplate_stmt,))
        return node
    
    def visit_FunctionDef(self, node):
        if node.name == 'main':
            self.has_main = True


class RuntimeImportPostprocessor(P.NodeTransformer):
    
    """Add a line to import the runtime library."""
    
    def visit_Module(self, node):
        import_stmt = P.Parser.ps('from incoq.mars.runtime import *')
        return node._replace(body=(import_stmt,) + node.body)


class PassPostprocessor(P.NodeTransformer):
    
    """Add a Pass statement to any empty suite."""
    
    # Just handle FunctionDef, For, While, and If. Don't worry about
    # other nodes. Don't touch the orelse field since it's allowed
    # to be empty (indicating no orelse logic).
    
    def suite_helper(self, node):
        node = self.generic_visit(node)
        
        if len(node.body) == 0:
            node = node._replace(body=[P.Pass()])
        return node
    
    visit_FunctionDef = suite_helper
    visit_For = suite_helper
    visit_While = suite_helper
    visit_If = suite_helper
