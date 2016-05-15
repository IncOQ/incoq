"""Cost analysis."""


__all__ = [
    'analyze_costs',
    'annotate_costs',
]


from incoq.util.collections import OrderedSet
from incoq.compiler.incast import L
from incoq.compiler.type import T
from incoq.compiler.symbol import N

from .costs import *
from .algebra import *


class BaseCostAnalyzer(L.NodeVisitor):
    
    """Base class for a visitor that traverses code and returns an
    asymptotic term.
    
    This class allows a subclass to specify three lists
    of node types:
    
        - nodes that have a constant cost
        
        - nodes that have a cost that is the sum of their children
        
        - and nodes that have an unknown cost
    
    Any node that is not handled in one of these lists must either have
    its own visit handler defined or else it raises an exception. The
    lists may include non-terminal node types (such as "operator") that
    summarize all the corresponding terminal types.
    
    Additionally, there are another three lists as above for names of
    functions that have the associated costs.
    """
    
    @property
    def const_nodes(self):
        raise NotImplementedError
    
    @property
    def sum_nodes(self):
        raise NotImplementedError
    
    @property
    def unknown_nodes(self):
        raise NotImplementedError
    
    @property
    def const_funcs(self):
        raise NotImplementedError
    
    @property
    def sum_funcs(self):
        raise NotImplementedError
    
    @property
    def unknown_funcs(self):
        raise NotImplementedError
    
    def process(self, tree):
        res = super().process(tree)
        res = normalize(res)
        return res
    
    def visit(self, tree):
        if isinstance(tree, L.AST):
            res = self.node_visit(tree)
        elif isinstance(tree, tuple):
            res = self.seq_visit(tree)
        else:
            # Primitive values are considered to have unit cost,
            # so they don't affect the costs of their parent nodes.
            res = Unit()
        
        return res
    
    def generic_visit(self, node):
        # Dispatch based on the lists.
        if isinstance(node, self.const_nodes):
            return Unit()
        
        elif isinstance(node, self.sum_nodes):
            costs = []
            for field in node._fields:
                value = getattr(node, field)
                cost = self.visit(value)
                costs.append(cost)
            return Sum(costs)
        
        elif isinstance(node, self.unknown_nodes):
            return Unknown()
        
        else:
            raise AssertionError('Unhandled node type: ' +
                                 type(node).__name__)
    
    def seq_visit(self, seq):
        # Sum up the costs of a sequence of nodes.
        costs = []
        for item in seq:
            cost = self.visit(item)
            costs.append(cost)
        return Sum(costs)
    
    def visit_Call(self, node):
        # Check if it matches one of the known function cases.
        if node.func in self.const_funcs:
            return Unit()
        
        elif node.func in self.sum_funcs:
            costs = []
            for arg in node.args:
                cost = self.visit(arg)
                costs.append(cost)
            return Sum(costs)
        
        elif node.func in self.unknown_funcs:
            return Unknown()
        
        else:
            raise NotImplementedError('Unknown function call')


