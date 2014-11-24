"""Run the OSQ-django experiments."""


import os, sys, importlib
from copy import deepcopy
from random import randrange

from frexp import (ExpWorkflow, Datagen,
                   MetricExtractor, NormalizedExtractor)

from experiments.util import SmallExtractor, LargeExtractor, canonize


class DjangoDatagen(Datagen):
    
    """Test procedure follows OSQ section 9, authentication query.
    
    The user to query after each update is chosen randomly.
    Obviously, the group is marked active.
    
    Additional facility for only querying over a certain size
    subset of all users.
    
    Parameters:
      n_users -- number of users
      n_q_users -- number of queryable users.
      n_perms -- number of permissions, add operations, and queries
    """
    
    def generate(self, P):
        n_users = P['n_users']
        n_q_users = P['n_q_users']
        n_perms = P['n_perms']
        
        assert n_q_users <= n_users
        
        qseq = [randrange(n_q_users) for _ in range(n_perms)]
        
        return dict(
            dsparams = P,
            qseq = qseq,
        )


class DjangoDriver:
    
    def __init__(self, pipe_filename):
        import gc
        import pickle
        
        gc.disable()
        
        with open(pipe_filename, 'rb') as pf:
            dataset, prog, other_tparams = pickle.load(pf)
        os.remove(pipe_filename)
        
        
        self.dataset = dataset
        self.prog = prog
        self.simplified_query = '_simp_' in prog
        self.module = None
        self.results = {}
        self.qseq = dataset['qseq']
        
        self.setUp()
        
        from frexp.util import StopWatch, user_time
        from time import process_time, perf_counter
        timer_user = StopWatch(user_time)
        timer_cpu = StopWatch(process_time)
        timer_wall = StopWatch(perf_counter)
        
        with timer_user, timer_cpu, timer_wall:
            self.run()
        
        import runtimelib
        self.results['size'] = runtimelib.get_total_structure_size(
                                    self.module.__dict__)
        self.results['time_user'] = timer_user.consume()
        self.results['time_cpu'] = timer_cpu.consume()
        self.results['time_wall'] = timer_wall.consume()
        
        self.results['stdmetric'] = self.results['time_cpu']
        
        self.tearDown()
        
        
        with open(pipe_filename, 'wb') as pf:
            pickle.dump(self.results, pf)
    
    def setUp(self):
        # Import driven program.
        dirname, filename = os.path.split(self.prog)
        if dirname:
            sys.path.append(dirname)
        try:
            self.module = importlib.import_module(
                    'experiments.django.' + filename)
        finally:
            if dirname:
                sys.path.pop()
        
        
        m = self.module
        ds = self.dataset
        
        # Populate dataset.
        self.group = m.make_group(True)
        self.users = []
        for i in range(ds['dsparams']['n_users']):
            u = m.make_user('u' + str(i))
            self.users.append(u)
            m.add_group(u, self.group)
        self.perms = []
        for i in range(ds['dsparams']['n_perms']):
            p = m.make_perm('p' + str(i))
            self.perms.append(p)
        
        # Preprocess operations.
        self.ops = []
        assert len(self.qseq) == len(self.perms)
        for i, ui in enumerate(self.qseq):
            # u is either a user or uid, depending on prog.
            u = self.users[ui]
            if not self.simplified_query:
                u = u.id
            self.ops.append((self.perms[i], u))
        
        # Query over each user that's ever queried
        # We should only have to query once to get users in the
        # U-set, but let's query each individual user just in
        # case the U-set strategy is altered.
        for _, u in self.ops:
            m.do_query(u)
    
    def run(self):
        g = self.group
        add_perm = self.module.add_perm
        do_query = self.module.do_query_nodemand
        
        for p, u in self.ops:
            add_perm(g, p)
            # For the implementations using the normal query,
            # u is a user uid. For the simplified query, it's
            # the actual user object itself.
            do_query(u)
    
    def tearDown(self):
        pass

