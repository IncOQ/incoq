"""Run distalgo experiments."""


import pickle
import os

from frexp import (ExpWorkflow, Datagen,
                   Extractor)

from .distalgo_bridge import get_config, launch

from experiments.util import SmallExtractor, LargeExtractor


class DistalgoDatagen(Datagen):
    
    """Stub datagen. Args for P depends on distalgo program."""
    
    def generate(self, P):
        return dict(
            dsparams = P,
        )

class DistalgoDriver:
    
    argnames = None
    
    def __init__(self, pipe_filename):
        with open(pipe_filename, 'rb') as pf:
            dataset, prog, other_tparams = pickle.load(pf)
        os.remove(pipe_filename)
        
        self.prog = prog
        self.module = None
        
        dafile = other_tparams.get('dafile', self.dafilename)
        
        P = dataset['dsparams']
        args = [str(P[key]) for key in self.argnames]
        
        config = get_config()
        res = launch(config, dafile,
                     prog, args)
        
        self.results = {}
        self.results['time_cpu'] = res['Total process time']
        self.results['time_wall'] = res['Wall time']
        self.results['stdmetric'] = self.results['time_cpu']
        
        with open(pipe_filename, 'wb') as pf:
            pickle.dump(self.results, pf)

class DistalgoWorkflow(ExpWorkflow):
    
    require_ac = False
    
    class ExpDatagen(DistalgoDatagen):
        
        use_progs_ex = False
        """If True, the implementations to run are specified using
        progs_ex instead of progs. progs_ex is a list of pairs of
        a dafile name and an inc interface file name.
        """
        
        def get_tparams_list(self, dsparams_list):
            if not self.use_progs_ex:
                return super().get_tparams_list(dsparams_list)
            
            return [
                dict(
                    tid = dsp['dsid'],
                    dsid = dsp['dsid'],
                    prog = prog,
                    dafile = dafile,
                )
                for dafile, prog in self.progs_ex
                for dsp in dsparams_list
            ]
    
    stddev_window = .1
    min_repeats = 1
    max_repeats = 1
    
    class ExpExtractor(SmallExtractor, Extractor):
        
        name = None
        noninline = False
        
        show_cpu = True
        show_wall = False
        
        # Doesn't work since we have multiple metrics to output.
        generate_csv = False
        
        series_template = [
            (('in', 'time_cpu'), 'original (total cpu time)',
             'red', '- s normal'),
            (('in', 'time_wall'), 'original (wall time)',
             'red', '1-2 _s normal'),
            (('inc', 'time_cpu'), 'incremental (total cpu time)',
             'blue', '- ^ normal'),
            (('inc', 'time_wall'), 'incremental (wall time)',
             'blue', '1-2 _^ normal'),
            (('inc_lru', 'time_cpu'), 'incremental (total cpu time)',
             'blue', '- ^ normal'),
            (('inc_lru', 'time_wall'), 'incremental (wall time)',
             'blue', '1-2 _^ normal'),
            (('dem', 'time_cpu'), 'filtered (total cpu time)',
             'green', '- ^ normal'),
            (('dem', 'time_wall'), 'filtered (wall time)',
             'green', '1-2 _^ normal'),
            
            (('dem_subdem', 'time_cpu'), 'filtered, subdem (total cpu time)',
             '#004400', '- ^ normal'),
            (('dem_subdem', 'time_wall'), 'filtered, subdem (wall time)',
             '#004400', '1-2 _^ normal'),
            
            (('opt in', 'time_cpu'), 'opt. original (total cpu time)',
             '#FFAAAA', '- s normal'),
            (('opt in', 'time_wall'), 'opt. original (wall time)',
             '#FFAAAA', '1-2 _s normal'),
            (('opt dem', 'time_cpu'), 'opt. filtered (total cpu time)',
             'lightgreen', '- ^ normal'),
            (('opt dem', 'time_wall'), 'opt. filtered (wall time)',
             'lightgreen', '1-2 _^ normal'),
        ]
        
        @property
        def series(self):
            series = list(self.series_template)
            for i, s in enumerate(series):
                (prog, metric), label, color, format = s
                if ((metric == 'time_cpu' and not self.show_cpu) or
                    (metric == 'time_wall' and not self.show_wall)):
                    continue
                
                if prog == 'dem':
                    new_prog = '{}_inc_dem{}'.format(
                        self.name,
                        '_noninline' if self.noninline else '')
                elif prog.startswith('opt '):
                    new_prog = self.name + '_opt_inc_' + prog[4:]
                else:
                    new_prog = self.name + '_inc_' + prog
                series[i] = (new_prog, metric), label, color, format
            return series
        
        # Hack it so we can project based on different metrics for
        # different sids. The proper refactoring would be to pass
        # sid to project_y() and the other functions that call it.
        
        def get_series_data(self, datapoints, sid):
            prog, metric = sid
            data = [p for p in datapoints if p['prog'] == prog]
            # Hack on a metric flag.
            for p in data:
                p['metric'] = metric
            return data
        
        def project_y(self, p):
            return p['results'][p['metric']]


