"""Miscellaneous utilities, mostly used outside this subpackage."""


__all__ = [
    'VarsFinder',
    'VarRenamer',
    'ScopeVisitor',
    'prefix_names',
    'NameGenerator',
    'is_injective',
    'QueryReplacer',
    'QueryMapper',
    'StmtTransformer',
    'OuterMaintTransformer',
    'rewrite_compclauses',
    'maint_skeleton',
    'FuncDefLister',
    'elim_deadfuncs',
    'N',
    'DemfuncMaker',
]


from itertools import chain
from contextlib import contextmanager
from collections.abc import Callable
from simplestruct.type import checktype, checktype_seq
import iast

from invinc.util.collections import OrderedSet
from .helpers import is_vartuple, get_vartuple, get_plainfuncdef, plainfuncdef
from .nodes import *
from .structconv import NodeVisitor, NodeTransformer, Templater


class VarsFinder(NodeVisitor):
    
    """Simple finder of variables (Name nodes).
    
    Flags:
    
        ignore_store:
            Name nodes with Store context are ignored, as are update
            operations (e.g. SetUpdate). As an exception, Name nodes
            on the LHS of Enumerators are not ignored. This is to
            ensure safety under pattern matching semantics.
        ignore_functions:
            Name nodes that appear to be functions are ignored.
        ignore_rels:
            Names that appear to be relations are ignored.
    
    The builtins None, True, and False are always excluded, as they
    are NameConstants, not variables.
    """
    
    def __init__(self, *,
                 ignore_store=False,
                 ignore_functions=False,
                 ignore_rels=False):
        super().__init__()
        self.ignore_store = ignore_store
        self.ignore_functions = ignore_functions
        self.ignore_rels = ignore_rels
    
    def process(self, tree):
        self.usedvars = OrderedSet()
        super().process(tree)
        return self.usedvars
    
    def visit_Name(self, node):
        self.generic_visit(node)
        if not (self.ignore_store and isinstance(node.ctx, Store)):
            self.usedvars.add(node.id)
    
    def visit_Call(self, node):
        class IGNORE(iast.AST):
            _meta = True
        
        if isinstance(node.func, Name) and self.ignore_functions:
            self.generic_visit(node._replace(func=IGNORE()))
        
        else:
            self.generic_visit(node)
    
    def visit_Enumerator(self, node):
        if is_vartuple(node.target):
            # Bypass ignore_store.
            vars = get_vartuple(node.target)
            self.usedvars.update(vars)
        else:
            self.visit(node.target)
        
        if not (self.ignore_rels and isinstance(node.iter, Name)):
            self.visit(node.iter)
    
    def visit_Comp(self, node):
        self.visit(node.resexp)
        # Hack to ensure we don't grab rels on RHS of
        # membership conditions.
        for i in node.clauses:
            if (self.ignore_rels and
                isinstance(i, Compare) and
                len(i.ops) == len(i.comparators) == 1 and
                isinstance(i.ops[0], In) and
                isinstance(i.comparators[0], Name)):
                self.visit(i.left)
            else:
                self.visit(i)
    
    def visit_Aggregate(self, node):
        if isinstance(node.value, Name) and self.ignore_rels:
            return
        else:
            self.generic_visit(node)
    
    def visit_SetMatch(self, node):
        if isinstance(node.target, Name) and self.ignore_rels:
            self.visit(node.key)
        else:
            self.generic_visit(node)
    
    def update_helper(self, node):
        IGNORE = object()
        
        if isinstance(node.target, Name) and self.ignore_store:
            self.generic_visit(node._replace(target=IGNORE))
        
        else:
            self.generic_visit(node)
    
    visit_SetUpdate = update_helper
    visit_RCSetRefUpdate = update_helper
    visit_AssignKey = update_helper
    visit_DelKey = update_helper


