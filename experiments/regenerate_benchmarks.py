"""Regenerate whole-program tests."""


__all__ = [
    'regenerate_test',
]


import sys
import argparse
from os import chdir
from os.path import dirname, normpath

from incoq.mars.symbol.config import get_argparser, extract_options
from incoq.mars.symbol import S
from incoq.mars import __main__ as main


# Input file, output file, dictionary of config options.
tasks = [
    ('twitter/twitter_in', 'twitter/twitter_inc',
     {'default_impl': S.Inc}),
    ('twitter/twitter_in', 'twitter/twitter_dem',
     {'default_impl': S.Filtered}),
]

tasks_by_target = {t[1]: t for t in tasks}


root_path = normpath(dirname(__file__))


def compile_task(task, *, options=None):
    """Run a benchmark compilation task. Assume the root path is the
    current directory.
    """
    in_name, out_name, task_opts = task
    in_file = in_name + '.py'
    out_file = out_name + '.py'
    
    opts = options.copy()
    opts.update(task_opts)
    
    print('Regenerating {}...'.format(out_name), flush=True)
    main.invoke(in_file, out_file, options=opts)


def compile_task_names(target_names, *, options=None):
    """Run the tasks with the given target names."""
    chdir(root_path)
    ts = []
    for name in target_names:
        if name not in tasks_by_target:
            raise ValueError('Unknown task target "{}"'.format(name))
        t = tasks_by_target[name]
        ts.append(t)
    
    for t in ts:
        compile_task(t, options=options)


def run(args):
    parent = get_argparser()
    parser = argparse.ArgumentParser(prog='incoq.experiments.'
                                          'mars.regenerate_benchmarks',
                                     parents=[parent])
    parser.add_argument('target_name', nargs='*', default=None)
    
    ns = parser.parse_args(args)
    
    options = extract_options(ns)
    
    if len(ns.target_name) == 0:
        print('No targets specified')
    else:
        compile_task_names(ns.target_name, options=options)


if __name__ == '__main__':
    run(sys.argv[1:])
