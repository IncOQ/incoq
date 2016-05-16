"""Regenerate whole-program tests."""


__all__ = [
    'regenerate_test',
]


import sys
import argparse
from os import chdir
from os.path import dirname, normpath
from itertools import chain

from incoq.compiler import get_argparser, extract_options, invoke


# Input file, output file, dictionary of config options.
# The third component may also be a pair of a dictionary of config
# options and a dictionary of query options (i.e., a mapping from
# query name to another dictionary).

twitter_tasks = [
    ('twitter/twitter_in', 'twitter/twitter_inc',
     {'default_impl': 'inc'}),
    ('twitter/twitter_in', 'twitter/twitter_dem',
     {'default_impl': 'filtered'}),
    
    ('twitter/twitter_in', 'twitter/twitter_dem_notcelim',
     {'default_impl': 'filtered',
      'elim_type_checks': 'false'}),
    
    ('twitter/twitter_in', 'twitter/twitter_dem_baseline',
     {'default_impl': 'filtered',
      'inline_maint_code': 'false',
      'elim_counts': 'false',
      'elim_dead_relations': 'false',
      'elim_type_checks': 'false'}),
    ('twitter/twitter_in', 'twitter/twitter_dem_inline',
     {'default_impl': 'filtered',
      'inline_maint_code': 'true',
      'elim_counts': 'false',
      'elim_dead_relations': 'false',
      'elim_type_checks': 'false'}),
    ('twitter/twitter_in', 'twitter/twitter_dem_rcelim',
     {'default_impl': 'filtered',
      'inline_maint_code': 'true',
      'elim_counts': 'true',
      'elim_dead_relations': 'false',
      'elim_type_checks': 'false'}),
    ('twitter/twitter_in', 'twitter/twitter_dem_rselim',
     {'default_impl': 'filtered',
      'inline_maint_code': 'true',
      'elim_counts': 'true',
      'elim_dead_relations': 'true',
      'elim_type_checks': 'false'}),
    ('twitter/twitter_in', 'twitter/twitter_dem_tcelim',
     {'default_impl': 'filtered',
      'inline_maint_code': 'true',
      'elim_counts': 'true',
      'elim_dead_relations': 'true',
      'elim_type_checks': 'true'}),
    
    ('twitter/twitter_in', 'twitter/twitter_dem_singletag',
     {'default_impl': 'filtered',
      'use_singletag_demand': 'true'}),
]

wifi_tasks = [
    ('wifi/wifi_in', 'wifi/wifi_inc',
     {'default_impl': 'inc'}),
    ('wifi/wifi_in', 'wifi/wifi_dem',
     {'default_impl': 'filtered'}),
]

django_tasks = [
    ('django/django_in', 'django/django_inc',
     {'default_impl': 'inc'}),
    ('django/django_in', 'django/django_dem',
     {'default_impl': 'filtered'}),
    ('django/django_simp_in', 'django/django_simp_inc',
     {'default_impl': 'inc'}),
    ('django/django_simp_in', 'django/django_simp_dem',
     {'default_impl': 'filtered'}),
]

jql_tasks = [
    ('jql/jql_1_in', 'jql/jql_1_inc',
     {'default_impl': 'inc'}),
    ('jql/jql_1_in', 'jql/jql_1_dem',
     {'default_impl': 'filtered'}),
    ('jql/jql_2_in', 'jql/jql_2_inc',
     {'default_impl': 'inc'}),
    ('jql/jql_2_in', 'jql/jql_2_dem',
     {'default_impl': 'filtered'}),
    ('jql/jql_3_in', 'jql/jql_3_inc',
     {'default_impl': 'inc'}),
    ('jql/jql_3_in', 'jql/jql_3_dem',
     {'default_impl': 'filtered'}),
]

checkaccess_opts = {'CA': dict(
    demand_param_strat = 'explicit',
    demand_params = 'object',
    clause_reorder = '3, 1, 2',
)}
corerbac_tasks = [
    ('rbac/corerbac/coreRBAC_in',
     'rbac/corerbac/coreRBAC_checkaccess_inc',
     {'default_impl': 'inc'}),
    ('rbac/corerbac/coreRBAC_in',
     'rbac/corerbac/coreRBAC_checkaccess_dem',
     ({'default_impl': 'filtered'},
      checkaccess_opts)),
    ('rbac/corerbac/coreRBAC_in',
     'rbac/corerbac/coreRBAC_inc',
     {'default_impl': 'inc', 'auto_query': 'true'}),
    ('rbac/corerbac/coreRBAC_in',
     'rbac/corerbac/coreRBAC_dem',
     ({'default_impl': 'filtered', 'auto_query': 'true'},
      checkaccess_opts)),
]
crbac_tasks = [
    ('rbac/constrainedrbac/crbac_in',
     'rbac/constrainedrbac/crbac_aux',
     {'default_impl': 'aux'}),
    ('rbac/constrainedrbac/crbac_in',
     'rbac/constrainedrbac/crbac_inc',
     {'default_impl': 'inc'}),
    ('rbac/constrainedrbac/crbac_in',
     'rbac/constrainedrbac/crbac_dem',
     {'default_impl': 'filtered'}),
]
rbac_tasks = corerbac_tasks + crbac_tasks