class VarRenamer(NodeTransformer):
    
    """Rename occurrences of variables according to a substitution
    mapping. The mapping values can either be strings, or functions
    that map from old variable name to new name. None indicates
    no change.
    """
    
    def __init__(self, subst):
        super().__init__()
        self.subst = subst
    
    def visit_Name(self, node):
        val = self.subst.get(node.id, None)
        if isinstance(val, Callable):
            val = val(node.id)
        
        if val is None:
            return node
        elif isinstance(val, str):
            return node._replace(id=val)
        else:
            raise ValueError("Bad substitution for '{}': {}".format(
                             node.id, repr(val)))


class ScopeVisitor(NodeVisitor):
    
    """Visitor that tracks current scope information during processing.
    The current scope is a stack of sets of names. Each stack entry
    corresponds to a lexical scope, and the sets contain names bound in
    that scope.
    
    Lexical scopes are created for the top-level program, function
    definitions, and comprehensions. Identifiers are considered bound
    if a Name node appears with Store context, or if it is a formal
    parameter to a FunctionDef. Binding is not flow-sensitive within
    a scope, and deletion (Del context) does not remove bindings.
    
    These rules are similar to Python's own scoping rules.
    """
    
    @staticmethod
    def bvars_from_scopestack(scope_stack):
        """Return an OrderedSet of all variables bound by some
        entry in a scope stack.
        """
        return OrderedSet(chain(*scope_stack))
    
    def current_bvars(self):
        """Return an OrderedSet of the variables bound at this
        point in the traversal.
        """
        return self.bvars_from_scopestack(self._scope_stack)
    
    def process(self, tree):
        self._scope_stack = []
        super().process(tree)
        assert len(self._scope_stack) == 0
    
    def enter(self):
        self._scope_stack.append(OrderedSet())
    
    def exit(self):
        self._scope_stack.pop()
    
    def bind(self, name):
        self._scope_stack[-1].add(name)
    
    def visit_Module(self, node):
        self.enter()
        self.generic_visit(node)
        self.exit()
    
    def visit_FunctionDef(self, node):
        # Bind the name of the function in the outer scope,
        # its parameters in the inner scope.
        # Fancy FunctionDef features (decorators, annotations,
        # variable/non-positional arguments) aren't accounted for.
        self.bind(node.name)
        self.enter()
        for a in node.args.args:
            self.bind(a.arg)
        self.generic_visit(node)
        self.exit()
    
    def visit_Comp(self, node):
        self.enter()
        self.generic_visit(node)
        self.exit()
    
    def visit_Name(self, node):
        if isinstance(node.ctx, Store):
            self.bind(node.id)
    
    # For nodes that introduce bindings, process the RHS
    # before the LHS.
    
    def visit_Enumerator(self, node):
        self.visit(node.iter)
        self.visit(node.target)
    
    def visit_Assign(self, node):
        self.visit(node.value)
        self.visit(node.targets)
    
    def visit_AugAssign(self, node):
        self.visit(node.value)
        self.visit(node.op)
        self.visit(node.target)
    
    def visit_For(self, node):
        self.visit(node.iter)
        self.visit(node.target)
        self.visit(node.body)
        self.visit(node.orelse)


def prefix_names(tree, names, prefix):
    """Given a tree and a sequence of names, produce a new tree
    where each occurrence of those names is prefixed with the given
    string.
    """
    checktype_seq(names, str)
    checktype(prefix, str)
    subst = {n: prefix + n for n in names}
    return Templater.run(tree, subst)

class NameGenerator:
    
    """Generates a sequence of distinct strings, e.g. for fresh
    identifiers or prefixes of fresh identifiers.
    """
    
    def __init__(self, fmt='v{}', counter=1):
        self.fmt = fmt
        """String format, including '{}' where the counter goes."""
        self.counter = counter
        """Counter."""
    
    def peek(self):
        """Return the next string without incrementing the counter."""
        return self.fmt.format(str(self.counter))
    
    def next(self):
        """Return the next string and increment the counter."""
        name = self.peek()
        self.counter += 1
        return name
    
    def next_prefix(self):
        """Return the next prefix and increment the counter."""
        return self.next() + '_'
    
    def __iter__(self):
        return self
    
    def __next__(self):
        return self.next()
    
    def prefix_names(self, code, names):
        """Use prefix_names() with a prefix based on this generator."""
        prefix = self.next_prefix()
        return prefix_names(code, names, prefix)


