# Authentication query from the OSQ paper, modeled on Django.

# Fields like user id, user.groups, and group.perms are 1-to-1.
# If U is small, we'd benefit from the join heuristic running
# U and the inverse of F_id first, since that would get us the
# few queried users.

from incoq.runtime import *

OPTIONS(
    obj_domain = True,
)

QUERYOPTIONS(
    '''{p.name for u in users for g in u.groups for p in g.perms
               if u.id == uid if g.active}''',
    # The parameters are users and uid. In the OSQ paper,
    # only users is tracked in the U-set because uid is a
    # constrained parameter. Here, since we don't reassign
    # to users, we view it as a relation. Consequently there
    # is no need for a distinct U-set at all.
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