graddb_queries = [
    'advisor_overdue',
    'advisors_by_student',
    'cur_stu',
    'good_tas',
    'new_stu',
    'new_ta_emails',
    'prelim_exam_overdue',
    'qual_exam_results',
    'ta_waitlist',
    'tas_and_instructors',
]
def graddb_helper(name):
    prefix = 'graddb/queries/'
    return [
        (prefix + name + '_in',
         prefix + name + '_inc',
         {'obj_domain': 'true', 'default_impl': 'inc',
          'elim_dead_funcs': 'false'}),
        (prefix + name + '_in',
         prefix + name + '_dem',
         {'obj_domain': 'true', 'default_impl': 'filtered',
          'elim_dead_funcs': 'false'}),
    ]
graddb_query_tasks = list(chain.from_iterable(graddb_helper(name)
                          for name in graddb_queries))
graddb_tasks = [
    ('graddb/newstudents/newstu_in',
     'graddb/newstudents/newstu_dem',
     {'obj_domain': 'true', 'default_impl': 'filtered'}),
] + graddb_query_tasks

probinf_tasks = [
    ('probinf/bday/bday_in',
     'probinf/bday/bday_inc',
     {'default_impl': 'inc', 'auto_query': 'true'}),
    ('probinf/bday/bday_in',
     'probinf/bday/bday_dem',
     {'default_impl': 'filtered', 'auto_query': 'true'}),
    ('probinf/bday/bday_obj_in',
     'probinf/bday/bday_obj_inc',
     {'default_impl': 'inc', 'auto_query': 'true'}),
    ('probinf/bday/bday_obj_in',
     'probinf/bday/bday_obj_dem',
     {'default_impl': 'filtered', 'auto_query': 'true'}),
    ('probinf/pubauth/pubauth_in',
     'probinf/pubauth/pubauth_inc',
     {'default_impl': 'inc', 'auto_query': 'true'}),
    ('probinf/pubauth/pubauth_in',
     'probinf/pubauth/pubauth_dem',
     {'default_impl': 'filtered', 'auto_query': 'true'}),
    ('probinf/pubcite/pubcite_in',
     'probinf/pubcite/pubcite_inc',
     {'default_impl': 'inc', 'auto_query': 'true'}),
    ('probinf/pubcite/pubcite_in',
     'probinf/pubcite/pubcite_dem',
     {'default_impl': 'filtered', 'auto_query': 'true'}),
]

