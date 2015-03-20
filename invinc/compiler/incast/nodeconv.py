"""Macro processors for converting between IncAST nodes and their
PyAST equivalent operations.
"""


__all__ = [
    'IncLangImporter',
    'IncLangExporter',
    'comp_to_setcomp',
]


from numbers import Number

from invinc.util.collections import make_frozen, frozendict

from .nodes import *
from .structconv import (NodeTransformer, parse_structast, MacroProcessor,
                         astargs, literal_eval)


def frozen_eval(tree):
    return make_frozen(literal_eval(tree))

def frozen_eval_dict(d):
    # As above but the keys are strings instead of ASTs.
    return {k: frozen_eval(v) for k, v in d.items()}

def value_to_ast(value):
    """Turn a structure of python values into an AST for a literal
    expression. Valid values include dictionaries, sets, lists,
    tuples, bools, numbers, strings, and None. ASTs are created with
    Load context. Set and dictionary contents are sorted.
    """
    if isinstance(value, (dict, frozendict)):
        if len(value) == 0:
            return Dict((), ())
        keys, vals = zip(*sorted(value.items()))
        keys = tuple(value_to_ast(k) for k in keys)
        vals = tuple(value_to_ast(v) for v in vals)
        return Dict(keys, vals)
    
    elif isinstance(value, (set, frozenset)):
        items = tuple(sorted(value_to_ast(i) for i in value))
        return Set(items)
    elif isinstance(value, list):
        items = tuple(value_to_ast(i) for i in value)
        return List(items, Load())
    elif isinstance(value, tuple):
        items = tuple(value_to_ast(i) for i in value)
        return Tuple(items, Load())
    
    elif isinstance(value, bool):
        return NameConstant(value)
    elif isinstance(value, Number):
        return Num(value)
    elif isinstance(value, str):
        return Str(value)
    
    elif isinstance(value, type(None)):
        return NameConstant(None)
    
    else:
        raise TypeError('Can\'t convert value to AST: ' + repr(value))


class IncLangImporter(MacroProcessor):
    
    """Expand PyAST patterns that encode IncAST nodes."""
    
    # Misc operations.
    
    @astargs
    def handle_fs_Comment(self, f, text:'Str'):
        return Comment(text)
    
    @astargs
    def handle_fs_OPTIONS(self, f, **opts):
        return NOptions(frozen_eval_dict(opts))
    
    @astargs
    def handle_fs_QUERYOPTIONS(self, f, query:'Str', **opts):
        return QOptions(query, frozen_eval_dict(opts))
    
    @astargs
    def handle_fw_MAINT(self, f, name:'Name', when:'Str', desc:'Str', _body):
        _body = self.visit(_body)
        if when == 'before':
            precode = _body[:-1]
            update = _body[-1:]
            postcode = ()
        elif when == 'after':
            precode = ()
            update = _body[0:1]
            postcode = _body[1:]
        else:
            assert()
        
        return Maintenance(name, desc, precode, update, postcode)
    
    # Allows specifying params and options for a Comp.
    @astargs
    def handle_fe_COMP(self, f, comp, params=None, options=None):
        comp = self.generic_visit(comp)
        
        # TODO: refactor this arg processing into astargs.
        
        if params is not None:
            if isinstance(params, NameConstant) and params.value is None:
                params = None
            else:
                if not (isinstance(params, (List, Tuple)) and
                            all(isinstance(e, Name) for e in params.elts)):
                        raise TypeError('Expected list of identifiers')
                params = tuple(p.id for p in params.elts)
        
        if options is not None:
            if isinstance(options, NameConstant) and options.value is None:
                options = None
            else:
                options = frozen_eval(options)
        
        comp = comp._replace(params=params, options=options)
        return comp
    
    @astargs
    def handle_fe_DEMQUERY(self, f, demname:'Name', args:'List', value):
        if isinstance(value, NameConstant) and value.value is None:
            value = None
        return DemQuery(demname, args, value)
    
    def handle_fe_NODEMQUERY(self, f, value):
        return NoDemQuery(value)
    
    handle_fe_NODEMAND = handle_fe_NODEMQUERY
    
    # Set operations.
    
    def handle_ms_add(self, f, target, elem):
        return SetUpdate(target, 'add', elem)
    
    def handle_ms_remove(self, f, target, elem):
        return SetUpdate(target, 'remove', elem)
    
    def handle_ms_update(self, f, target, other):
        return MacroUpdate(target, 'union', other)
    
    def handle_ms_intersection_update(self, f, target, other):
        return MacroUpdate(target, 'inter', other)
    
    def handle_ms_difference_update(self, f, target, other):
        return MacroUpdate(target, 'diff', other)
    
    def handle_ms_symmetric_difference_update(self, f, target, other):
        return MacroUpdate(target, 'symdiff', other)
    
    def handle_ms_assign_update(self, f, target, other):
        return MacroUpdate(target, 'assign', other)
    
    def handle_ms_clear(self, f, target):
        return MacroUpdate(target, 'clear', None)
    
    def handle_ms_mapassign_update(self, f, target, other):
        return MacroUpdate(target, 'mapassign', other)
    
    def handle_ms_mapclear(self, f, target):
        return MacroUpdate(target, 'mapclear', None)
    
    def handle_ms_incref(self, f, target, elem):
        return RCSetRefUpdate(target, 'incref', elem)
    
    def handle_ms_decref(self, f, target, elem):
        return RCSetRefUpdate(target, 'decref', elem)
    
    def handle_me_isempty(self, f, target):
        return IsEmpty(target)
    
    def handle_me_getref(self, f, target, elem):
        return GetRef(target, elem)
    
    # Map operations.
    
    def handle_ms_assignkey(self, f, target, key, value):
        return AssignKey(target, key, value)
    
    def handle_ms_delkey(self, f, target, key):
        return DelKey(target, key)
    
    def handle_me_lookup(self, f, target, key):
        return Lookup(target, key, None)
    
    def handle_me_deflookup(self, f, target, key, default):
        return Lookup(target, key, default)
    
    def handle_me_imglookup(self, f, target, key):
        return ImgLookup(target, key)
    
    def handle_me_rcimglookup(self, f, target, key):
        return RCImgLookup(target, key)
    
    # Setmap operations.
    
    @astargs
    def handle_me_smlookup(self, f, target, mask:'Str', key):
        return SMLookup(target, mask, key, None)
    
    @astargs
    def handle_me_smdeflookup(self, f, target, mask:'Str', key, default):
        return SMLookup(target, mask, key, default)
    
    # Query operations.
    
    @astargs
    def handle_fe_setmatch(self, f, target, mask:'Str', key):
        return SetMatch(target, mask, key)
    
    @astargs
    def handle_fe_deltamatch(self, f, target, mask:'Str', elem, limit:'Num'):
        return DeltaMatch(target, mask, elem, limit)
    
    def visit_SetComp(self, node):
        node = self.generic_visit(node)
        
        # Turn a SetComp's generators into a list of
        # Enumerator and expression nodes.
        clauses = []
        for gen in node.generators:
            ifs = gen.ifs
            enum = Enumerator(gen.target, gen.iter)
            clauses.append(enum)
            clauses.extend(ifs)
        
        return Comp(node.elt, tuple(clauses), None, None)
    
    @astargs
    def aggr_helper(self, f, value, options=None):
        assert f in ['count', 'sum', 'min', 'max'], \
            'Unknown aggregate "{}"'.format(f)
        
        if options is not None:
            if isinstance(options, NameConstant) and options.id is None:
                options = None
            else:
                options = frozen_eval(options)
        
        return Aggregate(value, f, options)
    
    handle_fe_count = aggr_helper
    handle_fe_sum = aggr_helper
    handle_fe_min = aggr_helper
    handle_fe_max = aggr_helper


