###############################################################################
# str.py                                                                      #
# Author: Jon Brandvein                                                       #
###############################################################################

"""String utilities."""


__all__ = [
    'brace_items',
    'quote_items',
    
    'tuple_str',
    'from_tuple_str',
    
    'dedent_trim',
    'join_lines',
    'indent_lines',
    
    'side_by_side',
    'side_by_side_cmp',
    
    'affirmative',
    'negative',
    'get_truth',
]


def brace_items(items, lbrace, rbrace):
    """Given a list of strings, return a comma-delimited string of
    each item in the specified braces.
    """
    return ', '.join(lbrace + item + rbrace for item in items)


def quote_items(items):
    """Given a list of strings, return a comma-delimited string of
    each item in quotes.
    """
    return brace_items(items, '"', '"')


def tuple_str(items):
    """Given a list of strings, return the strings comma-delimited
    and in parantheses, except that if the list is a singleton just
    return the one element.
    """
    if len(items) == 1:
        return items[0]
    else:
        return '(' + ', '.join(items) + ')'


def from_tuple_str(text):
    """Given a string representation of a Name or a Tuple of Names,
    return a list of the identifiers.
    """
    import ast
    tree = ast.parse(text).body[0].value
    if isinstance(tree, ast.Name):
        return [tree.id]
    elif (isinstance(tree, ast.Tuple) and
          all(isinstance(elt, ast.Name) for elt in tree.elts)):
        return [elt.id for elt in tree.elts]
    else:
        raise ValueError('Bad tuple string: "{}"'.format(text))


def dedent_trim(text):
    """Like textwrap.dedent, but also eliminate leading and trailing
    lines if they are whitespace or empty.
    
    This is useful for writing code as triple-quoted multi-line
    strings.
    """
    from textwrap import dedent
    
    lines = text.split('\n')
    if len(lines) > 0:
        if len(lines[0]) == 0 or lines[0].isspace():
            lines = lines[1 : ]
    if len(lines) > 0:
        if len(lines[-1]) == 0 or lines[-1].isspace():
            lines = lines[ : -1]
    
    return dedent('\n'.join(lines))


def join_lines(lines, prefix=''):
    """Given a list of lines, concatenate them into a single string
    holding a paragraph.
    """
    return ''.join(prefix + line + '\n' for line in lines)

def indent_lines(lines, prefix=''):
    """Given a list of lines, if prefix is a string, prepend it to each
    line. If prefix is an integer, prepend that number of spaces to
    each line.
    """
    if isinstance(prefix, int):
        prefix = ' ' * prefix
    return [prefix + line for line in lines]


def side_by_side(text1, text2, cmp=False):
    """Format two pieces of text into two boxes displayed side-by-side.
    If cmp is True, mark the first line that differs.
    """
    lines1 = text1.split('\n')
    lines2 = text2.split('\n')
    
    width1 = max(len(line) for line in lines1)
    width2 = max(len(line) for line in lines2)
    
    header = '.-' + '-' * width1 + '-.-' + '-' * width2 + '-.'
    footer = '^-' + '-' * width1 + '-^-' + '-' * width2 + '-^'
    
    out_lines = []
    out_lines.append(header)
    
    if len(lines1) == len(lines2):
        min_end = 0
    else:
        min_end = min(len(lines1), len(lines2))
    
    found_differ = False
    from itertools import zip_longest
    line_seq = zip_longest(lines1, lines2, fillvalue='')
    for i, (line1, line2) in enumerate(line_seq, 1):
        out_line = '| {} | {} |'.format(line1.ljust(width1),
                                        line2.ljust(width2))
        
        # Add marker if found first difference.
        if (cmp and not found_differ and
            (line1 != line2 or i == min_end)):
            found_differ = True
            out_line += ' <<<'
        
        out_lines.append(out_line)
    
    out_lines.append(footer)
    
    return '\n'.join(out_lines)


def side_by_side_cmp(text1, text2):
    """Wrapper around side_by_side."""
    return side_by_side(text1, text2, cmp=True)


def affirmative(s):
    """Return whether a string represents an affirmative
    (logical true).
    """
    return s.lower() in [
        'true', 'yes', '1', 'on'
    ]

def negative(s):
    """Return whether a string represents a negative
    (logical false).
    """
    return s.lower() in [
        'false', 'no', '0', 'off'
    ]

def get_truth(s):
    """Return True or False depending on whether the string represents
    an affirmative or negative. Raise ValueError if neither.
    """
    if affirmative(s):
        return True
    elif negative(s):
        return False
    else:
        raise ValueError('"{}" is not recognized as '
                         'true or false'.format(s))
