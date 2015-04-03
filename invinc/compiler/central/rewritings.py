"""Miscellaneous rewriters aimed at preprocessing, postprocessing,
optimization, and making other transformations applicable.
"""


__all__ = [
    'DistalgoImporter',
    'get_distalgo_message_sets',
    'RelationFinder',
    'MacroUpdateRewriter',
    'SetTypeRewriter',
    'ObjTypeRewriter',
    'StrictUpdateRewriter',
    'MapOpImporter',
    'UpdateRewriter',
    'MinMaxRewriter',
    'eliminate_deadcode',
    'PassEliminator',
]


from invinc.util.collections import OrderedSet
import invinc.compiler.incast as L
from invinc.compiler.obj import is_specialrel


class DistalgoImporter(L.MacroProcessor):
    
    """Perform a few simple preprocessing steps.
    
        - len() is converted to count()
        - set(<generator expr>) is converted to a SetComp
        - set(<list or tuple>) is converted to a Set literal
    """
    
    # Distalgo conversion is done even before importing basic IncAST
    # operations from their Python representation. For consistency,
    # we'll use parse_structast() to avoid creating IncAST-specific
    # nodes at this stage.
    
    def handle_fe_len(self, f, arg):
        return L.parse_structast('count(ARG)',
                                 subst={'ARG': arg}, mode='expr')
    
    def handle_fe_set(self, f, *args):
        if len(args) == 0:
            return None
        elif len(args) == 1:
            arg = args[0]
            if isinstance(arg, L.GeneratorExp):
                return L.SetComp(arg.elt, arg.generators)
            elif isinstance(arg, (L.List, L.Tuple)):
                return L.Set(arg.elts)
            else:
                return None
        else:
            raise L.ProgramError('set() takes at most one arg')


def get_distalgo_message_sets(tree):
    """Return all variable names that match the pattern for distalgo
    message sets.
    """
    vars = L.VarsFinder.run(tree)
    return [v for v in vars
              if v.startswith('_') and
                 ('ReceivedEvent_' in v or
                  'SentEvent_' in v)]


class RelationFinder(L.NodeVisitor):
    
    """Find variables that we can statically infer to be relations,
    i.e. sets that are unaliased and top-level.
    
    For R to be inferred to be a relation, it must have a global-scope
    initialization having one of the following forms:
    
        R = Set()
        R = invinc.runtime.Set()
        R = set()
    
    and its only other occurrences must have the forms:
    
        - a SetUpdate naming R as the target
        
        - the RHS of membership clauses (including condition clauses)
        
        - the RHS of a For loop
    """
    
    def process(self, tree):
        self.inited = OrderedSet()
        self.disqual = OrderedSet()
        super().process(tree)
        return self.inited - self.disqual
    
    # Manage a toplevel flag to record whether we're at global scope.
    
    def visit_Module(self, node):
        self.toplevel = True
        self.generic_visit(node)
    
    def nontoplevel_helper(self, node):
        last = self.toplevel
        self.toplevel = False
        self.generic_visit(node)
        self.toplevel = last
    
    visit_FunctionDef = nontoplevel_helper
    visit_ClassDef = nontoplevel_helper
    
    def visit_Assign(self, node):
        allowed_inits = [
            L.pe('Set()'),
            L.pe('invinc.runtime.Set()'),
            L.pe('set()'),
        ]
        # If this is a relation initializer, mark the relation name
        # and don't recurse.
        if (self.toplevel and
            L.is_varassign(node)):
            name, value = L.get_varassign(node)
            if value in allowed_inits:
                self.inited.add(name)
                return
        
        self.generic_visit(node)
    
    def visit_SetUpdate(self, node):
        # Skip the target if it's just a name.
        if isinstance(node.target, L.Name):
            self.visit(node.elem)
        else:
            self.generic_visit(node)
    
    def visit_For(self, node):
        # Skip the iter if it's just a name.
        if isinstance(node.iter, L.Name):
            self.visit(node.target)
            self.visit(node.body)
            self.visit(node.orelse)
        else:
            self.generic_visit(node)
    
    def visit_Comp(self, node):
        # Skip the iter of each clause if it's just a name.
        # Also recognize condition clauses that express memberships.
        # Always skip the params and options.
        self.visit(node.resexp)
        for cl in node.clauses:
            if (isinstance(cl, L.Enumerator) and
                isinstance(cl.iter, L.Name)):
                self.visit(cl.target)
            elif (isinstance(cl, L.Compare) and
                  len(cl.ops) == len(cl.comparators) == 1 and
                  isinstance(cl.ops[0], L.In) and
                  isinstance(cl.comparators[0], L.Name)):
                self.visit(cl.left)
            else:
                self.visit(cl)
    
    def visit_Name(self, node):
        # We got here through some disallowed use of R.
        self.disqual.add(node.id)