class TrivialCostAnalyzer(BaseCostAnalyzer):
    
    """Determine a cost for a piece of code that does not contain loops
    or calls to unknown functions.
    """
    
    # The three lists are populated with names and programmatically
    # replaced with nodes below.
    
    const_nodes = [
        'Comment',
        'Fun', 'Class',
        'Import', 'ImportFrom',
        'Global',
        'Pass', 'Break', 'Continue',
        'ResetDemand',
        'RelUpdate', 'RelClear',
        'MapAssign', 'MapDelete', 'MapClear',
        'Num', 'Str', 'NameConstant', 'Name',
        'mask', 'alias',
        'boolop', 'operator', 'unaryop', 'cmpop',
        'setupop', 'setbulkop', 'dictbulkop', 'aggrop',
    ]
    
    sum_nodes = [
        'Module',
        'Raise', 'Try', 'Assert',
        'Return',
        'If',
        'Expr',
        'Assign', 'DecompAssign',
        'SetUpdate', 'SetClear',
        'DictAssign', 'DictDelete', 'DictClear',
        'AttrAssign', 'AttrDelete',
        # These operations might be more than constant-time to execute
        # if their operands are sets. We'll ignore this for cost
        # analysis since we don't generate this kind of code in our
        # maintenance functions.
        'UnaryOp', 'BoolOp', 'BinOp', 'Compare',
        'IfExp',
        'List', 'Set', 'Dict', 'Tuple',
        'Attribute', 'Subscript', 'DictLookup',
        'FirstThen',
        # Cost analysis assumes ImgLookup and other set indexing
        # operations are incrementalized.
        'ImgLookup', 'SetFromMap', 'Unwrap', 'Wrap',
        'IsSet', 'HasField', 'IsMap', 'HasArity',
        'excepthandler',
    ]
    
    unknown_nodes = [
        # Should not appear at cost analysis stage.
        'SetBulkUpdate', 'DictBulkUpdate',
        # Should not appear in our generated code.
        'GeneralCall',
        'ListComp', 'Comp', 'Aggr', 'AggrRestr',
        'clause', 'comprehension',
    ]
    
    const_nodes = tuple(getattr(L, n) for n in const_nodes)
    sum_nodes = tuple(getattr(L, n) for n in sum_nodes)
    unknown_nodes = tuple(getattr(L, n) for n in unknown_nodes)
    
    # Note that non-nullary functions cannot be constant-time since
    # we need to spend time to evaluate their arguments.
    const_funcs = [
        'Set', 'Obj',
    ]
    sum_funcs = []
    unknown_funcs = []
    
    def notimpl_helper(self, node):
        raise NotImplementedError('Cannot handle {} node'.format(
                                  node.__class__.__name__))
    
    visit_For = notimpl_helper
    visit_DecompFor = notimpl_helper
    visit_While = notimpl_helper
    
    def visit_Query(self, node):
        return self.visit(node.query)


class SizeAnalyzer(BaseCostAnalyzer):
    
    """Given an expression, determine its cardinality as a cost term."""
    
    const_nodes = [
        'UnaryOp', 'BoolOp', 'BinOp', 'Compare',
        'Num', 'Str', 'NameConstant',
        'List', 'Set', 'Dict', 'Tuple',
        'IsSet', 'HasField', 'IsMap', 'HasArity',
        # Assuming aggregate results can't be sets.
        # E.g., no min({a, b}, {a}).
        'Aggr', 'AggrRestr',
    ]
    
    sum_nodes = [
        'Unwrap', 'Wrap',
    ]
    
    unknown_nodes = [
        'GeneralCall',
        'Attribute', 'Subscript', 'DictLookup',
        'ListComp',
        'SetFromMap',
        'Comp',
    ]
    
    const_nodes = tuple(getattr(L, n) for n in const_nodes)
    sum_nodes = tuple(getattr(L, n) for n in sum_nodes)
    unknown_nodes = tuple(getattr(L, n) for n in unknown_nodes)
    
    def visit_IfExp(self, node):
        body = self.visit(node.body)
        orelse = self.visit(node.orelse)
        return Sum([body, orelse])
    
    def visit_Call(self, node):
        try:
            return super().visit_Call(node)
        except NotImplementedError:
            return Unknown()
    
    def visit_Name(self, node):
        return Name(node.id)
    
    def visit_FirstThen(self, node):
        return self.visit(node.then)
    
    def visit_ImgLookup(self, node):
        if isinstance(node.set, L.Name):
            return DefImgset(node.set.id, node.mask, node.bounds)
        else:
            return Unknown()
    
    def visit_Query(self, node):
        return self.visit(node.query)


