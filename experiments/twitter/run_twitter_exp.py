"""Run twitter experiments."""

### TODO: Consider using a small-world graph generator
### in place of gendb


from random import sample, choice
from itertools import product
import os
import sys
import importlib

from frexp import (ExpWorkflow, Datagen,
                   SimpleExtractor, MetricExtractor,
                   TotalSizeExtractor, NormalizedExtractor,
                   Printer)

from experiments.twitter.gendb_wrapper import (
                        gen_pairs, gen_pairs_with_inverse,
                        steal_edges, move_edge)

from experiments.util import (SmallExtractor, LargeExtractor,
                              PosterExtractor, canonize)


class TwitterDatagen(Datagen):
    
    """Create users and groups. Each user has a specified number of
    followers. Perform initial queries on each (user, pair) that
    we want to demand (treating that user as a celeb within the query).
    "NYC" will always be one of the possible locations.
    
    Then, perform queries interleaved with location updates,
    on random data elements.
    
    Space usage is recorded after all operations are done.
    
    Parameters:
        n_users, n_groups -- number of users and groups
        user_deg -- number of users each user follows
        pad_celeb -- a celeb-follower out-degree to pad celebs up
          to, by stealing followers from other users. If None, take
          celebs as-is.
        group_deg -- number of groups each user is a member of
        n_locs -- number of possible locations (uniform probability)
        n_q_celebs, n_q_groups -- number of demanded celebs and groups
        n_q_pairs -- number of demanded pairs, chosen from the cross-
          product of demanded celebs and groups
        n_u -- number of updates to do
        q_p_u -- number of queries to do before each update
        reps -- number of repeats of the generated timed operations
        need_exact -- if True, require that queried celebs have
          an out-degree of precisely user_deg
        upkind -- kind of updates to do, one of: 'loc', 'celeb'
        celebusertag -- only update users following a tagged celeb
        groupusertag -- only update users in a tagged group
    """
    
    def genhelper(self, P):
        n_users, n_groups = P['n_users'], P['n_groups']
        user_deg = P['user_deg']
        pad_celeb = P['pad_celeb']
        group_deg = P['group_deg']
        n_q_celebs, n_q_groups = P['n_q_celebs'], P['n_q_groups']
        n_q_pairs = P['n_q_pairs']
        need_exact = P['need_exact']
        
        # (i, j) in R_follows means user i follows user j
        # (i, j) in R_memberof means user i is in group j
        
        # Normal benchmark: assign followers and group memberships
        # according to the degrees. Celebs are chosen from those
        # users with ideal out-degree first.
        req_inv = n_q_celebs if need_exact else None
        R_follows, Q_celebs = gen_pairs_with_inverse(
                    range(n_users), range(n_users), user_deg,
                    req_inv=req_inv, max_tries=10)
        Q_celebs = Q_celebs[:n_q_celebs]
        if pad_celeb is not None:
            # Invert the direction of R_follows to run steal_edges().
            R_follows = [(j, i) for i, j in R_follows]
            R_follows = steal_edges(range(n_users), R_follows,
                                    Q_celebs, pad_celeb)
            R_follows = [(j, i) for i, j in R_follows]
        R_memberof = gen_pairs(range(n_users), range(n_groups), group_deg)
        
        # Debug info.
