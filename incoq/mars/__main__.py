"""Entry point for transforming whole programs."""


__all__ = [
    'invoke',
    'main',
]


import sys
import argparse

from incoq.mars.config import all_attributes
from incoq.mars.transform import transform_source


def invoke(in_filename, out_filename, *, options=None):
    """Transform one file and report to the user. Use stdin or stdout
    if '-' is given as the input or output filename respectively.
    """
    in_file = None
    out_file = None
    
    try:
        # Use transform_source() rather than transform_file,
        # so we only open (and thereby truncate) the output
        # file if transformation was successful.
        if in_filename == '-':
            in_file = sys.stdin
        else:
            in_file = open(in_filename, 'rt')
        source = in_file.read()
        
        source = transform_source(source, options=options)
        
        if out_filename == '-':
            out_file = sys.stdout
        else:
            out_file = open(out_filename, 'wt')
        out_file.write(source)
    
    finally:
        if in_file is not None and in_filename != '-':
            in_file.close()
        if out_file is not None and out_filename != '-':
            out_file.close()


def main(args):
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
    main(sys.argv[1:])
