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


def latexrow_with_rowfunc(rowfunc):
    """Return a version of tabulate._latex_row() that dispatches to
    a custom function in place of tabulate._build_simple_row().
    """
    from tabulate import LATEX_ESCAPE_RULES, DataRow
    my_escape_rules = dict(LATEX_ESCAPE_RULES)
    del my_escape_rules['~']
    
    def _latex_row(cell_values, colwidths, colaligns):
        """Version of tabulate._latex_row() that dispatches to a local
        hook instead of tabulate()._build_simple_row().
        """
        def escape_char(c):
            return my_escape_rules.get(c, c)
        escaped_values = ["".join(map(escape_char, cell))
                          for cell in cell_values]
        rowfmt = DataRow("", "&", "\\\\")
        return rowfunc(escaped_values, rowfmt)
    
    return _latex_row


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
    ('graddb/queries/advisor_overdue_inc',      statfile_collector),
    ('graddb/queries/advisor_overdue_dem',      statfile_collector),
    ('graddb/queries/advisors_by_student_in',   loc_collector),
    ('graddb/queries/advisors_by_student_inc',  statfile_collector),
    ('graddb/queries/advisors_by_student_dem',  statfile_collector),
    ('graddb/queries/cur_stu_in',               loc_collector),
    ('graddb/queries/cur_stu_inc',              statfile_collector),
    ('graddb/queries/cur_stu_dem',              statfile_collector),
    ('graddb/queries/good_tas_in',              loc_collector),
    ('graddb/queries/good_tas_inc',             statfile_collector),
    ('graddb/queries/good_tas_dem',             statfile_collector),
    ('graddb/queries/new_stu_in',               loc_collector),
    ('graddb/queries/new_stu_inc',              statfile_collector),
    ('graddb/queries/new_stu_dem',              statfile_collector),
    ('graddb/queries/new_ta_emails_in',         loc_collector),
    ('graddb/queries/new_ta_emails_inc',        statfile_collector),
    ('graddb/queries/new_ta_emails_dem',        statfile_collector),
    ('graddb/queries/prelim_exam_overdue_in',   loc_collector),
    ('graddb/queries/prelim_exam_overdue_inc',  statfile_collector),
    ('graddb/queries/prelim_exam_overdue_dem',  statfile_collector),
    ('graddb/queries/qual_exam_results_in',     loc_collector),
    ('graddb/queries/qual_exam_results_inc',    statfile_collector),
    ('graddb/queries/qual_exam_results_dem',    statfile_collector),
    ('graddb/queries/ta_waitlist_in',           loc_collector),
    ('graddb/queries/ta_waitlist_inc',          statfile_collector),
    ('graddb/queries/ta_waitlist_dem',          statfile_collector),
    ('graddb/queries/tas_and_instructors_in',   loc_collector),
    ('graddb/queries/tas_and_instructors_inc',  statfile_collector),
    ('graddb/queries/tas_and_instructors_dem',  statfile_collector),
    
    # ProbInf.
    ('probinf/bday/bday_in',            loc_collector),
    ('probinf/bday/bday_inc',           statfile_collector),
    ('probinf/bday/bday_dem',           statfile_collector),
    ('probinf/bday/bday_obj_in',        loc_collector),
    ('probinf/bday/bday_obj_inc',       statfile_collector),
    ('probinf/bday/bday_obj_dem',       statfile_collector),
    ('probinf/pubauth/pubauth_in',      loc_collector),
    ('probinf/pubauth/pubauth_inc',     statfile_collector),
    ('probinf/pubauth/pubauth_dem',     statfile_collector),
    ('probinf/pubcite/pubcite_in',      loc_collector),
    ('probinf/pubcite/pubcite_inc',     statfile_collector),
    ('probinf/pubcite/pubcite_dem',     statfile_collector),
    
    # DistAlgo.
    ('distalgo/lamutex/lamutex_orig_inc_in',        loc_collector),
    ('distalgo/lamutex/lamutex_orig_inc_out',       statfile_collector),
    ('distalgo/lamutex/lamutex_spec_inc_in',        loc_collector),
    ('distalgo/lamutex/lamutex_spec_inc_out',       statfile_collector),
    ('distalgo/lamutex/lamutex_spec_lam_inc_in',    loc_collector),
    ('distalgo/lamutex/lamutex_spec_lam_inc_out',   statfile_collector),
    
    ('distalgo/clpaxos/clpaxos_inc_in',             loc_collector),
    ('distalgo/clpaxos/clpaxos_inc_out',            statfile_collector),
    ('distalgo/crleader/crleader_inc_in',           loc_collector),
    ('distalgo/crleader/crleader_inc_out',          statfile_collector),
    ('distalgo/dscrash/dscrash_inc_in',             loc_collector),
    ('distalgo/dscrash/dscrash_inc_out',            statfile_collector),
    ('distalgo/hsleader/hsleader_inc_in',           loc_collector),
    ('distalgo/hsleader/hsleader_inc_out',          statfile_collector),
    ('distalgo/lapaxos/lapaxos_inc_in',             loc_collector),
    ('distalgo/lapaxos/lapaxos_inc_out',            statfile_collector),
    ('distalgo/ramutex/ramutex_inc_in',             loc_collector),
    ('distalgo/ramutex/ramutex_inc_out',            statfile_collector),
    ('distalgo/ratoken/ratoken_inc_in',             loc_collector),
    ('distalgo/ratoken/ratoken_inc_out',            statfile_collector),
    ('distalgo/sktoken/sktoken_inc_in',             loc_collector),
    ('distalgo/sktoken/sktoken_inc_out',            statfile_collector),
    ('distalgo/tpcommit/tpcommit_inc_in',           loc_collector),
    ('distalgo/tpcommit/tpcommit_inc_out',          statfile_collector),
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
    bold_firstcol = True
    
    def __init__(self, all_stats):
        self.all_stats = all_stats
        """Map from file name to stats dict for that file."""
    
    def get_data(self):
        """Return a pair of header data (list of values) and body data
        (list of rows, i.e., list of lists of values). Newlines in the
        data will be normalized depending on the output.
        """
        raise NotImplementedError
    
    def normalize_string(self, s, *, latex, align='c', vertalign='c'):
        """If latex is False, turn newlines and tilde into spaces. If
        latex is True, turn newlines into a tabular row and enclose the
        whole string in a tabular environment (if any newlines are
        present), and keep tilde's as-is. Return the new string.
        
        If a non-string value is given, return it as-is.
        """
        if not isinstance(s, str):
            return s
        
        if not latex:
            s = s.replace('\n', ' ')
            s = s.replace('~', ' ')
            return s
        else:
            if '\n' in s:
                new_s = (r'\begin{tabular}[' + vertalign +
                         ']{@{}' + align + '}')
                new_s += s.replace('\n', r'\\')
                new_s += r'\end{tabular}'
                s = new_s
            return s
    
    def normalize_data(self, header, body, **kargs):
        """Apply normalize_string() to a header and body as returned
        by get_data().
        """
        header = [self.normalize_string(s, **kargs) for s in header]
        body = [[self.normalize_string(s, **kargs) for s in line]
                for line in body]
        return header, body
    
    def to_csv(self):
        """Return the data formatted as a CSV string."""
        filelike = io.StringIO(newline='')
        writer = csv.writer(filelike)
        
        header, body = self.get_data()
        header, body = self.normalize_data(header, body, latex=False)
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
        header, body = self.normalize_data(header, body, latex=False)
        return self.tabulate(header, body,
                             tablefmt='simple',
                             floatfmt=self.floatfmt)
    
    def latex_build_headerrow(self, padded_cells, rowfmt):
        """Hook for custom header row behavior."""
        from tabulate import _build_simple_row
        
        padded_cells = [self.normalize_string(cell, latex=True)
                        for cell in padded_cells]
        
        return _build_simple_row(padded_cells, rowfmt)
    
    def latex_build_datarow(self, padded_cells, rowfmt):
        """Hook for custom data row behavior."""
        from tabulate import _build_simple_row
        
        padded_cells = [self.normalize_string(cell, latex=True,
                                              align='l', vertalign='t')
                        for cell in padded_cells]
        
        if self.bold_firstcol:
            first_cell, *remaining_cells = padded_cells
            first_cell = r'\c{' + first_cell.lstrip() + '}'
            padded_cells = [first_cell] + remaining_cells
        
        return _build_simple_row(padded_cells, rowfmt)
    
    def to_latex(self):
        from tabulate import _latex_line_begin_tabular, Line, TableFormat
        latex_table_format = TableFormat(
            lineabove=_latex_line_begin_tabular,
            linebelowheader=Line("\\hline", "", "", ""),
            linebetweenrows=None,
            linebelow=Line("\\hline\n\\end{tabular}", "", "", ""),
            headerrow=latexrow_with_rowfunc(self.latex_build_headerrow),
            datarow=latexrow_with_rowfunc(self.latex_build_datarow),
            padding=1, with_header_hide=None)
        
        header, body = self.get_data()
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


