from incoq.util.linecount import get_loc_file

prog_dispnames = [
    ('twitter_dem_norcelim_nodrelim',            'Unoptimized'),
    ('twitter_dem_inline_norcelim_nodrelim',     'Inlining'),
    ('twitter_dem_inline_nodrelim',              'Ref count elim'),
    ('twitter_dem_inline',                       'Result set elim'),
    ('twitter_dem_inline_notypecheck',           'Type check elim'),
    ('twitter_dem_inline_notypecheck_maintelim', 'Maint case elim'),
    ('twitter_dem_inline_notypecheck_maintelim_native', 'Native sets'),
]

for prog, dispname in prog_dispnames:
    loc = get_loc_file(prog + '.py')
    print('{:<20} {}'.format(dispname + ': ', loc))
