"""Asymptotic cost analysis of program fragments."""


__all__ = [
    'CostAnalyzer',
    'func_costs',
    'CostLabelAdder',
    'analyze_costs',
]


import invinc.compiler.incast as L
from invinc.compiler.set import Mask

from .cost import *


class CostAnalyzer(L.NodeVisitor):
    
    """Determine a cost for a chunk of code. The cost is expressed in
    terms of the given args. Costs for function calls appearing in the
    code are determined using argmap and costmap.
    """
    
    # Most nodes either take constant time or the sum of the costs
    # of their children. We list these nodes below. The remaining
    # ones have visitor handlers.
    #
    # For conciseness, the lists may use a non-terminal node type
    # instead of all of its terminal node types, e.g. expr_context
    # instead of Load, Store, etc.
    #
    # Lists are by name, and programmatically replaced by nodes
    # after.
    
    const_nodes = [
        'FunctionDef', 'ClassDef', 'Import', 'ImportFrom',
        'Global', 'Nonlocal', 'Pass', 'Break', 'Continue',
        'Lambda', 'Yield', 'YieldFrom', 'Num', 'Str', 'Bytes',
        'NameConstant', 'Ellipsis', 'Name', 'NameConstant',
        
        'expr_context', 'boolop', 'operator', 'unaryop', 'cmpop',
        'alias',
        
        'Comment',
        
        'NOptions', 'QOptions', 'DeltaMatch',
    ]
    
    sum_nodes = [
        'Return', 'Delete', 'Assign', 'AugAssign', 'If', 'With',
        'Raise', 'Try', 'Assert', 'Expr',
        'BoolOp', 'BinOp', 'UnaryOp', 'IfExp', 'Dict', 'Set',
        'Compare', 'Attribute', 'Subscript', 'Starred',
        'List', 'Tuple',
        
        'slice', 'excepthandler', 'arguments', 'arg', 'keyword',
        'withitem',
        
        'Maintenance', 'SetUpdate', 'RCSetRefUpdate', 'IsEmpty',
        'GetRef', 'AssignKey', 'DelKey', 'Lookup', 'ImgLookup',
        'RCImgLookup', 'SMLookup',  'NoDemQuery', 'Instr',
    ]
    
    const_nodes = tuple(getattr(L, n) for n in const_nodes)
    sum_nodes = tuple(getattr(L, n) for n in sum_nodes)
    
    # We also have lists of known constant-time built-in functions
    # and methods.
    
    const_funcs = [
        'set', 'Set', 'Obj', 'Tree',
        'isinstance', 'hasattr',
        'next', 'iter',
        'globals',
        'len', # constant because when it's used in generated code,
               # it's used for checking tuple arity, not aggregate
               # queries
        'max2', 'min2', # constant because they're used on a
                        # fixed number of arguments
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
        # For loops are the one-time cost of evaluating the iter,
        # plus the product of the number of times repeated (size
        # of iter) with the cost of the body and evaluating the
        # target, plus the cost of the else branch.
        targetcost = self.visit(node.target)
        itercost = self.visit(node.iter)
        repeatcost = self.expr_tosizecost(node.iter)
        bodycost = self.visit(node.body)
        orelsecost = self.visit(node.orelse)
        loopcost = ProductCost([repeatcost, SumCost([bodycost, targetcost])])
        return SumCost([itercost, loopcost, orelsecost])
    
    def visit_While(self, node):
        # While loops run an unknown number of times.
        # Their cost is the product of an unknown with the
        # body cost, plus the else branch.
        bodycost = self.visit(node.body)
        orelsecost = self.visit(node.orelse)
        loopcost = ProductCost([UnknownCost(), bodycost])
        return SumCost([loopcost, orelsecost])
    
    def comp_helper(self, node):
        # Comprehensions and their variants are the products of all
        # generators and the result expression.
        gencosts = [self.visit(g) for g in node.generators]
        eltcost = self.visit(node.elt)
        return ProductCost(gencosts + [eltcost])
    
    visit_ListComp = comp_helper
    visit_SetComp = comp_helper
    
    def visit_DictComp(self, node):
        gencosts = [self.visit(g) for g in node.generators]
        eltcost = SumCost([self.visit(node.key), self.visit(node.value)])
        return ProductCost(gencosts + [eltcost])
    
    visit_GeneratorExp = comp_helper
    
    def visit_comprehension(self, node):
        itercost = self.visit(node.iter)
        targetcost = self.visit(node.target)
        ifcost = self.visit(node.ifs)
        repeatcost = self.expr_tosizecost(node.iter)
        loopcost = ProductCost([SumCost([targetcost, ifcost]), repeatcost])
        return SumCost([itercost, loopcost])
    
    # IncAST-specific nodes.
    
    def visit_MacroSetUpdate(self, node):
        # Cost of evaluating each side, plus cost of size of each side.
        leftcost = self.visit(node.target)
        leftsize = self.expr_tosizecost(node.target)
        if node.other is None:
            rightcost = rightsize = UnitCost()
        else:
            rightcost = self.visit(node.other)
            rightsize = self.expr_tosizecost(node.other)
        return SumCost([leftcost, leftsize, rightcost, rightsize])
    
    def visit_DemQuery(self, node):
        # Translate into a call to the demand function. Cost is
        # that plus the result retrieval cost.
        callnode = L.Call(L.ln(L.N.queryfunc(node.demname)), node.args,
                          (), None, None)
        callcost = self.visit(callnode)
        retrievecost = self.visit(node.value)
        return SumCost([callcost, retrievecost])
    
    def visit_SetMatch(self, node):
        # Cost of evaluating. Size doesn't matter since the image
        # set can be returned in constant time via auxiliary map.
        return SumCost([self.visit(node.target), self.visit(node.key)])
    
    def visit_Enumerator(self, node):
        itercost = self.visit(node.iter)
        targetcost = self.visit(node.target)
        repeatcost = self.expr_tosizecost(node.iter)
        loopcost = ProductCost([targetcost, repeatcost])
        return SumCost([itercost, loopcost])
    
    def visit_Comp(self, node):
        # Cost based on a left-to-right evaluation order.
        # We look at the clauses rightmost first and multiply
        # or add its cost depending on whether it is an
        # Enumerator or condition.
        cost = self.visit(node.resexp)
        for cl in node.clauses:
            clcost = self.visit(cl)
            if isinstance(cl, L.Enumerator):
                cost = ProductCost([clcost, cost])
            else:
                cost = SumCost([clcost, cost])
        return cost
    
    def visit_Aggregate(self, node):
        # Evaluation cost plus size cost.
        evalcost = self.visit(node.value)
        sizecost = self.expr_tosizecost(node.value)
        return SumCost([evalcost, sizecost])
    
    # The all-powerful Call case.
    
    def visit_Call(self, node):
        # If the function is invinc.runtime-qualified, strip it
        # so we can match const_funcs.
        if (isinstance(node.func, L.Attribute) and
            isinstance(node.func.value, L.Attribute) and
            node.func.value.attr == 'runtime' and
            isinstance(node.func.value.value, L.Name) and
            node.func.value.value.id == 'invinc'):
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


#def find_domain_constrs(manager, tree):
#    """Return domain constraints for the program."""
#    constrs = []
#    for inv in manager.invariants.values():
#        name = inv.name
#        new_constrs = inv.spec.get_domain_constraints(name)
#        constrs.extend(new_constrs)
#    
#    subst = unify(constrs)
#    return subst

def analyze_costs(manager, tree, *, warn=False):
    """Analyze function costs. Return a tree modified by adding cost
    annotations, a dictionary of these costs, and a substitution mapping
    for domain constraints.
    """
    costmap = func_costs(tree, warn=warn)
    tree = CostLabelAdder.run(tree, costmap)
#    domain_subst = find_domain_constrs(manager, tree)
    return tree, costmap #, domain_subst
