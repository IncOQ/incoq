"""Type system and analysis."""


from incoq.util.misc import new_namespace

from . import types
from . import analysis


T = new_namespace(types, analysis)
