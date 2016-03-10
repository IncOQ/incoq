"""Run the New Students experiment."""


import os, sys, importlib
from copy import deepcopy
from random import choice, randrange

from frexp import (ExpWorkflow, Datagen,
                   MetricExtractor, NormalizedExtractor)

from experiments.util import SmallExtractor, LargeExtractor, canonize


class NewStudentsDatagen(Datagen):
    
    """Generate a number of students, each with the same number of
    programs and a random year. Programs have random start years
    (semesters). The current year is random. All years are in the
    10-year range of 2006 to 2015 inclusive.
    
    Measure the time to perform a number of operations consisting of
    changing a random program's start year and performing the query.
    
    Parameters:
      n_stu -- number of students
      progs_per_stu -- programs per student
      n_ops -- number of query/update pairs
    """
    
    def generate(self, P):
        n_stu = P['n_stu']
        progs_per_stu = P['progs_per_stu']
        n_ops = P['n_ops']
        
        years = list(range(2006, 2015 + 1))
        
        # Generate student start year info.
        stu = [choice(years) for _ in range(n_stu)]
        
        # Generate program info for each student.
        # List whose positions correspond to students, and
        # whose elements are lists of start dates for programs
        # of that student.
        progs = [[] for _ in range(n_stu)]
        for i in range(n_stu):
            for _ in range(progs_per_stu):
                progs[i].append(choice(years))
        
        # Generate update operations.
        # List of triples of student index, program index, and new
        # semester value.
        updates = []
        for _ in range(n_ops):
            updates.append((randrange(n_stu), randrange(progs_per_stu),
                            choice(years)))
        
        return dict(
            dsparams = P,
            stu = stu,
            progs = progs,
            updates = updates,
            current_year = max(years),
        )


class NewStudentsDriver:
    
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
        self.second_query = other_tparams['second_query']
        
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
                    'experiments.graddb.newstudents.' + filename)
        finally:
            if dirname:
                sys.path.pop()
        
        
        m = self.module
        ds = self.dataset
        n_stu = ds['dsparams']['n_stu']
        progs_per_stu = ds['dsparams']['progs_per_stu']
        self.current_year = ds['current_year']
        
        # Populate dataset.
        self.students = []
        for i in range(n_stu):
            s = m.make_student(i, ds['stu'][i])
            self.students.append(s)
        self.progs = [[] for _ in range(n_stu)]
        for i, ys in enumerate(ds['progs']):
            for j, y in enumerate(ys):
                p = m.add_program(self.students[i], y)
                self.progs[i].append(p)
         
        # Preprocess operations.
        self.ops = []
        for i, j, y in ds['updates']:
            self.ops.append((self.progs[i][j],
                             y))
        
        # Compile the query without passing in the real parameters.
        m.init()
        
        # If requested, perform an initial query to prevent it from
        # counting toward the measured time.
        if self.second_query:
            m.do_query(self.current_year)
    
    def run(self):
        # Perform the initial query to add it to the demand set.
        year = self.current_year
        self.module.do_query(year)
        
        change = self.module.change_program_start
        do_query = self.module.do_query_nodemand
        
        for p, y in self.ops:
            change(p, y)
            q = do_query(year)
    
    def tearDown(self):
        pass


class NewStudentsWorkflow(ExpWorkflow):
    
    class ExpDatagen(NewStudentsDatagen):
        
        # Set to [False, True] to also run versions where
        # the first query is done before the timing loop.
        sqs = [False]
        
        def get_tparams_list(self, dsparams_list):
            # Versions with and without second_query,
            # except for the orig one.
            return [
                dict(
                    tid = dsp['dsid'] + '_' + str(sq),
                    dsid = dsp['dsid'],
                    prog = prog,
                    second_query = sq,
                )
                for prog in self.progs
                for dsp in dsparams_list
                for sq in self.sqs
                if not (prog == 'newstu_orig' and sq == True)
            ]
    
    class ExpExtractor(SmallExtractor):
        
        def get_series_data(self, datapoints, sid):
            inner_sid, sq = sid
            datapoints = super().get_series_data(datapoints, inner_sid)
            datapoints = [p for p in datapoints
                            if p['second_query'] == sq]
            return datapoints
    
    ExpDriver = NewStudentsDriver
    
    require_ac = False ###


class NewStudentsScale(NewStudentsWorkflow):
    
    """Vary the number of students, constant number of program updates."""
    
    prefix = 'results/newstudents_scale'
    
    class ExpDatagen(NewStudentsWorkflow.ExpDatagen):
        
        sqs = [False, True]
        
        progs = [
            'newstu_orig',
            'newstu_dem',
            'newstu_osq',
        ]
        
        def get_dsparams_list(self):
            return [
                dict(
                    dsid =          str(x),
                    x =             x,
                    
                    n_stu =         x,
                    progs_per_stu = 3,
                    n_ops =         100,
                )
                for x in range(500, 5000 + 1, 500)
            ]
    
    stddev_window = .1
    min_repeats = 10
    max_repeats = 50
    
    class ExpExtractor(NewStudentsWorkflow.ExpExtractor, MetricExtractor):
        
        _series = [
            (('newstu_orig', False), 'original',
             'red', '- s poly1'),
            (('newstu_osq', False), 'OSQ',
             '#CC8400', '-- o poly1'),
            (('newstu_osq', True), 'OSQ (no init)',
             '#CC8400', ': _o poly1'),
            (('newstu_dem', False), 'IncOQ',
             'green', '- ^ poly1'),
            (('newstu_dem', True), 'IncOQ (no init)',
             'green', ': _^ poly1'),
        ]
        
        multipliers = {
            ('newstu_orig', False): 0.5,
#            ('newstu_orig', False): 0.2,
        }
        
        @property
        def series(self):
            s = self._series
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
            sid = (p['prog'], p['second_query'])
            if sid in self.multipliers:
                return y * self.multipliers[sid]
            else:
                return y
        
        ylabel = 'Running time (in seconds)'
        xlabel = 'Number of students'
        
        metric = 'time_cpu'
        
        xmin = 250
        xmax = 5250
        ymin = -0.025
        ymax = 0.45
