"""Invoke the transformation system."""


from incoq.transform import *


STATS_DIR = 'stats/'
STATS_FILE = STATS_DIR + 'transstats.pickle'


all_tasks = []

def add_task(task):
    all_tasks.append(task)

def add_impls(display_name, base_name, templates):
    add_task(make_in_task(display_name, base_name))
    for template in templates:
        in_name = base_name + '_in.py'
        out_name = base_name + '.py'
        task = Task(display_name, in_name, out_name, {}, {})
        add_task(task_from_template(task, template))


# ---- Program-specific tasks ----

class INC_SUBDEM_LAMUTEX(INC_SUBDEM):
    _inherit_fields = True
    
    msgset_t = '''set(tuple([top, top, tuple([
                               enum('msglabel', str),
                               subtype('clocks', number),
                               subtype('procs', number)])]))'''
    
    extra_nopts = {
        'var_types': {
            '_PReceivedEvent_0': msgset_t,
            '_PReceivedEvent_1': msgset_t,
            '_PReceivedEvent_2': msgset_t,
            'SELF_ID': "subtype('procs', number)",
            'P_mutex_c':  "subtype('clocks', number)",
            'P_s':  "set(subtype('procs', number))",
            },
        'default_uset_lru': 1,
    }

class INC_SUBDEM_LAMUTEX_ORIG(INC_SUBDEM):
    _inherit_fields = True
    
    msgset_t = '''set(tuple([top, top, tuple([
                               enum('msglabel', str),
                               subtype('clocks', number),
                               subtype('procs', number)])]))'''
    
    extra_nopts = {
        'var_types': {
            '_PReceivedEvent_0': msgset_t,
            'SELF_ID': "subtype('procs', number)",
            'P_mutex_c':  "subtype('clocks', number)",
            'P_s':  "set(subtype('procs', number))",
            'P_q': '''set(tuple([enum('msglabel', str),
                                 subtype('clocks', number),
                                 subtype('procs', number)]))''',
            },
        'default_uset_lru': 1,
#        'maint_inline': True,
    }

class DEM_OBJ_NS_RATOKEN(DEM_OBJ_NS):
    _inherit_fields = True
    
    msgset1_t = '''set(tuple([top, top, tuple([
                                enum('msglabel', str),
                                subtype('clocks', number),
                                subtype('procs', number)])]))'''
    msgset2_t = '''set(tuple([top, top, tuple([
                                enum('msglabel', str),
                                top])]))'''
    msgset3_t = '''set(tuple([top, top, tuple([
                                enum('msglabel', str),
                                dict(top, top)])]))'''
    
    extra_nopts = {
        'var_types': {
            '_PReceivedEvent_2': msgset1_t,
            '_PSentEvent_3': msgset2_t,
            '_PReceivedEvent_4': msgset3_t,
            '_PSentEvent_5': msgset3_t,
            'SELF_ID': "subtype('procs', number)",
            'P_ps':  "set(subtype('procs', number))",
            'P_token': "dict(top, top)",
            },
    }

CHECKACCESS_STR = '{r for r in ROLES if (session,r) in SR if (operation,object,r) in PR}'
ASSIGNEDROLES_STR = '{r for r in ROLES if (user,r) in UR}'
DELETESESSION_STR = '{(session,r) for r in ROLES if (session, r) in SR}'
class INC_CORERBAC_CA(COM):
    _inherit_fields = True
    
    output_suffix = 'checkaccess_inc'
    display_suffix = 'Unfiltered (CA)'
    
    extra_qopts = {
        CHECKACCESS_STR:   {'impl': 'inc'},
        ASSIGNEDROLES_STR: {'impl': 'inc'},
        DELETESESSION_STR: {'impl': 'inc'},
        }

class DEM_CORERBAC_CA(COM):
    _inherit_fields = True
    
    output_suffix = 'checkaccess_dem'
    display_suffix = 'Filtered (CA)'
    
    extra_qopts = {
        CHECKACCESS_STR:   {'impl': 'dem',
                            'uset_mode': 'explicit',
                            'uset_params': ('object',),
                            'demand_reorder': [0, 3, 1, 2]},
        ASSIGNEDROLES_STR: {'impl': 'inc'},
        DELETESESSION_STR: {'impl': 'inc'},
        }


# ---- Uncomment to rebuild experiment programs. ---

