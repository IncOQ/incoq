"""Invoke the transformation system."""


import os
from time import clock
from simplestruct import Field, TypedField

from invinc.transform import Task, do_tasks


class TestProgramTask(Task):
    
    prog = Field(str)
    """Test program path, relative to the invinc/tests/programs
    directory, excluding the "_in.py" suffix.
    """
    
    def __init__(self, prog):
        path = os.path.join('invinc/tests/programs', prog)
        self.input_name = path + '_in.py'
        self.output_name = path + '_out.py'
        self.nopts = {'verbose': True, 'eol': 'lf'}
        self.qopts = {}
        self.display_name = prog


class TaskTemplate(Task):
    
    display_name = TypedField(str)
    base_name = TypedField(str)
    """Base name to use, relative to src/, excluding suffix like
    _in.py, _dem.py, etc.
    """
    qopts = Field()
    
    out_suffix_override = Field()
    display_suffix_override = Field()
    """If given, override the class default."""
    
    out_suffix = None
    """Suffix appended to output filename, excluding .py."""
    
    display_suffix = None
    """Suffix appended to display name."""
    
    extra_nopts = {}
    """nopts to use. Note that entries in this dictionary are inherited
    and merged with entries in subclasses.
    """
    
    def __init__(self, display_name, base_name, qopts,
                 out_suffix_override, display_suffix_override):
        if out_suffix_override is not None:
            self.out_suffix = out_suffix_override
        if display_suffix_override is not None:
            self.display_suffix = display_suffix_override
        
        self.input_name = base_name + '_in.py'
        self.output_name = '{}_{}.py'.format(base_name, self.out_suffix)
        
        bases = [c for c in type(self).__mro__
                   if issubclass(c, TaskTemplate)]
        self.nopts = {}
        for c in reversed(bases):
            self.nopts.update(c.extra_nopts)
        
        self.display_name = display_name + ' ' + self.display_suffix

class IN(Task):
    
    display_name = TypedField(str)
    base_name = TypedField(str)
    
    def __init__(self, display_name, base_name):
        self.display_name = display_name + ' Input'
        self.input_name = base_name + '_in.py'
        self.output_name = None

class COM(TaskTemplate):
    _inherit_fields = True
    extra_nopts = {'verbose': True,
                   'maint_inline': False,
                   'analyze_costs': True,
                   'selfjoin_strat': 'sub',
                   'default_aggr_halfdemand': True,
                   'autodetect_input_rels': True}

class AUX(COM):
    _inherit_fields = True
    out_suffix = 'aux'
    display_suffix = 'Batch w/ maps'
    extra_nopts = {'default_impl': 'auxonly'}

class INC(COM):
    _inherit_fields = True
    out_suffix = 'inc'
    display_suffix = 'Unfiltered'
    extra_nopts = {'default_impl': 'inc'}

class INC_SUBDEM(INC):
    _inherit_fields = True
    extra_nopts = {'subdem_tags': False}

class INC_SUBDEM_OBJ(INC_SUBDEM):
    _inherit_fields = True
    extra_nopts = {'obj_domain': True}

class DEM(COM):
    _inherit_fields = True
    out_suffix = 'dem'
    display_suffix = 'Filtered'
    extra_nopts = {'default_impl': 'dem'}

class DEM_NONINLINE(DEM):
    _inherit_fields = True
    out_suffix = 'dem_noninline'
    display_suffix = 'Filtered (no inline)'
    extra_nopts = {'maint_inline': False}

class DEM_NO_TAG_CHECK(DEM):
    _inherit_fields = True
    out_suffix = 'dem_notagcheck'
    display_suffix = 'Filtered (no demand checks)'
    extra_nopts = {'tag_checks': False}

class DEM_OBJ(DEM):
    _inherit_fields = True
    out_suffix = 'dem'
    display_suffix = 'Filtered (obj)'
    extra_nopts = {'obj_domain': True}

