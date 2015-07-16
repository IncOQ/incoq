"""Wrapper for launching DistAlgo programs.

This module provides a launch() function that invokes the interpreter
on this module in a subprocess. The __main__ routine in turn calls
the DistAlgo entry point.
"""


import os
import json
import subprocess
import re
import configparser
from os.path import join
from types import SimpleNamespace


class DistAlgoError(subprocess.CalledProcessError):
    
    def __str__(self):
        return ('Command {} returned non-zero exit status {}\n'
                'stderr output:\n{}'.format(
                self.cmd, self.returncode, self.output))


def get_config():
    """Read config.txt to determine appropriate environment variables
    and paths.
    """
    config = configparser.ConfigParser()
    dirname = os.path.dirname(__file__)
    config.read(join(dirname, '../config.txt'))
    pyconf = config['python']
    
    ns = SimpleNamespace()
    
    ns.python34 = pyconf['python34']
    ns.incoq_root = pyconf['INCOQ_ROOT']
    ns.distalgo_path = pyconf['DISTALGO_PATH']
    
    da_exp_dir = os.path.join(ns.incoq_root, 'experiments/distalgo')
    ns.pythonpath = (ns.incoq_root + ';' + ns.distalgo_path + ';' +
                     da_exp_dir)
    
    return ns


def parse_output(s):
    """Parse a string of standard output text for the "OUTPUT: <JSON>"
    line and return the parsed JSON object.
    """
    m = re.search(r'^###OUTPUT: (.*)', s, re.MULTILINE)
    if m is None:
        return None
    return json.loads(m.group(1))


def launch(config, dafile, incfile, daargs):
    """Launch the specified DistAlgo program in a subprocess that
    captures/parses standard output and error. Return a JSON object
    obtained by parsing stdout for a line "OUTPUT: <JSON>", where
    <JSON> is JSON-encoded data.
    """
    python = config.python34
    dirname = os.path.dirname(__file__)
    
    env = dict(os.environ.items())
    # Don't let python33's standard library paths override
    # python 34's.
    env['PYTHONPATH'] = config.pythonpath
    
    args = [
        python,
        __file__,
        '-i',
        '-m',
        incfile,
        dafile,
    ]
    args.extend(daargs)
    
    child = subprocess.Popen(
        args, bufsize=-1,
        # To debug, comment out this line to make stdout/stderr
        # the same standard out and error streams as the parent.
        # Alternatively (if the process terminates), uncomment
        # the print statements below.
        # In the future, maybe use something like
        #   http://stackoverflow.com/questions/375427/non-blocking-read-on-a-subprocess-pipe-in-python
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        cwd=dirname,
        env=env,
        universal_newlines=True)
    
    stdout, stderr = child.communicate()
    results = parse_output(stdout)
#    print(stderr)
#    print(stdout)
    
    if child.returncode != 0:
        raise DistAlgoError(child.returncode, args, stderr)
    
    return results


if __name__ == '__main__':
    import da
    da.libmain()
