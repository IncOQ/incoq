"""Aggregate and view transformation stats.

Stats are obtained by reading a *_stats.txt file or, for non-generated
files, directly computing the LOC directly. Stats for each file is
collected into a single dict for that file. These are then aggregated
into a table for output. Both the method of collection and the schema
for aggregation are controlled by the hardcoded schemas below.
"""


__all__ = [
    'regenerate_test',
]


import sys
import argparse
from os import chdir
from os.path import dirname, normpath
import io
import csv
import json

try:
    from tabulate import tabulate
    HAVE_TABULATE = True
except ImportError:
    HAVE_TABULATE = False

from incoq.util.linecount import get_loc_source


root_path = normpath(dirname(__file__))


def read_file(filename):
    """Return the content of a file or None if an exception occurs."""
    f = None
    data = None
    try:
        f = open(filename, 'rt')
        data = f.read()
    except OSError:
        pass
    finally:
        if f is not None:
            f.close()
    return data


def loc_collector(base_name):
    stats = {}
    source = read_file(base_name + '.py')
    if source is not None:
        stats['lines'] = get_loc_source(source)
    return stats


def statfile_collector(base_name):
    stats = {}
    data = read_file(base_name + '_stats.txt')
    if data is not None:
        stats = json.loads(data)
    return stats


stat_collections = [
    # Twitter.
    ('twitter/twitter_in',              loc_collector),
    ('twitter/twitter_inc',             statfile_collector),
    ('twitter/twitter_dem',             statfile_collector),
]


def do_collections():
    """Return an all_stats dict, mapping from each file name to a stats
    dict.
    """
    all_stats = {}
    for base_name, collector in stat_collections:
        stats = collector(base_name)
        all_stats[base_name] = stats
    return all_stats


class BaseAggregator:
    
    """Base class for aggregators."""
    
    def __init__(self, all_stats):
        self.all_stats = all_stats
        """Map from file name to stats dict for that file."""
    
    def get_data(self):
        """Return a pair of header data (list of values) and body data
        (list of rows, i.e., list of lists of values).
        """
        raise NotImplementedError
    
    def to_csv(self):
        """Return the data formatted as a CSV string."""
        filelike = io.StringIO(newline='')
        writer = csv.writer(filelike)
        header, body = self.get_data()
        writer.writerow(header)
        for line in body:
            writer.writerow(line)
        return filelike.getvalue()
    
    def tabulate(self, **kargs):
        """Return the data formatted using tabulate."""
        if not HAVE_TABULATE:
            raise ImportError('Tabulate library not available')
        header, body = self.get_data()
        return tabulate(body, header, **kargs)
    
    def to_table(self):
        return self.tabulate(tablefmt='simple')
    
    def to_latex(self):
        return self.tabulate(tablefmt='latex')
    
    def to_ascii(self):
        if HAVE_TABULATE:
            return self.to_table()
        else:
            return self.to_csv()


class SimpleAggregator(BaseAggregator):
    
    """Aggregator that returns a grid of stat key lookups."""
    
    @property
    def first_header(self):
        """Name to use for the top-left cell."""
        return 'Program'
    
    @property
    def cols(self):
        """Return a list of pairs of a stat attribute to look up, and
        the name to display the attribute as.
        """
        raise NotImplementedError
    
    @property
    def rows(self):
        """Return a list of pairs of a file name whose stats are
        displayed, and the name to use for that row heading.
        """
        raise NotImplementedError
    
    def get_data(self):
        col_names = [col_display for _, col_display in self.cols]
        header = [self.first_header] + col_names
        body = []
        for base_name, row_display in self.rows:
            stats = self.all_stats.get(base_name, {})
            row_data = [stats.get(attr, '') for attr, _ in self.cols]
            row = [row_display] + row_data
            body.append(row)
        return header, body


class LOCAggregator(SimpleAggregator):
    
    cols = [('lines', 'LOC')]


class TwitterAggregator(LOCAggregator):
    
    rows = [
        ('twitter/twitter_in',          'Social network, Original'),
        ('twitter/twitter_inc',         'Social network, Incremental'),
        ('twitter/twitter_dem',         'Social network, Filtered'),
    ]


stat_aggregations = [
    ('twitter',                         TwitterAggregator),
]

stat_aggregations_dict = dict(stat_aggregations)


def get_table(name, *, all_stats=None,
              format='table'):
    """Show the aggregation table with the given name."""
    if all_stats is None:
        all_stats = do_collections()
    
    if name not in stat_aggregations_dict:
        raise ValueError('Unknown table name: {}'.format(name))
    aggrcls = stat_aggregations_dict[name]
    aggr = aggrcls(all_stats)
    
    if format == 'csv':
        result = aggr.to_csv()
    elif format == 'table':
        result = aggr.to_table()
    elif format == 'latex':
        result = aggr.to_latex()
    else:
        raise ValueError('Unknown format: {}'.format(format))
    
    return result


def run(args):
    chdir(root_path)
    
    parser = argparse.ArgumentParser(prog='view_stats.py')
    parser.add_argument('table', nargs='+')
    parser.add_argument('--format', choices=['csv', 'table', 'latex'],
                        default='table')
    
    ns = parser.parse_args(args)
    
    all_stats = do_collections()
    for name in ns.table:
        print(get_table(name, all_stats=all_stats,
                        format=ns.format))


if __name__ == '__main__':
    run(sys.argv[1:])