class DEM_SUBDEM(DEM):
    _inherit_fields = True
    out_suffix = 'dem_subdem'
    display_suffix = 'Filtered (alternate subquery demand)'
    extra_nopts = {'subdem_tags': False}


all_tasks = []

def add_task(task):
    all_tasks.append(task)

def add_impls(display_name, base_name, templates):
    add_task(IN(display_name, base_name))
    for template in templates:
        add_task(template(display_name, base_name, {}, None, None))


# ---- Program-specific tasks ----

lamutex_lru = DEM('lamutex', 'experiments/distalgo/lamutex/lamutex_inc',
    {
     '''count({(c2, p) for (_, _, (_ConstantPattern11_, c2, p)) in
        _PReceivedEvent_0 if (_ConstantPattern11_ == 'request')
        if (not ((count({(c3, p) for (_, _, (_ConstantPattern25_, c3,
        _FreePattern27_)) in _PReceivedEvent_1 if (_ConstantPattern25_
        == 'release') if (_FreePattern27_ == p) if (c3 > c2)}) > 0) or
        ((P_mutex_c, SELF_ID) < (c2, p))))})
     ''':
        {'uset_lru': 1},
     
     '''count({p for p in P_s for (_, _, (_ConstantPattern40_, c2,
        _FreePattern42_)) in _PReceivedEvent_2 if (_ConstantPattern40_
        == 'ack') if (_FreePattern42_ == p) if (c2 > P_mutex_c)})
     ''':
        {'uset_lru': 1},
    }, 'dem_lru', '(LRU)')

class INC_SUBDEM_LAMUTEX(INC_SUBDEM):
    _inherit_fields = True
    extra_nopts = {
        'var_types': {
            '_PReceivedEvent_0':
                '''SetType(TupleType([
                    toptype, toptype, TupleType([
                        strtype, ObjType('clocks'), ObjType('procs')
                    ])]))''',
            '_PReceivedEvent_1':
                '''SetType(TupleType([
                    toptype, toptype, TupleType([
                        strtype, ObjType('clocks'), ObjType('procs')
                    ])]))''',
            '_PReceivedEvent_2':
                '''SetType(TupleType([
                    toptype, toptype, TupleType([
                        strtype, ObjType('clocks'), ObjType('procs')
                    ])]))''',
            'SELF_ID':
                '''ObjType('procs')''',
            'P_mutex_c':
                '''ObjType('clocks')''',
            'P_s':
                '''SetType(ObjType('procs'))''',
            },
        'dom_costs': {
            '_PReceivedEvent_0.2.0': '''UnitCost()''',
            '_PReceivedEvent_1.2.0': '''UnitCost()''',
            '_PReceivedEvent_2.2.0': '''UnitCost()''',
            },
    }
#    def __init__(self, *args, **kargs):
#        self.qopts = {
#            '''{(p, c3)
#                for (_, _, (_ConstantPattern25_, c3, _FreePattern27_))
#                  in _PReceivedEvent_1
#                if (_ConstantPattern25_ == 'release')
#                if (_FreePattern27_ == p) if (c3 > c2)}''':
#            {'uset_mode': 'explicit',
#             'uset_params': ['p', 'c2']
#            }
#        }
#        super().__init__(*args, **kargs)

class INC_SUBDEM_LAMUTEX2(INC_SUBDEM):
    _inherit_fields = True
    extra_nopts = {
        'var_types': {
            '_PReceivedEvent_0':
                '''SetType(TupleType([
                    toptype, toptype, toptype, ObjType('procs'),
                        TupleType([strtype, ObjType('clocks')
                    ])]))''',
            'SELF_ID':
                '''ObjType('procs')''',
            'P_mutex_c':
                '''ObjType('clocks')''',
            'P_cs_reqc':
                '''ObjType('clocks')''',
            'P_ps':
                '''SetType(ObjType('procs'))''',
            'P_q':
                '''SetType(TupleType([ObjType('clocks'),
                                      ObjType('procs')]))''',
            },
        'dom_costs': {
            '_PReceivedEvent_0.2.0': '''UnitCost()''',
            '_U_Comp1.0': '''UnitCost()''',
            '_U_Comp1.1': '''UnitCost()''',
            '_U_Comp6': '''UnitCost()''',
            },
    }


