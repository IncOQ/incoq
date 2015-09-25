"""Set benchmark experiments."""


import os, sys, importlib
from random import shuffle

from frexp import (ExpWorkflow, Datagen, Runner, Verifier,
                   SimpleExtractor, MetricExtractor, Task)

from experiments.util import SmallExtractor, LargeExtractor, canonize


class SetDatagen(Datagen):
    
    """Simple datagen.
    
    Parameters:
      N -- number of elements to add.
    """
    
    def generate(self, P):
        return dict(
            dsparams = P,
        )
    
    progs = [
        'sets_rcset_rcadd',
        'sets_rcset_add',
        'sets_set_add',
        'sets_set_fastadd',
    ]


class SetsDriver:
    
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
                    'experiments.other.setbenchmark.' + filename)
        finally:
            if dirname:
                sys.path.pop()
        
        
        m = self.module
        
        self.set = m.make_set()
        self.nums = list(range(self.N))
        shuffle(self.nums)
    
    def run(self):
        self.module.run(self.set, self.nums)


class Sets(ExpWorkflow):
    
    prefix = 'results/setbenchmark'
    
    require_ac = False ###
    
    ExpDriver = SetsDriver
    
    class ExpDatagen(SetDatagen):
        
        def get_dsparams_list(self):
            return [
                dict(
                    dsid = str(x),
                    x =    x,
                    N =    x
                )
                for x in [1000000]
            ]
    
    stddev_window = .1
    min_repeats = 10
    max_repeats = 50
    
    class ExpExtractor(MetricExtractor, SmallExtractor):
        
        series = [
            ('sets_rcset_rcadd', 'rcset rcadd',
             'red', '- s normal'),
            ('sets_rcset_add', 'rcset add',
             'orange', '-- s normal'),
            ('sets_set_add', 'set add',
             'green', '- ^ normal'),
            ('sets_set_fastadd', 'set fast add',
             'blue', '-- ^ normal'),
        ]
        
        ylabel = 'Running time (in seconds)'
        xlabel = 'Number of elements added (millions)'
        
        metric = 'time_cpu'
        
        def project_x(self, p):
            return super().project_x(p) / 1e6

class SetsTable(Sets):
    
    class ExpViewer(Task):
        
        def run(self):
            import pandas as pd
            
            with open(self.workflow.csv_filename, 'rt') as in_file:
                df = pd.DataFrame.from_csv(in_file)
            
            means = df.mean()
            means = means.apply(lambda x: round(x, 2))
            print(means)
