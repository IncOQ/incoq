"""Initial preprocessing for programs."""


__all__ = [
    'add_runtimelib',
    'remove_runtimelib',
    'OptionsParser',
    'parse_options',
    'infer_params',
    'attach_qopts_info',
    'MaintExpander',
    'export_program',
]


from .nodes import *
from .structconv import parse_structast, NodeTransformer
from .error import ProgramError
from .helpers import is_importstar, get_importstar
from .util import ScopeVisitor, VarsFinder, N
from .nodeconv import comp_to_setcomp
from .macros import IncMacroProcessor


def ts(tree):
    # Wrap the import for the package-level ts.
    from . import ts
    return ts(tree)


def add_runtimelib(tree):
    """Add the runtime import."""
    stmt = parse_structast('from invinc.runtime import *', mode='stmt')
    tree = tree._replace(body=(stmt,) + tree.body)
    return tree

def remove_runtimelib(tree):
    """Remove imports of form "from invinc.runtime import *"."""
    class Trans(NodeTransformer):
        def visit_ImportFrom(self, node):
            if is_importstar(node):
                module = get_importstar(node)
                if module == 'invinc.runtime':
                    return ()
    
    return Trans.run(tree)


def normalize_qopt(qstr):
    return IncMacroProcessor.run(parse_structast(qstr, mode='expr'))

class OptionsParser(NodeTransformer):
    
    """Gather all options together into an aggregated opts structure,
    comprising a pair of nopts and qopts dictionaries. Return a pair
    of the tree stripped of options nodes, and this opts structure.
    """
    
    def __init__(self, ext_opts=None):
        if ext_opts is None:
            ext_opts = ({}, {})
        self.nopts, self.qopts = ext_opts
    
    def process(self, tree):
        tree = super().process(tree)
        return tree, (self.nopts, self.qopts)
    
    def visit_NOptions(self, node):
        overlap = set(self.nopts.keys()).intersection(node.opts.keys())
        if len(overlap) > 0:
            raise ProgramError('Options declarations overlap on keys: ' +
                               ', '.join(overlap))
        
        self.nopts.update(node.opts)
        
        return ()
    
    def visit_QOptions(self, node):
        query = normalize_qopt(node.query)
        if query in self.qopts:
            raise ProgramError('Multiple query options declarations for ' +
                               ts(query))
        
        self.qopts[query] = node.opts
        
        return ()

def parse_options(tree, *, ext_opts=None):
    """Process and remove options directives from the tree.
    Return a tuple of the tree and the options info.
    
    If ext_opts is given, it is used to augment the options info,
    as if they were specified in the program.
    """
    # Normalize external qopts so that the keys are nodes instead
    # of source strings.
    if ext_opts is not None:
        ext_nopts, ext_qopts = ext_opts
        for k, v in dict(ext_qopts).items():
            new_k = normalize_qopt(k)
            ext_qopts[new_k] = v
            del ext_qopts[k]
        ext_opts = (ext_nopts, ext_qopts)
    
    return OptionsParser.run(tree, ext_opts)


def infer_params(tree, *, obj_domain):
    """Fill in omitted parameter information for queries by looking
    at what variables are bound in the scope of their occurrence.
    
    If obj_domain is True, the right-hand sides of comprehension
    enumerators are considered for finding uses of parameters.
    """
    # We consider a variable in a query to be a parameter if, at
    # the time the query is processed, the variable is in one of
    # the lexical scopes containing the query.
    #
    # This can cause confusion, as these semantics differ from Python.
    # For example, in Python you can define a global variable after
    # the function that uses it, so long as it is defined before
    # the function is called. This analysis makes no such allowance.
    #
    # The wildcard identifier '_' is never considered a parameter.
    #
    # Since ScopeVisitor is not written in a NodeTransformer-compatible
    # way, we take a two-pass approach. First, a map is built from
    # each query to a list of the scope information for each of its
    # occurrences. This scope info is just a set of the bound variables
    # of all lexical scopes containing the occurrence. Then, the
    # occurrences are processed again and assigned their parameter
    # information.
    
    scope_map = {}
    
    class ScopeMapper(ScopeVisitor):
        def visit_Comp(self, node):
            super().visit_Comp(node)
            occurrences = scope_map.setdefault(node, [])
            occurrences.append(self.current_bvars())
    
    ScopeMapper.run(tree)
    
    class ParamFiller(NodeTransformer):
        def visit_Comp(self, node):
            # Do the scope_map lookup before we modify
            # this node recursively.
            bvars = scope_map[node].pop(0)
            node = self.generic_visit(node)
            
            if node.params is None:
                qvars = VarsFinder.run(node, ignore_functions=True,
                                       ignore_rels=not obj_domain)
                qvars.discard('_')
                pvars = tuple(qvars.intersection(bvars))
                return node._replace(params=pvars)
    
    tree = ParamFiller.run(tree)
    return tree


