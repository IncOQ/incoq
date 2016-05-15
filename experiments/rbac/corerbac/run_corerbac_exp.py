"""Run the Core RBAC experiment."""


import os
import sys
import importlib
from copy import deepcopy
from random import sample, randrange

from frexp import (ExpWorkflow, Datagen, MetricExtractor, ScaledExtractor,
                   NormalizedExtractor)

from experiments.util import SmallExtractor, LargeExtractor, canonize


class CoreRBACDatagen(Datagen):
    
    """Generate structures and relate them according to a fixed
    proportion. Perform a series of operation patterns consisting
    of creating several sessions, performing checkaccess queries,
    and then deleting these sessions.
    
    Parameters:
        n_users -- number of users
        n_roles -- number of roles
        n_ops -- number of operations
        n_objs -- number of objects
        rpu -- roles per user
        ppr -- permissions per role
        rps -- active roles per session
        q_objs -- number of queryable objects
        n_pat -- number of patterns
        s_pat -- number of sessions created per pattern
        qs_pat -- number of queried sessions per pattern
        q_pat -- number of queries per session pattern
    """
    
    def generate(self, P):
        n_users = P['n_users']
        n_roles = P['n_roles']
        n_ops = P['n_ops']
        n_objs = P['n_objs']
        rpu = P['rpu']
        ppr = P['ppr']
        rps = P['rps']
        q_objs = P['q_objs']
        n_pat = P['n_pat']
        s_pat = P['s_pat']
        qs_pat = P['qs_pat']
        q_pat = P['q_pat']
        
        perms = [(i, j) for i in range(n_ops)
                        for j in range(n_objs)]
        
        UR = {i: sample(range(n_roles), rpu)
              for i in range(n_users)}
        PR = {i: sample(perms, ppr)
              for i in range(n_roles)}
        
        # Element format:
        #   [([(u, s, ars), ...], [(s, op, obj), ...]),
        #    ...
        #   ]
        OPS = []
        for _ in range(n_pat):
            SES = []
            for s in range(s_pat):
                u = randrange(n_users)
                ars = sample(UR[u], rps)
                SES.append((u, s, ars))
            
            CA = [(randrange(qs_pat), randrange(n_ops), randrange(q_objs))
                  for _ in range(q_pat)]    
            
            OPS.append((SES, CA))
        
        return dict(
            dsparams = P,
            UR = UR,
            PR = PR,
            OPS = OPS,
        )
    
    # Set to [False, True] to run two versions, first with all
    # operations and then with updates only (no queries).
    noqs = [False]
    
    def get_tparams_list(self, dsparams_list):
        return [dict(tid = dsp['dsid'] + '_' + str(noq),
                     dsid = dsp['dsid'],
                     prog = prog,
                     noq = noq)
                for prog in self.progs
                for dsp in dsparams_list
                for noq in self.noqs
        ]


