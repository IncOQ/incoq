"""Recompile Distalgo programs."""

import sys
import shutil

import da


def compile(dafile, incfile_from, incfile_to):
    sys.argv.append('-i')
    sys.argv.append('--jb-style')
    sys.argv.append('--no-table3')
    sys.argv.append('--no-table4')
    sys.argv.append(dafile)
    
    da.compiler.main()
    
    shutil.move(incfile_from, incfile_to)


# Uncomment at most one at a time.

#compile('clpaxos/clpaxos.da',
#        'clpaxos/clpaxos_inc.py',
#        'clpaxos/clpaxos_inc_in.py')

#compile('crleader/crleader.da',
#        'crleader/crleader_inc.py',
#        'crleader/crleader_inc_in.py')

#compile('dscrash/dscrash.da',
#        'dscrash/dscrash_inc.py',
#        'dscrash/dscrash_inc_in.py')

#compile('hsleader/hsleader.da',
#        'hsleader/hsleader_inc.py',
#        'hsleader/hsleader_inc_in.py')

#compile('lamutex/lamutex.da',
#        'lamutex/lamutex_inc.py',
#        'lamutex/lamutex_inc_in.py')

#compile('lamutex/lamutex_opt.da',
#        'lamutex/lamutex_opt_inc.py',
#        'lamutex/lamutex_opt_inc_in.py')

#compile('lamutex/lamutex_opt2.da',
#        'lamutex/lamutex_opt2_inc.py',
#        'lamutex/lamutex_opt2_inc_in.py')

#compile('lamutex/lamutex_orig.da',
#        'lamutex/lamutex_orig_inc.py',
#        'lamutex/lamutex_orig_inc_in.py')

#compile('lapaxos/lapaxos.da',
#        'lapaxos/lapaxos_inc.py',
#        'lapaxos/lapaxos_inc_in.py')

#compile('ramutex/ramutex.da',
#        'ramutex/ramutex_inc.py',
#        'ramutex/ramutex_inc_in.py')

#compile('ratoken/ratoken.da',
#        'ratoken/ratoken_inc.py',
#        'ratoken/ratoken_inc_in.py')

#compile('sktoken/sktoken.da',
#        'sktoken/sktoken_inc.py',
#        'sktoken/sktoken_inc_in.py')

#compile('tpcommit/tpcommit.da',
#        'tpcommit/tpcommit_inc.py',
#        'tpcommit/tpcommit_inc_in.py')

# Doesn't work until witnesses are supported.
#compile('vrpaxos/vrpaxos.da',
#        'vrpaxos/vrpaxos_inc.py',
#        'vrpaxos/vrpaxos_inc_in.py')

#compile('vrpaxos/orig_majority_top.da',
#        'vrpaxos/orig_majority_top_inc.py',
#        'vrpaxos/orig_majority_top_inc_in.py')
