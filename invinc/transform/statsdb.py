"""Persistent storage of transformation stats."""


__all__ = [
    'StatsDB',
    'BaseSession',
    'Session',
]


import os
import pickle
import code


try:
    from tabulate import tabulate
    HAVE_TABULATE = True
except ImportError:
    HAVE_TABULATE = False


class StatsDB:
    
    """A collection of transformation stats and an associated path
    to a persistent file. Stats are represented as a mapping from
    an entry name (the display name for that particular transformation)
    to a stats dictionary (as returned by the compiler).
    """
    
    def __init__(self, path):
        self.path = path
        self.allstats = {}
        self.load()
    
    def load(self):
        """Load stats from file if it exists."""
        if os.path.exists(self.path):
            with open(self.path, 'rb') as db:
                self.allstats = pickle.load(db)
    
    def save(self):
        """Save stats and csv."""
        with open(self.path, 'wb') as db:
            pickle.dump(self.allstats, db)


class BaseSession:
    
    """Encapsulates shell state and commands. Provides a namespace
    field ns to be used as the local namespace of the interactive
    shell. Commands are methods beginning with "cmd_"; this prefix
    is stripped in the session.
    """
    
    class Namespace(dict):
        
        def __init__(self, session):
            self.session = session
        
        def __missing__(self, key):
            cmd = getattr(self.session, 'cmd_' + key, None)
            if cmd is not None:
                return cmd
            raise KeyError(key)
    
    def __init__(self, statsdb):
        self.ns = self.Namespace(self)
        self.ns['statsdb'] = statsdb
        self.ns['allstats'] = statsdb.allstats
    
    def interact(self):
        """Enter an interactive session until the user types exit()."""
        banner = 'Stats editor ({})'.format(self.ns['statsdb'].path)
        try:
            code.interact(banner=banner, local=self.ns)
        except SystemExit:
            pass
    
    def cmd_reload(self):
        self.ns['statsdb'].load()
        print('Statsdb reloaded')
    
    def cmd_save(self):
        self.ns['statsdb'].save()
        print('Statsdb saved')
    
#    def cmd_viewstats(self):
#        self.ns['statsdb'].print()


class Session(BaseSession):
    
    def __init__(self, statsdb, name=None):
        super().__init__(statsdb)
        if name is not None:
            self.cmd_switch(name)
    
    def cmd_showentries(self):
        for k in sorted(self.ns['allstats'].keys()):
            print(k)
    
    def cmd_showstats(self):
        for k, v in sorted(self.ns['stats'].items()):
            print('{:<20}  {}'.format(k + ':', v))
    
    def cmd_switch(self, name):
        self.ns['stats'] = self.ns['allstats'][name]
    
    def cmd_showcosts(self, name=None):
        if name is not None:
            stats = self.ns['allstats'][name]
        else:
            stats = self.ns['stats']
        rows = []
        from invinc.compiler.cost import PrettyPrinter
        for func, cost in sorted(stats['costs'].items()):
            coststr = 'O({})'.format(PrettyPrinter.run(cost))
            rows.append([func, coststr])
        
        if HAVE_TABULATE:
            print(tabulate(rows, tablefmt='grid'))
        else:
            print('\n'.join('{:<20}  {}'.format(f + ':', c)
                            for f, c in rows))