def is_injective(tree):
    """Return True if the expression can be guaranteed to be injective,
    i.e., to evaluate to distinct results for distinct values of its
    variables.
    """
    # Currently we just consider names and tuples to be injective.
    class InjTester(NodeVisitor):
        
        def process(self, tree):
            self.answer = True
            super().process(tree)
            return self.answer
        
        def generic_visit(self, node):
            if not isinstance(node, (Name, Tuple, Load, Store, Del)):
                self.answer = False
            super().generic_visit(node)
    
    return InjTester.run(tree)


class QueryReplacer(NodeTransformer):
    
    """Replace each occurrence of one query with another."""
    
    def __init__(self, from_query, to_query):
        super().__init__()
        self.from_query = from_query
        self.to_query = to_query
    
    def visit_Comp(self, node):
        if node == self.from_query:
            return self.to_query
        else:
            return self.generic_visit(node)
    
    def visit_Aggregate(self, node):
        if node == self.from_query:
            return self.to_query
        else:
            return self.generic_visit(node)

class QueryMapper(NodeTransformer):
    
    """For each unique query, replace all occurrences of that query
    with the result of the methods map_Comp() or map_Aggregate(),
    provided by the subclass. Innermost queries are handled first.
    The map_* methods are called only once per unique query.
    
    If ignore_invalid is True, do not process queries having an
    'invalid' option key set to True. Subqueries of these queries
    will still be recursively processed.
    """
    
    ignore_invalid = False
    
    def __init__(self):
        super().__init__()
        # Replacement mapping.
        self.comps = {}
        self.aggrs = {}
    
    def helper(self, node, handler_name, replmap):
        node = self.generic_visit(node)
        
        assert node.options is not None
        invalid = node.options.get('_invalid', False)
        if invalid and self.ignore_invalid:
            return node
        
        handler = getattr(self, handler_name, None)
        if handler is None:
            return node
        
        repl = replmap.get(node, None)
        if repl is None:
            repl = handler(node)
            replmap[node] = repl
        
        return repl
    
    def visit_Comp(self, node):
        return self.helper(node, 'map_Comp', self.comps)
    
    def visit_Aggregate(self, node):
        return self.helper(node, 'map_Aggregate', self.aggrs)


class StmtTransformer(NodeTransformer):
    
    """Transformer for inserting code immediately before or after
    the statement containing the current node.
    
    We keep a stack of lists of statements to insert before and
    after the current statement node. (A stack is needed because
    statements may be nested in the case of function and class
    definitions.) The subclass may access the current tops of the
    stacks using the pre_stmts and post_stmts properties. When a
    statement node is done being processed, if either of these lists
    is non-empty, their contents are added around the (result of
    processing the) node. 
    """
    
    def process(self, tree):
        # One entry for each stmt-typed node we are inside of.
        self.pre_stmt_stack = []
        self.post_stmt_stack = []
        result = super().process(tree)
        assert len(self.pre_stmt_stack) == len(self.post_stmt_stack) == 0
        return result
    
    @property
    def pre_stmts(self):
        return self.pre_stmt_stack[-1]
    
    @property
    def post_stmts(self):
        return self.post_stmt_stack[-1]
    
    def node_visit(self, node):
        if isinstance(node, stmt):
            self.pre_stmt_stack.append([])
            self.post_stmt_stack.append([])
        
        result = super().node_visit(node)
        
        if isinstance(node, stmt):
            pre_stmts = self.pre_stmt_stack.pop()
            post_stmts = self.post_stmt_stack.pop()
            
            if len(pre_stmts) == len(post_stmts) == 0:
                # If there's nothing to insert, don't muck with the
                # result, which could cause unnecessary copying.
                return result
            else:
                if result is None:
                    result = (node,)
                elif isinstance(result, AST):
                    result = (result,)
                result = (tuple(pre_stmts) + tuple(result) +
                          tuple(post_stmts))
        
        return result


