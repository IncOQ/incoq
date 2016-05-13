"""Run benchmarks."""

import sys
import argparse
import os
import traceback

import experiments.twitter as twitter
import experiments.wifi as wifi
import experiments.django as django
import experiments.jql as jql
import experiments.rbac as rbac
import experiments.graddb.newstudents as newstudents
import experiments.distalgo as distalgo


all_tasks = [
    # Twitter.
    ('twitter_scale_time',              twitter.ScaleTime()),
    ('twitter_scale_size',              twitter.ScaleSize()),
    
    ('twitter_demand_time',             twitter.DemandTimeOps()),
    ('twitter_demand_size',             twitter.DemandSize()),
    ('twitter_demand_demtime',          twitter.DemandTimeDem()),
    ('twitter_demand_tottime',          twitter.DemandTimeTotal()),
    
    ('twitter_density',                 twitter.DensityLoc()),
    ('twitter_density_norm',            twitter.DensityLocNorm()),
    
    ('twitter_tag',                     twitter.TagTime()),
    
    # Wifi.
    ('wifi',                            wifi.Wifi()),
    
    # Django.
    ('django_scale',                    django.Scale()),
    ('django_demand',                   django.DemandTime()),
    ('django_demand_norm',              django.DemandTimeNorm()),
    ('django_demand_norm_nolegend',     django.DemandTimeNormNolegend()),
    
    # JQL.
    ('jql_ratio_1',                     jql.Ratio1()),
    ('jql_ratio_2',                     jql.Ratio2()),
    ('jql_ratio_3',                     jql.Ratio3()),
    ('jql_scale_1',                     jql.Scale1()),
    ('jql_scale_2',                     jql.Scale2()),
    ('jql_scale_3',                     jql.Scale3()),
    
    # RBAC.
    ('corerbac_roles',                  rbac.corerbac.CoreRoles()),
    ('corerbac_demand',                 rbac.corerbac.CoreDemand()),
    ('corerbac_demand_norm',            rbac.corerbac.CoreDemandNorm()),
    ('crbac',                           rbac.constrainedrbac.CRBACScale()),
    
    # Graddb.
    ('newstu_scale',                    newstudents.NewStudentsScale()),
    
    # DistAlgo.
    ('lamutex_orig_procs',              distalgo.LAMutexOrigProcs()),
    ('lamutex_orig_rounds',             distalgo.LAMutexOrigRounds()),
    ('lamutex_spec_procs',              distalgo.LAMutexSpecProcs()),
    ('lamutex_spec_rounds',             distalgo.LAMutexSpecRounds()),
    ('lamutex_spec_lam_procs',          distalgo.LAMutexSpecLamProcs()),
    ('lamutex_spec_lam_rounds',         distalgo.LAMutexSpecLamRounds()),
    
    ('clpaxos',                         distalgo.CLPaxos()),
    ('crleader',                        distalgo.CRLeader()),
    ('dscrash',                         distalgo.DSCrash()),
    ('hsleader',                        distalgo.HSLeader()),
    ('lapaxos',                         distalgo.LAPaxos()),
    ('ramutex',                         distalgo.RAMutex()),
    ('ratoken_procs',                   distalgo.RATokenProcs()),
    ('ratoken_rounds',                  distalgo.RATokenRounds()),
    ('sktoken',                         distalgo.SKToken()),
    ('tpcommit',                        distalgo.TPCommit()),
    ('vrpaxos',                         distalgo.VRPaxos()),
]

all_tasks_dict = dict(all_tasks)


def run_tasks(tasks, run=True, view=True, verify=False,
              light=False, no_generate=False):
    # Change to directory of this file so we can find the
    # results/ subdirectory.
    os.chdir(os.path.join('.', os.path.dirname(__file__)))
    
    for w in tasks:
        if light:
            w.min_repeats = 1
            w.max_repeats = 1
        
        print('\n---- Running {} ----\n'.format(w.__class__.__name__))
        try:
            if verify:
                if not no_generate:
                    w.generate()
                w.verify()
            else:
                if run:
                    if not no_generate:
                        w.generate()
                    w.benchmark()
                if view:
                    w.extract()
                    w.view()
        
        except Exception:
            traceback.print_exc()
            print('\n^--- Skipping test\n')


def run(args):
    parser = argparse.ArgumentParser(prog='run.py')
    parser.add_argument('task', nargs='+')
    parser.add_argument('--run', action='store_true')
    parser.add_argument('--view', action='store_true')
    parser.add_argument('--verify', action='store_true')
    parser.add_argument('--light', action='store_true')
    parser.add_argument('--no-generate', action='store_true')
    
    ns = parser.parse_args(args)
    
    do_tasks = []
    for t_name in ns.task:
        task = all_tasks_dict.get(t_name, None)
        if task is None:
            raise ValueError('Unknown task "{}"'.format(t_name))
        do_tasks.append(task)
    
    if ns.run or ns.view:
        run = ns.run
        view = ns.view
    else:
        run = True
        view = True
    
    run_tasks(do_tasks, run=run, view=view, verify=ns.verify,
              light=ns.light, no_generate=ns.no_generate)


if __name__ == '__main__':
    run(sys.argv[1:])