# ---- Uncomment to rebuild experiment programs. ---

#add_impls('Social', 'experiments/twitter/twitter', [
#    INC,
#    DEM,
#])
#
#add_impls('Auth', 'experiments/django/django', [
#    INC,
#    DEM,
#])
#add_impls('Simplified Auth', 'experiments/django/django_simp', [
#    INC,
#    DEM,
#])
#
#add_impls('Wifi', 'experiments/wifi/wifi', [
#    INC,
#    DEM,
#])
#
#for level in [
#        '1',
#        '2',
#        '3'
#    ]:
#    add_impls('JQL {}'.format(level), 'experiments/jql/jql_{}'.format(level), [
#        AUX,
#        INC,
#        DEM,
#        DEM_NO_TAG_CHECK,
#    ])
#
#add_impls('Constr. RBAC', 'experiments/rbac/constrainedrbac/crbac', [
#    INC,
#    DEM,
#])
#
#CHECKACCESS_STR = '{r for r in ROLES if (session,r) in SR if (operation,object,r) in PR}'
#ASSIGNEDROLES_STR = '{r for r in ROLES if (user,r) in UR}'
#DELETESESSION_STR = '{(session,r) for r in ROLES if (session, r) in SR}'
#add_task(IN('CoreRBAC', 'experiments/rbac/corerbac/coreRBAC'))
#add_task(COM('CoreRBAC', 'experiments/rbac/corerbac/coreRBAC',
#             {}, 'aux', 'Batch w/ maps'))
#add_task(COM('CoreRBAC', 'experiments/rbac/corerbac/coreRBAC',
#             {CHECKACCESS_STR: {'impl': 'inc'},
##              ASSIGNEDROLES_STR: {'impl': 'inc'},
##              DELETESESSION_STR: {'impl': 'inc'}
#             }, 'ca_inc', 'Unfiltered (CA)'))
#add_task(COM('CoreRBAC', 'experiments/rbac/corerbac/coreRBAC',
#             {CHECKACCESS_STR: {'impl': 'dem',
#                                'uset_mode': 'explicit',
#                                'uset_params': ('session',)},
##              ASSIGNEDROLES_STR: {'impl': 'dem',
##                                  'uset_mode': 'explicit',
##                                  'uset_params': ('user',)},
##              DELETESESSION_STR: {'impl': 'dem',
##                                  'uset_mode': 'explicit',
##                                  'uset_params': ('session',)}
#             }, 'ca_dem', 'Filtered (CA)'))
#add_task(INC('CoreRBAC', 'experiments/rbac/corerbac/coreRBAC',
#             {}, None, None))
#add_task(DEM('CoreRBAC', 'experiments/rbac/corerbac/coreRBAC',
#             {}, None, None))
#
#add_impls('bday', 'experiments/other/bday/bday', [
#    INC,
#])
#
#add_impls('clpaxos', 'experiments/distalgo/clpaxos/clpaxos_inc', [
#    INC_SUBDEM,
#    DEM,
#])
#add_impls('crleader', 'experiments/distalgo/crleader/crleader_inc', [
#    INC_SUBDEM,
#    DEM,
#])
#add_impls('dscrash', 'experiments/distalgo/dscrash/dscrash_inc', [
#    INC_SUBDEM_OBJ,
#    DEM_OBJ,
#])
#add_impls('hsleader', 'experiments/distalgo/hsleader/hsleader_inc', [
#    INC_SUBDEM,
#    DEM,
#])
#add_impls('lamutex', 'experiments/distalgo/lamutex/lamutex_inc', [
#    INC_SUBDEM,
#])
#add_task(lamutex_lru)
#add_impls('lamutex opt1', 'experiments/distalgo/lamutex/lamutex_opt1_inc', [
#    INC_SUBDEM,
#])
#add_impls('lamutex opt2', 'experiments/distalgo/lamutex/lamutex_opt2_inc', [
#    INC_SUBDEM,
#])
#add_impls('lamutex orig', 'experiments/distalgo/lamutex/lamutex_orig_inc', [
#    INC_SUBDEM,
#])
#add_impls('lapaxos', 'experiments/distalgo/lapaxos/lapaxos_inc', [
#    INC_SUBDEM,
#    DEM,
#])
#add_impls('ramutex', 'experiments/distalgo/ramutex/ramutex_inc', [
#    INC_SUBDEM,
#    DEM,
#])
#add_impls('2pcommit', 'experiments/distalgo/tpcommit/tpcommit_inc', [
#    INC_SUBDEM,
#    DEM,
#])
#add_impls('vrpaxos', 'experiments/distalgo/vrpaxos/vrpaxos_inc', [
#    DEM_NONINLINE,
#])
#add_impls('vrpaxos', 'experiments/distalgo/vrpaxos/orig_majority_top_inc', [
#    INC_SUBDEM,
#    DEM,
#])


