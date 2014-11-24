"""Asymptotic cost analysis and simplification."""


__all__ = [
    'CostAnalyzer',
    'analyze_costs',
]


from util.unify import unify

import invinc.incast as L
from invinc.set import Mask
from invinc.comp import IncComp

from .cost import *


class CostAnalyzer(L.NodeVisitor):
    
    """Determine a cost for a chunk of code. The cost is expressed in
    terms of the given args. Costs for function calls appearing in the
    code are determined using argmap and costmap.
    """
    
    # We list AST node types that have a simple rule for determining
    # their cost: ones that take constant time, ones that take the
    # sum of their children's times, and ones that are unknown or
    # not handled. Other cases like loops are covered with explicit
    # visitor methods below. Note that these lists may include non-
    # terminal types in the ASDL.
    
    ### Python 3.4: These lists will need to be modified.
    
    const_nodes = [
        'FunctionDef', 'ClassDef', 'Import', 'ImportFrom',
        'Global', 'Nonlocal', 'Pass', 'Break', 'Continue',
        'Lambda', 'Yield', 'Num', 'Str', 'Bytes', 'Ellipsis',
        'Name',
        'expr_context', 'boolop', 'operator', 'unaryop', 'cmpop',
        'alias', 'withitem',
        
        'Comment',
        # These two should be incrementalized away
        'SetMatch', 'DeltaMatch',
    ]
    
    sum_nodes = [
        'Return', 'Delete', 'Assign', 'AugAssign', 'If', 'With',
        'Raise', 'Try', 'Assert', 'Expr',
        'BoolOp', 'BinOp', 'UnaryOp', 'IfExp', 'Dict', 'Set',
        'Compare', 'Attribute', 'Subscript', 'Starred',
        'List', 'Tuple',
        'slice', 'excepthandler',
        
        'Maintenance', 'NoDemQuery', 'Instr',
        'SetUpdate', 'RCSetRefUpdate', 'IsEmpty', 'GetRef',
        'AssignKey', 'DelKey', 'Lookup', 'ImgLookup', 'RCImgLookup',
        'SMLookup',
    ]
    
    unknown_nodes = [
        'ListComp', 'SetComp', 'DictComp', 'GeneratorExp',
        'comprehension',
        'arguments', 'arg', 'keyword',
        
        'Enumerator', 'Comp', 'Aggregate',
    ]
    
    const_nodes = tuple(getattr(L, n) for n in const_nodes)
    sum_nodes = tuple(getattr(L, n) for n in sum_nodes)
    unknown_nodes = tuple(getattr(L, n) for n in unknown_nodes)
    
    # Also keep a list of known constant-time built-in functions.
    const_funcs = [
        'set', 'Set', 'Obj', 'Tree',
        'isinstance', 'hasattr',
        'next', 'iter',
        'globals',
        'len', # constant because when it's used in generated code,
               # it's used for checking tuple arity, not aggregate
               # queries
        'max2', 'min2',
    ]
    const_meths = [
        '__min__', '__max__', 'singlelookup'
    ]
    
    def __init__(self, args, argmap, costmap, *, warn=False):
        super().__init__()
        self.args = args
        self.argmap = argmap
        self.costmap = costmap
        self.warn = warn
    
    def WarnUnknownCost(self, node):
        """Return UnknownCost, but also print the node that led to it
        if self.warn is True.
        """
        if self.warn:
            print('---- Unknown cost ----    ' + str(L.ts(node)))
        return UnknownCost()
    
    def WarnNameCost(self, node, name):
        """As above, but return a NameCost to act as a placeholder
        instead.
        """
        unname = 'UNKNOWN_' + name
        if self.warn:
            print('---- Unknown cost ----    ' + str(L.ts(node)) +
                  '  (using placeholder ' + unname + ')')
        return NameCost(unname)
    
    def process(self, tree):
        res = super().process(tree)
        res = Simplifier.run(res)
        res = normalize(res)
        return res
    
    def visit(self, tree):
        # Primitive values in the tree are considered to have unit cost.
        if isinstance(tree, L.AST):
            res = self.node_visit(tree)
        elif isinstance(tree, tuple):
            res = self.seq_visit(tree)
        else:
            res = UnitCost()
        
        return res
    
    def generic_visit(self, node):
        # Dispatch based on the lists above.
        if isinstance(node, self.const_nodes):
            return UnitCost()
        
        elif isinstance(node, self.sum_nodes):
            costs = []
            for field in node._fields:
                value = getattr(node, field)
                cost = self.visit(value)
                costs.append(cost)
            return SumCost(costs)
        
        elif isinstance(node, self.unknown_nodes):
            return self.WarnUnknownCost(node)
        
        else:
            raise AssertionError('Unhandled node type: ' +
                                 type(node).__name__)
    
    def seq_visit(self, seq):
        # Sum up the costs of a sequence of nodes.
        costs = []
        for item in seq:
            cost = self.visit(item)
            costs.append(cost)
        return SumCost(costs)
    
    def visit_MacroSetUpdate(self, node):
        if isinstance(node.target, L.Name):
            if node.other is None:
                return NameCost(node.target.id)
            elif isinstance(node.other, L.Name):
                return SumCost([NameCost(node.target),
                                NameCost(node.other)])
        
        return self.WarnUnknownCost(node)
    
    def expr_tosizecost(self, expr):
        """Turn an iterated expression into a cost bound for its
        cardinality.
        """
        if isinstance(expr, L.Name):
            return NameCost(expr.id)
        
        # Catch case of iterating over a delta set.
        # We'll just say O(delta set), even though it can have
        # duplicates.
        elif (isinstance(expr, L.Call) and
              isinstance(expr.func, L.Attribute) and
              isinstance(expr.func.value, L.Name) and
              expr.func.attr == 'elements'):
            return NameCost(expr.func.value.id)
        
        elif isinstance(expr, L.SetMatch):
            if isinstance(expr.target, (L.Set, L.DeltaMatch)):
                return UnitCost()
            elif (isinstance(expr.target, L.Name) and
                  L.is_vartuple(expr.key)):
                keys = L.get_vartuple(expr.key)
                if all(k in self.args for k in keys):
                    return DefImgsetCost(expr.target.id, Mask(expr.mask),
                                         L.get_vartuple(expr.key))
                else:
                    return IndefImgsetCost(expr.target.id, Mask(expr.mask))
            else:
                return self.WarnUnknownCost(expr)
        
        elif isinstance(expr, L.DeltaMatch):
            return UnitCost()
        
        else:
            return self.WarnUnknownCost(expr)
    
    def visit_For(self, node):
        # For loops are the product of their body and the number
        # of times run, plus the else branch.
        sizecost = self.expr_tosizecost(node.iter)
        bodycost = self.visit(node.body)
        orelsecost = self.visit(node.orelse)
        loopcost = ProductCost([sizecost, bodycost])
        return SumCost([loopcost, orelsecost])
    
    def visit_While(self, node):
        # While loops run an unknown number of times.
        bodycost = self.visit(node.body)
        return ProductCost([UnknownCost(), bodycost])
    
    def visit_Call(self, node):
        # If the function is runtimelib qualified, strip it
        # so we can match const_funcs.
        if (isinstance(node.func, L.Attribute) and
            isinstance(node.func.value, L.Name) and
            node.func.value.id == 'runtimelib'):
            call = node._replace(func=L.ln(node.func.attr))
        else:
            call = node
        
        # Certain calls of methods are recognized
        # as constant.
        if (isinstance(call.func, L.Attribute) and
            call.func.attr in self.const_meths):
            return UnitCost()
        
        # Non-plain function calls are unknown.
        if not L.is_plaincall(call):
            return self.WarnUnknownCost(node)
        name, args = L.get_plaincall(call)
        
        # Some known built-in constant functions are recognized.
        if name in self.const_funcs:
            return UnitCost()
        
        # If the name doesn't appear in argmap and costmap, it's
        # unknown. But return a NameCost representing it anyway
        # so more info can be added later.
        if not (name in self.argmap and name in self.costmap):
            return self.WarnNameCost(node, name)
        
        formals = self.argmap[name]
        assert len(args) == len(formals), \
            'Function call args ({}) don\'t match definition ({})'.format(
            len(args), len(formals))
        
        # The call's actual arguments are preserved in the returned cost
        # only if they are simple variables and they are parameters to
        # the caller's own function. Otherwise they get simplified away.
        formalsub = []
        for a in args:
            if isinstance(a, L.Name) and a.id in self.args:
                formalsub.append(a.id)
            else:
                formalsub.append(None)
        subst = dict(zip(formals, formalsub))
        
        cost = ImgkeySubstitutor.run(self.costmap[name], subst)
        return cost
    
    def visit_DemQuery(self, node):
        callnode = L.Call(L.ln(L.N.queryfunc(node.demname)), node.args,
                          (), None, None)
        callcost = self.visit(callnode)
        retrievecost = self.visit(node.value)
        return SumCost([callcost, retrievecost])