class DjangoVerifyDriver:
    
    def __init__(self, pipe_filename):
        import gc
        import pickle
        
        gc.disable()
        
        with open(pipe_filename, 'rb') as pf:
            dataset, prog, other_tparams = pickle.load(pf)
        os.remove(pipe_filename)
        
        
        self.dataset = dataset
        self.prog = prog
        self.module = None
        self.results = {'output': []}
        self.qseq = dataset['qseq']
        
        self.setUp()
        
        from frexp.util import StopWatch, user_time
        from time import process_time, perf_counter
        timer_user = StopWatch(user_time)
        timer_cpu = StopWatch(process_time)
        timer_wall = StopWatch(perf_counter)
        
        with timer_user, timer_cpu, timer_wall:
            self.run()
        
        self.tearDown()
        
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
                    'experiments.django.' + filename)
        finally:
            if dirname:
                sys.path.pop()
        
        
        m = self.module
        ds = self.dataset
        
        # Populate dataset.
        self.group = m.make_group(True)
        self.users = []
        for i in range(ds['dsparams']['n_users']):
            u = m.make_user('u' + str(i))
            self.users.append(u)
            m.add_group(u, self.group)
        self.perms = []
        for i in range(ds['dsparams']['n_perms']):
            p = m.make_perm('p' + str(i))
            self.perms.append(p)
        m.do_query(self.users[0].id)
        
        # Preprocess operations.
        self.ops = []
        assert len(self.qseq) == len(self.perms)
        for i, ui in enumerate(self.qseq):
            self.ops.append((self.perms[i], self.users[ui].id))
    
    def run(self):
        g = self.group
        add_perm = self.module.add_perm
        do_query = self.module.do_query_nodemand
        
        for p, uid in self.ops:
            add_perm(g, p)
            output = do_query(uid)
            self.results['output'].append(deepcopy(output))
    
    def tearDown(self):
        pass


class DjangoWorkflow(ExpWorkflow):
    
    ExpDatagen = DjangoDatagen
    ExpExtractor = SmallExtractor
    
    ExpDriver = DjangoDriver
    
    # Verify out-of-date, needs to account for
    # simplified query implementations.
#    ExpVerifyDriver = DjangoVerifyDriver
    
    require_ac = False ###


class Scale(DjangoWorkflow):
    
    """Vary the number of permissions and queries.
    Use Tom's original parameters from the OSQ paper.
    """
    
    ###
    prefix = 'results/django_scale_small'
    
    class ExpDatagen(DjangoWorkflow.ExpDatagen):
        
        progs = [
            'django_orig',
            'django_dem',
            'django_osq',
        ]
        
        n_users_list = [100, 200, 300]
        batch_n_users = 100
        points = list(range(50, 500 + 1, 50))
        
        def get_dsparams_list(self):
            return [
                dict(
                    dsid =    str(n_users) + '_' + str(n_perms),
                    x =       n_perms,
                    
                    n_users = n_users,
                    n_q_users = n_users,
                    n_perms = n_perms,
                )
                for n_users in self.n_users_list
                for n_perms in self.points
            ]
        
        def get_tparams_list(self, dsparams_list):
            # Exclude all but one of the n_users possibilities
            # from running with Batch.
            return [
                dict(
                    tid = dsp['dsid'],
                    dsid = dsp['dsid'],
                    prog = prog,
                )
                for prog in self.progs
                for dsp in dsparams_list
                if not (prog == 'django_orig' and
                        dsp['n_users'] != self.batch_n_users)
            ]
    
    stddev_window = .1
    min_repeats = 10
    max_repeats = 50
    
    class ExpExtractor(DjangoWorkflow.ExpExtractor, MetricExtractor):
        
        # Post-processed below.
        _series = [
            ('django_orig', 'original',
             'red', '- !s poly2'),
            ('django_osq', 'osq',
             'orange', '-- !^ poly1'),
            ('django_dem', 'filtered',
             'green', '- !^ poly1'),
        ]
        
        @property
        def rcparams(self):
            return dict(super().rcparams,
                        **{'legend.handletextpad': .4,
                           'legend.borderaxespad': .2
                           })
        
        linestyles = ['-', '--', '-.', ':']
        # Keep this in sync with the attribute of same name
        # in the Datagen.
        n_users_list = [100, 200, 300]
        
        @property
        def series(self):
            lss = self.linestyles
            new_series = []
            for sid, name, color, style in self._series:
                for i, n_users in enumerate(self.n_users_list):
                    # Replace line style with one associated with
                    # this number of users.
                    ls = lss[i % len(lss)]
                    new_style = ' '.join([ls] + style.split()[1:])
                    new_name = name + ' (' + str(n_users) + ' users)'
                    new_series.append(((sid, n_users), new_name,
                                       color, new_style))
            return new_series
        
        ylabel = 'Running time (in seconds)'
        xlabel = 'Number of permissions'
        
        metric = 'time_cpu'
        
        def get_series_data(self, datapoints, sid):
            inner_sid, n_users = sid
            datapoints = super().get_series_data(datapoints, inner_sid)
            datapoints = [p for p in datapoints
                          if p['dsparams']['n_users'] == n_users]
            return datapoints
        
        ymin = 0
        ymax = 1.6
        max_xitvls = 5
        max_yitvls = 4