class LOCAggregator(SimpleAggregator):
    cols = [('lines', 'LOC')]

class LOCTimeAggregator(SimpleAggregator):
    cols = [('lines', 'LOC'), ('time', 'Time')]

class CombinedLOCTimeAggregator(CombinedAggregator):
    cols = [
        (0, 'lines', 'Orig.\nLOC'),
        (1, 'queries_input', '# queries'),
        (1, 'updates_input', '# updates'),
        (1, 'lines', 'Inc.\nLOC'),
        (1, 'time', 'Inc.\nTime'),
        (2, 'lines', 'Filt.\nLOC'),
        (2, 'time', 'Filt.\nTime'),
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
         'Django,\n~simplified'),
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

class GradDBAggregator(CombinedAggregator):
    
    cols = [
        (0, 'updatekinds_input', 'Update\nkinds'),
        (0, 'time', 'Inc.\nTime'),
        (0, 'lines', 'Inc.\nLines'),
        (0, 'ast_nodes', 'Inc.\nAST nodes'),
        (1, 'time', 'Filt.\nTime'),
        (1, 'lines', 'Filt.\nLines'),
        (1, 'ast_nodes', 'Filt.\nAST nodes'),
    ]
    
    equalities = [
        ((0, 'updatekinds_input'), (1, 'updatekinds_input')),
    ]
    
    _rows = [
        ('cur_stu',                     'Current Students'),
        ('new_stu',                     'New Students'),
        ('tas_and_instructors',         'TAs and Instructors'),
        ('new_ta_emails',               'New TA Emails'),
        ('ta_waitlist',                 'TA Waitlist'),
        ('good_tas',                    'Good TAs'),
        ('qual_exam_results',           'Qual Exam Results'),
        ('advisors_by_student',         'Advisors by Student'),
        ('advisor_overdue',             'Advisor Overdue'),
        ('prelim_exam_overdue',         'Prelim Exam Overdue'),
    ]
    
    @property
    def rows(self):
        return [(['graddb/queries/' + base + '_inc',
                  'graddb/queries/' + base + '_dem'], display)
                for base, display in self._rows]