#        from gendb_wrapper import print_pairinfo, print_deginfo
#        print_pairinfo(R_follows)
#        print_deginfo(R_follows, Q_celebs)
        
        Q_groups = sample(range(n_groups), n_q_groups)
        Q_pairs = sample(list(product(Q_celebs, Q_groups)), n_q_pairs)
        
        return R_follows, R_memberof, Q_pairs
    
    def generate(self, P):
        """Return a pair of a dataset with all operations and
        a dataset with no queries in the timed part.
        """
        n_users, n_groups = P['n_users'], P['n_groups']
        n_u = P['n_u']
        n_locs = P['n_locs']
        q_p_u = P['q_p_u']
        reps = P['reps']
        upkind = P['upkind']
        celebusertag = P['celebusertag']
        groupusertag = P['groupusertag']
        
        R_follows, R_memberof, Q_pairs = self.genhelper(P)
        
        # "NYC" is the one that satisfies the query.
        possible_locs = ['NYC'] + ['loc' + str(i) for i in range(1, n_locs)]
        # i -> loc in R_locs means user i has location loc.
        R_locs = {i: choice(possible_locs) for i in range(n_users)}
        
        # Figure out what users have what tags.
        Q_users = set(i for (i, _) in Q_pairs)
        Q_groups = set(j for (_, j) in Q_pairs)
        celebusertagged_users = set(i for (i, j) in R_follows
                                      if j in Q_users)
        groupusertagged_users = set(i for (i, j) in R_memberof
                                      if j in Q_groups)
        
        # Determine what users are fair game for location updating.
        valid_users = set(range(n_users))
        if celebusertag:
            valid_users &= celebusertagged_users
        if groupusertag:
            valid_users &= groupusertagged_users
        # Fail if we can't find a user satisfying the constraints.
        # FIXME: Change this so that we retry the whole dataset
        # generation procedure instead of raising an error.
        if len(valid_users) == 0:
            assert('Dataset generation failure: no valid users')
        
        # For the celeb update kind, store the current celeb-to-
        # follower relation, restricted to demanded celebs.
        Rcelebfollowers = [(y, x) for x, y in R_follows
                                  if y in Q_users]
        Rcelebfollowers_set = set(Rcelebfollowers)
        
        valid_users = list(valid_users)
        
        OPS_queries = []
        OPS_updates = []
        for _ in range(n_u):
            # Do some queries.
            ops = []
            for _ in range(q_p_u):
                c, g = choice(Q_pairs)
                ops.append((c, g))
            OPS_queries.append(ops)
            
            if upkind == 'loc':
                # Location update.
                i = choice(valid_users)
                
                loc = choice(possible_locs)
                OPS_updates.append((i, loc))
            elif upkind == 'celeb':
                # Following update.
                # Always chooses a queried celebrity.
                c, old_u, new_u = move_edge(
                        Rcelebfollowers, Rcelebfollowers_set,
                        range(n_users))
                OPS_updates.append((c, old_u, new_u))
            else:
                assert()
        
        
        return dict(
            dsparams = P,
            n_users = n_users,
            n_groups = n_groups,
            Q_pairs = Q_pairs,
            R_follows = R_follows,
            R_memberof = R_memberof,
            R_locs = R_locs,
            OPS_queries = OPS_queries,
            OPS_updates = OPS_updates,
            reps = reps,
            upkind = upkind,
        )
    
    # Set to [False, True] to run two versions, first with all
    # operations and then with updates only (no queries).
    noqs = [False]
    
    def get_tparams_list(self, dsparams_list):
        # Generate trialparams for versions with and without queries.
        return [dict(tid = dsp['dsid'] + '_' + str(noq),
                     dsid = dsp['dsid'],
                     prog = prog,
                     noq = noq)
                for prog in self.progs
                for dsp in dsparams_list
                for noq in self.noqs
        ]


