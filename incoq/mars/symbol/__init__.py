"""Config, symbols, names, and queries."""


from incoq.util.misc import new_namespace

from . import config
from . import symbols
from . import symtab


S = new_namespace(config, symbols, symtab)
N = symtab.N
