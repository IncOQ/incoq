# Authentication query from the OSQ paper, modeled on Django.

# Fields like user id, user.groups, and group.perms are 1-to-1.
# If U is small, we'd benefit from the join heuristic running
# U and the inverse of F_id first, since that would get us the
# few queried users.

from runtimelib import *

OPTIONS(
    obj_domain = True,
)

QUERYOPTIONS(
    '''{p.name for u in users for g in u.groups for p in g.perms
               if u.id == uid if g.active}''',
    uset_mode = 'explicit',
    # In the OSQ paper, only unconstrained parameters get
    # tracked in the demand set.
    uset_params = ['users'],
)

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
    return {p.name for u in users for g in u.groups for p in g.perms
                   if u.id == uid if g.active}

def do_query_nodemand(uid):
    return NODEMAND({p.name for u in users for g in u.groups for p in g.perms
                            if u.id == uid if g.active})
