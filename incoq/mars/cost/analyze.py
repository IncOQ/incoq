"""Cost analysis."""


__all__ = [
    
]


from incoq.mars.incast import L

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
        if node.name in self.const_funcs:
            return Unit()
        
        elif node.name in self.sum_funcs:
            costs = []
            for arg in node.args:
                cost = self.visit(arg)
                costs.append(cost)
            return Sum(costs)
        
        elif node.name in self.unknown_funcs:
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
    const_funcs = []
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
