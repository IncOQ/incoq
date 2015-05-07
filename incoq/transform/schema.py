"""Define views over stats data to produce tables."""


__all__ = [
    'BaseSchema',
    'StatkeySchema',
    'StandardSchema',
    'GroupedSchema',
    'OrigIncFilterSchema',
    'CostSchema',
]


import io
import csv

try:
    from tabulate import tabulate
    HAVE_TABULATE = True
except ImportError:
    HAVE_TABULATE = False


class BaseSchema:
    
    """View derived from an allstats dictionary."""
    
    def __init__(self, stats):
        self.header = self.get_header()
        self.body = self.get_body(stats)
    
    def get_header(self):
        """Return the header (list of strings)."""
        raise NotImplementedError
    
    def get_body(self, stats):
        """Generate a table instance from a stats dict. Return the body
        (2D list of values.)
        """
        raise NotImplementedError
    
    def to_csv(self):
        """Return this schema in csv format."""
        filelike = io.StringIO(newline='')
        writer = csv.writer(filelike)
        writer.writerow(self.header)
        for line in self.body:
            writer.writerow(line)
        return filelike.getvalue()
    
    def to_ascii(self):
        """Return the schema in pretty-printed format if tabulate
        is available, or csv format otherwise.
        """
        if HAVE_TABULATE:
            return tabulate(self.body, self.header, floatfmt='.2f')
        else:
            return self.to_csv()
    
    def save_csv(self, name):
        with open(name, 'wt') as file:
            file.write(self.to_csv())


class StatkeySchema(BaseSchema):
    
    """Table formed by using selected entry keys as rows and stats
    attributes as columns.
    """
    
    rows = []
    """List of pairs: (entry name, display name)."""
    
    cols = []
    """List of triples: (stat name, display name, display format)."""
    
    def get_header(self):
        return ['Program'] + [col_disp for _, col_disp, _ in self.cols]
    
    def get_rowdata(self, allstats, key):
        """Hook for modifying how rows are retrieved."""
        return allstats.get(key, None)
    
    def get_coldata(self, stats, key):
        return stats.get(key, None)
    
    def get_body(self, allstats):
        body = []
        for row_key, row_disp in self.rows:
            stats = self.get_rowdata(allstats, row_key)
            if stats is not None:
                row = []
                for col_key, col_disp, col_fmt in self.cols:
                    col_data = self.get_coldata(stats, col_key)
                    if col_data is not None:
                        if col_fmt is None:
                            col_fmt = ''
                        row.append(format(col_data, col_fmt))
                    else:
                        row.append(None)
            else:
                row_disp = '(!) ' + row_disp
                row = ['!' for _ in range(len(self.cols))]
            
            row = [row_disp] + row
            body.append(row)
        
        return body


class StandardSchema(StatkeySchema):
    
    cols = [
        ('lines', 'LOC', None),
        ('trans time', 'Time', '.2f'),
        ('orig queries', 'in. queries', None),
        ('orig updates', 'in. updates', None),
        ('incr comps', 'Incr. comps', None),
        ('incr aggrs', 'Incr. aggrs', None),
        ('dem structs', 'Dem invs', None),
        ('comps expanded', 'Comps exp.', None),
        ('auxmaps', 'Maps', None),
    ]


class GroupedSchema(StatkeySchema):
    
    """Schema that groups data from multiple entries."""
    
    rows = []
    """List of pairs: (group, display name), where group is
    a list of entries.
    """
    
    cols = []
    """List of quadruples: (variant identifier, stat name,
    display name, display format). variant identifier is the
    index of the entry we want to examine from the current group.
    """
    
    equalities = []
    """List of pairs of merged entries that should be equal."""
    
    def get_rowdata(self, allstats, key):
        # Merge dictionaries for each entry named by the
        # row into a single dict. The keys get augmented
        # with the corresponding entry id.
        rowdata = {}
        for i, entry in enumerate(key):
            stats = allstats.get(entry, {})
            for attr, value in stats.items():
                rowdata[(i, attr)] = value
        for lhs, rhs in self.equalities:
            if lhs in rowdata and rhs in rowdata:
                assert rowdata[lhs] == rowdata[rhs]
        return rowdata


class OrigIncFilterSchema(GroupedSchema):
    
    # Pull orig queries/updates from dem in case inc is missing.
    cols = [
        ((0, 'lines'), 'Original LOC', None),
        ((2, 'orig queries'), 'Queries', None),
        ((2, 'orig updates'), 'Updates', None),
        ((1, 'lines'), 'Inc. LOC', None),
        ((1, 'trans time'), 'Inc. trans. time', '.2f'),
        ((2, 'lines'), 'Filtered LOC', None),
        ((2, 'trans time'), 'Filtered trans. time', '.2f'),
    ]
    
    # Number of queries/updates should agree between inc and dem.
    equalities = [
        ((1, 'orig queries'), (2, 'orig queries')),
        ((1, 'orig updates'), (2, 'orig updates')),
    ]


class CostSchema(StatkeySchema):
    
    """Table of costs."""
    
    rows = []
    """List of pairs: (entry name, display name)."""
    
    cols = []
    """List of triples: (function name, display name, display format)."""
    
    def get_coldata(self, stats, key):
        from incoq.compiler.cost import PrettyPrinter
        cost = stats.get('costs', {}).get(key, None)
        if cost is None:
            return None
        coststr = PrettyPrinter.run(cost)
        return 'O({})'.format(coststr)
