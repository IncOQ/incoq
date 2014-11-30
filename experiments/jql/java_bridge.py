###############################################################################
# java_bridge.py                                                              #
# Author: Jon Brandvein                                                       #
###############################################################################

"""Bridge between frexp testing framework and a Java program for
running the JQL queries within the actual JQL system.

NOTE: This file is highly dependent on my system-specific paths,
and on my installations of Cygwin, Java, and JQL.

We use a custom test runner. The standard test runner uses the
multiprocessing library to spawn a Python process, and sends the
dataset over in pickled form. Here we use the subprocess library
to spawn Java (actually, the JQL wrapper script), and send the
dataset over in JSON form. Result data comes back as JSON too.
"""


import os
from os.path import join
import subprocess
import json
from types import SimpleNamespace
import configparser


class JavaError(subprocess.CalledProcessError):
    
    def __str__(self):
        return ('Command {} returned non-zero exit status {}\n'
                'stderr output:\n{}'.format(
                self.cmd, self.returncode, self.output))

# CLASSPATH is windows-style, but regular PATH is unix-style since
# it uses cygwin.

def get_config():
    """Read config.txt to determine appropriate environment variables
    and paths.
    """
    config = configparser.ConfigParser()
    dirname = os.path.dirname(__file__)
    config.read(join(dirname, '../config.txt'))
    jqlconf = config['jql']
    
    ns = SimpleNamespace()
    
    ns.bash_cmd = jqlconf['BASH_CMD']
    ns.jql_home = jqlconf['JQL_HOME']
    ns.java_home = jqlconf['JAVA_HOME']
    ns.aspectj_home = jqlconf['ASPECTJ_HOME']
    ns.jsonsimple_jarpath = jqlconf['JSONSIMPLE_JARPATH']
    ns.aspectj_jarpath = jqlconf['ASPECTJ_JARPATH']
    
    ns.working_dir = join(dirname, 'java')
    ns.jql_cmd = join(ns.jql_home, 'bin/jql')
    ns.path = join(ns.java_home, 'bin') + ':/bin'
    ns.cmd = [ns.bash_cmd, ns.jql_cmd, '-notracker', '-caching']
    ns.classpath = ';'.join([ns.jsonsimple_jarpath,
                             ns.aspectj_jarpath, ns.working_dir])
    
    return ns

def spawn_java(config, level, cache, verify, dataset):
    """Spawn the Java process, pass in a dataset object, and return
    a results object.
    
        - level ("1" | "2" | "3") controls which query is run
        - cache (boolean) controls whether JQL incrementalization is
          enabled
        - verify (boolean) controls whether we are timing or verifying
          output correctness
    """
    PIPE = subprocess.PIPE
    
    env = dict(os.environ.items())
    oldpath = env['PATH']
    newpath = config.path + ':' + oldpath
    env.update({'JQL_HOME': config.jql_home,
                'ASPECTJ_HOME': config.aspectj_home,
                'JAVA_HOME': config.java_home,
                'CLASSPATH': config.classpath,
                'PATH': newpath})
    
    args = list(config.cmd)
    args.append('jqlexp/Level' + level)
    args.append('cache' if cache else 'nocache')
    args.append('verify' if verify else 'benchmark')
    
    child = subprocess.Popen(
        args, bufsize=-1,
        stdin=PIPE, stdout=PIPE,
        cwd=config.working_dir, env=env, universal_newlines=True)
    
    data_in = json.dumps(dataset)
    stdout, stderr = child.communicate(data_in)
    
    # Uncomment to debug:
#    print('stdout:\n' + stdout)
#    print('stderr:\n' + stderr)
    
    if child.returncode != 0:
        raise JavaError(child.returncode, config.cmd, stderr)
    
    results = json.loads(stdout)
    return results