class OuterMaintTransformer(NodeTransformer):
    
    """Transformer for inserting new maintenance code outside all
    existing maintenance code for a given set of invariants. That is,
    if the code already contains maintenance
    
        I1's precode for change to R
        I2's precode for change to R
        update R
        I2's postcode for change to R
        I1's postcode for change to R
    
    this visitor can be used to place new maintenance for R before or
    between the precode for I1 and I2 -- and likewise after or between
    the postcode -- instead of immediately before or after the update.
    
    Precisely: Let S be a set of invariants. We define the "active" node
    A_S(N) for a node N to be the unique innermost node such that
    
        1) A_S(N) is a (non-strict) ancestor of N
        2) A_S(N) is not descended from the "update" field of a
           Maintenance node for any invariant in S, unless it is more
           recently descended from a "precode"/"postcode" field of
           another Maintenance node
    
    Note that A_S(N) is always either N itself, or else a Maintenance
    node for an invariant in S and from whose "update" field N is
    descended.
    
    Maintenance in response to update N gets inserted immediately before
    or after A_S(N). This ensures that all inserted code for the update
    sees a view of the invariants in S that is consistent with the
    state of the updated variable. Conversely, the already existing code
    for invariants in S see the new invariant as consistent with this
    variable's new value beforehand or old value afterwards.
    """
    
    def __init__(self, invs):
        super().__init__()
        if invs is not None:
            invs = set(invs)
        self.invs = invs
        """Set of invariants whose maintenance new code should be
        inserted outside of. If None, insert outside of all
        invariant maintenance.
        """
    
    # As we descend into Maintenance nodes, keep a stack to
    # remember 1) whether there is an active node, and 2) details
    # about currently pending code to be inserted.
    
    def process(self, tree):
        # One entry for every Maintenance node we're in, plus
        # one for the beginning. Tip indicates whether we are
        # currently strictly inside an active (maintenance) node.
        self.active_stack = [False]
        # One entry for every Maintenance node whose update
        # node we're in, plus one for the beginning.
        self.maintinfo_stack = [None]
        return super().process(tree)
    
    @property
    def inside_active(self):
        """True if we're strictly inside an active (maintenance) node.
        (False when we're at the active node itself.)
        """
        return self.active_stack[-1]
    
    def with_outer_maint(self, node, name, desc, precode, postcode):
        """In the handler for an update, call this method and return
        its value in place of "node" in order to wrap maintenance info
        around the update or its active maintenance node.
        """
        # We can only handle keeping track of one new piece of
        # maintenance at a time. Multiple pieces shouldn't really
        # happen, because the "update" field of Maintenance nodes
        # should only contain other Maintenance nodes and a single
        # update statement. (It's ok to be in the "update" portion
        # of an outer Maintenance node if we're also inside precode
        # or postcode of an inner Maintenance node, because then
        # the outer one isn't the active node.)
        if self.inside_active:
            assert self.maintinfo_stack[-1] is None
            self.maintinfo_stack[-1] = (name, desc, precode, postcode)
            return node
        else:
            return Maintenance(name, desc, precode, (node,), postcode)
    
    def visit_Maintenance(self, node):
        @contextmanager
        def active(b):
            self.active_stack.append(b)
            yield
            self.active_stack.pop()
        
        # We can only be the active node while we are visiting
        # update code, not pre and post code.
        
        with active(False):
            precode = self.visit(node.precode)
        
        # This node is the active one if no higher node is active,
        # and if this node maintains for one of the given invariants.
        we_are_active = (not self.inside_active and
                         (self.invs is None or
                          node.name in self.invs))
        # The update section is inside an active node if
        # we are inside one, or if we are it.
        inside_is_in_active = self.inside_active or we_are_active
        
        if we_are_active:
            # Create a stack entry for new code to insert
            # before/after this one.
            self.maintinfo_stack.append(None)
            with active(inside_is_in_active):
                update = self.visit(node.update)
            # Pop and save locally, so as not to interfere with
            # postcode processing below.
            saved_maintinfo = self.maintinfo_stack.pop()
        else:
            with active(inside_is_in_active):
                update = self.visit(node.update)
        
        with active(False):
            postcode = self.visit(node.postcode)
        
        # Do normal NodeTransformer replacements first,
        # before worrying about inserting outer maintenance.
        node = node._replace(precode=precode,
                             update=update,
                             postcode=postcode)
        
        # If we are the active maintenance node and new maintenance
        # info was added, create and return the new Maintenance node.
        if we_are_active and saved_maintinfo is not None:
            (name, desc, precode, postcode) = saved_maintinfo
            return Maintenance(name, desc, precode, (node,), postcode)
        else:
            return node


