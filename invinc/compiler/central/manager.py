###############################################################################
# manager.py                                                                  #
# Author: Jon Brandvein                                                       #
###############################################################################

"""Central manager construction."""


__all__ = [
    'get_clause_factory',
    
    'make_manager',
    
    'ManagerCase',
    'CentralCase',
]


from unittest import TestCase

import invinc.compiler.incast as L
from invinc.compiler.comp import Join, CompSpec, ClauseFactory
from invinc.compiler.obj import ObjClauseFactory_Mixin
from invinc.compiler.demand import DemClauseFactory_Mixin
from invinc.compiler.tup import TupClauseFactory_Mixin


from .options import OptionsManager


class CentralClauseFactory(TupClauseFactory_Mixin,
                           DemClauseFactory_Mixin,
                           ObjClauseFactory_Mixin,
                           ClauseFactory):
    pass

# TODO: This is an ugly hack so that clause factories can be pickled.
# (This in turn is needed to be able to pickle comp specs.) In the
# future I should change it so that clause factories are used as
# instances rather than as classes. Then the objdomain and typecheck
# flags would be instance attributes and would be naturally pickleable.

class ClauseFactory_ObjType(CentralClauseFactory):
    objdomain = True
    typecheck = True
class ClauseFactory_ObjNoType(CentralClauseFactory):
    objdomain = True
    typecheck = False
class ClauseFactory_NoObjType(CentralClauseFactory):
    objdomain = False
    typecheck = True
class ClauseFactory_NoObjNoType(CentralClauseFactory):
    objdomain = False
    typecheck = False

def get_clause_factory(*, use_objdomain, use_typecheck):
    """Construct a clause factory subclass with the desired flags."""
    return {(True, True): ClauseFactory_ObjType,
            (True, False): ClauseFactory_ObjNoType,
            (False, True): ClauseFactory_NoObjType,
            (False, False): ClauseFactory_NoObjNoType
           }[use_objdomain, use_typecheck]


class Manager:
    
    """Transformation manager. Keeps centralized information about
    transforming a single program.
    
    This information includes:
    
      - the parser (with registered macros)
      - the specified options
      - fresh name/prefix generator
      - pair sets used for representing object-domain relationships
    """
    
    def __init__(self, namegen=None):
        if namegen is None:
            namegen = L.NameGenerator()
        self.namegen = namegen
        """Unique variable identifier generator."""
        
        self.parser = L
        
        self.compnamegen = L.NameGenerator(fmt='Comp{}', counter=1)
        """Generator specifically for naming comprehension queries."""
        
        from invinc.compiler.aggr import AGGR_PREFIX
        self.aggrnamegen = L.NameGenerator(fmt=AGGR_PREFIX + '{}', counter=1)
        """Generator specifically for naming aggregate queries."""
        
        self.options = OptionsManager()
        """Options for transformation."""
        
        self.header_comments = []
        """List of comments to emit at top of code."""
        
        self.repinc_seen = set()
        """Set of comp queries already transformed."""
        
        self.stats = {
            'trans time': 0,        # transformation time (process time)
            'lines': 0,             # lines of code, excl. whitespace/comments
            
            'incr queries': 0,      # number of queries incrementalized
            'incr comps': 0,        # number of comps incrementalized
            'incr aggrs': 0,        # number of aggregates incrementalized
            
            'orig queries': 0,      # number of incr. queries that were
                                    # from the input program
            'orig updates': 0,      # number of updates to incr. queries
                                    # from the input program
            
            'dem structs': 0,       # number of tags/filters/inner-usets
                                    # created for filtered comps
            
            'comps expanded': 0,    # number of comps expanded as batch + maps 
            
            'auxmaps': 0,           # number of auxmaps created
            
            'queries processed': 0, # number of queries considered for
                                    # transformation (not necessarily actually
                                    # transformed)
            
            'queries skipped': 0,   # number of queries skipped for not
                                    # satisfying syntactic requirements
                                    # for transformation
            
            # The following are used for exporting transformation data
            # for later analysis.
            'funccosts': {},        # dictionary mapping from function name to
                                    # analyzed cost
            'domain_subst': {},     # domain constraint solutions
            'invariants': {},       # mapping from invariant name to spec obj
        }
        """Statistics about the transformation."""
        
        self.original_queryinvs = set()
        """Set of names of invariants corresponding to queries
        from the original program.
        """
        
        # Hackish.
        self.parser.manager = self
        self.parser.options = self.options
        
        # Still hackish.
        self.use_mset = False
        self.fields = []
        self.use_mapset = False
        
        self.invariants = {}
        """Map from name to IncComp/IncAggr object."""
    
    def add_macros(self, seq):
        """Register a sequence of ContextMacros, and update their
        manager to be this one.
        """
        for item in seq:
            self.parser.macros.add(item)
            item.manager = self
    
    def add_note(self, s):
        """Append a line to the header comments."""
        self.header_comments += [L.Comment(s)]
    
    def add_invariant(self, name, inv):
        from invinc.compiler.comp import IncComp
        from invinc.compiler.aggr import IncAggr
        assert isinstance(inv, (IncComp, IncAggr))
        self.invariants[name] = inv
        self.add_note('{name} := {inv.spec}'.format(**locals()))


def make_manager():
    """Construct and return a Manager with all macros."""
    man = Manager()
    man.factory = CentralClauseFactory
    return man


class ManagerCase:
    
    """Mixin for unit tests that need a manager for parsing purposes."""
    
    def setUp(self):
        super().setUp()
        
        self.manager = man = make_manager()
        self.options = man.options
        self.parser = man.parser
        self.p = man.parser.p
        self.pc = man.parser.pc
        self.ps = man.parser.ps
        self.pe = man.parser.pe
        self.trim = man.parser.trim
        self.ts = man.parser.ts
    
    def tearDown(self):
        del self.manager
        del self.options
        del self.parser, self.p, self.pc, self.ps, self.pe
        
        super().tearDown()
    
    def make_join(self, source):
        """Construct a Join from a comprehension's source code
        (ignoring the result expression).
        """
        node = L.pe(source)
        join = Join.from_comp(node, self.manager.factory)
        return join
    
    def make_relcompspec(self, source, params):
        """Construct a CompSpec from a comprehension's source code."""
        node = L.pe(source)
        node = node._replace(params=params)
        spec = CompSpec.from_comp(node, self.manager.factory)
        return spec


class CentralCase(ManagerCase, TestCase):
    
    """Combination-class for unit test cases with added functionality."""