class TwitterDriver:
    
    # Twitter-specific driver. TODO: refactor into frexp.
    
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
        self.reps = dataset['reps']
        self.upkind = dataset['upkind']
        
        self.setUp()
        
        from frexp.util import StopWatch, user_time
        from time import process_time, perf_counter
        timer_user = StopWatch(user_time)
        timer_cpu = StopWatch(process_time)
        timer_wall = StopWatch(perf_counter)
        
        with timer_user, timer_cpu, timer_wall:
            self.run_demand()
        
        self.results['demtime_user'] = timer_user.consume()
        self.results['demtime_cpu'] = timer_cpu.consume()
        self.results['demtime_wall'] = timer_wall.consume()
        
        with timer_user, timer_cpu, timer_wall:
            self.run_ops()
        
        import invinc.runtime
        self.results['size'] = invinc.runtime.get_total_structure_size(
                                    self.module.__dict__)
        self.results['opstime_user'] = timer_user.consume()
        self.results['opstime_cpu'] = timer_cpu.consume()
        self.results['opstime_wall'] = timer_wall.consume()
        
        # For the purpose of comparing standard deviation / mean,
        # don't worry about the time spent demanding things.
        self.results['stdmetric'] = self.results['opstime_cpu']
        
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
                    'experiments.twitter.' + filename)
        finally:
            if dirname:
                sys.path.pop()
        
        
        m = self.module
        ds = self.dataset
        
        # Populate dataset.
        self.users = [m.make_user('e' + str(i), ds['R_locs'][i])
                      for i in range(ds['n_users'])]
        self.groups = [m.make_group() for i in range(ds['n_groups'])]
        
        for i, j in ds['R_follows']:
            m.follow(self.users[i], self.users[j])
        for i, j in ds['R_memberof']:
            m.join_group(self.users[i], self.groups[j])
        
        # Preprocess operations.
        self.ops_queries = ds['OPS_queries']
        self.ops_updates = ds['OPS_updates']
        if self.noq:
            self.ops_queries = [[] for _ in range(len(self.ops_queries))]
        else:
            for qops in self.ops_queries:
                for i, (c, g) in enumerate(qops):
                    qops[i] = (self.users[c], self.groups[g])
        if self.upkind == 'loc':
            for i, (u, loc) in enumerate(self.ops_updates):
                self.ops_updates[i] = (self.users[u], loc)
        elif self.upkind == 'celeb':
            for i, (c, old_u, new_u) in enumerate(self.ops_updates):
                self.ops_updates[i] = \
                    (self.users[c], self.users[old_u], self.users[new_u])
        else:
            assert()
    
    def run_demand(self):
        for c, g in self.dataset['Q_pairs']:
            self.module.do_query(self.users[c], self.groups[g])
    
    def run_ops(self):
        ops_queries = self.ops_queries
        ops_updates = self.ops_updates
        do_query = self.module.do_query_nodemand
        follow = self.module.follow
        unfollow = self.module.unfollow
        change_loc = self.module.change_loc
        
        assert len(ops_queries) == len(ops_updates)
        
        if self.upkind == 'loc':
            for _ in range(self.reps):
                for qops, (u, loc) in zip(ops_queries, ops_updates):
                    for c, g in qops:
                        do_query(c, g)
                    change_loc(u, loc)
        elif self.upkind == 'celeb':
            for _ in range(self.reps):
                for qops, (c, old_u, new_u) in \
                        zip(ops_queries, ops_updates):
                    for c2, g in qops:
                        do_query(c2, g)
                    unfollow(old_u, c)
                    follow(new_u, c)
        else:
            assert()
    
    def tearDown(self):
        pass

class TwitterProfileDriver(TwitterDriver):
    
    def __init__(self, pipe_filename):
        import line_profiler
        import builtins
        self.prof = line_profiler.LineProfiler()
        builtins.__dict__['profile'] = self.prof
        super().__init__(pipe_filename)
    
#    def run_ops(self):
#        super().run_ops()
    
    def tearDown(self):
        print()
        self.prof.print_stats()
        super().tearDown()

class TwitterVerifyDriver(TwitterDriver):
    
    # Twitter-specific driver. TODO: refactor into frexp.
    
    condense_output = True
    
    def log_output(self, output):
        canon_value = canonize(output, use_hash=self.condense_output)
        self.results['output'].append(canon_value)
    
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
        self.reps = dataset['reps']
        self.upkind = dataset['upkind']
        
        self.setUp()
        
        from frexp.util import StopWatch, user_time
        from time import process_time, perf_counter
        timer_user = StopWatch(user_time)
        timer_cpu = StopWatch(process_time)
        timer_wall = StopWatch(perf_counter)
        
        self.results['output'] = []
        
        with timer_user, timer_cpu, timer_wall:
            self.run_demand()
        
        with timer_user, timer_cpu, timer_wall:
            self.run_ops()
        
        self.tearDown()
        
        self.results['output'] = canonize(self.results['output'],
                                          use_hash=self.condense_output)
        
        with open(pipe_filename, 'wb') as pf:
            pickle.dump(self.results, pf)
    
    def run_ops(self):
        ops_queries = self.ops_queries
        ops_updates = self.ops_updates
        do_query = self.module.do_query_nodemand
        follow = self.module.follow
        unfollow = self.module.unfollow
        change_loc = self.module.change_loc
        
        assert len(ops_queries) == len(ops_updates)
        
        if self.upkind == 'loc':
            for _ in range(self.reps):
                for qops, (u, loc) in zip(ops_queries, ops_updates):
                    for c, g in qops:
                        output = do_query(c, g)
                        self.log_output(output)
                    change_loc(u, loc)
        elif self.upkind == 'celeb':
            for _ in range(self.reps):
                for qops, (c, old_u, new_u) in \
                        zip(ops_queries, ops_updates):
                    for c2, g in qops:
                        output = do_query(c2, g)
                        self.log_output(output)
                    unfollow(old_u, c)
                    follow(new_u, c)
        else:
            assert()