def attach_qopts_info(tree, opts):
    """Attach query options info to queries. Return the new tree
    and a list of unmatched query options strings.
    
    Parameter information is also attached to queries, from the
    'params' option key.
    
    It is an error if parameter or option information is given
    when it is already specified in the node.
    
    Afterwards, all queries will have their options field set,
    although the params field may still be None.
    """
    _nopts, qopts = opts
    unused = set(qopts.keys())
    
    class Trans(NodeTransformer):
        
        # Attach options info before recursing, since we need
        # the old node for lookup into qopts.
        
        def visit_Comp(self, node):
            options = qopts.get(node, None)
            unused.discard(node)
            
            if options is not None:
                if node.options is not None:
                    raise ProgramError('Options info already exists '
                                       'for query ' + ts(node))
            else:
                options = node.options if node.options is not None else {}
            options = dict(options)
            
            params = options.pop('params', None)
            if params is not None:
                if node.params is not None:
                    ProgramError('Parameter info already exists '
                                 'for query ' + ts(node))
                params = tuple(params)
            else:
                params = node.params
            
            node = node._replace(params=params, options=options)
            node = self.generic_visit(node)
            return node
        
        def visit_Aggregate(self, node):
            options = qopts.get(node, None)
            unused.discard(node)
            
            if options is not None:
                if node.options is not None:
                    raise ProgramError('Options info already exists '
                                       'for query ' + ts(node))
            else:
                options = node.options if node.options is not None else {}
            options = dict(options)
            
            node = node._replace(options=options)
            node = self.generic_visit(node)
            return node
    
    tree = Trans.run(tree)
    
    return tree, unused


class MaintExpander(NodeTransformer):
    
    """Replace Maintenance nodes with the concatenation of their
    code.
    """
    
    def visit_Maintenance(self, node):
        from . import ts
        
        node = self.generic_visit(node)
        
        precode = node.precode
        postcode = node.postcode
        
        def wrap(when, code):
            template = '{} maint {} {} "{}"'
            begintext = template.format(
                'Begin', node.name, when, node.desc)
            endtext = template.format(
                'End', node.name, when, node.desc)
            
            return (Comment(begintext),) + code + (Comment(endtext),)
        
        if len(precode) > 0:
            precode = wrap('before', precode)
        if len(postcode) > 0:
            postcode = wrap('after', postcode)
        
        return precode + node.update + postcode


class TreeExporter(NodeTransformer):
    
    """Helper for export_program()."""
    
    def p(self, source, mode=None, subst=None):
        return parse_structast(source, mode=mode, subst=subst)
    
    def pc(self, source, **kargs):
        return self.p(source, mode='code', **kargs)
    
    def pe(self, source, **kargs):
        return self.p(source, mode='expr', **kargs)
    
    def visit_NOptions(self, node):
        return ()
    
    def visit_QOptions(self, node):
        return ()
    
    def visit_IsEmpty(self, node):
        node = self.generic_visit(node)
        return self.pe('len(TARGET) == 0',
                       subst={'TARGET': node.target})
    
    def visit_AssignKey(self, node):
        node = self.generic_visit(node)
        return self.pc('TARGET[KEY] = VALUE',
                       subst={'TARGET': node.target,
                              'KEY': node.key,
                              'VALUE': node.value})
    
    def visit_DelKey(self, node):
        node = self.generic_visit(node)
        return self.pc('del TARGET[KEY]',
                       subst={'TARGET': node.target,
                              'KEY': node.key})
    
    def visit_Lookup(self, node):
        node = self.generic_visit(node)
        if node.default is not None:
            code = self.pe('TARGET[KEY] if KEY in TARGET else DEFAULT',
                           subst={'TARGET': node.target,
                                  'KEY': node.key,
                                  'DEFAULT': node.default})
        else:
            code = self.pe('TARGET[KEY]',
                           subst={'TARGET': node.target,
                                  'KEY': node.key})
        return code
    
    def visit_ImgLookup(self, node):
        node = self.generic_visit(node)
        return self.pe('TARGET[KEY] if KEY in TARGET else set()',
                       subst={'TARGET': node.target,
                              'KEY': node.key})
    
    def visit_RCImgLookup(self, node):
        node = self.generic_visit(node)
        return self.pe('TARGET[KEY] if KEY in TARGET else RCSet()',
                       subst={'TARGET': node.target,
                              'KEY': node.key})
    
    def visit_DemQuery(self, node):
        node = self.generic_visit(node)
        call = Call(func=Name(N.queryfunc(node.demname), Load()),
                    args=node.args,
                    keywords=[],
                    starargs=None,
                    kwargs=None)
        if node.value is not None:
            code = BoolOp(op=And(), values=(call, node.value))
        else:
            code = call
        return code
    
    def visit_NoDemQuery(self, node):
        node = self.generic_visit(node)
        return node.value
    
    def visit_Comp(self, node):
        node = self.generic_visit(node)
        return comp_to_setcomp(node)
    
    def visit_Aggregate(self, node):
        node = self.generic_visit(node)
        return self.pe('OP(VALUE)',
                       subst={'OP': node.op,
                              'VALUE': node.value})


def export_program(tree):
    """Return an AST stripped of information that should not be in
    the output Python code. In particular, options and parameter
    information is removed from queries, and options directives are
    removed.
    """
    # Although options directives shouldn't be in the tree at
    # this stage anyway.
    return TreeExporter.run(tree)
