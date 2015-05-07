# Twitter example.

# Celebs to their set of followers is 1-to-1, but this
# fact doesn't really change the join orders.

from incoq.runtime import *

OPTIONS(
    obj_domain = True,
)

QUERYOPTIONS(
    '{user.email for user in celeb.followers if user in group if user.loc == "NYC"}',
    params = ['celeb', 'group'],
    uset_mode = 'all',
    no_rc = True,
)

def make_user(email, loc):
    u = Obj()
    u.followers = Set()
    u.email = email
    u.loc = loc
    return u

def make_group():
    g = Set()
    return g

def follow(u, c):
    assert u not in c.followers
    c.followers.add(u)

def unfollow(u, c):
    assert u in c.followers
    c.followers.remove(u)

def join_group(u, g):
    assert u not in g
    g.add(u)

def leave_group(u, g):
    assert u in g
    g.remove(u)

def change_loc(u, loc):
    del u.loc
    u.loc = loc

def do_query(celeb, group):
    return {user.email for user in celeb.followers if user in group
                       if user.loc == 'NYC'}

def do_query_nodemand(celeb, group):
    return NODEMAND({user.email for user in celeb.followers if user in group
                                if user.loc == 'NYC'})