def rewrite_compclauses(comp, rewriter, *,
                        after=False, enum_only=False, recursive=False,
                        resexp=True):
    """Apply a rewriter to each part of the comprehension, sometimes
    inserting new clauses to the left or right of the rewritten part.
    
    rewriter is applied to each clause in left-to-right order, and
    finally to the result expression. It returns a pair of the new
    clause/expression AST, and a list of clauses to be inserted
    immediately before or after this AST (depending on the after
    flag).
    
    If clauses are generated for the result expression, they are
    always appended to the end of the clause list, regardless of
    the after flag.
    
    If enum_only is True, only process enumerator clauses, not
    condition clauses or the result expression. If enum_only is False
    but resexp is True, process all clauses but not the result
    expression.
    
    If recursive is True, also call rewriter on the newly inserted
    clauses as well.
    """
    checktype(comp, Comp)
    
    # Use a recursive function to handle the case of recursively
    # processing added clauses.
    
    def process(clauses):
        result = []
        for cl in clauses:
            if enum_only and not isinstance(cl, Enumerator):
                result.append(cl)
                continue
            
            mod_clause, add_clauses = rewriter(cl)
            
            if recursive:
                add_clauses = process(add_clauses)
            
            if after:
                result.append(mod_clause)
                result.extend(add_clauses)
            else:
                result.extend(add_clauses)
                result.append(mod_clause)
        
        return result
    
    new_clauses = process(comp.clauses)
    
    # Handle result expression.
    if enum_only or not resexp:
        new_resexp = comp.resexp
    else:
        new_resexp, add_clauses = rewriter(comp.resexp)
        if recursive:
            add_clauses = process(add_clauses)
        new_clauses.extend(add_clauses)
    
    return comp._replace(resexp=new_resexp, clauses=tuple(new_clauses))


# TODO: The idiom used in the following code is a bit tricky.
# We need bottom-up info about whether a node contains a Maintenance
# node in any of its subtrees. So one visitor builds up a set of
# nodes for which this predicate is True. The set is by node id
# (memory address), not node value, for efficient comparisons.
# But another visitor transforms the tree, which means modifying
# this mapping to correctly include newly-introduced trees.
# This could be generalized into iast. Alternatively, this is all
# because the node-replacement transformer idiom makes it difficult
# to store auxiliary information on nodes. Maybe we could do a pre
# and post processing step that convert between a new node format
# that also includes this auxiliary info as fields.

class MaintFinder(NodeVisitor):
    
    """Return a set of ids (memory addresses) of nodes in a tree
    that are or contain Maintenance nodes.
    """
    
    # Should be O(n) for the whole tree, whereas a naive approach
    # is O(n^2).
    
    def process(self, tree):
        self.result = set()
        super().process(tree)
        return self.result
    
    # Redefine some NodeVisitor internals to return bools indicating
    # the presence of a Maintenance node in a subtree.
    
    def visit(self, tree):
        if isinstance(tree, AST):
            return self.node_visit(tree)
        elif isinstance(tree, tuple):
            return self.seq_visit(tree)
        else:
            return False
    
    def node_visit(self, node):
        hasmaint = super().node_visit(node)
        if hasmaint:
            self.result.add(id(node))
        return hasmaint
    
    def seq_visit(self, seq):
        hasmaint = False
        for item in seq:
            hasmaint |= self.visit(item)
        return hasmaint
    
    def generic_visit(self, node):
        hasmaint = False
        for field in node._fields:
            value = getattr(node, field)
            hasmaint |= self.visit(value)
        return hasmaint
    
    def visit_Maintenance(self, node):
        self.generic_visit(node)
        return True