class CLPaxosDriver(DistalgoDriver):
        dafilename = 'clpaxos/clpaxos.da'
        argnames = ['n_prop', 'n_acc', 'n_rounds', 'timeout']

class CLPaxos(DistalgoWorkflow):
    
    prefix = 'results/clpaxos'
    
    ExpDriver = CLPaxosDriver
    
    class ExpDatagen(DistalgoWorkflow.ExpDatagen):
        
        progs = [
            'clpaxos_inc_in',
            'clpaxos_inc_inc',
#            'clpaxos_inc_dem',
        ]
        
        def get_dsparams_list(self):
            return [
                dict(
                    dsid =     str(x),
                    x =        x,
                    
                    n_prop =   x * 3,
                    n_acc =    x * 1,
                    n_rounds = 1,
                    timeout =  3,
                )
                for x in range(1, 6 + 1, 1)
            ]
    
    class ExpExtractor(DistalgoWorkflow.ExpExtractor):
        
        name = 'clpaxos'
        noninline = True
        show_wall = True
        
        ylabel = 'Running time (in seconds)'
        xlabel = 'Number of processes'


class CRLeaderDriver(DistalgoDriver):
        dafilename = 'crleader/crleader.da'
        argnames = ['n_procs']

class CRLeader(DistalgoWorkflow):
    
    prefix = 'results/crleader'
    
    ExpDriver = CRLeaderDriver
    
    class ExpDatagen(DistalgoWorkflow.ExpDatagen):
        
        progs = [
            'crleader_inc_in',
            'crleader_inc_dem',
        ]
        
        def get_dsparams_list(self):
            return [
                dict(
                    dsid =     str(x),
                    x =        x,
                    
                    n_procs =  x,
                )
                for x in range(10, 80 + 1, 10)
            ]
    
#    min_repeats = 5
#    max_repeats = 5
    
    class ExpExtractor(DistalgoWorkflow.ExpExtractor):
        
        name = 'crleader'
        
        show_wall = True
        
        ylabel = 'Running time (in seconds)'
        xlabel = 'Number of processes'


class DSCrashDriver(DistalgoDriver):
        dafilename = 'dscrash/dscrash.da'
        argnames = ['n_procs', 'maxfail']

class DSCrash(DistalgoWorkflow):
    
    prefix = 'results/dscrash'
    
    ExpDriver = DSCrashDriver
    
    class ExpDatagen(DistalgoWorkflow.ExpDatagen):
        
        progs = [
            'dscrash_inc_in',
            'dscrash_inc_dem',
        ]
        
        def get_dsparams_list(self):
            return [
                dict(
                    dsid =     str(x),
                    x =        x,
                    
                    n_procs =  x,
                    maxfail =  2,#int(0.25 * x),
                )
                for x in range(5, 100 + 1, 5)
            ]
    
    class ExpExtractor(DistalgoWorkflow.ExpExtractor):
        
        name = 'dscrash'
        
        ylabel = 'Running time (in seconds)'
        xlabel = 'Number of processes'


class HSLeaderDriver(DistalgoDriver):
        dafilename = 'hsleader/hsleader.da'
        argnames = ['n_procs']

class HSLeader(DistalgoWorkflow):
    
    prefix = 'results/hsleader'
    
    ExpDriver = HSLeaderDriver
    
    class ExpDatagen(DistalgoWorkflow.ExpDatagen):
        
        progs = [
            'hsleader_inc_in',
            'hsleader_inc_inc',
#            'hsleader_inc_dem',
        ]
        
        def get_dsparams_list(self):
            return [
                dict(
                    dsid =     str(x),
                    x =        x,
                    
                    n_procs =  x,
                )
                for x in range(10, 100 + 1, 10)
            ]
    
