"""Basic features for manipulating Python and IncAST code."""


from types import SimpleNamespace

from incoq.util.misc import flood_namespace

from . import nodes
from . import pynodes as P
from . import pyconv


L = SimpleNamespace()
flood_namespace(L.__dict__, nodes, pyconv)
