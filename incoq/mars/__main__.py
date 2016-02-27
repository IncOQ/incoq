"""Entry point for transforming whole programs."""


__all__ = [
    'invoke',
    'run',
]


import sys
import argparse

from incoq.mars.symbol.config import all_attributes
from incoq.mars.transform import transform_filename


def invoke(in_filename, out_filename, *, options=None):
    """Transform one file and report to the user."""
    transform_filename(in_filename, out_filename, options=options)


def run(args):
    """Entry point for incoq.mars."""
    parser = argparse.ArgumentParser(prog='incoq.mars')
    parser.add_argument('in_file')
    parser.add_argument('out_file')
    
    # Programmatically add options for each config attribute.
    for attr in all_attributes:
        parser.add_argument('--' + attr.name,
                            help=attr.docstring,
                            **attr.argparse_kargs)
    
    ns = parser.parse_args(args)
    
    # Parse out config attribute options.
    options = {}
    for attr in all_attributes:
        val = getattr(ns, attr.name)
        if val is not None:
            options[attr.name] = val
    
    invoke(ns.in_file, ns.out_file, options=options)


if __name__ == '__main__':
    run(sys.argv[1:])
