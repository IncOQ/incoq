"""Whole-program tests, at the file input/output level. Both the
generated code and its output when executed are tested.

This module recursively scans this directory, finding and running
all test cases that match the black/whitelist.

A transformation test case FOO consists of a file FOO_in.py and
FOO_out.py. It transforms FOO_in.py and confirms that the resulting
program exactly matches FOO_out.py. This kind of test is thus sensitive
to non-determinism in the transformation, whether it's the order of
code insertion or the choice of fresh variable names. We make it a point
to avoid this kind of non-determinism throughout the system.

A behavior test consists of a file FOO_in.py and FOO_out.txt. It first
transforms FOO_in.py, then it runs both the original and transformed
program and confirms that the result is exactly the text specified in
FOO_out.txt. This test is sensitive to non-determinism in the program
semantics. Therefore, the test programs will sort sets before printing
them.
"""

# NOTE: If the bintrees library is installed without support for FastAVLTree,
# behavior tests will stupidly fail due to extra stdout warning-pollution by
# the bintrees library.


import unittest
import os

from incoq.util.pyexec import pyexec_source
from incoq.mars.transform import transform_source


test_directory = os.path.split(__file__)[0]
MAXDIFF = None


def make_transform_test(base_name, in_name, outpy_name, outtxt_name):
    
    def template(self):
        with open(in_name, 'r') as in_file, \
             open(outpy_name, 'r') as outpy_file:
            in_source = in_file.read()
            exp_source = outpy_file.read()
        
        result_source = transform_source(in_source)
        
        self.assertEqual(result_source, exp_source)
    
    base_relpath = os.path.relpath(base_name)
    template.__name__ = 'test_transform_' + base_relpath
    return template


def make_behavior_test(base_name, in_name, outpy_name, outtxt_name):
    
    def template(self):
        with open(in_name, 'r') as in_file, \
             open(outtxt_name, 'r') as outtxt_file:
            in_source = in_file.read()
            exp_txt = outtxt_file.read()
        
        result_source = transform_source(in_source)
        
        in_txt = pyexec_source(in_source)
        result_txt = pyexec_source(result_source)
        
        self.assertEqual(in_txt, exp_txt)
        self.assertEqual(result_txt, exp_txt)
    
    base_relpath = os.path.relpath(base_name)
    template.__name__ = 'test_behavior_' + base_relpath
    return template


def get_test_entries_for_filenames(dirfiles):
    """Given a list of pairs of directories and files, return a set of
    tuples (dir, base_name, in_name, outpy_name, outtxt_name)
    representing a group of test files. base_name is the common prefix
    to the three other files. An entry is returned iff the in_name file
    actually exists. If the other two files do not exist, None is
    substituted.
    """
    test_entries = set()
    for dir, filenames in dirfiles:
        for name in filenames:
            if name.endswith('_in.py'):
                base_name = name[:-len('_in.py')]
                in_name = name
                outpy_name = base_name + '_out.py'
                outtxt_name = base_name + '_out.txt'
                if outpy_name not in filenames:
                    outpy_name = None
                if outtxt_name not in filenames:
                    outtxt_name = None
                
                test_entries.add((dir, base_name, in_name,
                                  outpy_name, outtxt_name))
    
    return test_entries


def get_test_entries():
    """Return a set of test entry tuples for all tests in this
    test directory.
    """
    walk_entries = list(os.walk(test_directory))
    dirfiles = [(dirpath, filenames)
                for dirpath, _, filenames in walk_entries]
    test_entries = get_test_entries_for_filenames(dirfiles)
    return test_entries


def get_tests():
    """Find runnable tests by searching this directory for input files.
    Return a pair of a list of transformation tests and a list of
    behavior tests.
    """
    
    test_entries = get_test_entries()
    
    # Create test functions. Omit the transformation test if there's no
    # outpy file. Omit the behavior test if there's no outtxt file.
    
    transform_tests = []
    behavior_tests = []
    
    for (dir, *names) in test_entries:
        base_name, in_name, outpy_name, outtxt_name = names
        base_fullpath = os.path.join(dir, base_name)
        base_path = os.path.relpath(base_fullpath)
        
        args = [os.path.join(dir, name) if name is not None else None
                for name in names]
        
        if outpy_name is not None:
            test = make_transform_test(*args)
            transform_tests.append(test)
        
        if outtxt_name is not None:
            test = make_behavior_test(*args)
            behavior_tests.append(test)
    
    return transform_tests, behavior_tests


class TestTransform(unittest.TestCase):
    maxDiff = MAXDIFF

class TestBehavior(unittest.TestCase):
    maxDiff = MAXDIFF

transform_tests, behavior_tests = get_tests()
for func in transform_tests:
    assert getattr(TestTransform, func.__name__, None) is None
    setattr(TestTransform, func.__name__, func)
for func in behavior_tests:
    assert getattr(TestBehavior, func.__name__, None) is None
    setattr(TestBehavior, func.__name__, func)


# Run transform tests first, for convenience.
def load_tests(loader, tests, pattern):
    suite = unittest.TestSuite()
    transform_tests = loader.loadTestsFromTestCase(TestTransform)
    behavior_tests = loader.loadTestsFromTestCase(TestBehavior)
    suite.addTests(transform_tests)
    suite.addTests(behavior_tests)
    return suite


if __name__ == '__main__':
    import sys
    runner = unittest.TextTestRunner(stream=sys.stdout, verbosity=2)
    unittest.main(testRunner=runner)
