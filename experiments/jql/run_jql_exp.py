"""Run the JQL experiment. See WPN08 Section 4.3.

Queries:

  one-level:
    {a for a in attends if a.course == COMP101}

  two-level:
    {(a, s) for a in attends if a.course == COMP101
            for s in students if a.student == s}

  three-level:
    {(a, s, c) for a in attends if a.course == COMP101
               for s in students if a.student == s
               for c in courses if a.course == c}
"""


from random import random, randrange
import os
import sys
from copy import deepcopy
import importlib
from itertools import groupby
from operator import itemgetter

import numpy as np

from frexp import (ExpWorkflow, Datagen, Runner, Verifier,
                   SimpleExtractor, MetricExtractor)

from .java_bridge import get_config, spawn_java

from experiments.util import SmallExtractor, LargeExtractor, canonize


class JQLDatagen(Datagen):
    
    """Procedure as in WPN08. Create n students, courses, and attends.
    Use the ratio to decide whether to generate a query or a random
    add and remove.
    
    Params:
      N -- size
      nops -- number of operations
      ratio -- proportion of operations that are queries
    
    Note that WPN08 describes the ratio as a query-to-update ratio,
    rather than a query-to-all-ops ratio. This seems to be at odds with
    their graph data, which shows the cost of updates approaching zero
    as the ratio approaches 1, and which shows a behavioral change
    in "ratio caching" at x=0.2 when their stated threshold is 0.25.
    
    WPN08 is slightly unclear on whether an update operation
    deletes and re-adds the same Attends object, or removes
    an existing one and adds a brand new one. We interpret
    it as the latter.
    
    Each update, a random Attends object is chosen for removal.
    A new Attends object is constructed having a random Student
    and Course, and added in place of the old one. No attempt is
    made to detect or prevent redundant attend objects (having
    the same Course and Student). No explicit deallocation of
    the old Attends object is done.
    """
    
    # All three queries are handled with the same core.
    
    def generate(self, P):
        N = P['N']
        nops = P['nops']
        ratio = P['ratio']
        
        # Description of initial Attends objects.
        INIT_ATT = [(randrange(N), randrange(N)) for _ in range(N)]
        
        OPS = []
        for _ in range(nops):
            if random() < ratio:
                OPS += [('query', None)]
            
            else:
                # Index of Attends object to remove.
                a = randrange(N)
                # Indices describing new Attends object to replace it with.
                s = randrange(N)
                c = randrange(N)
                OPS += [('update', (a, s, c))]
        
        return dict(
            dsparams = P,
            N = N,
            ratio = ratio,
            INIT_ATT = INIT_ATT,
            OPS = OPS,
        )
    
    level = None
    
    def get_tparams_list(self, dsparams):
        # It is important to run all tests of the same kind
        # together. I've noticed a cache-recency effect where
        # Java processes that start immediately after other Java
        # processes, with no intervening Python processes, get
        # an unfair speedup. 
        
        return [
            dict(tid = dsp['dsid'],
                 dsid = dsp['dsid'],
                 prog = 'jql_' + self.level + progsuf)
            for progsuf in self.prog_suffixes
            for dsp in dsparams
        ]


