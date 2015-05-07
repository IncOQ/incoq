# Modified version of django_osq.py with the same
# changes as were made in django_simp_in.py.

from incoq.runtime import *
from osq import query

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
    return query('user -> {p.name for g in user.groups for p in g.perms if g.active}', user)

do_query_nodemand = do_query