class CoreRBACDriver:
    
    def __init__(self, pipe_filename):
        import gc
        import pickle
        
        gc.disable()
        
        with open(pipe_filename, 'rb') as pf:
            dataset, prog, other_tparams = pickle.load(pf)
        os.remove(pipe_filename)
        
        
        self.dataset = dataset
        self.prog = prog
        self.noq = other_tparams['noq']
        self.module = None
        self.results = {}
        
        self.setUp()
        
        from frexp.util import StopWatch, user_time
        from time import process_time, perf_counter
        timer_user = StopWatch(user_time)
        timer_cpu = StopWatch(process_time)
        timer_wall = StopWatch(perf_counter)
        
        with timer_user, timer_cpu, timer_wall:
            self.run()
        
        import incoq.runtime
        self.results['size'] = incoq.runtime.get_size_for_namespace(
                                    self.module.__dict__)
        self.results['time_user'] = timer_user.consume()
        self.results['time_cpu'] = timer_cpu.consume()
        self.results['time_wall'] = timer_wall.consume()
        
        self.results['stdmetric'] = self.results['time_cpu']
        
        
        with open(pipe_filename, 'wb') as pf:
            pickle.dump(self.results, pf)
    
    def setUp(self):
        # Import driven program.
        dirname, filename = os.path.split(self.prog)
        if dirname:
            sys.path.append(dirname)
        try:
            self.module = importlib.import_module(
                    'experiments.rbac.corerbac.' + filename)
        finally:
            if dirname:
                sys.path.pop()
        
        
        m = self.module
        ds = self.dataset
        P = ds['dsparams']
        
        def u(i):
            return 'u' + str(i)
        def r(i):
            return 'r' + str(i)
        def op(i):
            return 'op' + str(i)
        def obj(i):
            return 'obj' + str(i)
        def s(i):
            return 's' + str(i)
        
        # Initialize dataset.
        for i in range(P['n_users']):
            m.AddUser(u(i))
        for i in range(P['n_roles']):
            m.AddRole(r(i))
        for i in range(P['n_ops']):
            m.AddOperation(op(i))
        for i in range(P['n_objs']):
            m.AddObject(obj(i))
        for i, rs in ds['UR'].items():
            for j in rs:
                m.AssignUser(u(i), r(j))
        for i, ps in ds['PR'].items():
            for (j, k) in ps:
                m.GrantPermission(op(j), obj(k), r(i))
        
        # Preprocess operations.
        self.OPS = []
        for SES, CA in ds['OPS']:
            N_SES = [(u(i), s(j), {r(k) for k in ars})
                     for i, j, ars in SES]
            if self.noq:
                N_CA = []
            else:
                N_CA = [(s(i), op(j), obj(k))
                        for i, j, k in CA]
            self.OPS.append((N_SES, N_CA))
        
        # Do initial demand for all combinations of queried
        # sessions and objects. Since CheckAccess has membership
        # preconditions, we need to actually create these sessions
        # first, and we'll destroy them before actually starting
        # the test proper.
        qs_pat = self.dataset['dsparams']['qs_pat']
        q_objs = self.dataset['dsparams']['q_objs']
        queried_sessions = ['s' + str(i) for i in range(qs_pat)]
        queried_objects = ['obj' + str(i) for i in range(q_objs)]
        for s in queried_sessions:
            m.CreateSession('u0', s, set())
            for obj in queried_objects:
                m.CheckAccess(s, 'op0', obj)
            m.DeleteSession('u0', s)
    
    def run(self):
        CreateSession = self.module.CreateSession
        DeleteSession = self.module.DeleteSession
        CheckAccess_nodemand = self.module.CheckAccess_nodemand
        
        for SES, CA in self.OPS:
            for u, s, ars in SES:
                CreateSession(u, s, ars)
            for s, op, obj in CA:
                CheckAccess_nodemand(s, op, obj)
            for u, s, _ars in SES:
                DeleteSession(u, s)

class CoreRBACVerifyDriver:
    
    def __init__(self, pipe_filename):
        import gc
        import pickle
        
        gc.disable()
        
        with open(pipe_filename, 'rb') as pf:
            dataset, prog, other_tparams = pickle.load(pf)
        os.remove(pipe_filename)
        
        
        self.dataset = dataset
        self.prog = prog
        self.noq = other_tparams['noq']
        self.module = None
        self.results = {'output': []}
        
        self.setUp()
        
        from frexp.util import StopWatch, user_time
        from time import process_time, perf_counter
        timer_user = StopWatch(user_time)
        timer_cpu = StopWatch(process_time)
        timer_wall = StopWatch(perf_counter)
        
        with timer_user, timer_cpu, timer_wall:
            self.run()
        
        
        self.results = canonize(self.results)
        
        with open(pipe_filename, 'wb') as pf:
            pickle.dump(self.results, pf)
    
    def setUp(self):
        # Import driven program.
        dirname, filename = os.path.split(self.prog)
        if dirname:
            sys.path.append(dirname)
        try:
            self.module = importlib.import_module(
                    'experiments.rbac.corerbac.' + filename)
        finally:
            if dirname:
                sys.path.pop()
        
        
        m = self.module
        ds = self.dataset
        P = ds['dsparams']
        
        def u(i):
            return 'u' + str(i)
        def r(i):
            return 'r' + str(i)
        def op(i):
            return 'op' + str(i)
        def obj(i):
            return 'obj' + str(i)
        def s(i):
            return 's' + str(i)
        
        # Initialize dataset.
        for i in range(P['n_users']):
            m.AddUser(u(i))
        for i in range(P['n_roles']):
            m.AddRole(r(i))
        for i in range(P['n_ops']):
            m.AddOperation(op(i))
        for i in range(P['n_objs']):
            m.AddObject(obj(i))
        for i, rs in ds['UR'].items():
            for j in rs:
                m.AssignUser(u(i), r(j))
        for i, ps in ds['PR'].items():
            for (j, k) in ps:
                m.GrantPermission(op(j), obj(k), r(i))
        
        # Preprocess operations.
        self.OPS = []
        for SES, CA in ds['OPS']:
            N_SES = [(u(i), s(j), {r(k) for k in ars})
                     for i, j, ars in SES]
            if self.noq:
                N_CA = []
            else:
                N_CA = [(s(i), op(j), obj(k))
                        for i, j, k in CA]
            self.OPS.append((N_SES, N_CA))
    
    def run(self):
        CreateSession = self.module.CreateSession
        DeleteSession = self.module.DeleteSession
        CheckAccess = self.module.CheckAccess
        
        for SES, CA in self.OPS:
            for u, s, ars in SES:
                CreateSession(u, s, ars)
            for s, op, obj in CA:
                output = CheckAccess(s, op, obj)
                self.results['output'].append(deepcopy(output))
            for u, s, _ars in SES:
                DeleteSession(u, s)


