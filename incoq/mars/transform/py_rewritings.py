"""Pre- and post-processings applied at the Python AST level."""


__all__ = [
    # Preprocessings are paired with their postprocessings,
    # and listed in order of their application, outermost-first.
    
    'ConstructPreprocessor',
    
    'PassPostprocessor',
    
    'RuntimeImportPreprocessor',
    'RuntimeImportPostprocessor',
    
    'MainCallRemover',
    'MainCallAdder',
    
    'preprocess_vardecls',
    'postprocess_vardecls',
    
    'SymbolInfoImporter',
    
    # Main exports.
    'py_preprocess',
    'py_postprocess',
]


from incoq.util.seq import pairs
from incoq.util.type import typechecked
from incoq.util.collections import OrderedSet

from incoq.mars.incast import P, L


main_boilerplate_stmt = P.Parser.ps('''
    if __name__ == '__main__':
        main()
    ''')


class ConstructPreprocessor(P.NodeTransformer):
    
    """Preprocessor for Python code that eliminates some syntactic
    constructs that can't be directly expressed in IncAST.
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
    
    def visit_For(self, node):
        node = self.generic_visit(node)
        
        # Translate tuple decomposition into a separate assignment.
        if isinstance(node.target, P.Tuple):
            # TODO: Use a passed in generator of fresh var names.
            var = '_v'
            decomp_stmt = P.Assign([node.target], P.Name(var, P.Load()))
            new_body = (decomp_stmt,) + node.body
            node = node._replace(target=P.Name(var, P.Store()),
                                 body=new_body)
        
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


class RuntimeImportPostprocessor(P.NodeTransformer):
    
    """Add a line to import the runtime library."""
    
    def visit_Module(self, node):
        import_stmt = P.Parser.ps('from incoq.mars.runtime import *')
        return node._replace(body=(import_stmt,) + node.body)


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


class SymbolInfoImporter(P.MacroProcessor):
    
    """Parse and remove OPTIONS and INFO directives, whose forms are:
    
        OPTIONS(<key>=<value>, ...)
        INFO(<sym>, <key>=<value>, ...)
    
    Return a list of options dictionaries and a list of pairs of symbol
    names and info dictionaries.
    """
    
    def process(self, tree):
        self.options = []
        self.syminfo = []
        tree = super().process(tree)
        return tree, self.options, self.syminfo
    
    @typechecked
    def handle_fs_OPTIONS(self, _func, **kargs):
        opts = {}
        for k, v in kargs.items():
            opts[k] = P.LiteralEvaluator.run(v)
        self.options.append(opts)
        return ()
    
    @typechecked
    def handle_fs_INFO(self, _func, symbol:P.Name, **kargs):
        name = symbol.id
        info = {}
        for k, v in kargs.items():
            info[k] = P.LiteralEvaluator.run(v)
        self.syminfo.append((name, info))
        return ()


def py_preprocess(tree, symtab, config):
    # Admit some constructs as syntactic sugar that would otherwise
    # be excluded from IncAST.
    tree = ConstructPreprocessor.run(tree)
    # Get rid of import statement and qualifiers for the runtime
    # library.
    tree = RuntimeImportPreprocessor.run(tree)
    # Get rid of main boilerplate.
    tree = MainCallRemover.run(tree)
    # Get relation declarations.
    tree, rels = preprocess_vardecls(tree)
    for rel in rels:
        symtab.define_relation(rel)
    # Get symbol info.
    tree, options, syminfo = SymbolInfoImporter.run(tree)
    for opt in options:
        config.update(**opt)
    for name, info in syminfo:
        symtab.apply_syminfo(name, info)
    return tree


def py_postprocess(tree, symtab):
    rels = list(symtab.get_relations().keys())
    maps = list(symtab.get_maps().keys())
    # Add in declarations for relations.
    tree = postprocess_vardecls(tree, rels, maps)
    # Add in main boilerplate, if main() is defined.
    tree = MainCallAdder.run(tree)
    # Add the runtime import statement.
    tree = RuntimeImportPostprocessor.run(tree)
    # Correct any missing Pass statements.
    tree = PassPostprocessor.run(tree)
    return tree
