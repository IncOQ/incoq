"""Run the Constrained RBAC experiment."""


from random import sample, shuffle
from itertools import product
import os
import sys
import importlib

from frexp import (ExpWorkflow, Datagen, MetricExtractor,
                   ScaledExtractor, Runner)

from experiments.util import SmallExtractor


class CRBACDatagen(Datagen):
    
    """Create users, roles, and constraints. Alternately grant a
    permission to a user and check the condition.
    
    (Note: The integrity condition will be violated, but we're just
    treating it as a query for this experiment.)
    
    Parameters:
        nU, nR, nC -- number of users, roles, constraints
        sC -- number of roles in each constraint
        limit -- number of allowed roles from each constraint set
                 until condition is considered violated
    """
    
    def generate(self, P):
        nU, nR, nC = P['nU'], P['nR'], P['nC']
        sC = P['sC']
        limit = P['limit']
        
        UR = list(product(range(nU), range(nR)))
        shuffle(UR)
        
        SSDNR = [(i, j) for i in range(nC)
                        for j in sample(range(nR), sC)]
        
        return dict(
            dsparams = P,
            UR = UR,
            SSDNR = SSDNR,
        )


class CRBACDriver:
    
    check_interval = 10
    timeout = 60
    
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
        self.results = {}
        
        self.setUp()
        
        from frexp.util import StopWatch, user_time
        from time import process_time, perf_counter
        timer_user = StopWatch(user_time)
        timer_cpu = StopWatch(process_time)
        timer_wall = StopWatch(perf_counter)
        
        # Make available to run for timeouts.
        self.timer_cpu = timer_cpu
        
        with timer_user, timer_cpu, timer_wall:
            finished = self.run()
        
        if finished:
            import incoq.runtime
            self.results['size'] = incoq.runtime.get_size_for_namespace(
                                    self.module.__dict__)
            self.results['time_user'] = timer_user.consume()
            self.results['time_cpu'] = timer_cpu.consume()
            self.results['time_wall'] = timer_wall.consume()
            
            self.results['stdmetric'] = self.results['time_cpu']
        else:
            self.results['timedout'] = True
        
        
        with open(pipe_filename, 'wb') as pf:
            pickle.dump(self.results, pf)
    
    def setUp(self):
        # Import driven program.
        dirname, filename = os.path.split(self.prog)
        if dirname:
            sys.path.append(dirname)
        try:
            self.module = importlib.import_module(
                    'experiments.rbac.constrainedrbac.' + filename)
        finally:
            if dirname:
                sys.path.pop()
        
        
        m = self.module
        ds = self.dataset
        P = ds['dsparams']
        
        # Initialize dataset.
        for i in range(P['nU']):
            m.add_user('u' + str(i))
        for i in range(P['nC']):
            m.add_ssdnc('c' + str(i), P['limit'])
        for i, j in ds['SSDNR']:
            m.add_ssdnr('c' + str(i), 'r' + str(j))
        m.do_query()
        
        # Preprocess operations.
        self.OPS = []
        for i, j in ds['UR']:
            self.OPS.append(('u' + str(i), 'r' + str(j)))
    
    def run(self):
        add_ur = self.module.add_ur
        do_query = self.module.do_query_nodemand
        
        check_interval = self.check_interval
        timer_cpu = self.timer_cpu
        timeout = self.timeout
        
        for i, (u, r) in enumerate(self.OPS):
            # Check timeout every so often.
            if i % check_interval == 0:
                if timer_cpu.elapsed > timeout:
                    return False
            
            add_ur(u, r)
            do_query()
        
        return True


class CRBACRunner(Runner):
    
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


class CRBACWorkflow(ExpWorkflow):
    
    ExpDatagen = CRBACDatagen
    ExpDriver = CRBACDriver
    ExpRunner = CRBACRunner
#    verifier
    
    require_ac = False ###


class CRBACScale(CRBACWorkflow):
    
    """Scale up the number of users and constraints.
    
    Expectation: Linear for Inc, because for each update, we find a
    constant number of constraints that have the role, increment their
    counts (the inner query), and update the outer query in constant
    time. Cubic for Aux, because of three linear factors: number of
    users and constraints (both from outer query), and number of
    query operations (= # users). 
    """
    
    prefix = 'results/crbac'
    
    class ExpDatagen(CRBACWorkflow.ExpDatagen):
        
        progs = [
            'crbac_orig',
            'crbac_aux',
            'crbac_inc',
#            'crbac_dem',
        ]
        
        def get_dsparams_list(self):
            return [
                dict(
                    dsid = str(x),
                    x =    x,
                    
                    nU =   x,
                    nR =   5,
                    nC =   x,
                    sC =   5,
                    limit = 3,
                )
                for x in list(range(2, 20, 2)) + list(range(20, 100 + 1, 5))
            ]
    
    stddev_window = .1
    min_repeats = 10
    max_repeats = 50
    
    class ExpExtractor(MetricExtractor, SmallExtractor, ScaledExtractor):
        
        series = [
            ('crbac_orig', 'original',
             'red', '- s poly5'),
            ('crbac_aux', 'auxiliary maps',
             'orange', '-- s poly3'),
            ('crbac_inc', 'incremental',
             'blue', '- o poly2'),
#            ('crbac_dem', 'filtered',
#             'green', '- ^ poly2'),
        ]
        
        multipliers = {
#            'crbac_inc': 5,
        }
        
        legend_loc = 'upper center'
        
        ylabel = 'Running time (in seconds)'
        xlabel = 'Number of users and constraints'
        
        metric = 'time_cpu'
        
        ymin = -1
        ymax = 20
        xmin = -5
        xmax = 105
