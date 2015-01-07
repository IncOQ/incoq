"""Print and save transformation statistics.

Statistics are stored in a dictionary where the key is the name of
a transformation run, and the value is itself a dictionary from
standard attribute names (such as 'lines') to values.

Operations over a persistent database of statistics is managed by
StatsDB. The notion is that this database can grow and change with
subsequent invocations of the transformation system. The specific
tables of result data to render are configured via the Schema
classes.
"""


__all__ = [
    'BaseSchema',
    'StatkeySchema',
    'StandardSchema',
    
    'BaseStatsDB',
    'StatsDB',
]


import code
import pickle
import os
import csv
import io

try:
    from tabulate import tabulate
    HAVE_TABULATE = True
except ImportError:
    HAVE_TABULATE = False

from invinc.util.collections import SetDict
from invinc.compiler.cost import (add_domain_names, reinterpret_cost,
                                Simplifier, normalize, PrettyPrinter)


class BaseSchema:
    
    """Result table derived from a stats dictionary. Define a new table
    format as a subclass. Produce a table instance by instantiating with
    a stats dict.
    """
    
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
    
    def write_csv(self, outfile):
        """Write the csv-formatted contents of this schema to the given
        file-like object. The file should be opened with newline=''.
        """
        writer = csv.writer(outfile)
        writer.writerow(self.header)
        for line in self.data:
            writer.writerow(line)
    
    def to_ascii(self):
        """Format the data for pretty-printing. Use the tabulate
        library if available, else fall back on csv.
        """
        if HAVE_TABULATE:
            return tabulate(self.data, self.header, tablefmt='grid')
        else:
            filelike = io.StringIO(newline='')
            self.write_csv(filelike)
            return filelike.getvalue()

class StatkeySchema(BaseSchema):
    
    """Table formed by using selected stats keys as rows and stats
    attributes as columns.
    """
    
    rows = []
    """List of stat keys, or None to show all stat keys."""
    cols = []
    """List of stat attributes."""
    
    # Mappings for overriding the display names of rows and columns.
    row_disp = {}
    col_disp = {}
    
    decimal_cols = set()
    """Columns that should be displayed as numbers to the third
    decimal place.
    """
    
    def apply(self, stats):
        header = ['Program']
        header += [self.col_disp.get(c, c) for c in self.cols]
        
        if self.rows is None:
            rows = sorted(stats.keys())
        else:
            rows = self.rows
        body = []
        
        for k in rows:
            name = self.row_disp.get(k, k)
            attrs = stats.get(k, None)
            
            if attrs is not None:
                entries = []
                for c in self.cols:
                    if c in attrs:
                        e = attrs[c]
                        if c in self.decimal_cols:
                            e = format(e, '.3f')
                        entries.append(e)
                    else:
                        entries.append('---')
            
            else:
                name = '(!) ' + name
                entries = ['!' for _ in range(len(self.cols))]
            
            row = [name] + entries
            body.append(row)
        
        return header, body

class StandardSchema(StatkeySchema):
    
    cols = [
        'lines', 'trans time',
        'orig queries', 'orig updates',
        'incr comps', 'incr aggrs',
        'dem structs', 'comps expanded', 'auxmaps'
    ]
    
    col_disp = {
        'lines':          'LOC',
        'trans time':     'Time',
        'orig queries':   'in. queries',
        'orig updates':   'in. updates',
        'incr comps':     'Incr. comps',
        'incr aggrs':     'Incr. aggrs',
        'dem structs':    'Dem invs',
        'comps expanded': 'Comps exp.',
        'auxmaps':        'Maps',
    }
    
    decimal_cols = ['Time']

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


