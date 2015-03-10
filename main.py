"""Invoke the transformation system."""


from invinc.transform import *


STATS_FILE = 'transstats.pickle'


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
#    INC_SUBDEM_LAMUTEX,
#])
#add_task(lamutex_lru)
#add_impls('lamutex opt1', 'experiments/distalgo/lamutex/lamutex_opt1_inc', [
#    INC_SUBDEM_LAMUTEX,
#])
#add_impls('lamutex opt2', 'experiments/distalgo/lamutex/lamutex_opt2_inc', [
#    INC_SUBDEM_LAMUTEX,
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
    add_task(make_testprogram_task(name))


elapsed = do_tasks(all_tasks, STATS_FILE)

print('Done  ({:.3f} s)'.format(elapsed))

from invinc.transform import StatsDB, Session, StandardSchema

class OIFSchema(OrigIncFilterSchema):
    
    # (Not a method.)
    def _rowgen(dispname, name):
        return ([name + ' Input', name + ' Unfiltered', name + ' Filtered'],
                dispname)
    
    rows = [
        _rowgen('Social', 'Social'),
#        _rowgen('JQLbench1', 'JQL 1'),
#        _rowgen('JQLbench2', 'JQL 2'),
#        _rowgen('JQLbench3', 'JQL 3'),
        _rowgen('Wifi', 'Wifi'),
#        _rowgen('Auth', 'Auth'),
#        ('Access', 'CoreRBAC Input',
#         'CoreRBAC Unfiltered (CA)', 'CoreRBAC Filtered (CA)'),
#        _rowgen('CoreRBAC', 'CoreRBAC'),
#        _rowgen('SSD', 'Constr. RBAC'),
#        _rowgen('clpaxos', 'clpaxos'),
#        _rowgen('crleader', 'crleader'),
#        ('dscrash', 'dscrash Input',
#         'dscrash Unfiltered', 'dscrash Filtered (obj)'),
#        _rowgen('hsleader', 'hsleader'),
#        _rowgen('lamutex', 'lamutex'),
#        _rowgen('lapaxos', 'lapaxos'),
#        _rowgen('ramutex', 'ramutex'),
#        _rowgen('2pcommit', '2pcommit'),
    ]
    
#    rows = [
##        ('Social Input', 'Twitter Orig'),
##        ('Social Unfiltered', 'Twitter Inc'),
##        ('Social Filtered', 'Twitter Dem'),
#        (['Social Input', 'Social Unfiltered', 'Social Filtered'],
#         'Twitter'),
#    ]

class MySchema(StandardSchema):
    
    rows = [
        ('lamutex Unfiltered', 'lamutex')
    ]

stats = StatsDB(STATS_FILE)
#print(MySchema(stats.allstats).to_ascii())
print(MySchema(stats.allstats).to_ascii())
#Session.interact(stats, name='Social Unfiltered')
session = Session(stats, name='lamutex Unfiltered')
session.cmd_showcosts()
#session.interact()