# ---- Uncomment to rebuild test programs. ----

test_programs = [
#    'auxmap/basic',
#    'auxmap/degenerate',
#    'auxmap/equality',
#    'auxmap/inline',
#    'auxmap/wildcard',
#
#    'comp/basic',
#    'comp/deltaeq',
#    'comp/deltawild',
#    'comp/deltawildeq',
#    'comp/expr',
#    'comp/implmode',
#    'comp/inline',
#    'comp/nonpattern',
#    'comp/parameter',
##    'comp/inconlyonce',
#    'comp/pattern',
#    'comp/patternmaint',
#    'comp/setmatchcomp',
#    'comp/sjaug',
#    'comp/sjsub',
#    'comp/uset/uset',
#    'comp/uset/uset_explicit',
#    'comp/uset/auto',
#    'comp/uset/nodemand',
#    'comp/uset/lru',
#    'comp/nested/basic',
#    'comp/nested/obj',
#    'comp/nested/outline',
#    'comp/nested/param',
#    'comp/tup/flatten',
#    'comp/instr',
#    'comp/macroupdate',
#    'comp/unhandled',
#    'comp/types',
#
#    'objcomp/batch',
#    'objcomp/auxonly',
#    'objcomp/expr',
#    'objcomp/inc',
#    'objcomp/if',
#    'objcomp/pairmode',
#    'objcomp/notc',
#    'objcomp/map',
#    'objcomp/inputrel',
#    'objcomp/autoflatten',
#    
#    'deminc/aug1',
#    'deminc/aug2',
#    'deminc/basic',
#    'deminc/nested',
#    'deminc/nested_subdem',
#    'deminc/nocheck',
#    'deminc/nodas',
#    'deminc/obj',
#    'deminc/objwild',
#    'deminc/wildcard',
#    'deminc/tup/basic',
#    'deminc/tup/inc',
#    'deminc/tup/obj',
#    'deminc/tup/objnest',
#
#    'aggr/basic',
#    'aggr/comp',
#    'aggr/inline',
#    'aggr/minmax',
#    'aggr/obj',
#    'aggr/params',
#    'aggr/tuple',
#    'aggr/uset',
#    'aggr/lru',
#    'aggr/nested/basic',
#    'aggr/nested/aggrdem',
#    'aggr/nested/compdem',
#    'aggr/nested/halfdemand',
]

for name in test_programs:
    add_task(TestProgramTask(name))


t1 = clock()
do_tasks(all_tasks)
t2 = clock()

print('Done  ({:.3f} s)'.format(t2 - t1))