class LegalUpdateValidator(L.NodeVisitor):
    
    """Return True if an update operand expression is ok,
    or False if it needs rewriting.
    """
    
    class Invalid(BaseException):
        pass
    
    def process(self, tree):
        try:
            super().process(tree)
        except self.Invalid:
            return False
        return True
    
    # Any non-whitelisted node type causes failure.
    
    whitelist = [
        'Num', 'Str', 'Bytes', 'Name',
        'Tuple', 'List', 'Dict', 'Set',
        'Load',
        'BoolOp', 'BinOp', 'UnaryOp',
        'And', 'Or',
        # Exclude bitwise operators, which can construct new sets.
        'Add', 'Sub', 'Mult', 'Div', 'Mod', 'Pow', 'LShift',
        'RShift', 'FloorDiv',
        # Exclude Not, which can be used for cardinality tests on sets.
        'Invert', 'UAdd', 'USub',
        # Exclude membership operators In, NotIn.
        'Eq', 'NotEq', 'Lt', 'LtE', 'Gt', 'GtE', 'Is', 'IsNot',
    ]
    whitelist = [getattr(L, name) for name in whitelist]
    
    def generic_visit(self, node):
        if not isinstance(node, tuple(self.whitelist)):
            raise self.Invalid
        super().generic_visit(node)

class MacroUpdateRewriter(L.NodeTransformer):
    
    """Rewrite MacroUpdates into normal set and map updates."""
    
    # TODO: These could be refactored as macros in incast perhaps?
    
    def visit_MacroUpdate(self, node):
        op = node.op
        subst = {'TARGET': node.target,
                 'OTHER': node.other}
        # Remember that it's illegal to modify a set while iterating over it
        # in a For loop without making a copy. 
        if op == 'union':
            # No copy needed because if node.target and node.other are
            # aliased, the operation has no effect.
            code = L.pc('''
                for _upelem in OTHER:
                    TARGET.nsadd(_upelem)
                ''', subst=subst)
        elif op == 'inter':
            code = L.pc('''
                for _upelem in list(TARGET):
                    if _upelem not in OTHER:
                        TARGET.remove(_upelem)
                ''', subst=subst)
        elif op == 'diff':
            code = L.pc('''
                for _upelem in list(OTHER):
                    TARGET.nsremove(_upelem)
                ''', subst=subst)
        elif op == 'symdiff':
            code = L.pc('''
                for _upelem in list(OTHER):
                    if _upelem in TARGET:
                        TARGET.remove(_upelem)
                    else:
                        TARGET.add(_upelem)
                ''', subst=subst)
        elif op == 'assign':
            code = L.pc('''
                if TARGET is not OTHER:
                    while len(TARGET) > 0:
                        _upelem = next(iter(TARGET))
                        TARGET.remove(_upelem)
                    for _upelem in OTHER:
                        TARGET.add(_upelem)
                ''', subst=subst)
        elif op == 'clear':
            code = L.pc('''
                while len(TARGET) > 0:
                    _upelem = next(iter(TARGET))
                    TARGET.remove(_upelem)
                ''', subst=subst)
        elif op == 'mapassign':
            code = L.pc('''
                if TARGET is not OTHER:
                    while len(TARGET) > 0:
                        _upkey = next(iter(TARGET))
                        TARGET.delkey(_upkey)
                    for _upkey, _upval in OTHER.items():
                        TARGET.assignkey(_upkey, _upval)
                ''', subst=subst)
        elif op == 'mapclear':
            code = L.pc('''
                while len(TARGET) > 0:
                    _upkey = next(iter(TARGET))
                    TARGET.delkey(_upkey)
                ''', subst=subst)
        else:
            assert()
        return code