class ControlFlattener(NodeTransformer):
    
    """Flatten For, If, and While statements by replacing these nodes
    with their bodies, so long as there is no else clause.
    """
    
    def helper(self, node):
        # Recursing might not even be necessary since we call this
        # visitor bottom-up in Skeletonizer.
        node = self.generic_visit(node)
        if node.orelse == ():
            return node.body
    
    visit_For = helper
    visit_While = helper
    visit_If = helper

class Skeletonizer(NodeTransformer):
    
    """Remove details of maintenance code, retaining just the outline.
    
    Specifically, any precode or postcode that is not another
    Maintenance node is removed. If precode or postcode would be
    made empty by this, Pass is inserted. Where possible, statements
    that introduce new blocks of code are eliminated, and any nested
    Maintenance nodes are pushed up in the tree.
    """
    
    def process(self, tree):
        self.hasmaint_nodes = MaintFinder.run(tree)
        return super().process(tree)
    
    def node_visit(self, node):
        # Preserve hasmaint info when we substitute new nodes
        # into the tree.
        hasmaint = id(node) in self.hasmaint_nodes
        result = super().node_visit(node)
        if hasmaint:
            self.hasmaint_nodes.add(id(result))
        return result
    
    def filter(self, stmts):
        if len(stmts) == 0:
            return ()
        
        new_stmts = ControlFlattener.run(stmts)
        new_stmts = tuple(s for s in new_stmts if id(s) in self.hasmaint_nodes)
        if len(new_stmts) == 0:
            new_stmts = (Pass(),)
        
        return new_stmts
    
    def visit_Maintenance(self, node):
        node = self.generic_visit(node)
        
        precode = self.filter(node.precode)
        postcode = self.filter(node.postcode)
        
        return node._replace(precode=precode, postcode=postcode)

def maint_skeleton(tree):
    """Return a modified tree that contains just the skeleton of
    maintenance code, omitting the exact code but keeping uses of
    nested maintenance code.
    """
    return Skeletonizer.run(tree)


class FuncDefLister(NodeVisitor):
    
    """Given a predicate, find all functions whose names match the
    predicate, returned as a map from name to definition node. There
    must be exactly one definition per function.
    """
    
    def __init__(self, pred):
        super().__init__()
        self.pred = pred
    
    def process(self, tree):
        self.result = {}
        super().process(tree)
        return self.result
    
    def visit_FunctionDef(self, node):
        name = node.name
        if self.pred(name):
            if name in self.result:
                raise AssertionError('Multiple definitions for '
                                     'function \'{}\''.format(name))
            self.result[name] = node

class FuncEliminator(NodeTransformer):
    
    """Remove definitions of functions matching a predicate."""
    
    def __init__(self, pred):
        super().__init__()
        self.pred = pred
    
    def visit_FunctionDef(self, node):
        if self.pred(node.name):
            return ()

def elim_deadfuncs(tree, pred):
    """Remove definitions of functions matching the predicate, if they
    are not used.
    """
    ### TODO: Should be run to fixed-point.
    used_names = VarsFinder.run(tree, ignore_functions=False)
    new_pred = lambda n: pred(n) and n not in used_names
    return FuncEliminator.run(tree, new_pred)

class N:
    
    """Naming conventions."""
    
    @classmethod
    def uset(cls, n):
        return '_U_' + n
    
    @classmethod
    def usetext(cls, n):
        return '_UEXT_' + n
    
    @classmethod
    def queryfunc(cls, n):
        return 'query_' + n
    
    @classmethod
    def demfunc(cls, n):
        return 'demand_' + n
    
    @classmethod
    def undemfunc(cls, n):
        return 'undemand_' + n
    
    @classmethod
    def deltaset(cls, n):
        return n + '_delta'


