"""Invoke invinc and maintain the stats database."""


__all__ = [
    'Task',
    'do_tasks',
]


from os.path import normpath, relpath

from simplestruct import Struct, Field, TypedField

from invinc.util.linecount import get_loc_file
from invinc.compiler.incast import print_exc_with_ast
from invinc.compiler.central import transform_file

from .stats import StatsDB


class Task(Struct):
    
    display_name = TypedField(str)
    """Display name for status printing."""
    input_name = TypedField(str)
    """Input filename."""
    output_name = Field()
    """Output filename, or None if no transformation."""
    nopts = Field()
    """Normal options."""
    qopts = Field()
    """Query options."""
    
    def run(self):
        # Dummy case for generating a stats entry for an input file's LOC.
        if self.output_name is None:
            in_loc = get_loc_file(self.input_name)
            stats = {'lines': in_loc}
            return stats
        
        input_name = normpath(relpath(self.input_name))
        output_name = normpath(relpath(self.output_name))
        print('==== Task {:30}{} -> {} ===='.format(
                self.display_name + ': ', input_name, output_name))
        
        try:
            stats = transform_file(self.input_name, self.output_name,
                                   nopts=self.nopts, qopts=self.qopts)
            return stats
        except Exception:
            print_exc_with_ast()
            return None


def do_tasks(tasks):
    statsdb = StatsDB()
    statsdb.load()
    
    for t in tasks:
        cur_stats = t.run()
        if cur_stats is not None:
            # Merge new stats with old. Note that 'costrules' and
            # other persistent interactive data will be left alone.
            stats = statsdb.stats.setdefault(t.display_name, {})
            stats.update(cur_stats)
    
    statsdb.save()
