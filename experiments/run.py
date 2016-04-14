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
#import experiments.mars.distalgo as distalgo


all_tasks = [
    # Twitter.
    ('twitter_scale_time',              twitter.ScaleTime()),
    ('twitter_scale_size',              twitter.ScaleSize()),
    
    ('twitter_demand_time',             twitter.DemandTimeOps()),
    ('twitter_demand_size',             twitter.DemandSize()),
    
    ('twitter_density',                 twitter.DensityLoc()),
    ('twitter_density_norm',            twitter.DensityLocNorm()),
    
    # Wifi.
    ('wifi',                            wifi.Wifi()),
    
    # Django.
    ('django_scale',                    django.Scale()),
    ('django_demand',                   django.DemandTime()),
    ('django_demand_norm',              django.DemandTimeNorm()),
    
    # JQL.
    ('jql_ratio_1',                     jql.Ratio1()),
    ('jql_ratio_2',                     jql.Ratio2()),
    ('jql_ratio_3',                     jql.Ratio3()),
    
    # RBAC.
    ('corerbac_roles',                  rbac.corerbac.CoreRoles()),
    ('corerbac_demand',                 rbac.corerbac.CoreDemand()),
    ('corerbac_demand_norm',            rbac.corerbac.CoreDemandNorm()),
    ('constrainedrbac',                 rbac.constrainedrbac.CRBACScale()),
    
    # Graddb.
    ('newstu_scale',                    newstudents.NewStudentsScale()),
    
#    ('lamutex_spec_unopt_procs',        distalgo.LAMutexSpecProcs()),
]

all_tasks_dict = dict(all_tasks)


def run_tasks(tasks, run=True, view=True, light=False):
    # Change to directory of this file so we can find the
    # results/ subdirectory.
    os.chdir(os.path.join('.', os.path.dirname(__file__)))
    
    for w in tasks:
        if light:
            w.min_repeats = 1
            w.max_repeats = 1
        
        print('\n---- Running {} ----\n'.format(w.__class__.__name__))
        try:
            if run:
                w.generate()
                w.benchmark()
            
#            w.verify()
            
            if view:
                w.extract()
                w.view()
            
#            w.cleanup()
        except Exception:
            traceback.print_exc()
            print('\n^--- Skipping test\n')


def run(args):
    parser = argparse.ArgumentParser(prog='run.py')
    parser.add_argument('tasks', nargs='*')
    parser.add_argument('--run', action='store_true')
    parser.add_argument('--view', action='store_true')
    parser.add_argument('--light', action='store_true')
    
    ns = parser.parse_args(args)
    
    do_tasks = []
    for t_name in ns.tasks:
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
    
    run_tasks(do_tasks, run=run, view=view, light=ns.light)


if __name__ == '__main__':
    run(sys.argv[1:])
