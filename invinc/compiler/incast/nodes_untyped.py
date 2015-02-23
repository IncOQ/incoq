"""Node definitions for IncAST, without type information."""


__all__ = [
    'native_nodes',
    'incast_nodes',
    
    # Programmatically modified to include the keys of incast_nodes.
]


import ast
from iast.python.python34 import native_nodes as _native_nodes, py_nodes

from invinc.util.collections import make_frozen

# Flood the namespace with Struct nodes for PyASTs.
globals().update(py_nodes)


# Names of nodes unique to IncAST.
incast_node_names = [
    'Comment',
    
    'NOptions',
    'QOptions',
    
    'Maintenance',
    
    'SetUpdate',
    'MacroSetUpdate',
    'RCSetRefUpdate',
    'IsEmpty',
    'GetRef',
    'AssignKey',
    'DelKey',
    'Lookup',
    'ImgLookup',
    'RCImgLookup',
    'SMLookup',
    
    'DemQuery',
    'NoDemQuery',
    'Instr',
    
    'SetMatch',
    'DeltaMatch',
    'Enumerator',
    'Comp',
    'Aggregate',
]


# The only new node in native format is Comment, for source
# printing purposes.

class Comment(ast.stmt):
    _fields = ('text',)     # string

# Namespace for native nodes.
native_nodes = _native_nodes.copy()
native_nodes.update({
    'Comment': Comment,
})

del Comment


# Definitions for nodes unique to IncAST.

# Interesting detail: The typed versions of these nodes are
# generated in nodes.py by stealing entries from the namespace
# of their untyped equivalents. Since some of the below methods
# use super(), we need the explicit form of super with args so
# that they continue to work in the typed node classes, despite
# having the wrong __class__ cell entry. __new__() also has to
# work for the typed versions as well so it has to tolerate an
# extra type field.

class Comment(stmt):
    _fields = ('text',)     # string

class NOptions(stmt):
    _fields = ('opts',)     # dictionary
    
    def __new__(cls, opts):
        opts = make_frozen(opts)
        return super(cls, cls).__new__(cls, opts)

class QOptions(stmt):
    _fields = ('query',     # string
               'opts')      # dictionary
    
    def __new__(cls, query, opts):
        opts = make_frozen(opts)
        return super(cls, cls).__new__(cls, query, opts)

class Maintenance(stmt):
    _fields = ('name',      # identifier
               'desc',      # string
               'precode',   # statement list
               'update',    # statement list
               'postcode')  # statement list

class SetUpdate(stmt):
    _fields = ('target',    # expression
               'op',        # 'add' or 'remove'
               'elem')      # expression
    
    def is_varupdate(self):
        # Hackish. This only works for typed nodes, not untyped ones,
        # and has to import the typed version of the node module
        # to work. Should refactor.
        from .nodes import Name
        return isinstance(self.target, Name)
    
    def get_varupdate(self):
        assert self.is_varupdate()
        return self.target.id, self.op, self.elem

class MacroSetUpdate(stmt):
    _fields = ('target',    # expression
               'op',        # 'union', 'inter', 'diff', 'symdiff',
                            # 'assign', or 'clear'
               'other')     # expression or None

class RCSetRefUpdate(stmt):
    _fields = ('target',    # expression
               'op',        # 'incref' or 'decref'
               'elem')      # expression 

class IsEmpty(expr):
    _fields = ('target',)   # expression

class GetRef(expr):
    _fields = ('target',    # expression
               'elem')      # expression

class AssignKey(stmt):
    _fields = ('target',    # expression
               'key',       # expression
               'value')     # expression

class DelKey(stmt):
    _fields = ('target',    # expression
               'key')       # expression

class Lookup(expr):
    _fields = ('target',    # expression
               'key',       # expression
               'default')   # expression or None

class ImgLookup(expr):
    _fields = ('target',    # expression
               'key')       # expression

class RCImgLookup(expr):
    _fields = ('target',    # expression
               'key')       # expression

class SMLookup(expr):
    _fields = ('target',    # expression
               'mask',      # string
               'key',       # expression
               'default')   # expression or None

class DemQuery(expr):
    _fields = ('demname',   # string
               'args',      # expression list
               'value')     # expression option

class NoDemQuery(expr):
    _fields = ('value',)    # expression

class Instr(expr):
    _fields = ('value',     # expression
               'expvalue')  # expression

class SetMatch(expr):
    _fields = ('target',    # expression
               'mask',      # string
               'key')       # expression

class DeltaMatch(expr):
    _fields = ('target',    # expression
               'mask',      # string
               'elem',      # expression
               'limit')     # integer

class Enumerator(AST):
    _fields = ('target',    # expression
               'iter')      # expression

class Comp(expr):
    _fields = ('resexp',    # expression
               'clauses',   # list of Enumerator and expression nodes
               'params',    # identifier list, or None
               'options')   # dictionary, or None
    
    def __new__(cls, resexp, clauses, params, options, *args, **kargs):
        options = make_frozen(options)
        return super(cls, cls).__new__(
                            cls, resexp, clauses, params, options,
                            *args, **kargs)

class Aggregate(expr):
    _fields = ('value',     # expression
               'op',        # operation string
               'options')   # dictionary
    
    def __new__(cls, value, op, options, *args, **kargs):
        options = make_frozen(options)
        return super(cls, cls).__new__(cls, value, op, options,
                                       *args, **kargs)


# Namespace for IncAST nodes.
new_incast_nodes = {name: globals()[name]
                    for name in incast_node_names}
incast_nodes = py_nodes.copy()
incast_nodes.update(new_incast_nodes)

__all__.extend(incast_nodes.keys())