class LoopCostAnalyzer(TrivialCostAnalyzer):
    
    """Extends the trivial cost analyzer to handle loops."""
    
    def visit_For(self, node):
        # For loops take the one-time cost of evaluating the iter,
        # plus the size of the iter times the cost of running the
        # body.
        iter_size = SizeAnalyzer.run(node.iter)
        iter_cost = self.visit(node.iter)
        body_cost = self.visit(node.body)
        return Sum([iter_cost, Product([iter_size, body_cost])])
    
    # DecompFor is the same since we don't care about target/vars.
    visit_DecompFor = visit_For
    
    def visit_While(self, node):
        # Return the body cost times an unknown number of iterations.
        body_cost = self.visit(node.body)
        return Product([Unknown(), body_cost])


class CallCostAnalyzer(LoopCostAnalyzer):
    
    """Extends the loop cost analyzer to handle function calls."""
    
    def __init__(self, func_params, func_costs):
        super().__init__()
        self.func_params = func_params
        """Map from function name to list of formal parameter names."""
        self.func_costs = func_costs
        """Map from function name to known cost for it, in terms of its
        formal parameters.
        """
    
    def visit_Call(self, node):
        arg_cost = Sum([self.visit(arg) for arg in node.args])
        
        # Check for one of the special cases.
        try:
            call_cost = super().visit_Call(node)
        except NotImplementedError:
            call_cost = None
        
        if call_cost is None:
            # Try retrieving and instantiating the cost from the map.
            name = node.func
            if name in self.func_costs:
                cost = self.func_costs[name]
                params = self.func_params[name]
                assert len(params) == len(node.args)
                
                # Create a substitution from formal parameter name to
                # argument variable name, or None if the argument is not
                # a variable.
                arg_names = [arg.id if isinstance(arg, L.Name) else None
                             for arg in node.args]
                subst = dict(zip(params, arg_names))
                # Instantiate.
                call_cost = ImgkeySubstitutor.run(cost, subst)
            else:
                call_cost = Unknown()
        
        return Sum([arg_cost, call_cost])


def analyze_costs(tree):
    """Analyze the costs of the functions in the program and return
    a map from function name to cost. If recursion is present, only
    non-recursive functions are analyzed.
    """
    all_funcs = L.get_defined_functions(tree)
    graph = L.analyze_functions(tree, all_funcs,
                                allow_recursion=True)
    
    # Analyze the functions in topological order, constructing
    # func_costs as we go.
    func_costs = {}
    func_params = graph.param_map
    for f in graph.order:
        body = graph.body_map[f]
        cost = CallCostAnalyzer.run(body, func_params, func_costs)
        
        # Eliminate image key terms that aren't formal parameters.
        key_filter = lambda p: p if p in func_params[f] else None
        cost = ImgkeySubstitutor.run(cost, key_filter)
        
        func_costs[f] = cost
    
    return func_costs


def type_to_cost(t):
    """Turn a type into a cost term representing the size of its
    domain.
    """
    if t in [T.Top, T.Bottom]:
        return Unknown()
    elif isinstance(t, T.Primitive):
        if t is T.Bool:
            return Unit()
        else:
            return Name(t.t.__name__)
    elif isinstance(t, T.Tuple):
        return Product([type_to_cost(e) for e in t.elts])
    elif isinstance(t, T.Refine):
        return Name(t.name)
    elif isinstance(t, T.Enum):
        return Unit()
    else:
        return Unknown()