def func_costs(tree, *, warn=False):
    funcs = L.PlainFunctionFinder.run(tree, stmt_only=False)
    
    param_map, body_map, _edges, order = L.FunctionInfoGetter.run(
                                tree, funcs, require_nonrecursive=True)
    
    cost_map = {}
    for f in order:
        body = body_map[f]
        cost = CostAnalyzer.run(body, param_map[f], param_map, cost_map,
                                warn=warn)
        cost_map[f] = cost
    
    return cost_map

class CostLabelAdder(L.NodeTransformer):
    
    """Add a cost comment to each function that we have info for."""
    
    def __init__(self, costmap):
        super().__init__()
        self.costmap = costmap
    
    def visit_FunctionDef(self, node):
        cost = self.costmap.get(node.name, None)
        if cost is None:
            return node
        else:
            header = (L.Comment('Cost: O({})'.format(str(cost))),)
            return node._replace(body=header + node.body)

def find_domain_constrs(manager, tree):
    """Return domain constraints for the program."""
    constrs = []
    for inv in manager.invariants.values():
        name = inv.name
        new_constrs = inv.spec.get_domain_constraints(name)
        constrs.extend(new_constrs)
    
    subst = unify(constrs)
    return subst

def analyze_costs(manager, tree, *, warn=False):
    """Analyze function costs. Return a tree modified by adding cost
    annotations, a dictionary of these costs, and a substitution mapping
    for domain constraints.
    """
    costmap = func_costs(tree, warn=warn)
    tree = CostLabelAdder.run(tree, costmap)
    domain_subst = find_domain_constrs(manager, tree)
    return tree, costmap, domain_subst
