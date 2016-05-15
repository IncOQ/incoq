"""Pre- and post-processings applied at the Python AST level."""


__all__ = [
    # Preprocessings are paired with their postprocessings,
    # and listed in order of their application, outermost-first.
    
    'preprocess_query_directives',
    
    'preprocess_constructs',
    
    'postprocess_header',
    
    'postprocess_pass',
    
    'preprocess_runtime_import',
    'postprocess_runtime_import',
    
    'preprocess_main_call',
    'postprocess_main_call',
    
    'preprocess_var_decls',
    'postprocess_var_decls',
    
    'preprocess_directives',
    
    # Main exports.
    'py_preprocess',
    'py_postprocess',
]


from types import SimpleNamespace

from incoq.util.seq import pairs
from incoq.util.type import typechecked
from incoq.util.collections import OrderedSet

from incoq.compiler.incast import P, L


class QueryDirectiveRewriter(P.NodeTransformer):
    
    """Take QUERY(<source>, **<kargs>) directives and replace the
    first argument with the corresponding parsed Python AST.
    """
    
    # We'll use NodeTransformer rather than MacroProcessor because
    # MacroProcessor makes it hard to reconstruct the node.
    
    pat = P.Expr(P.Call(P.Name('QUERY', P.Load()),
                        [P.Str(P.PatVar('_source'))],
                        P.PatVar('_keywords'),
                        None, None))
    
    def visit_Expr(self, node):
        match = P.match(self.pat, node)
        if match is not None:
            query = P.Parser.pe(node.value.args[0].s)
            call = node.value._replace(args=[query])
            node = node._replace(value=call)
        return node

preprocess_query_directives = QueryDirectiveRewriter.run


