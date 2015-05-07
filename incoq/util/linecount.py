"""Get linecounts for files."""


__all__ = [
    'get_loc_source',
    'get_loc_file',
    'get_counts_for_files',
    'get_counts_for_dir',
]


from os import listdir
from os.path import join, normpath, isdir
from fnmatch import fnmatch


def get_loc_source(source,
                   ignore_whitespace=True,
                   ignore_comments=True):
    """Get the line count of the given source code, optionally ignoring
    empty lines, whitespace lines, and comment lines.
    """
    
    lines = source.split('\n')
    count = 0
    for line in lines:
        # Ignore empty lines and whitespace lines if requested.
        if ignore_whitespace and (len(line) == 0 or line.isspace()):
            continue
        # Ignore comment lines if requested.
        if ignore_comments and line.strip().startswith('#'):
            continue
        count += 1
    return count

def get_loc_file(filename, **kargs):
    """Same but for a file, which must exist."""
    with open(filename, 'rt') as file:
        return get_loc_source(file.read(), **kargs)

def get_counts_for_files(filenames, **kargs):
    """Given a list of file names, return the total line count, and
    a dict from filenames to individual line counts.
    """
    total = 0
    counts = {}
    for fn in filenames:
            count = get_loc_file(fn, **kargs)
            counts[fn] = count
            total += count
    
    return total, counts


def get_counts_for_dir(dir, exclude_pats, **kargs):
    """Given a directory, walk the directory and return a list of pairs
    of paths and line counts. Paths are either Python filenames (.py) or
    directory names. Counts for directories are the sum of the counts
    for their contents.
    """
    dir = normpath(dir)
    # Grab dir entries, split by directory / python file,
    # order alphabetically.
    entries = sorted(listdir(dir))
    entries = [join(dir, name)
               for name in entries
               if not any(fnmatch(name, pat) for pat in exclude_pats)]
    entries = [(name, isdir(name)) for name in entries]
    dir_entries = [name for name, d in entries if d]
    py_entries = [name for name, d in entries
                       if not d and name.endswith('.py')]
    
    count = 0
    result = []
    for name in dir_entries:
        subresult = get_counts_for_dir(name, exclude_pats, **kargs)
        result += subresult
        # First entry is the directory total.
        count += subresult[0][1]
    for name in py_entries:
        subcount = get_loc_file(name, **kargs)
        result += [(name, subcount)]
        count += subcount
    
    return [(dir, count)] + result
