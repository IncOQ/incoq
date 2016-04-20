"""Entry point for transforming whole programs."""


__all__ = [
    'invoke',
    'run',
]


import sys
import argparse

from incoq.mars.symbol.config import get_argparser, extract_options
from incoq.mars.transform import transform_filename


def invoke(in_filename, out_filename, *,
           options=None, query_options=None,
           stats_filename=None):
    """Transform one file and report to the user."""
    transform_filename(in_filename, out_filename,
                       options=options, query_options=query_options,
                       stats_filename=stats_filename)


def run(args):
    """Entry point for incoq.mars."""
    parent = get_argparser()
    parser = argparse.ArgumentParser(prog='incoq.mars', parents=[parent])
    parser.add_argument('in_file')
    parser.add_argument('out_file')
    parser.add_argument('--stats', nargs=1, default=[None])
    
    ns = parser.parse_args(args)
    
    options = extract_options(ns)
    
    # There's currently no way to pass query options from the
    # command line directly.
    invoke(ns.in_file, ns.out_file, options=options,
           stats_filename=ns.stats[0])


if __name__ == '__main__':
    run(sys.argv[1:])
