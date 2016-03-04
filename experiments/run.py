"""Run benchmarks."""

import sys
import argparse
import os
import traceback

import experiments.mars.twitter as twitter
import experiments.mars.distalgo as distalgo


tasks = [
    ('twitter_scale_time',              twitter.ScaleTime()),
    ('twitter_scale_size',              twitter.ScaleSize()),
    ('lamutex_spec_unopt_procs',        distalgo.LAMutexSpecProcs()),
]


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
    parser.add_argument('task')
    parser.add_argument('--run', action='store_true')
    parser.add_argument('--view', action='store_true')
    parser.add_argument('--light', action='store_true')
    
    ns = parser.parse_args(args)
    
    for task in tasks:
        t_name, w = task
        if t_name == ns.task:
            break
    else:
        raise ValueError('Unknown task "{}"'.format(ns.task))
    
    if ns.run or ns.view:
        run = ns.run
        view = ns.view
    else:
        run = True
        view = True
    
    run_tasks([w], run=run, view=view, light=ns.light)


if __name__ == '__main__':
    run(sys.argv[1:])
