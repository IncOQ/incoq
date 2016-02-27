"""Entry point for transforming whole programs."""


__all__ = [
    'invoke',
    'run',
]


import sys
import argparse

from incoq.mars.symbol.config import get_argparser, extract_options
from incoq.mars.transform import transform_filename


def invoke(in_filename, out_filename, *, options=None):
    """Transform one file and report to the user."""
    transform_filename(in_filename, out_filename, options=options)


def run(args):
    """Entry point for incoq.mars."""
    parent = get_argparser()
    parser = argparse.ArgumentParser(prog='incoq.mars', parents=[parent])
    parser.add_argument('in_file')
    parser.add_argument('out_file')
    
    ns = parser.parse_args(args)
    
    # Parse out config attribute options.
    options = extract_options(ns)
    
    invoke(ns.in_file, ns.out_file, options=options)


if __name__ == '__main__':
    run(sys.argv[1:])
