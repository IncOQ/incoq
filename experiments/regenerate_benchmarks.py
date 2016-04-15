"""Regenerate whole-program tests."""


__all__ = [
    'regenerate_test',
]


import sys
import argparse
from os import chdir
from os.path import dirname, normpath

from incoq.mars.symbol.config import get_argparser, extract_options
from incoq.mars.symbol import S
from incoq.mars import __main__ as main


# Input file, output file, dictionary of config options.
twitter_tasks = [
    ('twitter/twitter_in', 'twitter/twitter_inc',
     {'default_impl': S.Inc}),
    ('twitter/twitter_in', 'twitter/twitter_dem',
     {'default_impl': S.Filtered}),
    
    ('twitter/twitter_in', 'twitter/twitter_dem_notcelim',
     {'default_impl': S.Filtered,
      'elim_type_checks': False}),
    
    ('twitter/twitter_in', 'twitter/twitter_dem_baseline',
     {'default_impl': S.Filtered,
      'inline_maint_code': False,
      'elim_counts': False,
      'elim_dead_relations': False,
      'elim_type_checks': False}),
    ('twitter/twitter_in', 'twitter/twitter_dem_inline',
     {'default_impl': S.Filtered,
      'inline_maint_code': True,
      'elim_counts': False,
      'elim_dead_relations': False,
      'elim_type_checks': False}),
    ('twitter/twitter_in', 'twitter/twitter_dem_rcelim',
     {'default_impl': S.Filtered,
      'inline_maint_code': True,
      'elim_counts': True,
      'elim_dead_relations': False,
      'elim_type_checks': False}),
    ('twitter/twitter_in', 'twitter/twitter_dem_rselim',
     {'default_impl': S.Filtered,
      'inline_maint_code': True,
      'elim_counts': True,
      'elim_dead_relations': True,
      'elim_type_checks': False}),
    ('twitter/twitter_in', 'twitter/twitter_dem_tcelim',
     {'default_impl': S.Filtered,
      'inline_maint_code': True,
      'elim_counts': True,
      'elim_dead_relations': True,
      'elim_type_checks': True}),
    
    ('twitter/twitter_in', 'twitter/twitter_dem_singletag',
     {'default_impl': S.Filtered,
      'use_singletag_demand': True}),
]
wifi_tasks = [
    ('wifi/wifi_in', 'wifi/wifi_inc',
     {'default_impl': S.Inc}),
    ('wifi/wifi_in', 'wifi/wifi_dem',
     {'default_impl': S.Filtered}),
]
django_tasks = [
    ('django/django_in', 'django/django_inc',
     {'default_impl': S.Inc}),
    ('django/django_in', 'django/django_dem',
     {'default_impl': S.Filtered}),
    ('django/django_simp_in', 'django/django_simp_inc',
     {'default_impl': S.Inc}),
    ('django/django_simp_in', 'django/django_simp_dem',
     {'default_impl': S.Filtered}),
]
jql_tasks = [
    ('jql/jql_1_in', 'jql/jql_1_inc',
     {'default_impl': S.Inc}),
    ('jql/jql_1_in', 'jql/jql_1_dem',
     {'default_impl': S.Filtered}),
    ('jql/jql_2_in', 'jql/jql_2_inc',
     {'default_impl': S.Inc}),
    ('jql/jql_2_in', 'jql/jql_2_dem',
     {'default_impl': S.Filtered}),
    ('jql/jql_3_in', 'jql/jql_3_inc',
     {'default_impl': S.Inc}),
    ('jql/jql_3_in', 'jql/jql_3_dem',
     {'default_impl': S.Filtered}),
]
rbac_tasks = [
    ('rbac/corerbac/coreRBAC_in',
     'rbac/corerbac/coreRBAC_checkaccess_inc',
     {'default_impl': S.Inc}),
    ('rbac/corerbac/coreRBAC_in',
     'rbac/corerbac/coreRBAC_checkaccess_dem',
     {'default_impl': S.Filtered}),
    ('rbac/corerbac/coreRBAC_in',
     'rbac/corerbac/coreRBAC_inc',
     {'default_impl': S.Inc, 'auto_query': True}),
    ('rbac/corerbac/coreRBAC_in',
     'rbac/corerbac/coreRBAC_dem',
     {'default_impl': S.Filtered, 'auto_query': True}),
    
    ('rbac/constrainedrbac/crbac_in',
     'rbac/constrainedrbac/crbac_dem',
     {'default_impl': S.Filtered}),
]
graddb_tasks = [
    ('graddb/newstudents/newstu_in',
     'graddb/newstudents/newstu_dem',
     {'obj_domain': True, 'default_impl': S.Filtered}),
    
    ('graddb/queries/advisor_overdue_in',
     'graddb/queries/advisor_overdue_dem',
     {'obj_domain': True, 'default_impl': S.Filtered}),
    ('graddb/queries/advisors_by_student_in',
     'graddb/queries/advisors_by_student_dem',
     {'obj_domain': True, 'default_impl': S.Filtered}),
    ('graddb/queries/cur_stu_in',
     'graddb/queries/cur_stu_dem',
     {'obj_domain': True, 'default_impl': S.Filtered}),
    ('graddb/queries/good_tas_in',
     'graddb/queries/good_tas_dem',
     {'obj_domain': True, 'default_impl': S.Filtered}),
    ('graddb/queries/new_stu_in',
     'graddb/queries/new_stu_dem',
     {'obj_domain': True, 'default_impl': S.Filtered}),
    ('graddb/queries/new_ta_emails_in',
     'graddb/queries/new_ta_emails_dem',
     {'obj_domain': True, 'default_impl': S.Filtered}),
    ('graddb/queries/prelim_exam_overdue_in',
     'graddb/queries/prelim_exam_overdue_dem',
     {'obj_domain': True, 'default_impl': S.Filtered}),
    ('graddb/queries/qual_exam_results_in',
     'graddb/queries/qual_exam_results_dem',
     {'obj_domain': True, 'default_impl': S.Filtered}),
    ('graddb/queries/ta_waitlist_in',
     'graddb/queries/ta_waitlist_dem',
     {'obj_domain': True, 'default_impl': S.Filtered}),
    ('graddb/queries/tas_and_instructors_in',
     'graddb/queries/tas_and_instructors_dem',
     {'obj_domain': True, 'default_impl': S.Filtered}),
]
other_tasks = [
    ('other/bday/bday_in',
     'other/bday/bday_inc',
     {'obj_domain': True, 'default_impl': S.Inc, 'auto_query': True}),
]