distalgo_options = {
    'distalgo_mode': 'true',
    'auto_query': 'true',
    'default_impl': 'inc',
}
distalgo_obj_options = distalgo_options.copy()
distalgo_obj_options.update({
    'obj_domain': 'true',
    'default_impl': 'filtered',
})
distalgo_lamutex_options = distalgo_options.copy()
distalgo_lamutex_options.update({
    'default_demand_set_maxsize': '1',
    'typedefs': '''Label = Enum("Label");
                   Clock = Refine("Clock", Number);
                   Proc = Refine("Proc", Top);
                   Msgset = Set(Tuple([Label, Clock, Proc]));
                ''',
})
distalgo_lamutex_orig_symconfig = {
    '_PReceivedEvent_0': {'ann_type': 'Msgset'},
    'P_q': {'ann_type': 'Msgset'},
    'P_s': {'ann_type': 'Set(Proc)'},
    'SELF_ID': {'ann_type': 'Enum("SELF_ID")'},
    'P_mutex_c': {'ann_type': 'Clock'},
}
distalgo_lamutex_spec_symconfig = {
    '_PReceivedEvent_0': {'ann_type': 'Msgset'},
    '_PReceivedEvent_1': {'ann_type': 'Msgset'},
    '_PReceivedEvent_2': {'ann_type': 'Msgset'},
    'P_s': {'ann_type': 'Set(Proc)'},
    'SELF_ID': {'ann_type': 'Enum("SELF_ID")'},
    'P_mutex_c': {'ann_type': 'Clock'},
}
lamutex_tasks = [
    ('distalgo/lamutex/lamutex_orig_inc_in',
     'distalgo/lamutex/lamutex_orig_inc_out',
     (distalgo_lamutex_options, distalgo_lamutex_orig_symconfig)),
    ('distalgo/lamutex/lamutex_spec_inc_in',
     'distalgo/lamutex/lamutex_spec_inc_out',
     (distalgo_lamutex_options, distalgo_lamutex_spec_symconfig)),
    ('distalgo/lamutex/lamutex_spec_lam_inc_in',
     'distalgo/lamutex/lamutex_spec_lam_inc_out',
     (distalgo_lamutex_options, distalgo_lamutex_spec_symconfig)),
]
distalgo_other_tasks = [
    ('distalgo/clpaxos/clpaxos_inc_in',
     'distalgo/clpaxos/clpaxos_inc_out',
     distalgo_options),
    ('distalgo/crleader/crleader_inc_in',
     'distalgo/crleader/crleader_inc_out',
     distalgo_options),
    ('distalgo/dscrash/dscrash_inc_in',
     'distalgo/dscrash/dscrash_inc_out',
     distalgo_obj_options),
    ('distalgo/hsleader/hsleader_inc_in',
     'distalgo/hsleader/hsleader_inc_out',
     distalgo_options),
    ('distalgo/lapaxos/lapaxos_inc_in',
     'distalgo/lapaxos/lapaxos_inc_out',
     distalgo_options),
    ('distalgo/ramutex/ramutex_inc_in',
     'distalgo/ramutex/ramutex_inc_out',
     distalgo_options),
    ('distalgo/ratoken/ratoken_inc_in',
     'distalgo/ratoken/ratoken_inc_out',
     distalgo_obj_options),
    ('distalgo/sktoken/sktoken_inc_in',
     'distalgo/sktoken/sktoken_inc_out',
     distalgo_obj_options),
    ('distalgo/tpcommit/tpcommit_inc_in',
     'distalgo/tpcommit/tpcommit_inc_out',
     distalgo_options),
    ('distalgo/vrpaxos/vrpaxos_inc_in',
     'distalgo/vrpaxos/vrpaxos_inc_out',
     distalgo_obj_options),
]
distalgo_tasks = lamutex_tasks + distalgo_other_tasks

task_lists = [
    ('twitter', twitter_tasks),
    ('wifi', wifi_tasks),
    ('django', django_tasks),
    ('jql', jql_tasks),
    ('corerbac', corerbac_tasks),
    ('crbac', crbac_tasks),
    ('rbac', rbac_tasks),
    ('graddb', graddb_tasks),
    ('probinf', probinf_tasks),
    ('lamutex', lamutex_tasks),
    ('distalgo', distalgo_tasks),
]
task_groups = dict(task_lists)

tasks = [t for _, tasks in task_lists for t in tasks]

tasks_by_target = {t[1]: t for t in tasks}


root_path = normpath(dirname(__file__))


def compile_task(task, *, options=None):
    """Run a benchmark compilation task. Assume the root path is the
    current directory.
    """
    in_name, out_name, task_opts_qopts = task
    in_file = in_name + '.py'
    out_file = out_name + '.py'
    stats_file = out_name + '_stats.txt'
    
    opts = options.copy()
    qopts = {}
    if isinstance(task_opts_qopts, tuple) and len(task_opts_qopts) == 2:
        task_opts, task_qopts = task_opts_qopts
    else:
        task_opts = task_opts_qopts
        task_qopts = {}
    opts.update(task_opts)
    qopts.update(task_qopts)
    
    print('Regenerating {}...'.format(out_name), flush=True)
    invoke(in_file, out_file,
           options=opts, query_options=qopts,
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
    parent = get_argparser(with_help=False)
    parser = argparse.ArgumentParser(prog='regenerate_benchmarks.py',
                                     parents=[parent],
                                     epilog='IncOQ command line options are '
                                            'also permitted.')
    parser.add_argument('target_name', nargs='*', default=None)
    parser.add_argument('--list', action='store_true',
                        help='show available targets')
    
    ns = parser.parse_args(args)
    
    options = extract_options(ns)
    
    if ns.list:
        print('Available targets:')
        seen = set()
        for _in_name, out_name, _opts in chain.from_iterable(
                tasklist for _listname, tasklist in task_lists):
            if out_name not in seen:
                print('  ' + out_name)
                seen.add(out_name)
        print()
        print('Available task lists:')
        for listname, _tasklist in task_lists:
            print('  ' + listname)
        return
    
    if len(ns.target_name) == 0:
        print('No targets specified.\n')
        parser.print_usage()
        return
    
    compile_task_names(ns.target_name, options=options)


if __name__ == '__main__':
    run(sys.argv[1:])