class JQLDriver:
    
    check_interval = 100
    timeout = 60
    
    # Operation enum.
    Q = 1
    UP = 2
    
    def __init__(self, pipe_filename):
        import gc
        import pickle
        
        gc.disable()
        
        with open(pipe_filename, 'rb') as pf:
            dataset, prog, other_tparams = pickle.load(pf)
        os.remove(pipe_filename)
        
        
        self.prog = prog
        self.module = None
        self.N = dataset['N']
        self.init_att = dataset['INIT_ATT']
        self.ops = dataset['OPS']
        
        self.results = {}
        
        self.setUp()
        
        from frexp.util import StopWatch
        from time import process_time, perf_counter
        timer_cpu = StopWatch(process_time)
        timer_wall = StopWatch(perf_counter)
        
        # Make available to run for timeouts.
        self.timer_cpu = timer_cpu
        
        with timer_cpu, timer_wall:
            finished = self.run()
        
        if finished:
            import invinc.runtime
            self.results['size'] = invinc.runtime.get_total_structure_size(
                                    self.module.__dict__)
            self.results['time_cpu'] = timer_cpu.consume()
            self.results['time_wall'] = timer_wall.consume()
            
            self.results['stdmetric'] = self.results['time_cpu']
        else:
            self.results['timedout'] = True
        
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
                        'experiments.jql.' + filename)
        finally:
            if dirname:
                sys.path.pop()
        
        
        m = self.module
        N = self.N
        
        # Populate dataset.
        self.students = [m.make_student('s' + str(i))
                         for i in range(N)]
        self.courses = [m.make_course('c' + str(i))
                        for i in range(N)]
        self.course0 = self.courses[0]
        self.attends = [m.make_attends(self.students[s], self.courses[c])
                        for s, c in self.init_att]
        
        m.do_query(self.course0)
        
        # Preprocess operations.
        for i, (op, data) in enumerate(self.ops):
            if op == 'query':
                self.ops[i] = (self.Q, data)
            elif op == 'update':
                ai, s, c = data
                data = (ai, self.students[s], self.courses[c])
                self.ops[i] = (self.UP, data)
    
    def run(self):
        course0 = self.course0
        Q = self.Q
        UP = self.UP
        attends = self.attends
        do_query = self.module.do_query_nodemand
        replace_attends = self.module.replace_attends
        
        check_interval = self.check_interval
        timer_cpu = self.timer_cpu
        timeout = self.timeout
        
        for i, (op, data) in enumerate(self.ops):
            # Check timeout every so often.
            if i % check_interval == 0:
                if timer_cpu.elapsed > timeout:
                    return False
            
            if op is Q:
                do_query(course0)
            elif op is UP:
                i, s, c = data
                old_att = attends[i]
                new_att = replace_attends(old_att, s, c)
                attends[i] = new_att
            else:
                assert()
        
        return True
    
    def tearDown(self):
        pass

class JQLVerifyDriver:
    
    condense_output = True
    
    def log_output(self, output):
        canon_value = canonize(output, use_hash=self.condense_output)
        self.results['output'].append(canon_value)
    
    # Operation enum.
    Q = 1
    UP = 2
    
    def __init__(self, pipe_filename):
        import gc
        import pickle
        
        gc.disable()
        
        with open(pipe_filename, 'rb') as pf:
            dataset, prog, other_tparams = pickle.load(pf)
        os.remove(pipe_filename)
        
        
        self.prog = prog
        self.module = None
        self.N = dataset['N']
        self.init_att = dataset['INIT_ATT']
        self.ops = dataset['OPS']
        
        self.results = {}
        
        self.setUp()
        
        from frexp.util import StopWatch
        from time import process_time, perf_counter
        timer_cpu = StopWatch(process_time)
        timer_wall = StopWatch(perf_counter)
        
        self.results['output'] = []
        
        with timer_cpu, timer_wall:
            finished = self.run()
        
        self.tearDown()
        
        self.results['output'] = canonize(self.results['output'],
                                          use_hash=self.condense_output)
        
        
        with open(pipe_filename, 'wb') as pf:
            pickle.dump(self.results, pf)
    
    def setUp(self):
        # Import driven program.
        dirname, filename = os.path.split(self.prog)
        if dirname:
            sys.path.append(dirname)
        try:
            self.module = importlib.import_module(
                        'experiments.jql.' + filename)
        finally:
            if dirname:
                sys.path.pop()
        
        
        m = self.module
        N = self.N
        
        # Populate dataset.
        self.students = [m.make_student('s' + str(i))
                         for i in range(N)]
        self.courses = [m.make_course('c' + str(i))
                        for i in range(N)]
        self.course0 = self.courses[0]
        self.attends = [m.make_attends(self.students[s], self.courses[c])
                        for s, c in self.init_att]
        
        m.do_query(self.course0)
        
        # Preprocess operations.
        for i, (op, data) in enumerate(self.ops):
            if op == 'query':
                self.ops[i] = (self.Q, data)
            elif op == 'update':
                ai, s, c = data
                data = (ai, self.students[s], self.courses[c])
                self.ops[i] = (self.UP, data)
    
    def run(self):
        course0 = self.course0
        Q = self.Q
        UP = self.UP
        attends = self.attends
        do_query = self.module.do_query_nodemand
        replace_attends = self.module.replace_attends
        
        for i, (op, data) in enumerate(self.ops):
            if op is Q:
                output = do_query(course0)
                self.log_output(output)
            elif op is UP:
                i, s, c = data
                old_att = attends[i]
                new_att = replace_attends(old_att, s, c)
                attends[i] = new_att
            else:
                assert()
        
        return True
    
    def tearDown(self):
        pass

