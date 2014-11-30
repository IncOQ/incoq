###############################################################################
# pyexec.py                                                                   #
# Author: Jon Brandvein                                                       #
###############################################################################

"""Helper for executing a Python script as a subprocess."""


__all__ = [
    'pyexec_file',
    'pyexec_source',
]


import sys
import os.path
import subprocess
from imp import find_module


def get_runtimelib_env():
    """Return an OS environment that allows importing of runtimelib."""
    
    # Get the directory containing the runtimelib package.
    _, path, _ = find_module('runtimelib')
    prefix, _ = os.path.split(path)
    
    # Create a modified environment for the child that includes
    # this directory in PYTHONPATH.
    env = dict(os.environ.items())
    if 'PYTHONPATH' not in env:
        env['PYTHONPATH'] = prefix
    else:
        env['PYTHONPATH'] += ';' + prefix
    
    return env


def pyexec_file(filename):
    """Run a Python program as a subprocess. PYTHONPATH is modified
    to ensure that runtimelib is importable by the child. The output
    is returned as a byte string.
    """
    env = get_runtimelib_env()
    
    output = subprocess.check_output([sys.executable, filename], env=env,
                                     universal_newlines=True)
    
    return output


def pyexec_source(source):
    """As above, but the source code is passed in as an argument
    instead of read from a file.
    """
    env = get_runtimelib_env()
    
    output = subprocess.check_output([sys.executable, '-c', source], env=env,
                                     universal_newlines=True)
    
    return output
