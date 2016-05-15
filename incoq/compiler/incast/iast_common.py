"""Common iAST features used by both Python and IncAST."""


__all__ = [
    # iAST exports.
    'trim',
    'dump',
    'NodeVisitor',
    'AdvNodeVisitor',
    'NodeTransformer',
    'AdvNodeTransformer',
    'PatVar',
    'Wildcard',
    'match',
    'PatternTransformer',
    
    'ExtractMixin',
]


from iast import (trim, dump, NodeVisitor, AdvNodeVisitor,
                  NodeTransformer, AdvNodeTransformer,
                  PatVar, Wildcard, match, PatternTransformer)


class ExtractMixin:
    
    """Utility for providing various tree selector wrappers
    around an action() function. It is expected that action
    is a parsing function, supplied by the subclass, that
    takes in a 'mode' argument.  
    """
    
    @classmethod
    def action(cls, *args, mode=None, **kargs):
        raise NotImplementedError
    
    @classmethod
    def unaction(cls, *args, **kargs):
        raise NotImplementedError
    
    # Aliases/wrappers.
    
    @classmethod
    def p(cls, *args, **kargs):
        return cls.action(*args, mode='mod', **kargs)
    
    @classmethod
    def pc(cls, *args, **kargs):
        return cls.action(*args, mode='code', **kargs)
    
    @classmethod
    def ps(cls, *args, **kargs):
        return cls.action(*args, mode='stmt', **kargs)
    
    @classmethod
    def pe(cls, *args, **kargs):
        return cls.action(*args, mode='expr', **kargs)
    
    @classmethod
    def ts(cls, *args, **kargs):
        return cls.unaction(*args, **kargs)
