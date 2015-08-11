"""Symbol tables."""


__all__ = [
    'SymbolTable',
]


from incoq.util.collections import OrderedSet


class SymbolTable:
    
    def __init__(self):
        self.rels = OrderedSet()
        """Names of relations in declaration order."""