#    min_repeats = 5
#    max_repeats = 5
    
    class ExpExtractor(DistalgoWorkflow.ExpExtractor):
        
        name = 'hsleader'
        
        ylabel = 'Running time (in seconds)'
        xlabel = 'Number of processes'


class LAMutexDriver(DistalgoDriver):
    dafilename = 'lamutex/lamutex.da'
    argnames = ['n_procs', 'n_rounds']

class LAMutexSpecWorkflow(DistalgoWorkflow):
    
    ExpDriver = LAMutexDriver
    
    class ExpDatagen(DistalgoWorkflow.ExpDatagen):
        
        use_progs_ex = True
        progs_ex = [
            ('lamutex/lamutex.da', 'lamutex_inc_in'),
            ('lamutex/lamutex.da', 'lamutex_inc_inc'),
        ]
    
    class ExpExtractor(DistalgoWorkflow.ExpExtractor):
        name = 'lamutex'
        show_wall = True
    
    min_repeats = 5
    max_repeats = 5

class LAMutexSpecOptWorkflow(DistalgoWorkflow):
    
    ExpDriver = LAMutexDriver
    
    class ExpDatagen(DistalgoWorkflow.ExpDatagen):
        
        use_progs_ex = True
        progs_ex = [
#            ('lamutex/lamutex_opt1.da', 'lamutex_opt1_inc_in'),
#            ('lamutex/lamutex_opt1.da', 'lamutex_opt1_inc_inc'),
            
            ('lamutex/lamutex_opt2.da', 'lamutex_opt2_inc_in'),
            ('lamutex/lamutex_opt2.da', 'lamutex_opt2_inc_inc'),
        ]
    
    class ExpExtractor(DistalgoWorkflow.ExpExtractor):
        name = 'lamutex_opt2'
        show_wall = True
    
    min_repeats = 5
    max_repeats = 5

class LAMutexOrigWorkflow(DistalgoWorkflow):
    
    ExpDriver = LAMutexDriver
    
    class ExpDatagen(DistalgoWorkflow.ExpDatagen):
        
        use_progs_ex = True
        progs_ex = [
            ('lamutex/lamutex_orig.da', 'lamutex_orig_inc_in'),
            ('lamutex/lamutex_orig.da', 'lamutex_orig_inc_inc'),
        ]
    
    class ExpExtractor(DistalgoWorkflow.ExpExtractor):
        name = 'lamutex_orig'
        show_wall = True
    
    min_repeats = 5
    max_repeats = 5

class LAMutexSpecProcs(LAMutexSpecWorkflow):
    
    prefix = 'results/lamutexspec_procs'
    
    class ExpDatagen(LAMutexSpecWorkflow.ExpDatagen):
        
        def get_dsparams_list(self):
            return [
                dict(
                    dsid =     str(x),
                    x =        x,
                    
                    n_procs =  x,
                    n_rounds = 10,
                )
                for x in range(3, 30 + 1, 3)
            ]
    
    class ExpExtractor(LAMutexSpecWorkflow.ExpExtractor):
        ylabel = 'Running time (in seconds)'
        xlabel = 'Number of processes'  
        xmin = 1
        xmax = 31

class LAMutexSpecRounds(LAMutexSpecWorkflow):
    
    prefix = 'results/lamutexspec_rounds'
    
    class ExpDatagen(LAMutexSpecWorkflow.ExpDatagen):
        def get_dsparams_list(self):
            return [
                dict(
                    dsid =     str(x),
                    x =        x,
                    
                    n_procs =  10,
                    n_rounds = x,
                )
                for x in range(3, 30 + 1, 3)
            ]
    
    class ExpExtractor(LAMutexSpecWorkflow.ExpExtractor):
        ylabel = 'Running time (in seconds)'
        xlabel = 'Number of rounds'
        xmin = 1
        xmax = 31

class LAMutexSpecOptProcs(LAMutexSpecOptWorkflow):
    
    prefix = 'results/lamutexspecopt_procs'
    
    class ExpDatagen(LAMutexSpecOptWorkflow.ExpDatagen):
        
        def get_dsparams_list(self):
            return [
                dict(
                    dsid =     str(x),
                    x =        x,
                    
                    n_procs =  x,
                    n_rounds = 10,
                )
                for x in range(3, 30 + 1, 3)
            ]
    
    class ExpExtractor(LAMutexSpecOptWorkflow.ExpExtractor):
        ylabel = 'Running time (in seconds)'
        xlabel = 'Number of processes'
        xmin = 1
        xmax = 31