class ConstructRewriter(P.NodeTransformer):
    
    """Rewrite some syntactic constructs that can't be directly
    expressed in IncAST.
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

preprocess_constructs = ConstructRewriter.run


def postprocess_header(tree, header):
    """Add comment lines for each string in header."""
    header = tuple(P.Parser.ps('COMMENT(_S)', subst={'_S': P.Str(line)})
                   for line in header)
    return tree._replace(body=header + tree.body)


class PassAdder(P.NodeTransformer):
    
    """Add a Pass statement to any empty suite."""
    
    # Just handle FunctionDef, ClassDef, For, While, and If.
    # Don't worry about other nodes. Don't touch the orelse field since
    # it's allowed to be empty (indicating no orelse logic).
    
    def suite_helper(self, node):
        node = self.generic_visit(node)
        
        if len(node.body) == 0:
            node = node._replace(body=[P.Pass()])
        return node
    
    visit_FunctionDef = suite_helper
    visit_ClassDef = suite_helper
    visit_For = suite_helper
    visit_While = suite_helper
    visit_If = suite_helper

postprocess_pass = PassAdder.run


class RuntimeImportRemover(P.NodeTransformer):
    
    """Eliminate the runtime import statement and turn qualified
    names from the runtime into unqualified names, e.g.,
    
        incoq.runtime.Set -> Set
    
    The recognized import forms are:
    
        import incoq.runtime
        import incoq.runtime as <alias>
        from incoq.runtime import *
    
    If <alias> is used, the alias prefix is removed from qualified
    names.
    """
    
    def __init__(self):
        super().__init__()
    
    def process(self, tree):
        self.quals = set()
        self.quals.add(P.Parser.pe('incoq.runtime'))
        return super().process(tree)
    
    def visit_Import(self, node):
        pat = P.Import([P.alias('incoq.runtime', P.PatVar('_ALIAS'))])
        match = P.match(pat, node)
        if match is None:
            return node
        
        # Remove the import. Record the alias to remove its uses.
        if match['_ALIAS'] is not None:
            qual = P.Name(match['_ALIAS'], P.Load())
            self.quals.add(qual)
        return []
    
    def visit_ImportFrom(self, node):
        pat = P.Parser.ps('from incoq.runtime import *')
        if node != pat:
            return node
        
        return []
    
    def visit_Attribute(self, node):
        # Note: As written, this will remove all aliases, not just the
        # prefix alias. That is, if A is an alias for the runtime in
        # quals, this will rewrite A.A...A.foo as foo. This shouldn't
        # be a problem because we shouldn't see aliases chained in this
        # manner. 
        
        node = self.generic_visit(node)
        
        # Check prefix against each alias and the fully qualified path.
        # If none match, no change.
        for qual in self.quals:
            pat = P.Attribute(qual, P.PatVar('_ATTR'), P.Load())
            match = P.match(pat, node)
            if match is not None:
                break
        else:
            return node
        
        return P.Name(match['_ATTR'], P.Load())


class RuntimeImportAdder(P.NodeTransformer):
    
    """Add a line to import the runtime library."""
    
    def visit_Module(self, node):
        import_stmt = P.Parser.ps('from incoq.runtime import *')
        return node._replace(body=(import_stmt,) + node.body)


preprocess_runtime_import = RuntimeImportRemover.run
postprocess_runtime_import = RuntimeImportAdder.run


main_boilerplate_stmt = P.Parser.ps('''
    if __name__ == '__main__':
        main()
    ''')


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
    
    # TODO: Instead of checking for main() to be defined syntactically,
    # refactor so that we get this info passed in from the symbol table.
    # Has to wait until we track function definitions in symbol table.
    
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


preprocess_main_call = MainCallRemover.run
postprocess_main_call = MainCallAdder.run


def preprocess_var_decls(tree):
    """Eliminate global variable declarations of the form
    
        S = Set()
        M = Map()
    
    and return a list of pairs of variables names and type names (i.e.,
    'Set' or 'Map').
    """
    assert isinstance(tree, P.Module)
    pat = P.Assign([P.Name(P.PatVar('_VAR'), P.Wildcard())],
                   P.Call(P.Name(P.PatVar('_KIND'), P.Load()),
                          [], [], None, None))
    
    decls = OrderedSet()
    body = []
    changed = False
    for stmt in tree.body:
        match = P.match(pat, stmt)
        if match is not None:
            var, kind = match['_VAR'], match['_KIND']
            if kind not in ['Set', 'Map']:
                raise L.ProgramError('Unknown declaration initializer {}'
                                     .format(kind))
            decls.add((var, kind))
            changed = True
        else:
            body.append(stmt)
    
    if changed:
        tree = tree._replace(body=body)
    return tree, list(decls)


def postprocess_var_decls(tree, decls):
    """Prepend global variable declarations to the program. Each given
    declaration is a triple of a variable name, type name (e.g., 'Set'
    or 'Map'), and a declaration comment string.
    """
    assert isinstance(tree, P.Module)
    header = ()
    for var_name, type_name, comment in decls:
        header += P.Parser.pc('''
            COMMENT(_S)
            _VAR = _TYPE()
            ''', subst={'_S': P.Str(comment),
                        '_VAR': var_name,
                        '_TYPE': type_name})
    tree = tree._replace(body=header + tree.body)
    return tree


class DirectiveReader(P.MacroProcessor):
    
    """Parse and remove directives of the forms:
    
        CONFIG(<key>=<value>, ...)
        SYMCONFIG(<sym>, <key>=<value>, ...)
        QUERY(<source>, <key>=<value>, ...)
    
    Return a pair of the modified tree and an object with fields
    corresponding to each kind of directive. Each field holds a list
    of objects representing the parsed information for an occurrence
    of the corresponding kind of directive.
    
        Directive   Field            Element type
        CONFIG      config_info      dictionary
        SYMCONFIG   symconfig_info   pair of symbol name and dictionary
        QUERY       query_info       pair of query expression (Python AST)
                                       and dictionary
    """
    
    # Caution: QUERY is overloaded as both an in-line expression
    # annotation and as a top-level directive statement. The in-line
    # form is taken care of by the importing to IncAST that comes after
    # these Python rewriters. The directive statement is handled here
    # and not by the usual L.Parser.p*() functions.
    
    def process(self, tree):
        self.info = SimpleNamespace(config_info=[],
                                    symconfig_info=[],
                                    query_info=[])
        tree = super().process(tree)
        return tree, self.info
    
    @typechecked
    def handle_fs_CONFIG(self, _func, **kargs):
        d = {}
        for k, v in kargs.items():
            d[k] = P.literal_eval(v)
        self.info.config_info.append(d)
        return ()
    
    @typechecked
    def handle_fs_SYMCONFIG(self, _func, symbol:P.Str, **kargs):
        name = symbol.s
        d = {}
        for k, v in kargs.items():
            d[k] = P.literal_eval(v)
        self.info.symconfig_info.append((name, d))
        return ()
    
    @typechecked
    def handle_fs_QUERY(self, _func, query, **kargs):
        d = {}
        for k, v in kargs.items():
            d[k] = P.literal_eval(v)
        self.info.query_info.append((query, d))
        return ()

preprocess_directives = DirectiveReader.run


def py_preprocess(tree):
    """Take in a Python AST tree, partially preprocess it, and return
    the corresponding IncAST tree along with parsed information.
    """
    # Rewrite QUERY directives to replace their source strings with
    # the corresponding parsed Python ASTs. Provided that the other
    # preprocessing steps are functional (i.e., apply equally to
    # multiple occurrences of the same AST), this ensures that any
    # subsequent steps that modify occurrences of a query will also
    # modify its occurrence in the QUERY directive.
    tree = preprocess_query_directives(tree)
    
    # Admit some constructs as syntactic sugar that would otherwise
    # be excluded from IncAST.
    tree = preprocess_constructs(tree)
    
    # Get rid of import statement and qualifiers for the runtime
    # library.
    tree = preprocess_runtime_import(tree)
    
    # Get rid of main boilerplate.
    tree = preprocess_main_call(tree)
    
    # Get relation declarations.
    tree, decls = preprocess_var_decls(tree)
    
    # Get symbol info.
    tree, info = preprocess_directives(tree)
    
    # Convert the tree and parsed query info to IncAST.
    tree = L.import_incast(tree)
    info.query_info = [(L.import_incast(query), value)
                       for query, value in info.query_info]
    
    return tree, decls, info


def py_postprocess(tree, *, decls, header):
    """Take in an IncAST tree, postprocess it, and return the
    corresponding Python AST tree. See postprocess_var_decls()
    for the format of decls.
    """
    # Convert to Python AST.
    tree = L.export_incast(tree)
    
    # Add in declarations for relations.
    tree = postprocess_var_decls(tree, decls)
    
    # Add in main boilerplate, if main() is defined.
    tree = postprocess_main_call(tree)
    
    # Add the runtime import statement.
    tree = postprocess_runtime_import(tree)
    
    # Correct any missing Pass statements.
    tree = postprocess_pass(tree)
    
    # Add header information.
    tree = postprocess_header(tree, header)
    
    return tree