#add_impls('Eqwild Test 1', 'experiments/other/eqwild/eqwild1', [
#    INC,
#    DEM,
#])
#add_impls('Eqwild Test 2', 'experiments/other/eqwild/eqwild2', [
#    DEM,
#])
#add_impls('Friendless Test 1', 'experiments/other/eqwild/friendless1', [
#    DEM,
#])
#add_impls('Friendless Test 2', 'experiments/other/eqwild/friendless2', [
#    DEM,
#])

add_impls('Social', 'experiments/twitter/twitter', [
#    INC,
#    DEM,
#    DEM_SINGLE_TAG,
#    DEM_INLINE,
#    DEM_INLINE_NORCELIM,
#    DEM_INLINE_NOTYPECHECK,
])
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
##        AUX,
#        INC,
#        DEM,
##        DEM_NO_TAG_CHECK,
#    ])
#
#add_impls('Constr. RBAC', 'experiments/rbac/constrainedrbac/crbac', [
#    AUX,
#    INC,
#    DEM,
#])
#
#add_impls('CoreRBAC', 'experiments/rbac/corerbac/coreRBAC', [
#    INC_CORERBAC_CA,
#    DEM_CORERBAC_CA,
#    INC,
#    DEM,
#])
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
#    DEM_OBJ_NS,
#])
#add_impls('hsleader', 'experiments/distalgo/hsleader/hsleader_inc', [
#    INC_SUBDEM,
#    DEM,
#])
#add_impls('lamutex', 'experiments/distalgo/lamutex/lamutex_inc', [
#    INC_SUBDEM_LAMUTEX,
#    DEM_LRU,
#])
#add_impls('lamutex opt1', 'experiments/distalgo/lamutex/lamutex_opt1_inc', [
#    INC_SUBDEM_LAMUTEX,
#    DEM,
#])
#add_impls('lamutex opt2', 'experiments/distalgo/lamutex/lamutex_opt2_inc', [
#    INC_SUBDEM_LAMUTEX,
#    DEM_LRU,
#])
#add_impls('lamutex orig', 'experiments/distalgo/lamutex/lamutex_orig_inc', [
#    INC_SUBDEM_LAMUTEX_ORIG,
#    DEM_LRU,
#])
#add_impls('lapaxos', 'experiments/distalgo/lapaxos/lapaxos_inc', [
#    INC_SUBDEM,
#    DEM,
#])
#add_impls('ramutex', 'experiments/distalgo/ramutex/ramutex_inc', [
#    INC_SUBDEM,
#    DEM,
#])
#add_impls('ratoken', 'experiments/distalgo/ratoken/ratoken_inc', [
#    DEM_OBJ_NS_RATOKEN,
#])
#add_impls('sktoken', 'experiments/distalgo/sktoken/sktoken_inc', [
#    DEM_OBJ_NS,
#])
#add_impls('2pcommit', 'experiments/distalgo/tpcommit/tpcommit_inc', [
#    INC_SUBDEM,
#    DEM,
#])
#add_impls('vrpaxos', 'experiments/distalgo/vrpaxos/vrpaxos_inc', [
#    DEM,
#])


# ---- Uncomment to rebuild test programs. ----

test_programs = [
#    'auxmap/basic',
#    'auxmap/deadcode',
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
#    'comp/inconlyonce',
#    'comp/pattern',
#    'comp/patternmaint',
#    'comp/setmatchcomp',
#    'comp/sjaug',
#    'comp/sjsub',
#    'comp/uset/uset',
#    'comp/uset/uset_explicit',
#    'comp/uset/auto',
#    'comp/uset/nodemand',
#    'comp/uset/eager_param',
#    'comp/uset/lru',
#    'comp/nested/basic',
#    'comp/nested/obj',
#    'comp/nested/outline',
#    'comp/nested/param',
#    'comp/tup/flatten',
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
#    'deminc/reorder',
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
#    'aggr/rewrite',
#    'aggr/tuple',
#    'aggr/uset',
#    'aggr/lru',
#    'aggr/nested/basic',
#    'aggr/nested/aggrdem',
#    'aggr/nested/compdem',
#    'aggr/nested/halfdemand',
#    'aggr/nested/obj',
]

for name in test_programs:
    add_task(make_testprogram_task(name))


elapsed = do_tasks(all_tasks, STATS_FILE)

print('Done  ({:.3f} s)'.format(elapsed))

