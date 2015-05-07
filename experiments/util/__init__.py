"""Experiment utilities."""

__all__ = [
    'lprof_totaltime',
]


from functools import partial

from frexp.extractor import Extractor

import incoq.runtime
import osq


def lprof_totaltime(report):
    """Given a (possibly partial) string output of line_profiler,
    return the total time.
    """
    pat = r'^\s*(\d+)\s+(\d+)\s+(\d+).*'
    lines = report.split('\n')
    total_time = 0
    for line in lines:
        m = re.match(pat, line)
        if m is not None:
            total_time += int(m.group(3))
    return total_time


class SmallExtractor(Extractor):
    
    """Small format, for paper figures."""
    
    rcparams = {
        'font.size':           11,
        'legend.fontsize':     10,
        'legend.numpoints':    1,
        'legend.labelspacing': .2,
        'axes.titlesize':      11,
        'axes.linewidth':      .5,
        'lines.linewidth':     .5,
        'lines.markersize':    3,
        
        'font.family':         'serif',
        'font.serif':          ['Computer Modern'],
        'text.usetex':         True,
        
        'legend.frameon':      False,
    }
    
    timesop = '$\\times$'
    
    ylabelpad = 2
    xlabelpad = 2
    
    dpi = 200
    figsize = (3.5, 2.79)

class LargeExtractor(Extractor):
    
    """Large format, for clear, standalone images."""
    
    rcparams = {
        'font.size':           24,
        'legend.fontsize':     24,
        'lines.linewidth':     2,
        'lines.markersize':    5,
        
        'xtick.major.size':    10,
        'ytick.major.size':    10,
        'xtick.minor.size':    8,
        'ytick.minor.size':    8,
        'xtick.major.width':   2,
        'ytick.major.width':   2,
        'xtick.minor.width':   1,
        'ytick.minor.width':   1,
        
        'legend.frameon':      False,
    }
    
    figsize = (10, 7.5)

class PosterExtractor(Extractor):
    
    """Format for 8x6 figure in poster."""
    
    rcparams = {
        'font.size':           32,
        'legend.fontsize':     24,
        'legend.numpoints':    1,
        'lines.linewidth':     3,
        'lines.markersize':    8,
        
        'xtick.major.size':    10,
        'ytick.major.size':    10,
        'xtick.minor.size':    8,
        'ytick.minor.size':    8,
        'xtick.major.width':   2,
        'ytick.major.width':   2,
        'xtick.minor.width':   1,
        'ytick.minor.width':   1,
        
        'legend.frameon':      False,
    }
    
    figsize = (8, 6)
    
    tightlayout_pad = .1

def djb2(s):
    """Simple string hash algorithm."""
    val = 5381
    mod = 2**32
    for c in s:
        val = (val << 5 + val + ord(c)) % mod
    return val

def canonize(tree, *, use_hash=False):
    """Recursively convert a tree of values into a canonical form.
    Values of specific types are replaced as follows:
      
      - Primitive types (None, int, float, and string) are
        left alone.
      
      - Lists and tuples are turned into tuples.
      
      - Sets and frozensets are turned into frozensets.
      
      - Dictionaries become frozensets of (key, value) tuples.
      
          - The keys must be strings.
          
          - As a special case, dictionaries whose keys all begin with
            underscores are turned into frozensets of their values.
            This includes empty dictionaries.
      
      - Sets and RCSets from incoq.runtime get turned into frozensets.
      
      - Objs from incoq.runtime get turned into a pair of their class
        name and a frozenset of their __dict__, excluding keys that
        begin with one or more underscores.
      
      - RCSets from osq get replaced by frozensets.
    
    Aliasing is not preserved. Canonizing also has the effect of
    deep-copying.
    
    The purpose of this function is to create a nearly semantically
    equivalent value that can be compared for equality with other
    values. This is needed because the transformed program uses
    helper types that are similar to, but not identical to, their
    corresponding basic Python types.
    
    If hash is True, the returned values are deterministically
    hashed (not necessarily using __hash__, which is randomzied
    for some types).
    """
    can = partial(canonize, use_hash=use_hash)
    hash_kind = 'NORMAL'
    
    if isinstance(tree, (type(None), int, float, str, bool)):
        result = tree
        if isinstance(tree, str):
            hash_kind = 'STRING'
    
    elif isinstance(tree, (incoq.runtime.Set, incoq.runtime.RCSet,
                           osq.incr.RCSet)):
        result = frozenset(can(v) for v in tree)
    
    elif isinstance(tree, incoq.runtime.Obj):
        name = tree.__class__.__name__
        attrs = frozenset((k, can(v))
                          for k, v in tree.__dict__.items()
                          if not k.startswith('_'))
        hash_kind = 'OBJ'
        result = (name, attrs)
    
    elif isinstance(tree, (list, tuple)):
        result = tuple(can(v) for v in tree)
    
    elif isinstance(tree, (set, frozenset)):
        result = frozenset(can(v) for v in tree)
    
    elif isinstance(tree, dict):
        if all(k.startswith('_') for k in tree.keys()):
            result = frozenset(can(v) for v in tree.values())
        else:
            hash_kind = 'DICT'
            result = frozenset((k, can(v))
                               for k, v in tree.items())
    
    else:
        raise ValueError('Un-canonizable type: ' + str(type(tree)))
    
    assert type(result) in [type(None), int, float, str, bool,
                            tuple, frozenset]
    
    if use_hash:
        if hash_kind == 'STRING':
            result = djb2(result)
        elif hash_kind == 'OBJ':
            name, attrs = result
            name = djb2(name)
            attrs = frozenset((djb2(k), v) for k, v in attrs)
            result = (name, hash(attrs))
            result = hash(result)
        elif hash_kind == 'DICT':
            result = frozenset((djb2(k), v) for k, v in result)
            result = hash(result)
        else:
            result = hash(result)
    
    return result
