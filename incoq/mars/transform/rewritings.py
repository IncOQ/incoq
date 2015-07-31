"""Pre- and post-processing rewritings."""


__all__ = [
    'ImportPreprocessor',
]


from incoq.util.seq import pairs
from incoq.mars.incast import L, P


class ImportPreprocessor(L.NodeTransformer):
    
    """Preprocessor for Python code that eliminates some features
    that can't be directly expressed in IncAST.
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
