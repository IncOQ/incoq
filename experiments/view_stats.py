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
    import tabulate
    HAVE_TABULATE = True
except ImportError:
    HAVE_TABULATE = False

from incoq.util.linecount import get_loc_source


root_path = normpath(dirname(__file__))


# Custom TableFormat for Latex output that differs from the default
# 'latex' format.
def build_latex_table_format():
    from tabulate import (_latex_line_begin_tabular, Line,
                          _latex_row, TableFormat, LATEX_ESCAPE_RULES,
                          DataRow, _build_simple_row)
    
    # Provide our own version of _build_simple_row() that bolds the
    # first entry in teletype using our \c{} macro.
    def _bolded_build_simple_row(padded_cells, rowfmt):
        begin, sep, end = rowfmt
        
        first_cell, *data_cells = padded_cells
        first_cell = r'\c{' + first_cell + r'}'
        padded_cells = [first_cell] + data_cells
        
        return (begin + sep.join(padded_cells) + end).rstrip()
    
    # Provide our own version of _latex_row() that uses this function.
    def _bolded_latex_row(cell_values, colwidths, colaligns):
        def escape_char(c):
            return LATEX_ESCAPE_RULES.get(c, c)
        escaped_values = ["".join(map(escape_char, cell))
                          for cell in cell_values]
        rowfmt = DataRow("", "&", "\\\\")
        return _bolded_build_simple_row(escaped_values, rowfmt)
    
    # A version of _latex_row() that doesn't escape things.
    def _unescaped_latex_row(cell_values, colwidths, colaligns):
        rowfmt = DataRow("", "&", "\\\\")
        return _build_simple_row(cell_values, rowfmt)
    
    # Use tabulate's latex format, except use _my_latex_row for the datarow.
    return TableFormat(lineabove=_latex_line_begin_tabular,
                       linebelowheader=Line("\\hline", "", "", ""),
                       linebetweenrows=None,
                       linebelow=Line("\\hline\n\\end{tabular}", "", "", ""),
                       headerrow=_unescaped_latex_row,
                       datarow=_bolded_latex_row,
                       padding=1, with_header_hide=None)

latex_table_format = build_latex_table_format()


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