from incoq.transform import StatsDB, Session, StandardSchema

class RunningExSchema(StatkeySchema):
    
    cols = [
        ('lines', 'LOC', None),
        ('trans time', 'Time', '.2f'),
    ]
    
    rows = [
        ('Social Input', 'Running ex Input'),
        ('Social Unfiltered', 'Running ex Incremental'),
        ('Social Filtered', 'Running ex Filtered'),
        ('Social Filtered (no type checks)',
         'Running ex Filtered (no type checks)'),
        ('Social Filtered (no rc elim.)',
         'Running ex Filtered (no rc elim.)'),
        ('Social Filtered (inlined)',
         'Running ex Filtered (inlined)'),
        ('Social Filtered (single tag)', 'Running ex Filtered (osq strat)'),
    ]

class ComparisonSchema(OrigIncFilterSchema):
    
    def _rowgen(name):
        return ([name + ' Input', name + ' Unfiltered', name + ' Filtered'],
                name)
    
    rows = [
        _rowgen('Wifi'),
        _rowgen('Auth'),
        _rowgen('Simplified Auth'),
        _rowgen('JQL 1'),
        _rowgen('JQL 2'),
        _rowgen('JQL 3'),
    ]

class ApplicationsSchema(OrigIncFilterSchema):
   
    def _rowgen(name, dispname=None):
        if dispname is None:
            dispname = name
        return ([name + ' Input', name + ' Unfiltered', name + ' Filtered'],
                dispname)
    
    def _rowgen2(name):
        return ([name + ' Input', name + ' Unfiltered (obj)',
                 name + ' Filtered (obj)'],
                name)
    
    rows = [
        (['CoreRBAC Input', 'CoreRBAC Unfiltered (CA)',
          'CoreRBAC Filtered (CA)'],
         'CheckAccess'),
        _rowgen('CoreRBAC'),
        _rowgen('Constr. RBAC', 'SSD'),
        (['lamutex orig Input', 'lamutex orig Unfiltered',
          'lamutex orig Filtered'], 'lamutex_orig'),
        (['lamutex Input', 'lamutex Unfiltered', 'lamutex Filtered'],
         'lamutex_spec'),
        (['lamutex opt2 Input', 'lamutex opt2 Unfiltered',
          'lamutex opt2 Filtered'],
         'lamutex_specsimp'),
        _rowgen('2pcommit'),
        _rowgen('clpaxos'),
        _rowgen('crleader'),
        _rowgen2('dscrash'),
        _rowgen('hsleader'),
#        _rowgen('lapaxos'),
        _rowgen('ramutex'),
        _rowgen2('ratoken'),
#        _rowgen2('sktoken'),
    ]

class DistalgoSchema(OrigIncFilterSchema):
    
    def _rowgen(name):
        return ([name + ' Input', name + ' Unfiltered', name + ' Filtered'],
                name)
    
    def _rowgen2(name):
        return ([name + ' Input', name + ' Unfiltered (obj)',
                 name + ' Filtered (obj)'],
                name)
    
    rows = [
        _rowgen('2pcommit'),
        _rowgen('clpaxos'),
        _rowgen('crleader'),
        _rowgen2('dscrash'),
        _rowgen('hsleader'),
        _rowgen('lamutex'),
        _rowgen('lamutex opt1'),
        _rowgen('lamutex opt2'),
        _rowgen('lamutex orig'),
#        _rowgen('lapaxos'),
        _rowgen('ramutex'),
        _rowgen2('ratoken'),
#        _rowgen2('sktoken'),
    ]

class RunningExCostSchema(CostSchema):
    rows = [
        ('Social Unfiltered', 'incremental'),
        ('Social Filtered', 'filtered'),
    ]
    cols = [
        ('make_user', 'make_user', None),
        ('make_group', 'make_group', None),
        ('follow', 'follow', None),
        ('unfollow', 'unfollow', None),
        ('join_group', 'join_group', None),
        ('leave_group', 'leave_group', None),
        ('change_loc', 'change_loc', None),
        ('do_query', 'do_query', None),
    ]

class LamutexspecCostSchema(CostSchema):
    rows = [
        ('lamutex Unfiltered', 'lamutex'),
#        ('lamutex opt1 Unfiltered', 'lamutex opt1'),
        ('lamutex opt2 Unfiltered', 'lamutex optimized'),
    ]
    cols = [
        ('Query_0', 'Query', None),
        ('Update__PReceivedEvent_0', 'Rec Request', None),
        ('Update__PReceivedEvent_1', 'Rec Release', None),
        ('Update__PReceivedEvent_2', 'Rec Ack', None),
    ]
