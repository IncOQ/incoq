"""Regenerate whole-program tests."""


__all__ = [
    'regenerate_test',
]


import sys
import argparse
from os.path import join, dirname, basename, normpath, relpath

from incoq.compiler import get_argparser, extract_options, invoke

from .programs.test_transformation import get_test_entries


test_root_path = join(dirname(__file__), 'programs')
test_root_path = normpath(test_root_path)


def regenerate_test(test_name, *, options=None):
    """Regenerate the *_out.py file for the given test. Tests are
    specified by the path to their *_in.py file, omitting the _in.py
    suffix, and relative to the programs directory.
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
    
    print('Regenerating {}...'.format(test_name), flush=True)
    
    # Tests do not do cost analysis, in order to run faster.
    options['costs'] = 'false'
    
    invoke(in_path, out_path, options=options)


def regenerate_all(*, options=None):
    """Regenerate *_out.py files for all tests in the whole-program
    tests directory.
    """
    test_entries = sorted(get_test_entries())
    for test_dir, test_base, *_ in test_entries:
        test_name_abs = join(test_dir, test_base)
        test_name = relpath(test_name_abs, test_root_path)
        regenerate_test(test_name, options=options)


def run(args):
    parent = get_argparser(with_help=False)
    parser = argparse.ArgumentParser(prog='regenerate_tests',
                                     parents=[parent],
                                     epilog='IncOQ command line options are '
                                            'also permitted.')
    parser.add_argument('test_name', nargs='?', default=None,
                        help='path prefix of test to regenerate, e.g., '
                             '"comp/basic"; omit to regenerate all tests')
    
    ns = parser.parse_args(args)
    
    options = extract_options(ns)
    
    if ns.test_name is None:
        regenerate_all(options=options)
    else:
        regenerate_test(ns.test_name, options=options)


if __name__ == '__main__':
    run(sys.argv[1:])