task_lists = [
    ('twitter', twitter_tasks),
    ('wifi', wifi_tasks),
    ('django', django_tasks),
    ('jql', jql_tasks),
    ('rbac', rbac_tasks),
    ('graddb', graddb_tasks),
    ('other', other_tasks),
]
task_groups = dict(task_lists)

tasks = [t for _, tasks in task_lists for t in tasks]

tasks_by_target = {t[1]: t for t in tasks}


root_path = normpath(dirname(__file__))


def compile_task(task, *, options=None):
    """Run a benchmark compilation task. Assume the root path is the
    current directory.
    """
    in_name, out_name, task_opts = task
    in_file = in_name + '.py'
    out_file = out_name + '.py'
    stats_file = out_name + '_stats.txt'
    
    opts = options.copy()
    opts.update(task_opts)
    
    print('Regenerating {}...'.format(out_name), flush=True)
    main.invoke(in_file, out_file, options=opts,
                stats_filename=stats_file)


def compile_task_names(target_names, *, options=None):
    """Run the tasks with the given target names."""
    chdir(root_path)
    ts = []
    for name in target_names:
        if name in tasks_by_target:
            ts.append(tasks_by_target[name])
        elif name in task_groups:
            ts.extend(task_groups[name])
        else:
            raise ValueError('Unknown task target "{}"'.format(name))
        
    for t in ts:
        compile_task(t, options=options)


def run(args):
    parent = get_argparser()
    parser = argparse.ArgumentParser(prog='regenerate_benchmarks.py',
                                     parents=[parent])
    parser.add_argument('target_name', nargs='*', default=None)
    
    ns = parser.parse_args(args)
    
    options = extract_options(ns)
    
    if len(ns.target_name) == 0:
        print('No targets specified')
    else:
        compile_task_names(ns.target_name, options=options)


if __name__ == '__main__':
    run(sys.argv[1:])
