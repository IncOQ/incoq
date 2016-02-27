"""Regenerate whole-program tests."""


__all__ = [
    'regenerate_test',
]


import sys
import argparse
from os.path import join, dirname, basename, normpath, relpath

from incoq.tests.mars.programs.test_transformation import get_test_entries
from . import __main__ as main


test_root_path = join(dirname(__file__), '../tests/mars/programs')
test_root_path = normpath(test_root_path)


def regenerate_test(test_name, *):
    """Regenerate the *_out.py file for the given test. Tests are
    specified by the path to their *_in.py file, omitting the _in.py
    suffix, and relative to the incoq/tests/mars/programs directory.
    """
    test_path = join(test_root_path, test_name)
    test_dir = dirname(test_path)
    test_base = basename(test_path)
    
    in_base = test_base + '_in.py'
    in_path = join(test_dir, in_base)
    in_path = normpath(in_path)
    
    out_base = test_base + '_out.py'
    out_path = join(test_dir, out_base)
    out_path = normpath(out_path)
    
    options = {}
    if verbose is not None:
        options['verbose'] = verbose
    
    print('Regenerating {}...'.format(test_name), flush=True)
    
    main.invoke(in_path, out_path, options=options)


def regenerate_all():
    """Regenerate *_out.py files for all tests in the whole-program
    tests directory.
    """
    test_entries = get_test_entries()
    for test_dir, test_base, *_ in test_entries:
        test_name_abs = join(test_dir, test_base)
        test_name = relpath(test_name_abs, test_root_path)
        regenerate_test(test_name)


def run(args):
    parser = argparse.ArgumentParser(prog='incoq.mars.regenerate_tests')
    parser.add_argument('test_name', nargs='?', default=None)
    parser.add_argument('--verbose', action='store_true', default=None)
    parser.add_argument('--pretend', action='store_true', default=None)
    
    ns = parser.parse_args(args)
    
    if ns.test_name is None:
        if ns.pretend:
            raise ValueError('Cannot use --pretend when regenerating '
                             'all tests')
        regenerate_all()
    else:
        regenerate_test(ns.test_name,
                        verbose=ns.verbose,
                        pretend=ns.pretend)


if __name__ == '__main__':
    run(sys.argv[1:])