class BaseStatsDB:
    
    """Encapsulates stats schema information and handles persistence.
    Stats are directly exposed as an attribute. Schema classes are
    instantiated upon saving/printing.
    """
    
    db_path = None
    """Directory where results will be persisted."""
    db_name = None
    """Pickle file name."""
    csv_format = None
    """Format for csv files."""
    
    schemas = []
    """List of schemas that can be formed from this data."""
    
    def __init__(self):
        self.stats = {}
    
    def inst_schemas(self):
        return [sch(self.stats) for sch in self.schemas]
    
    def load(self):
        """Load stats from file if it exists."""
        path = os.path.join(self.db_path, self.db_name)
        if os.path.exists(path):
            with open(path, 'rb') as db:
                self.stats = pickle.load(db)
    
    def save(self, print=False):
        """Save stats and csv."""
        insts = self.inst_schemas()
        
        path = os.path.join(self.db_path, self.db_name)
        with open(path, 'wb') as db:
            pickle.dump(self.stats, db)
        
        for inst in insts:
            schema_fn = self.csv_format.format(inst.name)
            with open(schema_fn, 'w', newline='') as outfile:
                inst.write_csv(outfile)
        
        if print:
            self.print(insts=insts)
    
    def print(self, insts=None):
        """Print stats to stdout."""
        if insts is None:
            insts = self.inst_schemas()
        
        for inst in insts:
            print(inst.name)
            print(inst.to_ascii())
    
    def interact(self, edit=None):
        """Open an interactive console session to edit the stats
        database.
        """
        code.interact(banner='Stats editor', local=Session(edit).ns)

class StatsDB(BaseStatsDB):
    
    db_path = os.path.dirname(__file__)
    db_name = 'transstats.pickle'
    csv_format = 'transstats-{}.csv'
    
    class AllSchema(StandardSchema):
        name = 'all'
        rows = None
    
    class SocialSchema(StandardSchema):
        
        name = 'social'
        
        rows = [
            'Ex (Input)',
            'Ex Unfiltered',
            'Ex Filtered',
            'Ex Filtered (aug)',
            'Ex Filtered (DAS)',
            'Ex Filtered (non-inlined)',
            'Ex Filtered (no demand checks)',
            'Ex Filtered (no type checks)',
            'Ex Filtered (no rc elim.)',
        ]
    
    class OIFSchema(OrigIncFilterSchema):
        
        name = 'stats'
        
        # (Not a method.)
        def _rowgen(dispname, name):
            return (dispname, name + ' Input',
                    name + ' Unfiltered', name + ' Filtered')
        
        rows = [
            _rowgen('Social', 'Social'),
            _rowgen('JQLbench1', 'JQL 1'),
            _rowgen('JQLbench2', 'JQL 2'),
            _rowgen('JQLbench3', 'JQL 3'),
            _rowgen('Wifi', 'Wifi'),
            _rowgen('Auth', 'Auth'),
            ('Access', 'CoreRBAC Input',
             'CoreRBAC Unfiltered (CA)', 'CoreRBAC Filtered (CA)'),
            _rowgen('CoreRBAC', 'CoreRBAC'),
            _rowgen('SSD', 'Constr. RBAC'),
            _rowgen('clpaxos', 'clpaxos'),
            _rowgen('crleader', 'crleader'),
            ('dscrash', 'dscrash Input',
             'dscrash Unfiltered', 'dscrash Filtered (obj)'),
            _rowgen('hsleader', 'hsleader'),
            _rowgen('lamutex', 'lamutex'),
            _rowgen('lapaxos', 'lapaxos'),
            _rowgen('ramutex', 'ramutex'),
            _rowgen('2pcommit', '2pcommit'),
        ]
    
    schemas = [
#        AllSchema,
#        SocialSchema,
        OIFSchema,
    ]


