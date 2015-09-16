"""Invoke incoq and maintain the stats database."""


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
    'INC_NORCELIM_NODRELIM',
    'INC_SUBDEM',
    'INC_SUBDEM_NORCELIM_NODRELIM',
    'INC_SUBDEM_OBJ',
    'DEM',
    'DEM_LRU',
    'DEM_INLINE',
    'DEM_NO_TAG_CHECK',
    'DEM_SINGLE_TAG',
    'DEM_NORCELIM_NODRELIM',
    'DEM_LRU_NORCELIM_NODRELIM',
    'DEM_INLINE_NORCELIM_NODRELIM',
    'DEM_INLINE_NONATIVE_NODRELIM',
    'DEM_INLINE_NODRELIM',
    'DEM_NOTYPECHECK',
    'DEM_INLINE_NOTYPECHECK',
    'DEM_OBJ',
    'DEM_SUBDEM',
    'DEM_OBJ_NS',
    'DEM_OBJ_NS_NORCELIM_NODRELIM',
]


from time import clock
from os.path import normpath, relpath, join, splitext

from simplestruct import Struct, Field, TypedField

from incoq.util.linecount import get_loc_file
from incoq.compiler.incast import print_exc_with_ast
from incoq.compiler.central import transform_file

from .statsdb import StatsDB


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


def do_tasks(tasks, path):
    """Run a sequence of transformation tasks, updating the
    stats database. Return the time elapsed.
    """
    t1 = clock()
    statsdb = StatsDB(path)
    statsdb.load()
    
    for t in tasks:
        cur_stats = run_task(t)
        if cur_stats is not None:
            statsdb.allstats[t.display_name] = cur_stats
    
    statsdb.save()
    t2 = clock()
    return t2 - t1


def make_testprogram_task(prog):
    """Make a Task for transforming a test program. prog is the path
    to the program, relative to the incoq/tests/programs directory,
    excluding the '_in.py' suffix.
    """
    path = join('incoq/tests/programs', prog)
    nopts = {'verbose': True, 'eol': 'lf'}
    return Task(prog, path + '_in.py', path + '_out.py', nopts, {})


class TaskTemplate:
    
    display_suffix = None
    """Suffix appended to display name."""
    
    output_suffix = 'out'
    """Suffix appended to output file name."""
    
    extra_nopts = {}
    """nopts to use. Inherited from base classes as well."""
    
    extra_qopts = {}
    """qopts to use. Inherited from base classes as well."""

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
    
    qopts = {}
    for d in [c.extra_qopts for c in reversed(bases)] + [task.qopts]:
        for q, opts in d.items():
            qopts.setdefault(q, {}).update(opts)
    
    return task._replace(display_name=display_name,
                         output_name=output_name,
                         nopts=nopts,
                         qopts=qopts)


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

class INC_NORCELIM_NODRELIM(INC):
    output_suffix = 'inc_norcelim_nodrelim'
    display_suffix = 'Unfiltered (no rc+dr elim.)'
    extra_nopts = {'rc_elim': False,
                   'deadcode_elim': False}

class INC_SUBDEM(INC):
    extra_nopts = {'subdem_tags': False}

class INC_SUBDEM_NORCELIM_NODRELIM(INC_SUBDEM):
    output_suffix = 'inc_norcelim_nodrelim'
    display_suffix = 'Unfiltered (no rc+dr elim.)'
    extra_nopts = {'rc_elim': False,
                   'deadcode_elim': False}

class INC_SUBDEM_OBJ(INC_SUBDEM):
    extra_nopts = {'obj_domain': True}

class DEM(COM):
    output_suffix = 'dem'
    display_suffix = 'Filtered'
    extra_nopts = {'default_impl': 'dem'}

class DEM_LRU(DEM):
    extra_nopts = {'default_uset_lru': 1}

class DEM_INLINE(DEM):
    output_suffix = 'dem_inline'
    display_suffix = 'Filtered (inlined)'
    extra_nopts = {'maint_inline': True}

class DEM_NO_TAG_CHECK(DEM):
    output_suffix = 'dem_notagcheck'
    display_suffix = 'Filtered (no demand checks)'
    extra_nopts = {'tag_checks': False}

class DEM_SINGLE_TAG(DEM):
    output_suffix = 'dem_singletag'
    display_suffix = 'Filtered (single tag)'
    extra_nopts = {'single_tag': True}

class DEM_NORCELIM_NODRELIM(DEM):
    output_suffix = 'dem_norcelim_nodrelim'
    display_suffix = 'Filtered (no rc+dr elim.)'
    extra_nopts = {'rc_elim': False,
                   'deadcode_elim': False}

class DEM_LRU_NORCELIM_NODRELIM(DEM):
    output_suffix = 'dem_norcelim_nodrelim'
    display_suffix = 'Filtered (no rc+dr elim.)'
    extra_nopts = {'default_uset_lru': 1,
                   'rc_elim': False,
                   'deadcode_elim': False}

class DEM_INLINE_NORCELIM_NODRELIM(DEM):
    output_suffix = 'dem_inline_norcelim_nodrelim'
    display_suffix = 'Filtered (inline; no rc+dr elim.)'
    extra_nopts = {'maint_inline': True,
                   'rc_elim': False,
                   'deadcode_elim': False}

class DEM_INLINE_NONATIVE_NODRELIM(DEM):
    output_suffix = 'dem_inline_nonative_nodrelim'
    display_suffix = 'Filtered (inline; no native+dr elim.)'
    extra_nopts = {'maint_inline': True,
                   'native_sets': False,
                   'deadcode_elim': False}

class DEM_INLINE_NODRELIM(DEM):
    output_suffix = 'dem_inline_nodrelim'
    display_suffix = 'Filtered (inline; no dr elim.)'
    extra_nopts = {'maint_inline': True,
                   'deadcode_elim': False}

class DEM_NOTYPECHECK(DEM):
    output_suffix = 'dem_notypecheck'
    display_suffix = 'Filtered (no type checks)'
    extra_nopts = {'maint_emit_typechecks': False}

class DEM_INLINE_NOTYPECHECK(DEM):
    output_suffix = 'dem_inline_notypecheck'
    display_suffix = 'Filtered (inline; no type checks)'
    extra_nopts = {'maint_inline': True,
                   'maint_emit_typechecks': False}

class DEM_OBJ(DEM):
    output_suffix = 'dem'
    display_suffix = 'Filtered'
    extra_nopts = {'obj_domain': True}

class DEM_SUBDEM(DEM):
    output_suffix = 'dem_subdem'
    display_suffix = 'Filtered'
    extra_nopts = {'subdem_tags': False}

class DEM_OBJ_NS(DEM_OBJ):
    extra_nopts = {'nonstrict_fields': True,
                   'nonstrict_maps': True}

class DEM_OBJ_NS_NORCELIM_NODRELIM(DEM_OBJ_NS):
    output_suffix = 'dem_norcelim_nodrelim'
    display_suffix = 'Filtered (no rc+dr elim.)'
    extra_nopts = {'rc_elim': False,
                   'deadcode_elim': False}