class TwitterExtractor(SimpleExtractor, SmallExtractor):
    
    """Extractor that distinguishes all-ops runs from
    no-queries runs.
    """
    
    def scale(self, y, sid):
        # Hook for scaling after project_y() and the subtraction
        # have already run.
        return y
    
    # The series ids are pairs. The second component can be
    # one of 'all', 'updates', or 'queries'. The first two
    # refer to runs without and with the no-queries modifier.
    # The third refers to a virtual series computed by
    # subtracting the averages of updates from all.
    
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
            data = self.project_and_average_data(q_data, average=average)
        elif kind == 'updates':
            data = self.project_and_average_data(noq_data, average=average)
        elif kind == 'queries':
            q_avg = self.project_and_average_data(q_data, average=True)
            noq_avg = self.project_and_average_data(noq_data, average=True)
            
            data = []
            for ((ax, ay, _alo, _ahi), (ux, uy, _ulo, _uhi)) in \
                    zip(q_avg, noq_avg):
                assert ax == ux
                # Use 0 for errorbar data.
                data.append((ax, ay - uy, 0, 0))
        else:
            assert()
        
        for i, (x, y, lo, hi) in enumerate(data):
            data[i] = (x, self.scale(y, sid),
                       self.scale(lo, sid), self.scale(hi, sid))
        
        return data


class TwitterWorkflow(ExpWorkflow):
    
    ExpDatagen = TwitterDatagen
    ExpExtractor = TwitterExtractor
    ExpDriver = TwitterDriver
    ExpVerifyDriver = TwitterVerifyDriver
    
    require_ac = False ###


class Scale(TwitterWorkflow):
    
    """Increase number of users and degree of users and groups
    proportionally. Low demand.
    """
    
    prefix = 'results/twitter_scale'
    
    class ExpDatagen(TwitterWorkflow.ExpDatagen):
        
        progs = [
            'twitter_orig',
            'twitter_inc',
            'twitter_dem',
        ]
        
        noqs = [
            False,
            True,
        ]
        
        def get_dsparams_list(self):
            return [
                dict(
                    dsid =           str(x),
                    x =              2000 * x,
                    
                    n_users =        2000 * x,
                    n_groups =       20 * x,
                    pad_celeb =      None,
                    
                    user_deg =       10 * x,
                    group_deg =      1 * x,
                    
                    n_locs =         20,
                    
                    n_q_celebs =     3,
                    n_q_groups =     1,
                    n_q_pairs =      3,
                    
                    n_u =            200000,
                    q_p_u =          1,
                    reps =           1,
                    
                    need_exact =     True,
                    upkind =         'loc',
                    celebusertag =   False,
                    groupusertag =   False,
                )
                for x in range(1, 10 + 1)
            ]
    
    stddev_window = .1
    min_repeats = 10
    max_repeats = 100
    
    class ExpExtractor(TwitterWorkflow.ExpExtractor):
        
        xlabel = 'Number of users (in thousands)'
        
        def project_x(self, p):
            return super().project_x(p) / 1e3
        
        xmin = 1
        xmax = 21
        x_ticklocs = [0, 4, 8, 12, 16, 20]

class ScaleTime(Scale):
    
    class ExpExtractor(Scale.ExpExtractor,
                       MetricExtractor):
        
        series = [
#            (('twitter_orig', 'all'), 'original',
#             'red', '-- s points'),
#            (('twitter_inc', 'all'), 'incremental',
#             'blue', '-- o line'),
#            (('twitter_dem', 'all'), 'filtered',
#             'green', '-- ^ line'),
            
            (('twitter_orig', 'queries'), 'original query',
             'red', '1-2 s poly1'),
            (('twitter_orig', 'updates'), 'original update',
             'red', '1-4 _s poly1'),
            (('twitter_inc', 'queries'), 'incremental query',
             'blue', '1-2 o poly1'),
            (('twitter_inc', 'updates'), 'incremental update',
             'blue', '1-4 _o poly1'),
            (('twitter_dem', 'queries'), 'filtered query',
             'green', '1-2 ^ poly1'),
            (('twitter_dem', 'updates'), 'filtered update',
             'green', '1-4 _^ poly1'),
        ]
        
