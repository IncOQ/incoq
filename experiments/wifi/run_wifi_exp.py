"""Run the wifi experiment."""


import os, sys, importlib
from copy import deepcopy

from frexp import (ExpWorkflow, Datagen, Runner, Verifier,
                   SimpleExtractor, MetricExtractor)

from experiments.util import SmallExtractor, LargeExtractor, canonize


class WifiDatagen(Datagen):
    
    """Procedure as in Tom's dissertation (p74-75). There's just
    one wifi parameter value, and we alternate adding a new ap, and
    performing a query that amounts to listing all aps up to this
    point.
    
    Parameters:
      N -- number of updates and queries
    """
    
    def generate(self, P):
        # Nothing to do, since there's no randomness,
        # or really any generated data to speak of.
        return dict(
            dsparams = P,
        )
    
    progs = [
        'wifi_orig',
        'wifi_dem',
        'wifi_osq',
    ]


class WifiDriver:
    
    def __init__(self, pipe_filename):
        import gc
        import pickle
        
        gc.disable()
        
        with open(pipe_filename, 'rb') as pf:
            dataset, prog, other_tparams = pickle.load(pf)
        os.remove(pipe_filename)
        
        
        self.dataset = dataset
        self.N = dataset['dsparams']['N']
        self.prog = prog
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
        
        import incoq.mars.runtime
        self.results['size'] = incoq.mars.runtime.get_size_for_namespace(
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
                    'experiments.wifi.' + filename)
        finally:
            if dirname:
                sys.path.pop()
        
        
        m = self.module
        
        self.wifi = m.make_wifi(5)
        m.do_query(self.wifi)
    
    def run(self):
        make_ap = self.module.make_ap
        add_ap = self.module.add_ap
        do_query = self.module.do_query_nodemand
        wifi = self.wifi
        
        for i in range(self.N):
            ap = make_ap(str(i), 10)
            add_ap(wifi, ap)
            do_query(wifi)

class WifiVerifyDriver:
    
    def __init__(self, pipe_filename):
        import gc
        import pickle
        
        gc.disable()
        
        with open(pipe_filename, 'rb') as pf:
            dataset, prog, other_tparams = pickle.load(pf)
        os.remove(pipe_filename)
        
        
        self.dataset = dataset
        self.N = dataset['dsparams']['N']
        self.prog = prog
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
                    'experiments.wifi.' + filename)
        finally:
            if dirname:
                sys.path.pop()
        
        
        m = self.module
        
        self.wifi = m.make_wifi(5)
        m.do_query(self.wifi)
    
    def run(self):
        make_ap = self.module.make_ap
        add_ap = self.module.add_ap
        do_query = self.module.do_query_nodemand
        wifi = self.wifi
        
        for i in range(self.N):
            ap = make_ap(str(i), 10)
            add_ap(wifi, ap)
            output = do_query(wifi)
            self.results['output'].append(deepcopy(output))


class Wifi(ExpWorkflow):
    
    prefix = 'results/wifi'
    
    require_ac = False ###
    
    ExpDriver = WifiDriver
    ExpVerifyDriver = WifiVerifyDriver
    
    class ExpDatagen(WifiDatagen):
        
        def get_dsparams_list(self):
            return [
                dict(
                    dsid = str(x),
                    x =    x,
                    N =    x
                )
                for x in range(250, 2501, 250)
            ]
    
    stddev_window = .1
    min_repeats = 20
    max_repeats = 20
    
    class ExpExtractor(MetricExtractor, SmallExtractor):
        
        series = [
            ('wifi_orig', 'original', 'red', '- s poly2'),
            ('wifi_osq', 'OSQ', 'orange', '-- ^ poly1'),
            ('wifi_dem', 'filtered', 'green', '- ^ poly1'),
        ]
        
        ylabel = 'Running time (in seconds)'
        xlabel = 'Number of queries and updates'
        
        metric = 'time_cpu'
        
        xmin = 150
        xmax = 2600
