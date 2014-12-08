"""Miscellaneous rewriters aimed at preprocessing, postprocessing,
optimization, and making other transformations applicable.
"""


__all__ = [
    'DistalgoImporter',
    'get_distalgo_message_sets',
    'MacroSetUpdateRewriter',
    'UpdateRewriter',
    'MinMaxRewriter',
    'eliminate_deadcode',
    'PassEliminator',
]


from iast.pylang import MacroProcessor

import invinc.incast as L
from invinc.obj import is_specialrel


class DistalgoImporter(MacroProcessor):
    
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

class MacroSetUpdateRewriter(L.NodeTransformer):
    
    """Rewrite MacroSetUpdates into normal SetUpdates."""
    
    # TODO: These could be refactored as macros in incast perhaps?
    
    def visit_MacroSetUpdate(self, node):
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
        else:
            assert()
        return code

class UpdateRewriter(L.NodeTransformer):
    
    """Rewrite SetUpdates to ensure that the operand is a vartuple."""
    
    def __init__(self, namegen):
        self.namegen = namegen
    
    def visit_SetUpdate(self, node):
        assert L.is_name(node.target)
        if LegalUpdateValidator.run(node.elem):
            return
        
        tempvar = next(self.namegen)
        return (L.Assign((L.sn(tempvar),), node.elem),
                node._replace(elem=L.ln(tempvar)))


class MinMaxRewriter(L.NodeTransformer):
    
    """If a min/max operation is over a union of set literals or
    set comprehensions, distribute the min/max to each operand
    and take the overall min/max. The overall aggregate uses the
    runtimelib's min2() and max2() functions, which are not
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
        # a call to runtimelib's min2()/max2() instead of an
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


def eliminate_deadcode(tree, *, obj_domain_out, verbose=False):
    """Modify the program to remove sets that are not read from."""
    # Find variables that are only written to, not read from.
    # Exclude special names.
    special_vars = set(['__all__'])
    all_vars = L.VarsFinder.run(tree)
    read_vars = L.VarsFinder.run(
            tree, ignore_store=True)
    write_only_vars = all_vars - read_vars - special_vars
    
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
