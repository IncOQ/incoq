from invinc.runtime import *
from osq import query

users = Set()

def make_user(id):
    user = Obj()
    user.id = id
    user.groups = Set()
    users.add(user)
    return user

def make_group(active):
    group = Obj()
    group.active = active
    group.perms = Set()
    return group

def make_perm(name):
    perm = Obj()
    perm.name = name
    return perm

def add_group(u, g):
    u.groups.add(g)

def add_perm(g, p):
    g.perms.add(p)

def do_query(uid):
    return query('users, uid -> {p.name for u in users for g in u.groups for p in g.perms if u.id is uid if g.active}', users, uid)

do_query_nodemand = do_query