class CoreRBACExtractor(MetricExtractor, SmallExtractor):
    
    def get_series_points(self, datapoints, sid, *,
                          average):
        inner_sid, kind = sid
        # Grab all data for the inner sid, and split based on noq.
        inner_data = self.get_series_data(datapoints, inner_sid)
        q_data = [p for p in inner_data
                    if not p['noq']]
        noq_data = [p for p in inner_data
                      if p['noq']]
        
        # For 'all' and 'updates', normal behavior on the q or
        # noq points.
        if kind == 'all':
            return self.project_and_average_data(q_data, average=average)
        elif kind == 'updates':
            return self.project_and_average_data(noq_data, average=average)
        elif kind == 'queries':
            q_avg = self.project_and_average_data(q_data, average=True)
            noq_avg = self.project_and_average_data(noq_data, average=True)
            
            data = []
            for ((ax, ay, _alo, _ahi), (ux, uy, _ulo, _uhi)) in \
                    zip(q_avg, noq_avg):
                assert ax == ux
                # Use 0 for errorbar data.
                data.append((ax, ay - uy, 0, 0))
            return data
        else:
            assert()


class CoreRBACWorkflow(ExpWorkflow):
    
    ExpDatagen = CoreRBACDatagen
    ExpExtractor = CoreRBACExtractor
    ExpDriver = CoreRBACDriver
    ExpVerifyDriver = CoreRBACVerifyDriver
    
    require_ac = False ###


