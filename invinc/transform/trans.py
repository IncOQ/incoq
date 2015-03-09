"""Invoke invinc and maintain the stats database."""


__all__ = [
    'Task',
    'run_task',
    'do_tasks',
    'make_testprogram_task',
    'TaskTemplate',
    'task_from_template',
    
    'make_in_task',
    'COM',
    'AUX',
    'INC',
    'INC_SUBDEM',
    'INC_SUBDEM_OBJ',
    'DEM',
    'DEM_NONINLINE',
    'DEM_NO_TAG_CHECK',
    'DEM_OBJ',
    'DEM_SUBDEM',
]


from os.path import normpath, relpath, join, splitext

from simplestruct import Struct, Field, TypedField

from invinc.util.linecount import get_loc_file
from invinc.compiler.incast import print_exc_with_ast
from invinc.compiler.central import transform_file

from .stats import StatsDB


class Task(Struct):
    
    """A single transformation task."""
    
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


def run_task(task):
    # Dummy case for generating a stats entry for an input file's LOC.
    if task.output_name is None:
        in_loc = get_loc_file(task.input_name)
        stats = {'lines': in_loc}
        return stats
    
    input_name = normpath(relpath(task.input_name))
    output_name = normpath(relpath(task.output_name))
    print('==== Task {:30}{} -> {} ===='.format(
            task.display_name + ': ', input_name, output_name))
    
    try:
        stats = transform_file(task.input_name, task.output_name,
                               nopts=task.nopts, qopts=task.qopts)
        return stats
    except Exception:
        print_exc_with_ast()
        return None


def do_tasks(tasks):
    """Run a sequence of transformation tasks, updating the
    stats database.
    """
    statsdb = StatsDB()
    statsdb.load()
    
    for t in tasks:
        cur_stats = run_task(t)
        if cur_stats is not None:
            statsdb.stats[t.display_name] = cur_stats
    
    statsdb.save()


def make_testprogram_task(prog):
    """Make a Task for transforming a test program. prog is the path
    to the program, relative to the invinc/tests/programs directory,
    excluding the '_in.py' suffix.
    """
    path = join('invinc/tests/programs', prog)
    nopts = {'verbose': True, 'eol': 'lf'}
    return Task(prog, path + '_in.py', path + '_out.py', nopts, {})


class TaskTemplate:
    
    display_suffix = None
    """Suffix appended to display name."""
    
    output_suffix = 'out'
    """Suffix appended to output file name."""
    
    extra_nopts = {}
    """nopts to use. Inherited from base classes as well."""

def task_from_template(task, template):
    display_name = task.display_name
    if template.display_suffix is not None:
        display_name += ' ' + template.display_suffix
    
    output_name = task.output_name
    if template.output_suffix is not None:
        base, ext = splitext(output_name)
        output_name = base + '_' + template.output_suffix + ext
    
    bases = [c for c in template.__mro__
               if issubclass(c, TaskTemplate)]
    nopts = {}
    for c in reversed(bases):
        nopts.update(c.extra_nopts)
    nopts.update(task.nopts)
    
    return task._replace(display_name=display_name,
                         output_name=output_name,
                         nopts=nopts)


def make_in_task(display_name, base_name):
    return Task(display_name + ' Input',
                base_name + '_in.py',
                None, {}, {})


class COM(TaskTemplate):
    extra_nopts = {'verbose': True,
                   'maint_inline': False,
                   'analyze_costs': True,
                   'selfjoin_strat': 'sub',
                   'default_aggr_halfdemand': True,
                   'autodetect_input_rels': True}

class AUX(COM):
    output_suffix = 'aux'
    display_suffix = 'Batch w/ maps'
    extra_nopts = {'default_impl': 'auxonly'}

class INC(COM):
    output_suffix = 'inc'
    display_suffix = 'Unfiltered'
    extra_nopts = {'default_impl': 'inc'}

class INC_SUBDEM(INC):
    extra_nopts = {'subdem_tags': False}

class INC_SUBDEM_OBJ(INC_SUBDEM):
    extra_nopts = {'obj_domain': True}

class DEM(COM):
    output_suffix = 'dem'
    display_suffix = 'Filtered'
    extra_nopts = {'default_impl': 'dem'}

class DEM_NONINLINE(DEM):
    output_suffix = 'dem_noninline'
    display_suffix = 'Filtered (no inline)'
    extra_nopts = {'maint_inline': False}

class DEM_NO_TAG_CHECK(DEM):
    output_suffix = 'dem_notagcheck'
    display_suffix = 'Filtered (no demand checks)'
    extra_nopts = {'tag_checks': False}

class DEM_OBJ(DEM):
    output_suffix = 'dem'
    display_suffix = 'Filtered (obj)'
    extra_nopts = {'obj_domain': True}

class DEM_SUBDEM(DEM):
    output_suffix = 'dem_subdem'
    display_suffix = 'Filtered (alternate subquery demand)'
    extra_nopts = {'subdem_tags': False}
