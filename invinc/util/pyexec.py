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
import subprocess


def pyexec_file(filename):
    """Run a Python program as a subprocess. PYTHONPATH is modified
    to ensure that runtimelib is importable by the child. The output
    is returned as a byte string.
    """
    output = subprocess.check_output([sys.executable, filename],
                                     universal_newlines=True)
    
    return output


def pyexec_source(source):
    """As above, but the source code is passed in as an argument
    instead of read from a file.
    """
    output = subprocess.check_output([sys.executable, '-c', source],
                                     universal_newlines=True)
    
    return output
