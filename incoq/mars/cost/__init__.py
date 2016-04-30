"""Asymptotic cost analysis."""


from incoq.util.misc import new_namespace

from .costs import *
from .algebra import *
from .analyze import *


C = new_namespace(costs, algebra, analyze)
