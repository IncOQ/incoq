# Simplified version that gets rid of the users parameter
# in favor of passing in the actual user object. This version
# is also closer to the actual query appearing in the Django
# source code.

# Changed from django_in.py:
# - the query is different, and takes in a user instead of a user id
# - the users set is deleted, and make_user() modified accordingly

from runtimelib import *

OPTIONS(
    obj_domain = True,
)

QUERYOPTIONS(
    '{p.name for g in user.groups for p in g.perms if g.active}',
    uset_mode = 'explicit',
    uset_params = ['user'],
)

def make_user(id):
    user = Obj()
    user.id = id
    user.groups = Set()
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

def do_query(user):
    return {p.name for g in user.groups for p in g.perms if g.active}

def do_query_nodemand(user):
    return NODEMAND({p.name for g in user.groups for p in g.perms if g.active})