#        def scale(self, y, sid):
#            if sid in [('twitter_orig', 'updates'),
#                       ('twitter_inc', 'queries'),
#                       ('twitter_dem', 'queries')]:
#                return y * 5
#            else:
#                return y
        
        @property
        def rcparams(self):
            return dict(super().rcparams,
                        **{'legend.handletextpad': .4,
                           'legend.borderaxespad': .2})
        
        metric = 'opstime_cpu'
        
        ylabel = 'Running time (in seconds)'
        ymin = 0
        ymax = 4.5
        y_ticklocs = [0, 1, 2, 3, 4]
    
    imagename = 'time'

class ScaleTimePoster(ScaleTime):
    
    class ExpExtractor(PosterExtractor, ScaleTime.ExpExtractor):
        
        series = [
            (('twitter_orig', 'queries'), 'orig. query',
             'red', '3-6 s poly1'),
            (('twitter_inc', 'queries'), 'incr. query',
             'blue', '3-6 o poly1'),
            (('twitter_dem', 'queries'), 'dem. query',
             'green', '3-6 ^ poly1'),
            (('twitter_orig', 'updates'), 'orig. update',
             'red', '3-16 _s poly1'),
            (('twitter_inc', 'updates'), 'incr. update',
             'blue', '3-16 _o poly1'),
            (('twitter_dem', 'updates'), 'dem. update',
             'green', '3-16 _^ poly1'),
        ]
        
        xlabel = 'Users (thousands)'
        ylabel = 'Time (s)'
        
        figsize = (8, 7)
        tightlayout_bbox = (0, .25, 1, 1)
        legend_bbox = (0, -.45, 1, .20)
        legend_loc = 'upper center'
        legend_ncol = 2
        
        @property
        def rcparams(self):
            return dict(super().rcparams,
                        **{'legend.borderaxespad': .2,
                           'legend.handlelength': 1.7})

class ScaleSize(Scale):
    
    class ExpExtractor(Scale.ExpExtractor,
                       TotalSizeExtractor):
        
        series = [
            (('twitter_inc', 'all'), 'incremental',
             'blue', '- !o poly2'),
            (('twitter_dem', 'all'), 'filtered $\\times$ 100',
             'green', '- !^ poly1'),
        ]
        
        demscale = 100
        
        max_xitvls = 5
        ylabel = 'Add\'l space (in millions)'
        def project_y(self, p):
            y = super().project_y(p)
            # Scale dem separately from inc.
            if p['prog'] == 'twitter_dem':
                return y / 1e6 * self.demscale
            return y / 1e6
    
    imagename = 'size'

class ScaleSizePoster(ScaleSize):
    
    class ExpExtractor(PosterExtractor, ScaleSize.ExpExtractor):
        
        series = [
            (('twitter_inc', 'all'), 'incr.',
             'blue', '- !o poly2'),
            (('twitter_dem', 'all'), 'incr. w/ demand (x 10)',
             'green', '- !^ poly1'),
        ]
        
        demscale = 10
        
        xlabel = 'Users (thousands)'
        ylabel = 'Add\'l size (millions)'


class Demand(TwitterWorkflow):
    
    """Increase number of demanded pairs."""
    
    prefix = 'results/twitter_demand'
    
    class ExpDatagen(TwitterWorkflow.ExpDatagen):
        
        progs = [
            'twitter_inc',
            'twitter_dem',
        ]
        
        def get_dsparams_list(self):
            return [
                dict(
                    dsid =           str(x),
                    x =              x,
                    
                    n_users =        20000,
                    n_groups =       200,
                    pad_celeb =      None,
                    
                    user_deg =       100,
                    group_deg =      10,
                    
                    n_locs =         20,
                    
                    n_q_celebs =     x,
                    n_q_groups =     1,
                    n_q_pairs =      x,
                    
                    n_u =            200000,
                    q_p_u =          1,
                    reps =           1,
                    
                    need_exact =     False,
                    upkind =         'loc',
                    celebusertag =   True,
                    groupusertag =   True,
                )
                for x in [1] + list(range(2000, 20001, 2000))
            ]
    
    stddev_window = .1
    min_repeats = 10
    max_repeats = 100
    
    class ExpExtractor(TwitterWorkflow.ExpExtractor):
        
        series = [
            (('twitter_inc', 'all'), 'incremental',
             'blue', '- !o poly1'),
            (('twitter_dem', 'all'), 'filtered',
             'green', '- !^ poly1'),
        ]
        
        xlabel = 'Number of users in \\texttt{U} (in thousands)'
        # For Annie's writing, use "demand" instead of U.
