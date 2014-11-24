###############################################################################
# cleanexpdata.py                                                             #
# Author: Jon Brandvein                                                       #
###############################################################################

"""Delete generated experiment data files."""

expdir = '../experiments'

import os

resdirs = []

for dirpath, dirnames, filenames in os.walk(expdir):
    for name in dirnames:
        if name == 'results':
            resdirs.append(os.path.join(dirpath, name))

expfiles = []
for resdir in resdirs:
    for dirpath, dirnames, filenames in os.walk(resdir):
        for name in filenames:
            if name.endswith('.pickle'):
                expfiles.append(os.path.join(dirpath, name))

for x in expfiles:
    print('Deleting ' + x)
    os.remove(x)

print('Done')