class LamutexorigCostSchema(CostSchema):
    rows = [
        ('lamutex orig Unfiltered', 'lamutex orig'),
    ]
    cols = [
        ('Query_0', 'Query 1', None),
        ('Query_1', 'Query 2', None),
        ('Query_2', 'Query 3', None),
        ('Update_P_q3', 'Update request queue', None),
        ('Update_P_q4', 'Update request queue', None),
        ('Update_P_q5', 'Update request queue', None),
        ('Update_P_q6', 'Update request queue', None),
        ('Update__PReceivedEvent_0', 'Rec Ack', None),
    ]

class OOPSLA15Schema(OrigIncFilterSchema):
    
    # (Not a method.)
    def _rowgen(dispname, name):
        return ([name + ' Input', name + ' Unfiltered', name + ' Filtered'],
                dispname)
    
    def _rowgen2(dispname, name):
        return ([name + ' Input', name + ' Unfiltered (obj)',
                 name + ' Filtered (obj)'],
                dispname)
    
    rows = [
        _rowgen('Running', 'Social'),
        _rowgen('JQLbench1', 'JQL 1'),
        _rowgen('JQLbench2', 'JQL 2'),
        _rowgen('JQLbench3', 'JQL 3'),
        _rowgen('Wifi', 'Wifi'),
        _rowgen('Auth', 'Auth'),
        (['CoreRBAC Input', 'CoreRBAC Unfiltered (CA)',
          'CoreRBAC Filtered (CA)'],
         'Access'),
        _rowgen('CoreRBAC', 'CoreRBAC'),
        _rowgen('SSD', 'Constr. RBAC'),
        
        (['lamutex orig Input', 'lamutex orig Unfiltered',
          'lamutex orig Filtered'],
         'La mutex'),
        _rowgen('RA mutex', 'ramutex'),
        _rowgen2('RA token', 'ratoken'),
#        _rowgen2('SK token', 'sktoken'),
        _rowgen('CR leader', 'crleader'),
        _rowgen('HS leader', 'hsleader'),
        _rowgen('2P commit', '2pcommit'),
        _rowgen2('DS crash', 'dscrash'),
        _rowgen('CL Paxos', 'clpaxos'),
    ]

stats = StatsDB(STATS_FILE)
runningex_schema = RunningExSchema(stats.allstats)
comparison_schema = ComparisonSchema(stats.allstats)
applications_schema = ApplicationsSchema(stats.allstats)
distalgo_schema = DistalgoSchema(stats.allstats)
runningex_costschema = RunningExCostSchema(stats.allstats)
lamutexspec_costschema = LamutexspecCostSchema(stats.allstats)
lamutexorig_costschema = LamutexorigCostSchema(stats.allstats)
oopsla15_schema = OOPSLA15Schema(stats.allstats)

runningex_schema.save_csv(STATS_DIR + 'stats-runningex.csv')
comparison_schema.save_csv(STATS_DIR + 'stats-comparison.csv')
applications_schema.save_csv(STATS_DIR + 'stats-applications.csv')
distalgo_schema.save_csv(STATS_DIR + 'stats-distalgo.csv')
oopsla15_schema.save_csv(STATS_DIR + 'stats-oopsla15.csv')
runningex_costschema.save_csv(STATS_DIR + 'stats-runninex_cost.csv')
lamutexspec_costschema.save_csv(STATS_DIR + 'stats-lamutexspec_cost.csv')
lamutexorig_costschema.save_csv(STATS_DIR + 'stats-lamutexorig_cost.csv')

#print(runningex_schema.to_ascii())
#print(comparison_schema.to_ascii())
#print(applications_schema.to_ascii())
#print(distalgo_schema.to_ascii())
#print(oopsla15_schema.to_ascii())

#print(runningex_costschema.to_ascii())
#print(lamutexspec_costschema.to_ascii())
#print(lamutexorig_costschema.to_ascii())

#session = Session(stats)
#Session.interact(stats, name='Social Unfiltered')
#session = Session(stats, name='lamutex Unfiltered')
#session.cmd_showcosts()
#session.interact()
