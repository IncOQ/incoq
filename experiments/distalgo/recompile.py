"""Recompile Distalgo programs."""

import sys
import shutil
from multiprocessing import Process

import da


def compile(dafile, incfile_from, incfile_to):
    sys.argv = [
        sys.argv[0],
        '-i', '--jb-style',
        '--no-table3', '--no-table4'
    ]
    sys.argv.append(dafile)
    
    # Use a separate subprocess because the compiler doesn't
    # like being called multiple times from the same process.
    p = Process(target=da.compiler.main)
    p.start()
    p.join()
    
    shutil.move(incfile_from, incfile_to)

def task(path):
    compile('{}.da'.format(path),
            '{}_inc.py'.format(path),
            '{}_inc_in.py'.format(path))


if __name__ == '__main__':
    pass
#    task('clpaxos/clpaxos')
#    task('crleader/crleader')
#    task('dscrash/dscrash')
#    task('hsleader/hsleader')
#    task('lamutex/lamutex')
#    task('lamutex/lamutex_opt')
#    task('lamutex/lamutex_opt2')
#    task('lamutex/lamutex_orig')
#    task('lapaxos/lapaxos')
#    task('ramutex/ramutex')
#    task('ratoken/ratoken')
#    task('sktoken/sktoken')
#    task('tpcommit/tpcommit')
#    task('vrpaxos/vrpaxos')
#    task('vrpaxos/orig_majority_top')
