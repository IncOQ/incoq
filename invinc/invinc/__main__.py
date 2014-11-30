###############################################################################
# __main__.py                                                                 #
# Author: Jon Brandvein                                                       #
###############################################################################

"""Driver program for running invinc to transform a file."""


import sys

from . import transform_file, print_exc_with_ast 


if __name__ == '__main__':
    usage_str = ('Usage: {} -m invinc <input file> <output file>'.format(
                 sys.executable))
    
    if len(sys.argv) != 3:
        print(usage_str, file=sys.stderr)
        sys.exit(1)
    
    input_filename, output_filename = sys.argv[1:3]
    
    try:
        transform_file(input_filename, output_filename)
    except Exception as exc:
        print_exc_with_ast()
        sys.exit(1)
        
    print('Done')
