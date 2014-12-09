"""Node definitions for IncAST."""

# We use "PyAST" to refer to ASTs that use only node types that exist
# in Python code, and "IncAST" for ASTs that may also include our own
# node types. This terminology is independent of whether the
# representation of the AST uses the classes defined in the standard
# library's ast module or the structs in the iast package.


__all__ = [
    'incpy_nodes',
    'incstruct_nodes',
    
    # Programmatically modified to include the struct representations
    # for all IncAST nodes.
]


import copy

from simplestruct.util import make_frozen

import iast.node
from iast.node import *
from iast.node import struct_nodes
from iast.pattern import PatVar


# IncAST-specific node type names.
inc_node_names = [
    # Include Patvar, for completeness.
    'PatVar',
    
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


import ast

from iast.node import py_nodes


# The only new node in Python node format is Comment, for source
# printing purposes.

class Comment(ast.stmt):
    _fields = ('text',)     # string

# Mapping for Python nodes.
newpy_nodes = {'Comment': Comment}
incpy_nodes = py_nodes.copy()
incpy_nodes.update(newpy_nodes)

del Comment


# Struct node versions of invinc nodes.

class Comment(stmt):
    _fields = ('text',)     # string

class NOptions(stmt):
    _fields = ('opts',)     # dictionary
    
    def __new__(cls, opts):
        opts = make_frozen(opts)
        return super().__new__(cls, opts)

class QOptions(stmt):
    _fields = ('query',     # string
               'opts')      # dictionary
    
    def __new__(cls, query, opts):
        opts = make_frozen(opts)
        return super().__new__(cls, query, opts)

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
    
    def __new__(cls, resexp, clauses, params, options):
        options = make_frozen(options)
        return super().__new__(cls, resexp, clauses, params, options)

class Aggregate(expr):
    _fields = ('value',     # expression
               'op',        # operation string
               'options')   # dictionary
    
    def __new__(cls, value, op, options):
        options = make_frozen(options)
        return super().__new__(cls, value, op, options)


# Mapping for struct nodes including invinc nodes.
newstruct_nodes = {name: globals()[name]
                   for name in inc_node_names}
incstruct_nodes = struct_nodes.copy()
incstruct_nodes.update(newstruct_nodes)


# Programmatically update __all__. Re-export all struct nodes
# from iast.node.
__all__.extend(sorted(incstruct_nodes))
