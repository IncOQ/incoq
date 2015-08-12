"""Entry point for transforming whole programs."""


__all__ = [
    'invoke',
    'main',
]


import sys
import argparse

from incoq.mars.transform import transform_file


def invoke(in_filename, out_filename):
    """Transform one file and report to the user. Use stdin or stdout
    if '-' is given as the input or output filename respectively.
    """
    in_file = None
    out_file = None
    
    try:
        if in_filename == '-':
            in_file = sys.stdin
        else:
            in_file = open(in_filename, 'rt')
        if out_filename == '-':
            out_file = sys.stdout
        else:
            out_file = open(out_filename, 'wt')
        
        transform_file(in_file, out_file)
    
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
    
    ns = parser.parse_args(args)
    
    invoke(ns.in_file, ns.out_file)


if __name__ == '__main__':
    main(sys.argv[1:])