class JQLRunner(Runner):
    
    # Special-cased for using spawn_java() instead of the
    # normal driver, when the program to run is one of the
    # Java versions.
    
    def dispatch_test(self, dataset, prog, other_tparams):
        if 'java' in prog:
            # jql_<level>_java_<cache>
            level = prog[4:5]
            cache = {'cache': True, 'nocache': False}[prog.split('_')[-1]]
            config = get_config()
            results = spawn_java(config, level, cache, False, dataset)
            return results
        else:
            return super().dispatch_test(dataset, prog, other_tparams)
    
    def run_all_tests(self, tparams_list):
        # Hack to skip trials for a prog after there's been a timeout.
        blacklist = set()
        
        datapoint_list = []
        for i, trial in enumerate(tparams_list, 1):
            prog = trial['prog']
            if prog in blacklist:
                self.print('Skipping test ' + str(i))
                continue
            
            itemstr = 'Running test {} of {} ...'.format(i, len(tparams_list))
            self.print(itemstr, end='')
            
            datapoints, timedout = self.repeat_single_test(trial, len(itemstr))
            if timedout:
                blacklist.add(prog)
            datapoint_list.extend(datapoints)
        
        return datapoint_list

class JQLVerifier(Verifier):
    
    condense_output = JQLVerifyDriver.condense_output
    
    def dispatch_test(self, dataset, prog, other_tparams):
        # Use verify=True for spawn_java().
        # Canonize result.
        
        if 'java' in prog:
            # jql_<level>_java_<cache>
            level = prog[4:5]
            cache = {'cache': True, 'nocache': False}[prog.split('_')[-1]]
            config = get_config()
            results = spawn_java(config, level, cache, True, dataset)
            results['output'] = canonize(results['output'],
                                         use_hash=self.condense_output)
            return results
        else:
            return super().dispatch_test(dataset, prog, other_tparams)


class JQLExtractor(SimpleExtractor, SmallExtractor):
    
    orig_format = 'poly1'
    jqlcache_format = 'normal'
    jqlnocache_format = 'normal'
    
    @property
    def series(self):
        # Post-process to copy 3 times for the 3 levels.
        template_list = [
            ('jql_{}_java_nocache', 'JQL no caching',
             'purple', '-- s ' + self.jqlnocache_format),
            ('jql_{}_java_cache', 'JQL always caching',
             'teal', '-- o ' + self.jqlcache_format),
            ('jql_{}_orig', 'original',
             'red', '- s ' + self.orig_format),
            ('jql_{}_inc', 'incremental',
             'blue', '- o poly1'),
            ('jql_{}_dem', 'filtered',
             'green', '- ^ poly1'),
        ]
        
        return [(sid.format(level), name.format(level), color, style)
                for level in ['1', '2', '3']
                for sid, name, color, style in template_list]
    
    def get_series_points(self, datapoints, sid, *,
                          average):
        # Hook into this so we can dump std convergence info.mail.g
        points = super().get_series_points(datapoints, sid, average=False)
        
        fmtstring = ('{}: x = {:.3f},   stddev = {:.3f},   '
                     'mean = {:.3f},   rsd = {:.3f}')
        
        if len(points) > 0:
            points = [(x, y) for x, y, _, _ in points]
            points.sort(key=itemgetter(0))
            groups = groupby(points, key=itemgetter(0))
            
            worst = 0
            for x, grouppoints in groups:
                ys = [y for (_, y) in grouppoints]
                m = np.mean(ys)
                s = np.std(ys)
                print(fmtstring.format(sid, x, s, m, s / m))
                worst = max(worst, s / m)
            print('-' * 16)
            print('{}: worst = {:.3f}'.format(sid, worst))
            print()
        
        return super().get_series_points(datapoints, sid, average=average)


class JQLWorkflow(ExpWorkflow):
    
    class ExpDatagen(JQLDatagen):
        
        prog_suffixes = [
            # Note that Inc is identical to Dem without filter checks,
            # because the tags and filters aren't needed and get
            # eliminated automatically.
            #
            # Orig takes forever to run because it's a Cartesian product
            # followed by join conditions.
            
            '_orig',
            '_inc',
            '_dem',
            '_java_nocache',
            '_java_cache',
        ]
    
    class ExpExtractor(JQLExtractor):
        pass