class DemfuncMaker:
    
    """Generates code for demanding, undemanding, and query-demanding
    combinations of parameter values.
    
    There are two kinds of demand: extensional and intensional.
    Extensional demand is when something becomes demanded because the
    user says so. E.g. the user is about to perform a query, or the
    user thinks it is a good policy to precompute an answer for these
    parameter values. Intesional demand is when something becomes
    demanded for an inner query because it may be needed by the outer
    query. Intensional demand is controlled by invariants.
    
    We can think of intensional demand as being stored in a reference-
    counted set, and extensional demand as being stored in an ordinary
    set. The actual U-set is then their reference-counted union.
    LRU cache information is only tracked for extensional items.
    """
    
    def __init__(self, name, specstr, demparams, lrulimit):
        self.name = name
        """Query name, base name for functions."""
        self.specstr = specstr
        """Docstring description of query."""
        self.demparams = tuple(demparams)
        """Tuple of demand parameter names."""
        self.lrulimit = lrulimit
        """Number of entries in LRU cache; None if no LRU cache."""
        
        from . import pe, ln, Str, Num, tuplify
        demcall_node = pe('DEMFUNC(__ARGS)',
                          subst={'DEMFUNC': ln(N.demfunc(self.name))})
        demcall_node = demcall_node._replace(
                        args=tuple(ln(p) for p in self.demparams))
        
        topvars = ['_top_v' + str(i)
                   for i in range(1, len(self.demparams) + 1)]
        undemcall_node = pe('UNDEMFUNC(__ARGS)',
                            subst={'UNDEMFUNC': ln(N.undemfunc(self.name))})
        undemcall_node = undemcall_node._replace(
                          args=tuple(ln(p) for p in topvars))
        
        extset = 'Set' if self.lrulimit is None else 'LRUSet'
        
        self.subst = {'SPEC_STR': Str(self.specstr),
                      'USET': N.uset(self.name),
                      'USET_EXT': N.usetext(self.name),
                      'EXTSET': ln(extset),
                      'DEMPARAMS': tuplify(self.demparams),
                      'DEMCALL': demcall_node,
                      'UNDEMCALL': undemcall_node,
                      'UNDEMFUNC': ln(N.undemfunc(self.name)),
                      'S_TOPVARS': tuplify(topvars, lval=True)}
        if self.lrulimit is not None:
            self.subst['LRUSIZE'] = Num(lrulimit)
    
    def make_usetvars(self):
        from . import pc
        code = pc('''
            USET = RCSet()
            USET_EXT = EXTSET()
            ''', subst=self.subst)
        return code
    
    def make_demfunc(self):
        from . import pc
        code = pc('''
            SPEC_STR
            USET.rcadd(DEMPARAMS)
            ''', subst=self.subst)
        code = plainfuncdef(N.demfunc(self.name), self.demparams, code)
        return code
    
    def make_undemfunc(self):
        from . import pc
        code = pc('''
            SPEC_STR
            USET.rcremove(DEMPARAMS)
            ''', subst=self.subst)
        code = plainfuncdef(N.undemfunc(self.name), self.demparams, code)
        return code
    
    def make_queryfunc(self):
        from . import pc
        
        if self.lrulimit is None:
            code = pc('''
                SPEC_STR
                if DEMPARAMS not in USET_EXT:
                    USET_EXT.add(DEMPARAMS)
                    DEMCALL
                return True
                ''', subst=self.subst)
        
        else:
            code = pc('''
                SPEC_STR
                if DEMPARAMS not in USET_EXT:
                    while len(USET_EXT) >= LRUSIZE:
                        S_TOPVARS = _top = USET_EXT.peek()
                        UNDEMCALL
                        USET_EXT.remove(_top)
                    USET_EXT.add(DEMPARAMS)
                    DEMCALL
                else:
                    USET_EXT.ping(DEMPARAMS)
                return True
                ''', subst=self.subst)
        
        code = plainfuncdef(N.queryfunc(self.name), self.demparams, code)
        return code
    
    def make_alldem(self):
        code = (self.make_usetvars() +
                self.make_demfunc() +
                self.make_undemfunc() +
                self.make_queryfunc())
        return code