class CoreRoles(CoreRBACWorkflow):
    
    prefix = 'results/corerbac'
    
    class ExpDatagen(CoreRBACWorkflow.ExpDatagen):
        
        # The PEPM paper used the version where all queries were
        # incrementalized, not just checkaccess and its two helper
        # queries. But I think just checkaccess is more appropriate,
        # and switching to the other implementation doesn't resolve
        # our problems with reproducing PEPM results.
        
        progs = [
            'coreRBAC_in',
            'coreRBAC_checkaccess_inc',
            'coreRBAC_checkaccess_dem',
        ]
        
        noqs = [
            False,
            True,
        ]
        
        # Looking at the source code for what is supposed to be the PEPM
        # benchmark script, best I can figure, the number of queries per
        # create/delete session pattern is 100, not 1000 as reported,
        # and the number of active roles per session is 1, not 10, due
        # to a bug and oversight where users only get assigned 5
        # sessions.
        
        def get_dsparams_list(self):
            return [
                dict(
                    dsid =           str(x),
                    x =              x,
                    
                    n_users =        50,
                    n_roles =        x,
                    n_ops =          20,
                    n_objs =         20,
                    
                    rpu =            10,
                    ppr =            10,
                    rps =            10,
                    
                    q_objs =         20,
                    n_pat =          1000,
                    s_pat =          1,
                    qs_pat =         1,
                    q_pat =          1000,
                )
                for x in range(10, 101, 10)
            ]
    
    stddev_window = .1
    min_repeats = 10
    max_repeats = 50
    
    class ExpExtractor(CoreRBACWorkflow.ExpExtractor, ScaledExtractor):
        
        series = [
            (('coreRBAC_in', 'queries'),
             'original query',
             'red', '1-2 s poly1'),
            (('coreRBAC_in', 'updates'),
             'original create/delete session',
             'red', '1-4 _s poly1'),
            (('coreRBAC_checkaccess_inc', 'queries'),
             'incremental query',
             'blue', '1-2 o poly1'),
            (('coreRBAC_checkaccess_inc', 'updates'),
             'incremental create/delete session',
             'blue', '1-4 _o poly1'),
            (('coreRBAC_checkaccess_dem', 'queries'),
             'filtered query',
             'green', '1-2 ^ poly1'),
            (('coreRBAC_checkaccess_dem', 'updates'),
             'filtered create/delete session',
             'green', '1-4 _^ poly1'),
        ]
        
        multipliers = {
            ('coreRBAC_in', 'queries'): .2,
        }
        
        title = None
        ylabel = 'Running time (in seconds)'
        xlabel = 'Number of roles'
        metric = 'time_cpu'
        
        # Adjust geometry for external legend.
        width = 6
        figsize = (width, 2.625)
        tightlayout_bbox = (0, 0, 3.5/width, 1)
        legend_bbox = (1, 0, 1, 1)
        legend_loc = 'center left'
        
        xmin = 5
        xmax = 105
        ymin = -0.2


class CoreDemand(CoreRBACWorkflow):
    
    prefix = 'results/corerbac_demand'
    
    class ExpDatagen(CoreRBACWorkflow.ExpDatagen):
        
        progs = [
            'coreRBAC_checkaccess_inc',
            'coreRBAC_checkaccess_dem',
        ]
        
        def get_dsparams_list(self):
            return [
                dict(
                    dsid =           str(x),
                    x =              x,
                    
                    n_users =        50,
                    n_roles =        100,
                    n_ops =          20,
                    n_objs =         1000,
                    
                    rpu =            10,
                    ppr =            100,
                    rps =            10,
                    
                    q_objs =         x,
                    n_pat =          1000,
                    s_pat =          1,
                    qs_pat =         1,
                    q_pat =          1000,
                )
                for x in [1] + list(range(50, 1000 + 1, 50))
            ]
    
    stddev_window = .1
    min_repeats = 10
    max_repeats = 50
    
    class ExpExtractor(CoreRBACWorkflow.ExpExtractor):
        
        series = [
            (('coreRBAC_checkaccess_inc', 'all'),
             'incremental',
             'blue', '- o poly1'),
            (('coreRBAC_checkaccess_dem', 'all'),
             'filtered',
             'green', '- ^ poly1'),
        ]
        
        title = None
        
#        xlabel = 'Number of queried objects'
#        xmin = -50
#        xmax = 1050
        
        xlabel = 'Percentage of demanded objects'
        def project_x(self, p):
            return super().project_x(p) / 1000 * 100
        xmin = -5
        xmax = 105
        
        ylabel = 'Running time (in seconds)'
        metric = 'time_cpu'
        
        ymin = 0
        ymax = 5

class CoreDemandNorm(CoreDemand):
    
    prefix = 'results/corerbac_demand'
    imagename = 'norm'
    
    class ExpExtractor(NormalizedExtractor, CoreDemand.ExpExtractor):
        
        series = [
            (('coreRBAC_checkaccess_inc', 'all'),
             'incremental',
             'blue', '- o normal'),
            (('coreRBAC_checkaccess_dem', 'all'),
             'filtered',
             'green', '- ^ poly1'),
        ]
        
        base_sid_map = {
            ('coreRBAC_checkaccess_dem', 'all'):
                ('coreRBAC_checkaccess_inc', 'all'),
        }
        
        def normalize(self, pre_y, base_y):
            return pre_y / base_y
        
        ylabel = 'Running time (normalized)'
        ymax = 1.3