class ProbInfAggregator(CombinedLOCTimeAggregator):
    
    rows = [
#        (['probinf/bday/bday_in',
#          'probinf/bday/bday_inc',
#          'probinf/bday/bday_dem'],
#         'Birthday'),
        (['probinf/bday/bday_obj_in',
          'probinf/bday/bday_obj_inc',
          'probinf/bday/bday_obj_dem'],
         'Birthday'),
        (['probinf/pubauth/pubauth_in',
          'probinf/pubauth/pubauth_inc',
          'probinf/pubauth/pubauth_dem'],
         'Publications'),
        (['probinf/pubcite/pubcite_in',
          'probinf/pubcite/pubcite_inc',
          'probinf/pubcite/pubcite_dem'],
         'Citations'),
    ]

class DistAlgoAggregator(CombinedAggregator):
    cols = [
        (0, 'lines', 'Orig.\nLOC'),
        (1, 'queries_input', '# queries'),
        (1, 'updates_input', '# updates'),
        (1, 'lines', 'Trans.\nLOC'),
        (1, 'time', 'Trans.\nTime'),
    ]
    _rows1 = [
        'clpaxos',
        'crleader',
        'dscrash',
        'hsleader',
    ]
    _rows2 = [
        'lapaxos',
        'ramutex',
        'ratoken',
        'sktoken',
        'tpcommit',
    ]
    @property
    def rows(self):
        rows1 = [(['distalgo/{0}/{0}_inc_in'.format(name),
                   'distalgo/{0}/{0}_inc_out'.format(name)],
                  name)
                 for name in self._rows1]
        rows2 = [(['distalgo/{0}/{0}_inc_in'.format(name),
                   'distalgo/{0}/{0}_inc_out'.format(name)],
                  name)
                 for name in self._rows2]
        rows_lamutex = [(['distalgo/lamutex/lamutex_orig_inc_in',
                          'distalgo/lamutex/lamutex_orig_inc_out'],
                         'lamutex_orig'),
                        (['distalgo/lamutex/lamutex_spec_inc_in',
                          'distalgo/lamutex/lamutex_spec_inc_out'],
                         'lamutex_spec'),
                        (['distalgo/lamutex/lamutex_spec_lam_inc_in',
                          'distalgo/lamutex/lamutex_spec_lam_inc_out'],
                         'lamutex_spec_lam')]
        return rows1 + rows_lamutex + rows2

aggregations = [
    ('twitter',                         TwitterAggregator),
    ('twitter_opt',                     TwitterOptAggregator),
    ('wifi',                            WifiAggregator),
    ('django',                          DjangoAggregator),
    ('jql',                             JQLAggregator),
    ('comparisons',                     ComparisonsAggregator),
    ('comparisons_combined',            CombinedComparisonsAggregator),
    ('rbac',                            RBACAggregator),
    ('graddb',                          GradDBAggregator),
    ('probinf',                         ProbInfAggregator),
    ('distalgo',                        DistAlgoAggregator),
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
