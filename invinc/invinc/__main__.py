"""Entry point for invoking the system."""


import sys
import argparse

from . import transform_file, print_exc_with_ast 


def boolval(s):
    if s.lower() == 'true':
        return True
    elif s.lower() == 'false':
        return False
    else:
        raise argparse.ArgumentTypeError("Expected 'true' or 'false'")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Incrementalize input_file, '
                                     'writing to output_file.')
    
    parser.add_argument('input_file', help=argparse.SUPPRESS)
    parser.add_argument('output_file', help=argparse.SUPPRESS)
    
    general_group = parser.add_argument_group('general options')
    general_group.add_argument('-v', '--verbose', action='store_true',
                               default=None,
                               help='print transformation details')
    general_group.add_argument('--eol', choices=['native', 'lf', 'crlf'],
                               default=None,
                               help='end-of-line markers in output file')
    
    trans_group = parser.add_argument_group('transformation options')
    trans_group.add_argument('--obj_domain', type=boolval, metavar='<bool>',
                             default=None,
                             help='use object-domain flattening')
    
    args = parser.parse_args()
    
    # Arguments that are not provided get set to None by the arg parser.
    # These are not set in nopts so that the system defaults are applied.
    optkeys = ['verbose', 'eol', 'obj_domain']
    nopts = {k: getattr(args, k)
             for k in optkeys
             if getattr(args, k) is not None}
    
    try:
        transform_file(args.input_file, args.output_file, nopts=nopts)
    except Exception as exc:
        print_exc_with_ast()
        sys.exit(1)
        
    print('Done')
