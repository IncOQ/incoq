###############################################################################
# astnodes.py                                                                 #
# Author: Jon Brandvein                                                       #
###############################################################################

"""Print Python AST node names alphabetically."""


import ast


all_nodetypes = [nt for nt in ast.__dict__.values()
                    if isinstance(nt, type)
                    if issubclass(nt, ast.AST)]

all_names = sorted(nt.__name__ for nt in all_nodetypes)

#for x in all_names:
#    print(x)

# Three per line, evenly spaced.
for i in range(0, len(all_names), 3):
    print('    ' + ''.join("'{}',".format(name).ljust(20)
                           for name in all_names[i : i+3]))
