"""Persistent storage of transformation stats."""


__all__ = [
    'StatsDB',
    'Session',
]


import os
import pickle
import code


class StatsDB:
    
    def __init__(self, path):
        self.path = path
        self.stats = {}
        self.load()
    
    def load(self):
        """Load stats from file if it exists."""
        if os.path.exists(self.path):
            with open(self.path, 'rb') as db:
                self.stats = pickle.load(db)
    
    def save(self):
        """Save stats and csv."""
        with open(self.path, 'wb') as db:
            pickle.dump(self.stats, db)


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
    
    @classmethod
    def interact(cls, statsdb, **kargs):
        """Open an new session for the given database."""
        session = cls(statsdb, **kargs)
        code.interact(banner='Stats editor ({})'.format(statsdb.path),
                      local=session.ns)
    
    def __init__(self, statsdb):
        self.ns = self.Namespace(self)
        self.ns['statsdb'] = statsdb
        self.ns['allstats'] = statsdb.stats
    
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