#        xlabel = 'Number of users in \\texttt{demand} (in thousands)'
        
        def project_x(self, p):
            return super().project_x(p) / 1e3
        
        xmin = -1
        xmax = 21
        x_ticklocs = [0, 4, 8, 12, 16, 20]

class DemandTime(Demand):
    
    class ExpExtractor(Demand.ExpExtractor,
                       MetricExtractor):
        
        ymin = 0

class DemandTimeOps(DemandTime):
    
    class ExpExtractor(DemandTime.ExpExtractor):
        
        metric = 'opstime_cpu'
        ylabel = 'Running time (in seconds)'
    
    imagename = 'time'

class DemandTimeDem(DemandTime):
    
    class ExpExtractor(DemandTime.ExpExtractor):
        metric = 'demtime_cpu'
        ylabel = 'Demand time (in seconds)'
#        y_ticklocs = [5, 10, 15, 20, 25, 30]
    
    imagename = 'demtime'

class DemandTimeTotal(DemandTime):
    
    class ExpExtractor(DemandTime.ExpExtractor):
        ylabel = 'Total time (in seconds)'
#        y_ticklocs = [5, 10, 15, 20, 25, 30]
        def project_y(self, p):
            return p['results']['demtime_cpu'] + p['results']['opstime_cpu']
    
    imagename = 'time_plusdemand'

class DemandSize(Demand):
    
    class ExpExtractor(Demand.ExpExtractor,
                       TotalSizeExtractor):
        
        ylabel = 'Add\'l space (in millions)'
        
        def project_y(self, p):
            return super().project_y(p) / 1e6
        
        y_ticklocs = [0, 1, 2, 3, 4]
        
    imagename = 'size'


class Factor(TwitterWorkflow):
    
    """Do queries and following updates on a fixed dataset."""
    
    class ExpDatagen(TwitterWorkflow.ExpDatagen):
        
        progs = [
            'twitter_dem',
            
            'twitter_dem_aug',
            'twitter_dem_das',
            
            'twitter_dem_noninline',
            'twitter_dem_norcelim',
            'twitter_dem_notypecheck',
            'twitter_dem_handopt',
            'twitter_dem_noalias',
            'twitter_dem_notypecheck_noalias',
        ]
    
    stddev_window = .1
    min_repeats = 10
    max_repeats = 100
     
    class ExpExtractor(TwitterWorkflow.ExpExtractor):
        
        xlabel = 'x'
    
    class ExpViewer(Printer):
        
        transpose = True
        
        def round_y(self, y):
            return round(y, 3)

class Factor1A(Factor):
    
    prefix = 'results/twitter_factor1a'
    
    class ExpDatagen(Factor.ExpDatagen):
        
        def get_dsparams_list(self):
            return [
                dict(
                    dsid =           str(x),
                    x =              x,
                    
                    n_users =        20000,
                    n_groups =       200,
                    pad_celeb =      None,
                    
                    user_deg =       100,
                    group_deg =      10,
                    
                    n_locs =         20,
                    
                    n_q_celebs =     3,
                    n_q_groups =     1,
                    n_q_pairs =      3,
                    
                    n_u =            200000,
                    q_p_u =          1,
                    reps =           1,
                    
                    need_exact =     False,
                    upkind =         'loc',
                    celebusertag =   True,
                    groupusertag =   True,
                )
                for x in [1]
            ]

class Factor1B(Factor):
    
    prefix = 'results/twitter_factor1b'
    
    class ExpDatagen(Factor.ExpDatagen):
        
        def get_dsparams_list(self):
            return [
                dict(
                    dsid =           str(x),
                    x =              x,
                    
                    n_users =        20000,
                    n_groups =       200,
                    pad_celeb =      None,
                    
                    user_deg =       100,
                    group_deg =      10,
                    
                    n_locs =         20,
                    
                    n_q_celebs =     20000,
                    n_q_groups =     1,
                    n_q_pairs =      20000,
                    
                    n_u =            200000,
                    q_p_u =          1,
                    reps =           1,
                    
                    need_exact =     False,
                    upkind =         'loc',
                    celebusertag =   True,
                    groupusertag =   True,
                )
                for x in [1]
            ]

