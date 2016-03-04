# Redefine do_query() without the overhead of the no-op QUERY
# annotation, and likewise for do_query_nodemand().

from .twitter_in import *

def do_query(celeb, group):
    return {user.email for user in celeb.followers if user in group
                       if user.loc == 'NYC'}

do_query_nodemand = do_query