class IncLangExporter(NodeTransformer):
    
    """Export IncAST-specific nodes to PyAST format.
    
    Some information is lost. This includes options dictionaries
    and query parameter info. The result is not necessarily
    round-trippable.
    """
    
    def pc(self, source, subst=None):
        return parse_structast(source, mode='code', subst=subst)
    
    def pe(self, source, subst=None):
        return parse_structast(source, mode='expr', subst=subst)
    
    def visit_NOptions(self, node):
        return self.pc('OPTIONS(...)')
    
    def visit_QOptions(self, node):
        return self.pc('QUERYOPTIONS(QSTR, ...)',
                       subst={'QSTR': node.query})
    
    def visit_Maintenance(self, node):
        node = self.generic_visit(node)
        
        precode = node.precode
        if len(precode) > 0:
            precode = precode + (Comment('^-- Precode'),)
        postcode = node.postcode
        if len(postcode) > 0:
            postcode = (Comment('Postcode --v'),) + postcode
        
        return self.pc('''
            with MAINT(NAME, DESC):
                PRECODE
                UPDATE
                POSTCODE
            ''', subst={'NAME': Name(node.name, Load()),
                        'DESC': Str(node.desc),
                        '<c>PRECODE': precode,
                        '<c>UPDATE': node.update,
                        '<c>POSTCODE': postcode})
    
    def set_helper(self, node):
        node = self.generic_visit(node)
        return self.pc('TARGET.OP(ELEM)',
                       subst={'TARGET': node.target,
                              '@OP': node.op,
                              'ELEM': node.elem})
    
    visit_SetUpdate = set_helper
    visit_RCSetRefUpdate = set_helper
    
    def visit_MacroUpdate(self, node):
        op = {'union': 'update',
              'inter': 'intersection_update',
              'diff': 'difference_update',
              'symdiff': 'symmetric_difference_update',
              'assign': 'assign_update',
              'clear': 'clear',
              'mapassign': 'mapassign_update',
              'mapclear': 'mapclear'}[node.op]
        if op == 'clear':
            return self.pc('TARGET.clear()',
                           subst={'TARGET': node.target})
        else:
            return self.pc('TARGET.OP(OTHER)',
                           subst={'TARGET': node.target,
                                  '@OP': op,
                                  'OTHER': node.other})
    
    def visit_AssignKey(self, node):
        node = self.generic_visit(node)
        return self.pc('TARGET.assignkey(KEY, VALUE)',
                       subst={'TARGET': node.target,
                              'KEY': node.key,
                              'VALUE': node.value})
    
    def visit_DelKey(self, node):
        node = self.generic_visit(node)
        return self.pc('TARGET.delkey(KEY)',
                       subst={'TARGET': node.target,
                              'KEY': node.key})
    
    def visit_IsEmpty(self, node):
        node = self.generic_visit(node)
        return self.pe('TARGET.isempty()',
                       subst={'TARGET': node.target})
    
    def visit_GetRef(self, node):
        node = self.generic_visit(node)
        return self.pe('TARGET.getref(ELEM)',
                       subst={'TARGET': node.target,
                              'ELEM': node.elem})
    
    def visit_Lookup(self, node):
        node = self.generic_visit(node)
        default = (node.default if node.default is not None
                   else NameConstant(None))
        return self.pe('TARGET.lookup(KEY, DEFAULT)',
                       subst={'TARGET': node.target,
                              'KEY': node.key,
                              'DEFAULT': default})
    
    def visit_ImgLookup(self, node):
        node = self.generic_visit(node)
        return self.pe('TARGET.imglookup(KEY)',
                       subst={'TARGET': node.target,
                              'KEY': node.key})
    
    def visit_RCImgLookup(self, node):
        node = self.generic_visit(node)
        return self.pe('TARGET.rcimglookup(KEY)',
                       subst={'TARGET': node.target,
                              'KEY': node.key})
    
    def visit_SMLookup(self, node):
        node = self.generic_visit(node)
        default = (node.default if node.default is not None
                   else NameConstant(None))
        return self.pe('TARGET.smlookup(MASK, KEY, DEFAULT)',
                       subst={'TARGET': node.target,
                              'MASK': Str(node.mask),
                              'KEY': node.key,
                              'DEFAULT': default})
    
    def visit_DemQuery(self, node):
        node = self.generic_visit(node)
        args_list = List(node.args, Load())
        return self.pe('DEMQUERY(DEMNAME, ARGS, VALUE)',
                       subst={'DEMNAME': Name(node.demname, Load()),
                              'ARGS': args_list,
                              'VALUE': node.value})
    
    def visit_NoDemQuery(self, node):
        node = self.generic_visit(node)
        return self.pe('NODEMQUERY(VALUE)',
                       subst={'VALUE': node.value})
    
    def visit_SetMatch(self, node):
        node = self.generic_visit(node)
        return self.pe('setmatch(TARGET, MASK, KEY)',
                       subst={'TARGET': node.target,
                              'MASK': Str(node.mask),
                              'KEY': node.key})
    
    def visit_DeltaMatch(self, node):
        node = self.generic_visit(node)
        return self.pe('deltamatch(TARGET, MASK, ELEM, LIMIT)',
                       subst={'TARGET': node.target,
                              'MASK': Str(node.mask),
                              'ELEM': node.elem,
                              'LIMIT': Num(node.limit)})
    
    def visit_Enumerator(self, node):
        # Enumerators are converted by comp_to_setcomp() inside
        # visit_Comp(). Nonetheless, we still need to handle them
        # in this visitor in order to transform other nested
        # expressions, and to be able to print source for
        # Enumerator nodes by themselves.
        node = self.generic_visit(node)
        return comprehension(node.target, node.iter, ())
    
    def visit_Comp(self, node):
        node = self.generic_visit(node)
        setcomp = comp_to_setcomp(node)
        if node.params is None:
            paramslist = NameConstant(None)
        else:
            paramslist = List(tuple(Name(p, Load())
                                    for p in node.params), Load())
        opts = value_to_ast(node.options)
        result = self.pe('COMP(SETCOMP, PARAMS, OPTS)',
                         subst={'SETCOMP': setcomp,
                                'PARAMS': paramslist,
                                'OPTS': opts})
        result = result._replace(type=node.type)
        return result
    
    def visit_Aggregate(self, node):
        node = self.generic_visit(node)
        opts = value_to_ast(node.options)
        return self.pe('OP(VALUE, OPTS)',
                       subst={'OP': node.op,
                              'VALUE': node.value,
                              'OPTS': opts})


def comp_to_setcomp(node):
    """Convert a Comp node to a SetComp. The generators may either
    be "comprehension" or Enumerator nodes.
    """
    generators = []
    for clause in node.clauses:
        if isinstance(clause, Enumerator):
            gen = comprehension(clause.target, clause.iter, ())
            generators.append(gen)
        elif isinstance(clause, comprehension):
            assert len(clause.ifs) == 0
            generators.append(clause)
        elif isinstance(clause, expr):
            last = generators[-1]
            last = last._replace(ifs=last.ifs + (clause,))
            generators[-1] = last
        else:
            assert()
    return SetComp(node.resexp, tuple(generators))