collections = [
    # Twitter.
    ('twitter/twitter_in',              loc_collector),
    ('twitter/twitter_inc',             statfile_collector),
    ('twitter/twitter_dem',             statfile_collector),
    ('twitter/twitter_dem_notcelim',    statfile_collector),
    ('twitter/twitter_dem_baseline',    statfile_collector),
    ('twitter/twitter_dem_inline',      statfile_collector),
    ('twitter/twitter_dem_rcelim',      statfile_collector),
    ('twitter/twitter_dem_rselim',      statfile_collector),
    ('twitter/twitter_dem_tcelim',      statfile_collector),
    ('twitter/twitter_dem_mcelim',      loc_collector),
    ('twitter/twitter_dem_singletag',   statfile_collector),
    
    # Wifi.
    ('wifi/wifi_in',                    loc_collector),
    ('wifi/wifi_inc',                   statfile_collector),
    ('wifi/wifi_dem',                   statfile_collector),
    
    # Django.
    ('django/django_in',                loc_collector),
    ('django/django_inc',               statfile_collector),
    ('django/django_dem',               statfile_collector),
    ('django/django_simp_in',           loc_collector),
    ('django/django_simp_inc',          statfile_collector),
    ('django/django_simp_dem',          statfile_collector),
    
    # JQL.
    ('jql/jql_1_in',                    loc_collector),
    ('jql/jql_1_inc',                   statfile_collector),
    ('jql/jql_1_dem',                   statfile_collector),
    ('jql/jql_2_in',                    loc_collector),
    ('jql/jql_2_inc',                   statfile_collector),
    ('jql/jql_2_dem',                   statfile_collector),
    ('jql/jql_3_in',                    loc_collector),
    ('jql/jql_3_inc',                   statfile_collector),
    ('jql/jql_3_dem',                   statfile_collector),
    
    # RBAC.
    ('rbac/corerbac/coreRBAC_in',               loc_collector),
    ('rbac/corerbac/coreRBAC_checkaccess_inc',  statfile_collector),
    ('rbac/corerbac/coreRBAC_checkaccess_dem',  statfile_collector),
    ('rbac/corerbac/coreRBAC_inc',              statfile_collector),
    ('rbac/corerbac/coreRBAC_dem',              statfile_collector),
    ('rbac/constrainedrbac/crbac_in',           loc_collector),
    ('rbac/constrainedrbac/crbac_aux',          statfile_collector),
    ('rbac/constrainedrbac/crbac_inc',          statfile_collector),
    ('rbac/constrainedrbac/crbac_dem',          statfile_collector),
    
    # GradDB.
    ('graddb/newstudents/newstu_in',            loc_collector),
    ('graddb/newstudents/newstu_dem',           statfile_collector),
    ('graddb/queries/advisor_overdue_in',       loc_collector),
    ('graddb/queries/advisor_overdue_dem',      statfile_collector),
    ('graddb/queries/advisors_by_student_in',   loc_collector),
    ('graddb/queries/advisors_by_student_dem',  statfile_collector),
    ('graddb/queries/cur_stu_in',               loc_collector),
    ('graddb/queries/cur_stu_dem',              statfile_collector),
    ('graddb/queries/good_tas_in',              loc_collector),
    ('graddb/queries/good_tas_dem',             statfile_collector),
    ('graddb/queries/new_stu_in',               loc_collector),
    ('graddb/queries/new_stu_dem',              statfile_collector),
    ('graddb/queries/new_ta_emails_in',         loc_collector),
    ('graddb/queries/new_ta_emails_dem',        statfile_collector),
    ('graddb/queries/prelim_exam_overdue_in',   loc_collector),
    ('graddb/queries/prelim_exam_overdue_dem',  statfile_collector),
    ('graddb/queries/qual_exam_results_in',     loc_collector),
    ('graddb/queries/qual_exam_results_dem',    statfile_collector),
    ('graddb/queries/ta_waitlist_in',           loc_collector),
    ('graddb/queries/ta_waitlist_dem',          statfile_collector),
    ('graddb/queries/tas_and_instructors_in',   loc_collector),
    ('graddb/queries/tas_and_instructors_dem',  statfile_collector),
    
    # ProbInf.
    ('probinf/bday/bday_in',            loc_collector),
    ('probinf/bday/bday_inc',           statfile_collector),
    ('probinf/bday/bday_dem',           statfile_collector),
    ('probinf/pubauth/pubauth_in',      loc_collector),
    ('probinf/pubauth/pubauth_inc',     statfile_collector),
    ('probinf/pubauth/pubauth_dem',     statfile_collector),
    ('probinf/pubcite/pubcite_in',      loc_collector),
    ('probinf/pubcite/pubcite_inc',     statfile_collector),
    ('probinf/pubcite/pubcite_dem',     statfile_collector),
]


def do_collections():
    """Return an all_stats dict, mapping from each file name to a stats
    dict.
    """
    all_stats = {}
    for base_name, collector in collections:
        stats = collector(base_name)
        all_stats[base_name] = stats
    return all_stats


class BaseAggregator:
    
    """Base class for aggregators."""
    
    floatfmt = '.2f'
    
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
    
    def tabulate(self, header, body, **kargs):
        """Return the data formatted using tabulate."""
        if not HAVE_TABULATE:
            raise ImportError('Tabulate library not available')
        return tabulate.tabulate(body, header, **kargs)
    
    def to_table(self):
        header, body = self.get_data()
        return self.tabulate(header, body,
                             tablefmt='simple',
                             floatfmt=self.floatfmt)
    
    def latex_header_hook(self, header):
        """Hook for modifying header for formatting in latex output."""
        return header
    
    def to_latex(self):
        header, body = self.get_data()
        header = self.latex_header_hook(header)
        return self.tabulate(header, body,
                             tablefmt=latex_table_format,
                             floatfmt=self.floatfmt)
    
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
            row_data = [stats.get(attr, None) for attr, _ in self.cols]
            row = [row_display] + row_data
            body.append(row)
        return header, body