class Factor1C(Factor):
    
    prefix = 'results/twitter_factor1c'
    
    class ExpDatagen(Factor.ExpDatagen):
        
        def get_dsparams_list(self):
            return [
                dict(
                    dsid =           str(x),
                    x =              x,
                    
                    n_users =        10000,
                    n_groups =       100,
                    pad_celeb =      None,
                    
                    user_deg =       200,
                    group_deg =      5,
                    
                    n_locs =         20,
                    
                    n_q_celebs =     10000,
                    n_q_groups =     1,
                    n_q_pairs =      10000,
                    
                    n_u =            200000,
                    q_p_u =          1,
                    reps =           1,
                    
                    need_exact =     False,
                    upkind =         'loc',
                    celebusertag =   True,
                    groupusertag =   True,
                )
                for x in [1]
            ]

class Factor1D(Factor):
    
    prefix = 'results/twitter_factor1d'
    
    class ExpDatagen(Factor.ExpDatagen):
        
        def get_dsparams_list(self):
            return [
                dict(
                    dsid =           str(x),
                    x =              x,
                    
                    n_users =        2000,
                    n_groups =       20,
                    pad_celeb =      None,
                    
                    user_deg =       1000,
                    group_deg =      1,
                    
                    n_locs =         20,
                    
                    n_q_celebs =     2000,
                    n_q_groups =     1,
                    n_q_pairs =      2000,
                    
                    n_u =            200000,
                    q_p_u =          1,
                    reps =           1,
                    
                    need_exact =     False,
                    upkind =         'loc',
                    celebusertag =   True,
                    groupusertag =   True,
                )
                for x in [1]
            ]

class Factor2A(Factor):
    
    prefix = 'results/twitter_factor2a'
    
    class ExpDatagen(Factor.ExpDatagen):
        
        def get_dsparams_list(self):
            return [
                dict(
                    dsid =           str(x),
                    x =              x,
                    
                    n_users =        20000,
                    n_groups =       200,
                    pad_celeb =      None,
                    
                    user_deg =       100,
                    group_deg =      10,
                    
                    n_locs =         20,
                    
                    n_q_celebs =     1,
                    n_q_groups =     1,
                    n_q_pairs =      1,
                    
                    n_u =            200000,
                    q_p_u =          1,
                    reps =           1,
                    
                    need_exact =     False,
                    upkind =         'celeb',
                    celebusertag =   False,
                    groupusertag =   False,
                )
                for x in [1]
            ]

class Factor2B(Factor):
    
    prefix = 'results/twitter_factor2b'
    
    class ExpDatagen(Factor.ExpDatagen):
        
        def get_dsparams_list(self):
            return [
                dict(
                    dsid =           str(x),
                    x =              x,
                    
                    n_users =        20000,
                    n_groups =       200,
                    pad_celeb =      None,
                    
                    user_deg =       100,
                    group_deg =      10,
                    
                    n_locs =         20,
                    
                    n_q_celebs =     1,
                    n_q_groups =     200,
                    n_q_pairs =      200,
                    
                    n_u =            200000,
                    q_p_u =          1,
                    reps =           1,
                    
                    need_exact =     False,
                    upkind =         'celeb',
                    celebusertag =   False,
                    groupusertag =   False,
                )
                for x in [1]
            ]

class Factor2C(Factor):
    
    prefix = 'results/twitter_factor2c'
    
    class ExpDatagen(Factor.ExpDatagen):
        
        def get_dsparams_list(self):
            return [
                dict(
                    dsid =           str(x),
                    x =              x,
                    
                    n_users =        10000,
                    n_groups =       100,
                    pad_celeb =      None,
                    
                    user_deg =       200,
                    group_deg =      5,
                    
                    n_locs =         1,
                    
                    n_q_celebs =     1,
                    n_q_groups =     100,
                    n_q_pairs =      100,
                    
                    n_u =            200000,
                    q_p_u =          1,
                    reps =           1,
                    
                    need_exact =     False,
                    upkind =         'celeb',
                    celebusertag =   False,
                    groupusertag =   False,
                )
                for x in [1]
            ]

