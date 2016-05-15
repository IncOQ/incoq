"""Entry point for transforming whole programs."""


__all__ = [
    'run',
]


import sys
import argparse

from incoq.compiler import get_argparser, extract_options, invoke


def run(args):
    """Entry point for incoq.compiler."""
    parent = get_argparser()
    parser = argparse.ArgumentParser(prog='incoq', parents=[parent])
    parser.add_argument('in_file', help='path to input file')
    parser.add_argument('out_file', help='path to output file')
    parser.add_argument('--stats', nargs=1, default=[None],
                        help='if present, path to write transformation '
                             'stats to')
    
    ns = parser.parse_args(args)
    
    options = extract_options(ns)
    
    # There's currently no way to pass query options from the
    # command line directly. Use a Python script and call invoke().
    invoke(ns.in_file, ns.out_file, options=options,
           stats_filename=ns.stats[0])


if __name__ == '__main__':
    run(sys.argv[1:])