class Demand(DjangoWorkflow):
    
    """Vary the number of users that are demanded."""
    
    prefix = 'results/django_demand'
    
    class ExpDatagen(DjangoWorkflow.ExpDatagen):
        
        progs = [
            'django_inc',
            'django_dem',
            'django_osq',
            'django_simp_inc',
            'django_simp_dem',
            'django_simp_osq',
        ]
        
        def get_dsparams_list(self):
            return [
                dict(
                    dsid =    str(x),
                    x =       x,
                    
                    n_users = 300,
                    n_q_users = x,
                    n_perms = 500,
                )
                for x in [1, 10] + list(range(20, 300 + 1, 20))
            ]
    
    stddev_window = .1
    min_repeats = 10
    max_repeats = 50
    
    class ExpExtractor(DjangoWorkflow.ExpExtractor, MetricExtractor):
        
        series = [
            ('django_inc', 'incremental',
             'blue', '- !o normal'),
            ('django_osq', 'osq',
             'orange', '-- !^ normal'),
            ('django_dem', 'filtered',
             'green', '- !^ normal'),
            ('django_simp_inc', 'incremental (simplified)',
             'blue', '- _o normal'),
            ('django_simp_osq', 'osq (simplified)',
             'orange', '-- _^ normal'),
            ('django_simp_dem', 'filtered (simplified)',
             'green', '- _^ normal'),
        ]
        
        xlabel = 'Number of demanded users'
        
        metric = 'time_cpu'

class DemandTime(Demand):
    
    class ExpExtractor(Demand.ExpExtractor):
        
        # Adjust geometry for external legend.
        width = 5.25
        figsize = (width, 2.625)
        tightlayout_bbox = (0, 0, 3.5/width, 1)
        legend_bbox = (1, 0, 1, 1)
        legend_loc = 'center left'
        
        ylabel = 'Running time (in seconds)'

class DemandTimeNorm(Demand):
    
    class ExpExtractor(Demand.ExpExtractor, NormalizedExtractor):
        
        base_sid_map = {
            'django_dem': 'django_inc',
            'django_osq': 'django_inc',
            'django_simp_dem': 'django_simp_inc',
            'django_simp_osq': 'django_simp_inc',
        }
        
        def normalize(self, pre_y, base_y):
            return pre_y / base_y
        
        no_legend = True
        
        ylabel = 'Running time (normalized)'