class CombinedAggregator(BaseAggregator):
    
    """Aggregator that allows a single row to contain data from multiple
    collections.
    """
    
    @property
    def first_header(self):
        """Name to use for the top-left cell."""
        return 'Program'
    
    @property
    def cols(self):
        """Return a list of triples of an index of a filename, a stat
        attribute to look up, and a name to display the attribute as.
        The index corresponds to the entry in the tuple for the row.
        """
        raise NotImplementedError
    
    @property
    def rows(self):
        """Return a list of pairs of a tuple of file names whose stats
        are displayed, and the name to use for that row heading. The
        tuple indices are used in cols to identify what file a column
        refers to.
        """
        raise NotImplementedError
    
    @property
    def equalities(self):
        """Equalities to enforce in the stat data. Return a list of
        pairs of column pairs that are constrained to have the same
        value. Each column pair is a tuple indexing into a row's
        sequence of file names, and a stat key. get_data() will raise
        an AssertionError if any equality does not hold.
        """
        return []
    
    def get_data(self):
        col_names = [col_display for _, _, col_display in self.cols]
        header = [self.first_header] + col_names
        body = []
        for base_names, row_display in self.rows:
            row_stats = [self.all_stats.get(bn, {})
                         for bn in base_names]
            row_data = [row_stats[ind].get(attr, None)
                        for ind, attr, _ in self.cols]
            row = [row_display] + row_data
            body.append(row)
            # Check equalities.
            for eq in self.equalities:
                (l_ind, l_attr), (r_ind, r_attr) = eq
                left = row_stats[l_ind].get(l_attr, None)
                right = row_stats[r_ind].get(r_attr, None)
                if left != right:
                    raise AssertionError('Unequal values for stat keys {}:{} '
                                         'and {}:{}'.format(
                                         base_names[l_ind], l_attr,
                                         base_names[r_ind], r_attr))
        return header, body
    
    twoline_header = True
    
    def latex_header_hook(self, header):
        # Make LOC/Time column headers take up two lines.
        if self.twoline_header:
            new_header = []
            for h in header:
                i = h.find(' LOC')
                if i == -1:
                    i = h.find(' Time')
                if i == -1:
                    new_header.append(h)
                else:
                    new_header.append(r'\begin{{tabular}}{{c}}{}\\{}'
                                      r'\end{{tabular}}'
                                      .format(h[:i], h[i+1:]))
            return new_header
        else:
            return header


class LOCAggregator(SimpleAggregator):
    cols = [('lines', 'LOC')]

class LOCTimeAggregator(SimpleAggregator):
    cols = [('lines', 'LOC'), ('time', 'Time')]

class CombinedLOCTimeAggregator(CombinedAggregator):
    cols = [
        (0, 'lines', 'Orig. LOC'),
        (1, 'queries_input', r'\# queries'),
        (1, 'updates_input', r'\# updates'),
        (1, 'lines', 'Inc. LOC'),
        (1, 'time', 'Inc. Time'),
        (2, 'lines', 'Filt. LOC'),
        (2, 'time', 'Filt. Time'),
    ]
    equalities = [
        ((1, 'queries_input'), (2, 'queries_input')),
        ((1, 'updates_input'), (2, 'updates_input')),
    ]


class TwitterAggregator(LOCTimeAggregator):
    
    rows = [
        ('twitter/twitter_in',          'Original'),
        ('twitter/twitter_inc',         'Incremental'),
        ('twitter/twitter_dem',         'Filtered'),
        ('twitter/twitter_dem_notcelim', 'Filtered (w/ type checks)'),
        ('twitter/twitter_dem_singletag', 'Filtered (OSQ strategy)'),
    ]

class TwitterOptAggregator(LOCTimeAggregator):
    
    rows = [
        ('twitter/twitter_dem_baseline', 'Unoptimized'),
        ('twitter/twitter_dem_inline',  'Inlining'),
        ('twitter/twitter_dem_rcelim',  'Counting elim'),
        ('twitter/twitter_dem_rselim',  'Result set elim'),
        ('twitter/twitter_dem_tcelim',  'Type check elim'),
        ('twitter/twitter_dem_mcelim',  'Maint case elim'),
    ]

class WifiAggregator(LOCTimeAggregator):
    
    rows = [
        ('wifi/wifi_in',                'Wifi, Original'),
        ('wifi/wifi_inc',               'Wifi, Incremental'),
        ('wifi/wifi_dem',               'Wifi, Filtered'),
    ]