class SetTypeRewriter(L.StmtTransformer):
    
    """Rewrite set expressions to use invinc.runtime.Set.
    
    If set_literals is True, handle set literal expressions, including
    ones that use set(...).
    
    If orig_set_comps is True, handle set comprehensions marked
    with the in_original option.
    """
    
    def __init__(self, namegen, *, set_literals, orig_set_comps):
        super().__init__()
        self.namegen = namegen
        self.set_literals = set_literals
        self.orig_set_comps = orig_set_comps
    
    def helper(self, node, no_update=False):
        fresh = next(self.namegen)
        
        if no_update:
            template = L.trim('''
                S_VAR = Set()
                ''')
        else:
            template = L.trim('''
                S_VAR = Set()
                L_VAR.update(EXPR)
                ''')
        new_code = L.pc(template, subst={'L_VAR': L.ln(fresh),
                                         'S_VAR': L.sn(fresh),
                                         'EXPR': node})
        
        self.pre_stmts.extend(new_code)
        return L.ln(fresh)
    
    def visit_Comp(self, node):
        node = self.generic_visit(node)
        
        if (self.orig_set_comps and
            node.options.get('in_original', False)):
            return self.helper(node)
        else:
            return node
    
    def visit_Set(self, node):
        node = self.generic_visit(node)
        
        if self.set_literals:
            return self.helper(node)
        else:
            return node
    
    def visit_Call(self, node):
        # Handle set(...) syntax as if it were {...}.
        if (self.set_literals and
            isinstance(node.func, L.Name) and
            node.func.id == 'set'):
            no_update = len(node.args) == 0
            return self.helper(node, no_update=no_update)
        else:
            return node
    
    def visit_For(self, node):
        # Skip the top level of node.iter, because set iteration
        # looks at the set contents, not the constructed set value.
        #
        # This is accomplished by using generic_visit() instead of
        # visit() on the iter, to avoid dispatch to any of the
        # above handlers.
        iter_result = self.generic_visit(node.iter)
        # Handle special case return values. Tuple return values
        # are not permitted in this context, so it's just the None
        # case.
        if iter_result is None:
            iter_result = node.iter
        
        target = self.visit(node.target)
        body = self.visit(node.body)
        orelse = self.visit(node.orelse)
        
        new_node = L.For(target, iter_result, body, orelse)
        # If there's no change, avoid returning a newly constructed
        # node, which would force copying up the tree.
        if new_node == node:
            new_node = node
        
        return new_node

class ObjTypeRewriter(L.NodeTransformer):
    
    """Add invinc.runtime.Obj as a base class to all class definitions."""
    
    def valid_baseclass(self, expr):
        if isinstance(expr, L.Name):
            return True
        elif (isinstance(expr, L.Attribute) and
              self.valid_baseclass(expr.value)):
            return True
        else:
            return False
    
    def visit_ClassDef(self, node):
        node = self.generic_visit(node)
        
        assert all(self.valid_baseclass(b) for b in node.bases), \
            'Illegal base class'
        objbase = L.ln('Set')
        if objbase not in node.bases:
            new_bases = node.bases + (objbase,)
            node = node._replace(bases=new_bases)
        
        return node


class StrictUpdateRewriter(L.NodeTransformer):
    
    """Rewrite set, field, and/or map updates with if-guards
    to ensure that they can be considered strict. To be run
    after macro updates have already been turned into elementary
    updates.
    """
    
    def __init__(self, *, rewrite_sets=True, rewrite_fields=True,
                          rewrite_maps=True):
        super().__init__()
        self.rewrite_sets = rewrite_sets
        self.rewrite_fields = rewrite_fields
        self.rewrite_maps = rewrite_maps
    
    # No need to generic_visit() since updates can't contain
    # other updates.
    
    def visit_SetUpdate(self, node):
        if not self.rewrite_sets:
            return node
        nsop = {'add': 'nsadd',
                'remove': 'nsremove'}[node.op]
        template = 'TARGET.{}(ELEM)'.format(nsop)
        return L.pc(template, subst={'TARGET': node.target,
                                     'ELEM': node.elem})
    
    def visit_Assign(self, node):
        if not self.rewrite_fields:
            return node
        if not L.is_attrassign(node):
            return node
        cont, field, value = L.get_attrassign(node)
        return L.pc('''
            CONT.nsassignfield(FIELD, VALUE)
            ''', subst={'CONT': cont,
                        'FIELD': L.ln(field),
                        'VALUE': value})
    
    def visit_Delete(self, node):
        if not self.rewrite_fields:
            return node
        if not L.is_delattr(node):
            return node
        cont, field = L.get_delattr(node)
        return L.pc('''
            CONT.nsdelfield(FIELD)
            ''', subst={'CONT': cont,
                        'FIELD': L.ln(field)})
    
    def visit_AssignKey(self, node):
        if not self.rewrite_maps:
            return node
        return L.pc('''
            TARGET.nsassignkey(KEY, VALUE)
            ''', subst={'TARGET': node.target,
                        'KEY': node.key,
                        'VALUE': node.value})
    
    def visit_DelKey(self, node):
        if not self.rewrite_maps:
            return node
        return L.pc('''
            TARGET.nsdelkey(KEY)
            ''', subst={'TARGET': node.target,
                        'KEY': node.key})