#        @property
#        def title(self):
#            return 'Query ' + str(self.level)
    
    ExpRunner = JQLRunner
    ExpVerifier = JQLVerifier
    ExpDriver = JQLDriver
    ExpVerifyDriver = JQLVerifyDriver
    
    require_ac = False ###


class Ratio(JQLWorkflow):
    
    """Vary the query ratio."""
    
    class ExpDatagen(JQLWorkflow.ExpDatagen):
        
        N = 1000
        nops = 5000
        divs = 20
        
        def get_dsparams_list(self):
            return [
                dict(
                    dsid =   str(ratio),
                    x =      ratio,
                    
                    N =      self.N,
                    nops =   self.nops,
                    ratio =  ratio,
                )
                for ratio in [.01] + [i/self.divs for i in
                                      range(0, self.divs + 1)]
            ]
    
    stddev_window = .1
    min_repeats = 50
    max_repeats = 50
    
    class ExpExtractor(JQLWorkflow.ExpExtractor, MetricExtractor):
        
        ylabel = 'Running time (in seconds)'
        xlabel = 'Fraction of operations that are queries'
        
        metric = 'time_cpu'
        
        xmin = -.05
        xmax = 1.05

class Ratio1(Ratio):
    prefix = 'results/jql_ratio_1'
    class ExpDatagen(Ratio.ExpDatagen):
        level = '1'
    class ExpExtractor(Ratio.ExpExtractor):
        level = '1'

class Ratio2(Ratio):
    
    prefix = 'results/jql_ratio_2'
    
    class ExpDatagen(Ratio.ExpDatagen):
        level = '2'
    
    class ExpExtractor(Ratio.ExpExtractor):
        
        level = '2'
        
        @property
        def series(self):
            s = super().series
            new_s = []
            for sid, name, color, style in s:
                if sid in ['jql_2_orig']:
                    name += ' / 20'
                new_s.append((sid, name, color, style))
            return new_s
        
        def project_y(self, p):
            y = super().project_y(p)
            if p['prog'] in ['jql_2_orig']:
                return y / 2e1
            else:
                return y
        
        ymax = 2
        legend_loc = 'upper center'

class Ratio3(Ratio):
    prefix = 'results/jql_ratio_3'
    class ExpDatagen(Ratio.ExpDatagen):
        level = '3'
    class ExpExtractor(Ratio.ExpExtractor):
        level = '3'
        ymax = 2
        legend_loc = 'upper center'


class Scale(JQLWorkflow):
    
    """Scale up the number of elements."""
    
    class ExpDatagen(JQLWorkflow.ExpDatagen):
        
        ratio = .5
        points = list(range(2000, 20000 + 1, 2000))
        nops = 5000
        
        def get_dsparams_list(self):
            return [
                dict(
                    dsid =   str(x),
                    x =      x,
                    
                    N =      x,
                    nops =   self.nops,
                    ratio =  self.ratio,
                )
                for x in self.points
            ]
    
    stddev_window = .1
    min_repeats = 50
    max_repeats = 50
    
    class ExpExtractor(JQLWorkflow.ExpExtractor, MetricExtractor):
        
        ylabel = 'Running time (in seconds)'
        xlabel = 'Size of source collections (in thousands)'
        
        metric = 'time_cpu'
        
        def project_x(self, p):
            return super().project_x(p) / 1e3
        
        ymin = 0
        xmin = 1
        xmax = 21
        x_ticklocs = [0, 4, 8, 12, 16, 20]

class Scale1(Scale):
    
    prefix = 'results/jql_scale_1'
    
    class ExpDatagen(Scale.ExpDatagen):
        level = '1'
    
    class ExpExtractor(Scale.ExpExtractor):
        
        level = '1'
        orig_format = 'poly1'
        jqlcache_format = 'poly1'
        jqlnocache_format = 'poly1'
        
        multipliers = {
            'jql_1_orig':          1e-2,
            'jql_1_java_nocache':  1e-2,
        }
        
        @property
        def series(self):
            s = super().series
            new_s = []
            for sid, name, color, style in s:
                mult = self.multipliers.get(sid, None)
                if mult is not None:
                    op = ' $\\times$ ' if mult >= 1 else ' / '
                    if mult < 1:
                        mult = 1 / mult
                    if round(mult, 3) == round(mult):
                        mult = round(mult)
                    else:
                        mult = round(mult, 3)
                    name += op + str(mult)
                new_s.append((sid, name, color, style))
            return new_s
        
        def project_y(self, p):
            y = super().project_y(p)
            if p['prog'] in self.multipliers:
                return y * self.multipliers[p['prog']]
            else:
                return y

