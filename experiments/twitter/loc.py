from incoq.util.linecount import get_loc_file

prog_dispnames = [
    ('twitter_dem_norcelim_nodrelim',            'Standard'),
    ('twitter_dem_inline_norcelim_nodrelim',     'Inlined'),
    ('twitter_dem_inline_nodrelim',              'RC elim'),
    ('twitter_dem_inline_nodrelim_rcsettoset',   'RC elim (set)'),
    ('twitter_dem_inline',                       'DR elim'),
    ('twitter_dem_inline_notypecheck',           'TC elim'),
    ('twitter_dem_inline_notypecheck_maintelim', 'Maint elim'),
]

for prog, dispname in prog_dispnames:
    loc = get_loc_file(prog + '.py')
    print('{:<15} {}'.format(dispname + ': ', loc))