class MapOpImporter(L.NodeTransformer):
    
    """Convert assignment and deletion of map keys to AssignKey
    and DelKey nodes. Uses of the map "globals()" are ignored.
    """
    
    def visit_Assign(self, node):
        if L.is_mapassign(node):
            target, key, value = L.get_mapassign(node)
            return L.AssignKey(target, key, value)
        return node
    
    def visit_Delete(self, node):
        if L.is_delmap(node):
            target, key = L.get_delmap(node)
            return L.DelKey(target, key)
        return node

class UpdateRewriter(L.NodeTransformer):
    
    """Rewrite set and map updates to ensure that the operands
    are legal update expressions.
    """
    
    def __init__(self, namegen):
        self.namegen = namegen
    
    # No need to recurse since we only deal with update statements,
    # which can't be nested.
    
    def visit_SetUpdate(self, node):
        target_ok = LegalUpdateValidator.run(node.target)
        elem_ok = LegalUpdateValidator.run(node.elem)
        if target_ok and elem_ok:
            return node
        
        code = ()
        if not target_ok:
            targetvar = next(self.namegen)
            code += (L.Assign((L.sn(targetvar),), node.target),)
            node = node._replace(target=L.ln(targetvar))
        if not elem_ok:
            elemvar = next(self.namegen)
            code += (L.Assign((L.sn(elemvar),), node.elem),)
            node = node._replace(elem=L.ln(elemvar))
        return code + (node,)
    
    def visit_AssignKey(self, node):
        target_ok = LegalUpdateValidator.run(node.target)
        key_ok = LegalUpdateValidator.run(node.key)
        value_ok = LegalUpdateValidator.run(node.value)
        if target_ok and key_ok and value_ok:
            return node
        
        code = ()
        if not target_ok:
            targetvar = next(self.namegen)
            code += (L.Assign((L.sn(targetvar),), node.target),)
            node = node._replace(target=L.ln(targetvar))
        if not key_ok:
            keyvar = next(self.namegen)
            code += (L.Assign((L.sn(keyvar),), node.key),)
            node = node._replace(key=L.ln(keyvar))
        if not value_ok:
            valuevar = next(self.namegen)
            code += (L.Assign((L.sn(valuevar),), node.value),)
            node = node._replace(value=L.ln(valuevar))
        
        return code + (node,)
    
    def visit_DelKey(self, node):
        target_ok = LegalUpdateValidator.run(node.target)
        key_ok = LegalUpdateValidator.run(node.key)
        if target_ok and key_ok:
            return node
        
        code = ()
        if not target_ok:
            targetvar = next(self.namegen)
            code += (L.Assign((L.sn(targetvar),), node.target),)
            node = node._replace(target=L.ln(targetvar))
        if not key_ok:
            keyvar = next(self.namegen)
            code += (L.Assign((L.sn(keyvar),), node.key),)
            node = node._replace(key=L.ln(keyvar))
        
        return code + (node,)