class Session:
    
    """Encapsulates shell state and commands. Provides a namespace
    field ns to be used as the local namespace of the interactive
    shell.
    """
    
    def __init__(self, edit=None):
        self.ns = {'statsdb': statsdb,
                   'stats': statsdb.stats}
        # Programmatically add the cmd_* methods to the namespace.
        for method in type(self).__dict__.keys():
            if not method.startswith('cmd_'):
                continue
            cmdname = method[len('cmd_'):]
            self.ns[cmdname] = getattr(self, method)
        
        self.current = None
        """Stat entry currently being examined."""
        
        if edit is not None:
            self.cmd_edit(edit)
    
    def augmented_domains(self):
        # We need to add the equations for dompaths for any relation
        # we talk about, and then resolve the equations.
        # TODO: The dompath equation part should be emitted in the
        # generated domain subst originally, instead of doing it here.
        domainnames = self.ns['domainnames']
        subst = self.ns['domains']
        return add_domain_names(subst, domainnames)
    
    def cmd_edit(self, name):
        import invinc.cost
        
        self.current = name
        
        for k in invinc.cost.cost.__all__:
            self.ns[k] = getattr(invinc.cost, k)
        
        stats = self.ns['stats']
        self.ns['invariants'] = stats[name]['invariants']
        self.ns['funccosts'] = stats[name]['funccosts']
        self.ns['costrules'] = stats[name].setdefault('costrules', {})
        self.ns['domains'] = stats[name]['domain_subst']
        self.ns['domainsizes'] = stats[name].setdefault('domainsizes', {})
        self.ns['domainrules'] = stats[name].setdefault('domainrules', {})
        self.ns['domainnames'] = stats[name].setdefault('domainnames', {})
        self.ns['importantfuncs'] = stats[name].setdefault(
                                        'importantfuncs', [])
        print('Editing ' + name)
    
    def cmd_save(self):
        if self.current is not None:
            # This is to ensure persistent interactive data is saved
            # even if the names get rebound during the session.
            stat_entry = self.ns['stats'][self.current]
            stat_entry['costrules'] = self.ns['costrules']
            stat_entry['domainrules'] = self.ns['domainrules']
            stat_entry['domainsizes'] = self.ns['domainsizes']
            stat_entry['domainnames'] = self.ns['domainnames']
            stat_entry['importantfuncs'] = self.ns['importantfuncs']
        self.ns['statsdb'].save()
        if self.current is not None:
            print('Statsdb saved, interactive data saved')
        else:
            print('Statsdb saved')
    
    def cmd_viewstats(self):
        self.ns['statsdb'].print()
    
    def cmd_viewdomains(self):
        domain_subst = self.augmented_domains()
        
        for k, v in sorted(domain_subst.items(), key=lambda x: str(x[0])):
            print('{:<25}  {}'.format(k, v))
        print()
        
        inv_subst = SetDict()
        for k, v in domain_subst.items():
            inv_subst[v].add(k)
        for k, vs in sorted(inv_subst.items(), key=lambda x: str(x[0])):
            print(k)
            for v in sorted(vs, key=str):
                print('  ' + str(v))
    
    def cmd_viewcosts(self, all=False):
        importantfuncs = self.ns['importantfuncs']
        
        costs = self.ns['funccosts']
        if all:
            costs = sorted(costs.items(), key=lambda x: x[0].lower())
        else:
            costs = [(k, costs[k]) for k in importantfuncs]
        
        domain_subst = self.augmented_domains()
        
        costrules = self.ns['costrules']
        domainsizes = self.ns['domainsizes']
        domainrules = self.ns['domainrules']
        domainnames = self.ns['domainnames']
        invs = self.ns['invariants']
        
        for k, v in costs:
            cost1 = v
            cost2 = reinterpret_cost(cost1,
                                    invs=invs,
#                                    invs={},
                                     domain_subst=domain_subst,
                                     domain_sizes=domainsizes,
                                     domain_costs=domainrules,
                                     domain_names=domainnames)
            cost3 = Simplifier.run(cost2)
            cost4 = normalize(cost3)
            cost5 = PrettyPrinter.run(cost4)
            
            print('    {:<31} O({})'.format(k + ':', cost5))
            
#            print(k)
#            print('    O({})'.format(cost5))
#            print('    O({})\n'
#                  '    O({})\n'
#                  '    O({})\n'
#                  '    O({})\n'
#                  '    O({})'.format(cost1, cost2, cost3,
#                                     cost4, cost5))


if __name__ == '__main__':
    statsdb = StatsDB()
    statsdb.load()
    statsdb.print()
