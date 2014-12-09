"""Get linecounts for files."""


from os import walk, chdir
from os.path import join, normpath
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

def get_loc_file(filename,
                 ignore_whitespace=True,
                 ignore_comments=True):
    """Same but for a file, which must exist."""
    with open(filename, 'rt') as file:
        return get_loc_source(file.read(),
                              ignore_whitespace=ignore_whitespace,
                              ignore_comments=ignore_comments)

def get_counts_for_files(filenames,
                         ignore_whitespace=True,
                         ignore_comments=True):
    """Given a list of file names, return the total line count, and
    a dict from filenames to individual line counts.
    """
    
    total = 0
    counts = {}
    for fn in filenames:
            count = get_loc_file(fn,
                                 ignore_whitespace=ignore_whitespace,
                                 ignore_comments=ignore_comments)
            counts[fn] = count
            total += count
    
    return total, counts


def get_files_for_spec(include, exclude):
    """Given a list of paths to include and exclude, with exclude
    taking precedence, generate a list of Python program filenames.
    """
    
    files = []
    include = list(map(normpath, include))
    exclude = list(map(normpath, exclude))
    
    # Help catch errors in pathnames that would otherwise produce
    # wrong results.
    used_specifiers = set()
    
    def any_match(name, patterns):
        for pat in patterns:
            if fnmatch(name, pat):
                used_specifiers.add(pat)
                return True
        return False
    
    for dirpath, dirnames, filenames in walk('.'):
        
        for name in list(dirnames):
            path = normpath(join(dirpath, name))
            if any_match(path, exclude):
                dirnames.remove(name)
        
        for name in filenames:
            path = normpath(join(dirpath, name))
            if (not any_match(path, include) or
                any_match(path, exclude) or
                not path.endswith('.py')):
                continue
            
            files.append(path)
    
    unused = set(include + exclude) - used_specifiers
    if unused:
        raise AssertionError('Unused path specifier(s): ' +
                             ', '.join(unused))
    
    return files


def get_counts_for_spec(include, exclude,
                        ignore_whitespace=True,
                        ignore_comments=True):
    """Given a list of included and excluded file paths, return
    the total count and count dict.
    """
    files = get_files_for_spec(include, exclude)
    return get_counts_for_files(files,
                                ignore_whitespace=ignore_whitespace,
                                ignore_comments=ignore_comments)


if __name__ == '__main__':
    # All paths relative to top-level source dir.
    chdir('../')
    
    TESTS = '*/test*.py'
    
    specs = [
        ('Runtime library', ['runtimelib/runtimelib.py'], []),
        ('Utilities', ['util/*'], ['*/test*.py']),
        
        ('Transformation system', ['oinc/*'],
         ['oinc/testprograms/*', TESTS]),
        (' |-- incast', ['oinc/incast/*'], [TESTS]),
        (' |-- sets', ['oinc/set/*'], [TESTS]),
        (' |-- comprehensions', ['oinc/comp/*'], [TESTS]),
        (' |-- objects', ['oinc/obj/*'], [TESTS]),
        (' |-- tup', ['oinc/tup/*'], [TESTS]),
        (' |-- demand', ['oinc/demand/*'], [TESTS]),
        (' |-- aggregates', ['oinc/aggr/*'], [TESTS]),
        (' |-- cost', ['oinc/cost/*'], [TESTS]),
        (' `-- central', ['oinc/central/*'], [TESTS]),
        
        ('Tests', ['oinc/testprograms/*', 'oinc/*/test*.py'], []),
        
        ('Experiments (incl. generated)', ['experiments/*'], []),
    ]
    
    all_total = 0
    for name, include, exclude in specs:
        
        # Uncomment to debug file listing.
#        print(name)
#        for f in get_files_for_spec(include, exclude):
#            print('  ' + f)
        
        total, _counts = get_counts_for_spec(include, exclude)
        print('{:<35}{:>6}'.format(name + ': ', total))
        if not name.startswith(' '):
            all_total += total
    print('-' * 41)
    print('{:<35}{:>6}'.format('Everything: ', all_total))