class DjangoAggregator(LOCTimeAggregator):
    
    rows = [
        ('django/django_in',            'Django, Original'),
        ('django/django_inc',           'Django, Incremental'),
        ('django/django_dem',           'Django, Filtered'),
        ('django/django_simp_in',       'Django simplified, Original'),
        ('django/django_simp_inc',      'Django simplified, Incremental'),
        ('django/django_simp_dem',      'Django simplified, Filtered'),
    ]

class JQLAggregator(LOCTimeAggregator):
    
    rows = [
        ('jql/jql_1_in',                'JQL 1, Original'),
        ('jql/jql_1_inc',               'JQL 1, Incremental'),
        ('jql/jql_1_dem',               'JQL 1, Filtered'),
        ('jql/jql_2_in',                'JQL 2, Original'),
        ('jql/jql_2_inc',               'JQL 2, Incremental'),
        ('jql/jql_2_dem',               'JQL 2, Filtered'),
        ('jql/jql_3_in',                'JQL 3, Original'),
        ('jql/jql_3_inc',               'JQL 3, Incremental'),
        ('jql/jql_3_dem',               'JQL 3, Filtered'),
    ]

class ComparisonsAggregator(LOCTimeAggregator):
    
    @property
    def rows(self):
        return (WifiAggregator.rows +
                DjangoAggregator.rows +
                JQLAggregator.rows)

class CombinedComparisonsAggregator(CombinedLOCTimeAggregator):
    
    rows = [
        (['wifi/wifi_in',
          'wifi/wifi_inc',
          'wifi/wifi_dem'],
         'Wifi'),
        (['django/django_in',
          'django/django_inc',
          'django/django_dem'],
         'Django'),
        (['django/django_simp_in',
          'django/django_simp_inc',
          'django/django_simp_dem'],
         'Django (simp)'),
        (['jql/jql_1_in',
          'jql/jql_1_inc',
          'jql/jql_1_dem'],
         'JQL 1'),
        (['jql/jql_2_in',
          'jql/jql_2_inc',
          'jql/jql_2_dem'],
         'JQL 2'),
        (['jql/jql_3_in',
          'jql/jql_3_inc',
          'jql/jql_3_dem'],
         'JQL 3'),
    ]

class RBACAggregator(LOCTimeAggregator):
    
    rows = [
        ('rbac/corerbac/coreRBAC_in',
         'RBAC, Original'),
        ('rbac/corerbac/coreRBAC_checkaccess_inc', 
         'RBAC, Incremental (CheckAccess)'),
        ('rbac/corerbac/coreRBAC_checkaccess_dem', 
         'RBAC, Filtered (CheckAccess)'),
        ('rbac/corerbac/coreRBAC_inc', 
         'RBAC, Incremental (all)'),
        ('rbac/corerbac/coreRBAC_dem', 
         'RBAC, Filtered (all)'),
        ('rbac/constrainedrbac/crbac_in',
         'Constrained RBAC, Original'),
        ('rbac/constrainedrbac/crbac_aux',
         'Constrained RBAC, Auxmap'),
        ('rbac/constrainedrbac/crbac_inc',
         'Constrained RBAC, Incremental'),
        ('rbac/constrainedrbac/crbac_dem',
         'Constrained RBAC, Filtered'),
    ]

aggregations = [
    ('twitter',                         TwitterAggregator),
    ('twitter_opt',                     TwitterOptAggregator),
    ('wifi',                            WifiAggregator),
    ('django',                          DjangoAggregator),
    ('jql',                             JQLAggregator),
    ('comparisons',                     ComparisonsAggregator),
    ('comparisons_combined',            CombinedComparisonsAggregator),
    ('rbac',                            RBACAggregator),
]

aggregations_dict = dict(aggregations)


def get_table(name, *, all_stats=None,
              format='table'):
    """Show the aggregation table with the given name."""
    if all_stats is None:
        all_stats = do_collections()
    
    if name not in aggregations_dict:
        raise ValueError('Unknown table name: {}'.format(name))
    aggrcls = aggregations_dict[name]
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