class LAMutexSpecOptRounds(LAMutexSpecOptWorkflow):
    
    prefix = 'results/lamutexspecopt_rounds'
    
    class ExpDatagen(LAMutexSpecOptWorkflow.ExpDatagen):
        def get_dsparams_list(self):
            return [
                dict(
                    dsid =     str(x),
                    x =        x,
                    
                    n_procs =  10,
                    n_rounds = x,
                )
                for x in range(3, 30 + 1, 3)
            ]
    
    class ExpExtractor(LAMutexSpecOptWorkflow.ExpExtractor):
        ylabel = 'Running time (in seconds)'
        xlabel = 'Number of rounds'
        xmin = 1
        xmax = 31

class LAMutexOrigProcs(LAMutexOrigWorkflow):
    
    prefix = 'results/lamutexorig_procs'
    
    class ExpDatagen(LAMutexOrigWorkflow.ExpDatagen):
        
        def get_dsparams_list(self):
            return [
                dict(
                    dsid =     str(x),
                    x =        x,
                    
                    n_procs =  x,
                    n_rounds = 5,
                )
                for x in range(5, 50 + 1, 5)
            ]
    
    class ExpExtractor(LAMutexOrigWorkflow.ExpExtractor):
        ylabel = 'Running time (in seconds)'
        xlabel = 'Number of processes'
        xmin = 5
        xmax = 55

class LAMutexOrigRounds(LAMutexOrigWorkflow):
    
    prefix = 'results/lamutexorig_rounds'
    
    class ExpDatagen(LAMutexOrigWorkflow.ExpDatagen):
        
        def get_dsparams_list(self):
            return [
                dict(
                    dsid =     str(x),
                    x =        x,
                    
                    n_procs =  5,
                    n_rounds = x,
                )
                for x in range(100, 1000 + 1, 100)
            ]
    
    class ExpExtractor(LAMutexOrigWorkflow.ExpExtractor):
        ylabel = 'Running time (in seconds)'
        xlabel = 'Number of rounds'
        xmin = 50
        xmax = 1050


class LAPaxosDriver(DistalgoDriver):
        dafilename = 'lapaxos/lapaxos.da'
        argnames = ['n_prop', 'n_acc', 'n_rounds']

class LAPaxos(DistalgoWorkflow):
    
    prefix = 'results/lapaxos'
    
    ExpDriver = LAPaxosDriver
    
    class ExpDatagen(DistalgoWorkflow.ExpDatagen):
        
        progs = [
            'lapaxos_inc_in',
#            'lapaxos_inc_inc',
#            'lapaxos_inc_dem',
        ]
        
        def get_dsparams_list(self):
            return [
                dict(
                    dsid =     str(x),
                    x =        x,
                    
                    n_prop =   x,
                    n_acc =    x * 3,
                    n_rounds = 3,
                )
                for x in [1]#[1, 3, 6, 9, 12]
            ]
    
    class ExpExtractor(DistalgoWorkflow.ExpExtractor):
        
        name = 'lapaxos'
        noninline = True
        
        ylabel = 'Running time (in seconds)'
        xlabel = 'Number of processes'


class RAMutexDriver(DistalgoDriver):
        dafilename = 'ramutex/ramutex.da'
        argnames = ['n_procs', 'n_rounds']

class RAMutex(DistalgoWorkflow):
    
    prefix = 'results/ramutex'
    
    ExpDriver = RAMutexDriver
    
    class ExpDatagen(DistalgoWorkflow.ExpDatagen):
        
        progs = [
            'ramutex_inc_in',
            'ramutex_inc_inc',
            'ramutex_inc_dem',
        ]
        
        def get_dsparams_list(self):
            return [
                dict(
                    dsid =     str(x),
                    x =        x,
                    
                    n_procs =  x,
                    n_rounds = 10,
                )
                for x in range(2, 20 + 1, 2)
            ]
    
#    min_repeats = 5
#    max_repeats = 5
    
    class ExpExtractor(DistalgoWorkflow.ExpExtractor):
        
        name = 'ramutex'
        
        ylabel = 'Running time (in seconds)'
        xlabel = 'Number of processes'


class RATokenDriver(DistalgoDriver):
        dafilename = 'ratoken/ratoken.da'
        argnames = ['n_procs', 'n_rounds']

