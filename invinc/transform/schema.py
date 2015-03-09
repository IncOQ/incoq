"""Define views over stats data to produce tables."""


__all__ = [
    'BaseSchema',
    'StatkeySchema',
    'StandardSchema',
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
        self.header, self.data = self.apply(stats)
    
    def apply(self, stats):
        """Generate a table instance from a stats dict. Return in the
        form of a header (list of strings) and body (2D list of
        values).
        """
        raise NotImplementedError
    
    def to_csv(self):
        """Return this schema in csv format."""
        filelike = io.StringIO(newline='')
        writer = csv.writer(filelike)
        writer.writerow(self.header)
        for line in self.data:
            writer.writerow(line)
        return filelike.getvalue()
    
    def to_ascii(self):
        """Return the schema in pretty-printed format if tabulate
        is available, or csv format otherwise.
        """
        if HAVE_TABULATE:
            return tabulate(self.data, self.header, tablefmt='grid')
        else:
            return self.to_csv()


class StatkeySchema(BaseSchema):
    
    """Table formed by using selected entry keys as rows and stats
    attributes as columns.
    """
    
    rows = []
    """List of pairs: (entry name, display name)."""
    
    cols = []
    """List of triples: (stat name, display name, display format)."""
    
    def apply(self, allstats):
        header = ['Program']
        header += [col_disp for _, col_disp, _ in self.cols]
        
        body = []
        for row_name, row_disp in self.rows:
            stats = allstats.get(row_name, None)
            if stats is not None:
                row = []
                for col_name, col_disp, col_fmt in self.cols:
                    if col_name in stats:
                        if col_fmt is None:
                            col_fmt = ''
                        row.append(format(stats[col_name], col_fmt))
                    else:
                        row.append('---')
            else:
                row_name = '(!) ' + row_name
                row = ['!' for _ in range(len(self.cols))]
            
            row = [row_name] + row
            body.append(row)
        
        return header, body

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

class OrigIncFilterSchema(BaseSchema):
    
    """Produce a table as in the DLS submission."""
    
    rows = []
    row_disp = {}
    
    def apply(self, stats):
        header = ['Name', 'Original LOC', 'Queries', 'Updates',
                  'Inc. LOC', 'Inc. trans. time',
                  'Filtered LOC', 'Filtered trans. time']
        body = []
        
        for name, orig, inc, filt in self.rows:
            if orig in stats:
                orig_lines = stats[orig]['lines']
            else:
                orig_lines = '---'
            
            if inc in stats:
                inc_lines = stats[inc]['lines']
                inc_time = format(stats[inc]['trans time'], '.3f')
                inc_in_queries = stats[inc]['orig queries']
                inc_in_updates = stats[inc]['orig updates']
            else:
                inc_lines = '---'
                inc_time = '---'
                inc_in_queries = None
                inc_in_updates = None
            
            if filt in stats:
                filt_lines = stats[filt]['lines']
                filt_time = format(stats[filt]['trans time'], '.3f')
                filt_in_queries = stats[filt]['orig queries']
                filt_in_updates = stats[filt]['orig updates']
            else:
                filt_lines = '---'
                filt_time = '---'
                filt_in_queries = None
                filt_in_updates = None
            
            def oneof(x, y):
                if x is None:
                    return y
                elif y is None:
                    return x
                else:
                    assert x == y
                    return x
            
            in_queries = oneof(inc_in_queries, filt_in_queries)
            in_updates = oneof(inc_in_updates, filt_in_updates)
            if in_queries is None:
                in_queries = '---'
            if in_updates is None:
                in_updates = '---'
            
            row = [name, orig_lines, in_queries, in_updates,
                   inc_lines, inc_time, filt_lines, filt_time]
            body.append(row)
        
        return header, body
