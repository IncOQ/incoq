"""Definition of the IncAST language nodes, and a suite of utilities
for manipulating and converting them.

We use "PyAST" to refer to ASTs representing Python programs. These
ASTs may only contain Python node types, plus the special Comment
node type. We use "IncAST" to refer to ASTs that may also include
the types defined in nodes.py.
"""


# Mostly re-export things from our modules, but also define parse
# and unparse functions that do PyInc importing/exporting and
# macro node processing.

# Exports.
from .nodes import *
from .structconv import *
from .error import *
from .types import *
from .typeconstraints import *
from .typeeval import *
from .helpers import *
from .util import *
from .nodeconv import *
from .macros import *
from .inline import *
from .treeconv import *


def import_incast(tree):
    return IncLangImporter.run(tree)

def export_incast(tree):
    return IncLangExporter.run(tree)

def p(*args, **kargs):
    tree = parse_structast(*args, **kargs)
    tree = IncMacroProcessor.run(tree)
    return tree

def pc(*args, mode=None, **kargs):
    return p(*args, mode='code', **kargs)

def ps(*args, mode=None, **kargs):
    return p(*args, mode='stmt', **kargs)

def pe(*args, mode=None, **kargs):
    return p(*args, mode='expr', **kargs)

def ts(tree):
    tree = IncLangExporter.run(tree)
    return unparse_structast(tree)

def ts_typed(tree):
    tree = IncLangExporter.run(tree)
    return unparse_structast_typed(tree)