class RATokenProcs(DistalgoWorkflow):
    
    prefix = 'results/ratoken'
    
    ExpDriver = RATokenDriver
    
    class ExpDatagen(DistalgoWorkflow.ExpDatagen):
        
        progs = [
            'ratoken_inc_in',
            'ratoken_inc_dem',
        ]
        
        def get_dsparams_list(self):
            return [
                dict(
                    dsid =     str(x),
                    x =        x,
                    
                    n_procs =  x,
                    n_rounds = 10,
                )
                for x in range(10, 70 + 1, 10)
            ]
    
#    min_repeats = 3
#    max_repeats = 3
    
    class ExpExtractor(DistalgoWorkflow.ExpExtractor):
        
        name = 'ratoken'
        
        ylabel = 'Running time (in seconds)'
        xlabel = 'Number of processes'

class RATokenRounds(DistalgoWorkflow):
    
    prefix = 'results/ratoken_rounds'
    
    ExpDriver = RATokenDriver
    
    class ExpDatagen(DistalgoWorkflow.ExpDatagen):
        
        progs = [
#            'ratoken_inc_in',
            'ratoken_inc_dem',
        ]
        
        def get_dsparams_list(self):
            return [
                dict(
                    dsid =     str(x),
                    x =        x,
                    
                    n_procs =  20,
                    n_rounds = x,
                )
                for x in range(10, 100 + 1, 10)
            ]
    
#    min_repeats = 3
#    max_repeats = 3
    
    class ExpExtractor(DistalgoWorkflow.ExpExtractor):
        
        name = 'ratoken'
        
        ylabel = 'Running time (in seconds)'
        xlabel = 'Number of rounds'


class SKTokenDriver(DistalgoDriver):
        dafilename = 'sktoken/sktoken.da'
        argnames = ['n_procs', 'n_rounds']

class SKToken(DistalgoWorkflow):
    
    prefix = 'results/sktoken'
    
    ExpDriver = SKTokenDriver
    
    class ExpDatagen(DistalgoWorkflow.ExpDatagen):
        
        progs = [
            'sktoken_inc_in',
            'sktoken_inc_dem',
        ]
        
        def get_dsparams_list(self):
            return [
                dict(
                    dsid =     str(x),
                    x =        x,
                    
                    n_procs =  x,
                    n_rounds = 10,
                )
                for x in range(5, 40 + 1, 5)
            ]
    
    min_repeats = 3
    max_repeats = 3
    
    class ExpExtractor(DistalgoWorkflow.ExpExtractor):
        
        name = 'sktoken'
        
        ylabel = 'Running time (in seconds)'
        xlabel = 'Number of processes'


class TPCommitDriver(DistalgoDriver):
        dafilename = 'tpcommit/tpcommit.da'
        argnames = ['n_procs', 'failrate']

class TPCommit(DistalgoWorkflow):
    
    prefix = 'results/twophasecommit'
    
    ExpDriver = TPCommitDriver
    
    class ExpDatagen(DistalgoWorkflow.ExpDatagen):
        
        progs = [
            'tpcommit_inc_in',
            'tpcommit_inc_inc',
#            'tpcommit_inc_dem',
        ]
        
        def get_dsparams_list(self):
            return [
                dict(
                    dsid =     str(x),
                    x =        x,
                    
                    n_procs =  x,
                    failrate = 10,
                )
                for x in range(10, 60 + 1, 10)
            ]
    
    min_repeats = 5
    max_repeats = 5
    
    class ExpExtractor(DistalgoWorkflow.ExpExtractor):
        
        name = 'tpcommit'
        
        ylabel = 'Running time (in seconds)'
        xlabel = 'Number of proposers'


class VRPaxosDriver(DistalgoDriver):
        dafilename = 'vrpaxos/vrpaxos.da'
        argnames = []

class VRPaxos(DistalgoWorkflow):
    
    prefix = 'results/vrpaxos'
    
    ExpDriver = VRPaxosDriver
    
    class ExpDatagen(DistalgoWorkflow.ExpDatagen):
        
        progs = [
            'vrpaxos_inc_in',
            'vrpaxos_inc_dem',
        ]
        
        def get_dsparams_list(self):
            return [
                dict(
                    dsid =     str(x),
                    x =        x,
                )
                for x in [1]
            ]
    
    class ExpExtractor(DistalgoWorkflow.ExpExtractor):
        
        name = 'vrpaxos'
        
        ylabel = 'Running time (in seconds)'
        xlabel = 'Number of processes'
