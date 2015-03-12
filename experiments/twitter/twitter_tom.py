# This example DOES NOT WORK. The current OSQ system implementation
# does not generate clauses over U, so the computed maintenance join
# is actually incorrect. In this example, this manifests as a
# reference count error. 

from invinc.runtime import *
from osq import query

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
    # In the original program we do "del u.loc" for strictness,
    # but that's not necessary or allowed in Tom's system.
    u.loc = loc

def do_query(celeb, group):
    return query('celeb, group -> '
                   '{user.email for user in celeb.followers '
                               'for user2 in group '
                               'if user.loc == "NYC" '
                               'if user is user2}',
                 celeb, group)

do_query_nodemand = do_query