class Scale2(Scale):
    
    prefix = 'results/jql_scale_2'
    
    class ExpDatagen(Scale.ExpDatagen):
        level = '2'
        
        # Don't run orig, which takes forever even before
        # reaching the 100 step timeout checkpoint.
        prog_suffixes = [
            '_inc',
            '_dem',
            '_java_nocache',
            '_java_cache',
        ]
    
    class ExpExtractor(Scale.ExpExtractor):
        
        level = '2'
        jqlcache_format = 'poly2'
        jqlnocache_format = 'poly2'
        
        multipliers = {
            'jql_2_inc':  1e1,
            'jql_2_dem':  1e1,
        }
        
        @property
        def series(self):
            s = super().series
            new_s = []
            for sid, name, color, style in s:
                mult = self.multipliers.get(sid, None)
                if mult is not None:
                    op = ' $\\times$ ' if mult >= 1 else ' / '
                    if mult < 1:
                        mult = 1 / mult
                    if round(mult, 3) == round(mult):
                        mult = round(mult)
                    else:
                        mult = round(mult, 3)
                    name += op + str(mult)
                new_s.append((sid, name, color, style))
            return new_s
        
        def project_y(self, p):
            y = super().project_y(p)
            if p['prog'] in self.multipliers:
                return y * self.multipliers[p['prog']]
            else:
                return y
        
        max_yitvl = 4

class Scale2Bigger(Scale2):
    
    prefix = 'results/jql_scale_2_bigger'
    
    class ExpDatagen(Scale2.ExpDatagen):
        prog_suffixes = [
            '_inc',
            '_dem',
            '_java_nocache',
            '_java_cache',
        ]
        
        points = [1000] + list(range(10000, 100000 + 1, 10000))
    
    stddev_window = .1
    min_repeats = 10
    max_repeats = 10
    
    class ExpExtractor(Scale2.ExpExtractor):
        xmin = 0
        xmax = 105
        x_ticklocs = [0, 20, 40, 60, 80, 100]

class Scale3(Scale):
    
    """JQL with caching experiences apparent linear growth from
    x = 5k to about 45k, but then a sudden discontinuity at 50k
    where it jumps four-fold. JQL without caching jumps even
    higher.
    """
    
    prefix = 'results/jql_scale_3'
    
    class ExpDatagen(Scale.ExpDatagen):
        level = '3'
        
        # Don't run orig, which takes forever even before
        # reaching the 100 step timeout checkpoint.
        prog_suffixes = [
            '_inc',
            '_dem',
            '_java_nocache',
            '_java_cache',
        ]
    
    class ExpExtractor(Scale.ExpExtractor):
        
        level = '3'
        jqlcache_format = 'poly2'
        jqlnocache_format = 'poly2'
        
        multipliers = {
            'jql_3_inc':  1e1,
            'jql_3_dem':  1e1,
#            'jql_3_java_nocache':  1e-2,
#            'jql_3_java_cache':    1e-2,
        }
        
        @property
        def series(self):
            s = super().series
            new_s = []
            for sid, name, color, style in s:
                mult = self.multipliers.get(sid, None)
                if mult is not None:
                    op = ' $\\times$ ' if mult >= 1 else ' / '
                    if mult < 1:
                        mult = 1 / mult
                    if round(mult, 3) == round(mult):
                        mult = round(mult)
                    else:
                        mult = round(mult, 3)
                    name += op + str(mult)
                new_s.append((sid, name, color, style))
            return new_s
        
        def project_y(self, p):
            y = super().project_y(p)
            if p['prog'] in self.multipliers:
                return y * self.multipliers[p['prog']]
            else:
                return y

class Scale3Bigger(Scale3):
    
    prefix = 'results/jql_scale_3_bigger'
    
    class ExpDatagen(Scale3.ExpDatagen):
        prog_suffixes = [
            '_inc',
            '_dem',
            '_java_nocache',
            '_java_cache',
        ]
        
        points = [1000] + list(range(5000, 30000 + 1, 5000))
    
    stddev_window = .1
    min_repeats = 5
    max_repeats = 5
    
    class ExpExtractor(Scale3.ExpExtractor):
        xmin = 0
        xmax = 31
        x_ticklocs = [0, 5, 10, 15, 20, 25, 30]
