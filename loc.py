"""Print line count breakdown."""

from os import chdir
from os.path import dirname
from pathlib import PurePath

from invinc.util.linecount import get_counts_for_dir


def show(dir, dirs_only=False):
    # All paths relative to this file (top-level dir).
    ex = [
        '.git',
        '.tox',
        '__pycache__',
    ]
    res = get_counts_for_dir(dir, ex)
    for name, count in res:
        p = PurePath(name)
        indent = len(p.parts) - 1
        label = '|    ' * (indent - 1) + '|--- ' if indent > 0 else ''
        label += p.name
        number = str(count)
        if name.endswith('.py'):
            number = '    ' + number
            if dirs_only:
                continue
        print('{:40}  {}'.format(label, number))

if __name__ == '__main__':
    chdir(dirname(__file__))
    show('invinc', dirs_only=True)
#    show('experiments', dirs_only=True)