class MinMaxRewriter(L.NodeTransformer):
    
    """If a min/max operation is over a union of set literals or
    set comprehensions, distribute the min/max to each operand
    and take the overall min/max. The overall aggregate uses the
    runtime's min2() and max2() functions, which are not
    incrementalized but allow their arguments to be None.
    """
    
    def visit_Aggregate(self, node):
        node = self.generic_visit(node)
        
        if not node.op in ['min', 'max']:
            return node
        func2 = {'min': 'min2', 'max': 'max2'}[node.op]
        
        if not L.is_setunion(node.value):
            return node
        sets = L.get_setunion(node.value)
        if len(sets) == 1:
            # If there's just one set, don't change anything.
            return node
        
        # Wrap each operand in an aggregate query with the same
        # options as the original aggregate. (This ensures that
        # 'impl' is carried over.) Set literals are wrapped in
        # a call to invinc.runtime's min2()/max2() instead of an
        # Aggregate query node.
        terms = []
        for s in sets:
            if isinstance(s, (L.Comp, L.Name)):
                new_term = L.Aggregate(s, node.op, node.options)
            else:
                new_term = L.pe('OP(__ARGS)', subst={'OP': L.ln(func2)})
                new_term = new_term._replace(args=s.elts)
            terms.append(new_term)
        
        # The new top-level aggregate is min2()/max2().
        new_node = L.pe('OP(__ARGS)',
                        subst={'OP': L.ln(func2)})
        new_node = new_node._replace(args=tuple(terms))
        return new_node


# TODO: There are two cases where dead code elimination will fail to
# get rid of a relation. One is when the relation is reference-counted,
# because the reference-counted add/remove operations are already
# broken down into operations that inspect the current refcount to
# decide what to do. We'd have to change it so rcadd and rcremove
# operations are not expanded until the end. This would also entail
# changing auxmap transformation to work for rcadd/rcremove.
#
# The second case is when the contents of the set are read directly,
# such as in filter checks. This could be fixed by rewriting these tests
# to use an arbitrary map over the set instead.

class DeadCodeEliminator(L.NodeTransformer):
    
    def __init__(self, deadvars):
        self.deadvars = set(deadvars)
    
    def visit_Assign(self, node):
        if (len(node.targets) == 1 and
            isinstance(node.targets[0], L.Name) and
            node.targets[0].id in self.deadvars):
            return L.Pass()
    
    def update_helper(self, node):
        if isinstance(node.target, L.Name):
            if node.target.id in self.deadvars:
                return L.Pass()
    
    visit_SetUpdate = update_helper
    visit_RCSetRefUpdate = update_helper
    visit_AssignKey = update_helper
    visit_DelKey = update_helper


class PassEliminator(L.NodeTransformer):
    
    def filter_pass(self, stmts):
        """Update a list of statements to exclude Pass nodes."""
        if len(stmts) == 1:
            # Can't remove a lone Pass.
            return stmts
        else:
            return tuple(s for s in stmts if not isinstance(s, L.Pass))
    
    def body_helper(self, node):
        node = self.generic_visit(node)
        
        new_body = self.filter_pass(node.body)
        node = node._replace(body=new_body)
        if hasattr(node, 'orelse'):
            new_orelse = self.filter_pass(node.orelse)
            node = node._replace(orelse=new_orelse)
        
        return node
    
    visit_Module = body_helper
    visit_FunctionDef = body_helper
    visit_ClassDef = body_helper
    visit_For = body_helper
    visit_While = body_helper
    visit_If = body_helper
    visit_With = body_helper


def eliminate_deadcode(tree, *, keepvars=None, obj_domain_out, verbose=False):
    """Modify the program to remove sets that are not read from."""
    if keepvars is None:
        keepvars = set()
    keepvars = set(keepvars)
    
    # Find variables that are only written to, not read from.
    # Exclude special names and keepvars.
    special_vars = set(['__all__'])
    all_vars = L.VarsFinder.run(tree)
    read_vars = L.VarsFinder.run(
            tree, ignore_store=True)
    write_only_vars = all_vars - read_vars - special_vars - keepvars
    
    if obj_domain_out:
        # Also exclude pairsets since they will be translated into
        # actual obj-domain updates.
        for v in set(write_only_vars):
            if is_specialrel(v):
                write_only_vars.remove(v)
    
    # Delete most updates to these variables. Some cases, such as
    # the target of a For loop, are left alone.
    tree = DeadCodeEliminator.run(tree, write_only_vars)
    
    if verbose:
        if len(write_only_vars) > 0:
            print('Eliminated dead variables: ' + ', '.join(write_only_vars))
        else:
            print('No dead vars eliminated')
    
    return tree