class Factor2D(Factor):
    
    prefix = 'results/twitter_factor2d'
    
    class ExpDatagen(Factor.ExpDatagen):
        
        def get_dsparams_list(self):
            return [
                dict(
                    dsid =           str(x),
                    x =              x,
                    
                    n_users =        2000,
                    n_groups =       20,
                    pad_celeb =      None,
                    
                    user_deg =       1000,
                    group_deg =      1,
                    
                    n_locs =         1,
                    
                    n_q_celebs =     1,
                    n_q_groups =     20,
                    n_q_pairs =      20,
                    
                    n_u =            200000,
                    q_p_u =          1,
                    reps =           1,
                    
                    need_exact =     False,
                    upkind =         'celeb',
                    celebusertag =   False,
                    groupusertag =   False,
                )
                for x in [1]
            ]

class FactorTime(Factor):
    
    class ExpExtractor(Factor.ExpExtractor,
                       MetricExtractor):
        
        series = [
            (('twitter_dem', 'all'), 'filtered (normal)',
             'green', '-- ^ normal'),
            
            (('twitter_dem_aug', 'all'), 'augmented',
             'blue', '-- o normal'),
            (('twitter_dem_das', 'all'), 'das.',
             'cyan', '-- o normal'),
            
            (('twitter_dem_noninline', 'all'), 'non-inlined',
             'orange', '-- s normal'),
            (('twitter_dem_norcelim', 'all'), 'no RC elim',
             'red', '-- s normal'),
            (('twitter_dem_notypecheck', 'all'), 'no type checks',
             'yellow', '-- s normal'),
            (('twitter_dem_handopt', 'all'), 'hand-optimized',
             'fuchsia', '-- s normal'),
            (('twitter_dem_noalias', 'all'), 'alias-optimized',
             'purple', '-- s normal'),
            (('twitter_dem_notypecheck_noalias', 'all'),
             'no type checks + alias-opt',
             'lightpurple', '-- s normal'),
        ]
        
        metric = 'opstime_cpu'
        
        ylabel = 'Running time (in seconds)'
        ymin = 0
    
    imagename = 'time'

class FactorTimeNorm(FactorTime):
    
    class ExpExtractor(NormalizedExtractor,
                       FactorTime.ExpExtractor):
        
        base_sid = ('twitter_dem', 'all')
        
        def normalize(self, pre_y, base_y):
            return pre_y / base_y

class Factor1ATimeNorm(Factor1A, FactorTimeNorm):
    pass
class Factor1BTimeNorm(Factor1B, FactorTimeNorm):
    pass
class Factor1CTimeNorm(Factor1C, FactorTimeNorm):
    pass
class Factor1DTimeNorm(Factor1D, FactorTimeNorm):
    pass
class Factor2ATimeNorm(Factor2A, FactorTimeNorm):
    pass
class Factor2BTimeNorm(Factor2B, FactorTimeNorm):
    pass
class Factor2CTimeNorm(Factor2C, FactorTimeNorm):
    pass
class Factor2DTimeNorm(Factor2D, FactorTimeNorm):
    pass


class Tag(TwitterWorkflow):
    
    prefix = 'results/twitter_tag'
    
    class ExpDatagen(TwitterWorkflow.ExpDatagen):
        
        progs = [
            'twitter_dem',
            'twitter_dem_singletag',
        ]
        
        def get_dsparams_list(self):
            return [
                dict(
                    dsid =           str(x),
                    x =              2000 * x,
                    
                    n_users =        2000 * x,
                    n_groups =       20 * x,
                    pad_celeb =      None,
                    
                    user_deg =       10 * x,
                    group_deg =      5,
                    
                    n_locs =         20,
                    
                    n_q_celebs =     2000 * x,
                    n_q_groups =     1,
                    n_q_pairs =      2000 * x,
                    
                    n_u =            200000,
                    q_p_u =          1,
                    reps =           1,
                    
                    need_exact =     False,
                    upkind =         'loc',
                    celebusertag =   False,
                    groupusertag =   False,
                )
                for x in range(1, 10 + 1)
            ]
    
    stddev_window = .1
    min_repeats = 10
    max_repeats = 100
    
    class ExpExtractor(Scale.ExpExtractor):
        pass

class TagTime(Tag):
    
    class ExpExtractor(Tag.ExpExtractor,
                       MetricExtractor):
        
        series = [
            (('twitter_dem_singletag', 'all'), 'OSQ strategy',
             'orange', '-- !^ poly1'),
            (('twitter_dem', 'all'), 'filtered',
             'green', '- !^ poly1'),
        ]
        
        metric = 'opstime_cpu'
        
        ylabel = 'Running time (in seconds)'
        ymin = 0
        max_yitvls = 4
    
    imagename = 'time'