def get_constant_bounded_rels(symtab):
    """Return a set of all names of relations whose size is bounded by a
    constant.
    """
    ct = symtab.clausetools
    
    const_rels = set()
    
    # Get constant-bounded U-sets.
    for q in symtab.get_queries().values():
        if (q.demand_set is not None and
            q.demand_set_maxsize is not None):
            const_rels.add(q.demand_set)
    
    # Get constant-bounded comprehension results.
    #
    # Iterate over all relations in order of their definition. (This
    # is consistent with the order in which the comprehension invariants
    # were transformed.)
    for r in symtab.get_relations().values():
        # Look for the hackish for_comp attribute to know that it's
        # a relation for a comprehension query.
        if not hasattr(r, 'for_comp'):
            continue
        comp = r.for_comp
        assert isinstance(comp, L.Comp)
        
        # Find all the LHS vars that are constrained to be in a
        # constant-bounded relation.
        determined = set()
        for cl in comp.clauses:
            if ct.rhs_rel(cl) in const_rels:
                determined.update(ct.lhs_vars(cl))
        
        # If all variables are determined, this comprehension is itself
        # constant-bounded.
        if ct.all_vars_determined(comp.clauses, determined):
            const_rels.add(r.name)
    
    return const_rels


def rewrite_cost_using_types(cost, symtab):
    """Rewrite a cost expression by using type information. Name costs
    for Set-typed variables are replaced by the domains of their
    elements. IndefImgset and DefImgset costs over relation-typed
    variables are replaced by the domains of the unbound components.
    """
    const_rels = get_constant_bounded_rels(symtab)
    
    class Trans(CostTransformer):
        def visit_Name(self, cost):
            # See if this is a constant-size relation.
            if cost.name in const_rels:
                return Unit()
            
            # Retrieve symbol.
            sym = symtab.get_symbols().get(cost.name, None)
            if sym is None:
                return cost
            
            # Retrieve element type.
            t = sym.type
            if t is None:
                return cost
            t = t.join(T.Set(T.Bottom))
            if not t.issmaller(T.Set(T.Top)):
                return cost
            elt_t = t.elt
            
            # Convert to cost.
            new_cost = type_to_cost(elt_t)
            new_cost = normalize(new_cost)
            if not isinstance(new_cost, Unknown):
                cost = new_cost
            
            return cost
        
        def visit_IndefImgset(self, cost):
            # Check for constant-time relations.
            if cost.rel in const_rels:
                return Unit()
            
            # Field lookups are constant time.
            if N.is_F(cost.rel) and cost.mask == L.mask('bu'):
                return Unit()
            
            sym = symtab.get_symbols().get(cost.rel, None)
            if sym is None:
                return cost
            
            # Get types for unbound components.
            t = sym.type
            if t is None:
                return cost
            if not (isinstance(t, T.Set) and
                    isinstance(t.elt, T.Tuple) and
                    len(t.elt.elts) == len(cost.mask.m)):
                return cost
            
            mask = cost.mask
            elts = t.elt.elts
            # Process out aggregate SetFromMap result components,
            # which are functionally determined by the map keys.
            if N.is_SA(cost.rel) and mask.m[-1] == 'u':
                mask = mask._replace(m=mask.m[:-1])
                elts = elts[:-1]
            
            _b_elts, u_elts = L.split_by_mask(mask, elts)
            
            new_cost = type_to_cost(T.Tuple(u_elts))
            new_cost = normalize(new_cost)
            if not isinstance(new_cost, Unknown):
                cost = new_cost
            
            return cost
        
        # Same logic for definite image sets.
        visit_DefImgset = visit_IndefImgset
    
    cost = Trans.run(cost)
    cost = normalize(cost)
    return cost


def annotate_costs(tree, symtab):
    """Analyze and annotate the costs of maintenance functions."""
    func_costs = analyze_costs(tree)
    
    class Trans(L.NodeTransformer):
        def visit_Fun(self, node):
            node = self.generic_visit(node)
            
            if node.name in func_costs:
                cost = func_costs[node.name]
                simp_cost = rewrite_cost_using_types(cost, symtab)
                cost_str = PrettyPrinter.run(cost)
                simp_cost_str = PrettyPrinter.run(simp_cost)
                comment = (L.Comment('Cost: O({})'.format(cost_str)),
                           L.Comment('      O({})'.format(simp_cost_str)))
                node = node._replace(body=comment + node.body)
            return node
    tree = Trans.run(tree)
    
    symtab.func_costs = func_costs
    
    return tree
