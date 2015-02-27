"""Recompile Distalgo programs."""

import sys
import os
from os.path import dirname, join
from multiprocessing import Process
from configparser import ConfigParser
from shutil import copy

import da


def get_benchmark_path():
    """Return the path to the distalgo benchmarks directory."""
    config = ConfigParser()
    mydir = dirname(__file__)
    config.read(join(mydir, '../config.txt'))
    dapath = config['python']['DISTALGO_PATH']
    return join(dapath, 'benchmarks')


def compile(dafile, pyfile, incfile):
    """Compile the input dafile to two output files: the main module
    pyfile and the incrementalization interface incfile.
    """
    sys.argv = [
        sys.argv[0],
        '-o', pyfile,
        '-i', '-m', incfile,
        '--jb-style',
        '--no-table3', '--no-table4',
        dafile
    ]
    
    # Use a separate subprocess because the distalgo compiler
    # doesn't like being called multiple times from the same
    # process.
    p = Process(target=da.compiler.main)
    p.start()
    p.join()

def do_tasks(tasks):
    """Perform several compilation steps. For each task, copy over
    the .da file from the distalgo benchmarks directory to the local
    directory, and do the compilation. Also copy the controller.da
    file to the local directory.
    
    Each task is a pair of the input filename minus the .da suffix,
    relative to the distalgo benchmarks directory; and the output
    file prefix minus the .py or _inc_in.py suffix, relative to the
    local directory.
    """
    mydir = dirname(__file__)
    os.chdir(mydir)
    benchpath = get_benchmark_path()
    
    for inpath, outpath in tasks:
        os.makedirs(dirname(outpath))
        orig_dafile = join(benchpath, '{}.da'.format(inpath))
        copy(orig_dafile, '{}.da'.format(outpath))
        compile('{}.da'.format(outpath),
                '{}.py'.format(outpath),
                '{}_inc_in.py'.format(outpath))
    
    copy(join(benchpath, 'controller.da'), 'controller.da')


tasks = [
#    ('clpaxos/spec', 'clpaxos/clpaxos'),
#    ('crleader/orig', 'crleader/crleader'),
#    ('dscrash/spec', 'dscrash/dscrash'),
#    ('hsleader/spec', 'hsleader/hsleader'),
#    
#    ('lamutex/spec_unopt_relack', 'lamutex/lamutex'),
#    ('lamutex/spec_unopt_ack', 'lamutex/lamutex_opt1'),
#    ('lamutex/spec', 'lamutex/lamutex_opt2'),
#    ('lamutex/orig', 'lamutex/lamutex_orig'),
    
#    ('lapaxos/orig', 'lapaxos/lapaxos'),
#    ('ramutex/spec', 'ramutex/ramutex'),
#    ('ratoken/spec', 'ratoken/ratoken'),
#    ('sktoken/orig', 'sktoken/sktoken'),
#    ('2pcommit/spec', 'tpcommit/tpcommit'),
#    ('vrpaxos/orig', 'vrpaxos/vrpaxos'),
]

if __name__ == '__main__':
    do_tasks(tasks)
