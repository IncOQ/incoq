"""Define views over stats data to produce tables."""


__all__ = [
    'BaseSchema',
    'StatkeySchema',
    'StandardSchema',
    'GroupedSchema',
    'OrigIncFilterSchema',
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
    
    name = None
    """Name of schema."""
    
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
            return tabulate(self.body, self.header, tablefmt='grid')
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
    
    def get_body(self, allstats):
        body = []
        for row_key, row_disp in self.rows:
            stats = self.get_rowdata(allstats, row_key)
            if stats is not None:
                row = []
                for col_key, col_disp, col_fmt in self.cols:
                    if col_key in stats:
                        if col_fmt is None:
                            col_fmt = ''
                        row.append(format(stats[col_key], col_fmt))
                    else:
                        row.append('---')
            else:
                row_disp = '(!) ' + row_disp
                row = ['!' for _ in range(len(self.cols))]
            
            row = [row_disp] + row
            body.append(row)
        
        return body


class StandardSchema(StatkeySchema):
    
    cols = [
        ('lines', 'LOC', None),
        ('trans time', 'Time', '.3f'),
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
    display name, display format). varient identifier is the
    index of the entry we want to examine from the current group.
    """
    
    def get_rowdata(self, allstats, key):
        # Merge dictionaries for each entry named by the
        # row into a single dict. The keys get augmented
        # with the corresponding entry id.
        rowdata = {}
        for i, entry in enumerate(key):
            stats = allstats.get(entry, {})
            for attr, value in stats.items():
                rowdata[(i, attr)] = value
        return rowdata


class OrigIncFilterSchema(GroupedSchema):
    
    cols = [
        ((0, 'lines'), 'Original LOC', None),
        ((1, 'orig queries'), 'Queries', None),
        ((1, 'orig updates'), 'Updates', None),
        ((1, 'lines'), 'Inc. LOC', None),
        ((1, 'trans time'), 'Inc. trans. time', '.3f'),
        ((2, 'lines'), 'Filtered LOC', None),
        ((2, 'trans time'), 'Filtered trans. time', '.3f'),
    ]
