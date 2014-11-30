# author: annie liu, programed based on ANSI RBAC.

# Changes by Jon:
# - de-classified things (methods to functions, fields to globals)
# - import runtimelib
# - set() to comprehension syntax
# - flattened PR to triples
# - turned set difference operations (-=) into iterated removals
# - for set difference comprehensions, added membership clauses for
#   the set being removed from, in order to constrain enumvar domains
#   (as in section 4 of PEPM)
# - split some "and" comprehension conditions into individual conditions
# - eliminated the comprehension over parameter "ars" in CreateSession
# - added methods AddOperation and AddObject (no corresponding
#   deletion methods) 
# - wherever a for loop iterates over a comprehension, create
#   a copy of the result if it may change during the loop
# - added CheckAccess_nodemand() for doing a CheckAccess query without
#   checking and adding to the demand set -- only for use when the
#   parameters are already known to be demanded

from runtimelib import *

OBJS = set()  
OPS = set()   # an operation-object pair is called a permission
USERS = set()
ROLES = set()
PR = set()    # PR subset OPS * OBJS * ROLES, for PA in std
UR = set()    # UR subset USERS * ROLES,      for UA in std
SESSIONS = set()
SU = set()    # SU subset SESSIONS * USERS
SR = set()    # SR subset SESSIONS * ROLES

# administrative commands

def AddUser(user):
    assert user not in USERS
    USERS.add(user)

def DeleteUser(user):
    assert user in USERS
    for _user, _r in set({(user,r) for r in ROLES if (user, r) in UR}):        # maintain UR
        UR.remove((_user, _r))
    for s in set({s for s in SESSIONS if (s,user) in SU}):
        DeleteSession(user,s)                             # maintain sessions
    USERS.remove(user)                                 # delete user last  -yl

def AddRole(role):
    assert role not in ROLES
    ROLES.add(role)

def DeleteRole(role):
    assert role in ROLES
    for _op, _obj, _role in set({(op,obj,role) for op in OPS for obj in OBJS if (op, obj, role) in PR}):
        PR.remove((_op, _obj, _role))
    for _u, _role in set({(u,role) for u in USERS if (u, role) in UR}):        # maintain PR and UR
        UR.remove((_u, _role))
    for (s,u) in set({(s,u) for s in SESSIONS for u in USERS
                            if (s,u) in SU if (s,role) in SR}):
        DeleteSession(u,s)                        # maintain sessions
    ROLES.remove(role)                         # delete role last  -cw

def AssignUser(user, role):
    assert user in USERS
    assert role in ROLES
    assert (user,role) not in UR
    UR.add((user,role))

def DeassignUser(user, role):
    assert user in USERS
    assert role in ROLES
    assert (user,role) in UR
    for s in set({s for s in SESSIONS 
                    if (s,user) in SU if (s,role) in SR}):
        DeleteSession(user,s)                        # maintain sessions
    UR.remove((user,role))

def AddOperation(operation):
    assert operation not in OPS
    OPS.add(operation)

def AddObject(object):
    assert object not in OBJS
    OBJS.add(object)

def GrantPermission(operation, object, role):
    assert operation in OPS and object in OBJS
    assert role in ROLES
    assert (operation,object,role) not in PR  #+
    PR.add((operation,object,role))

def RevokePermission(operation, object, role):
    assert operation in OPS and object in OBJS
    assert role in ROLES
    assert (operation,object,role) in PR
    PR.remove((operation,object,role))

# supporting system functions

def CreateSession(user, session, ars):
    assert user in USERS
    assert session not in SESSIONS
    assert ars.issubset(AssignedRoles(user))
    SESSIONS.add(session)      # add first for subset constraints  -ag
    SU.add((session,user))     # ok to do in any order if atomic   -yl
    # Can't put ars in a comprehension since it's a local var, not a
    # top level relation.
    for r in ars:
        SR.add((session, r))

def DeleteSession(user, session):
    assert user in USERS
    assert session in SESSIONS
    assert (session,user) in SU
    SU.remove((session,user))
    for _session, _r in set({(session,r) for r in ROLES if (session, r) in SR}):        # maintain SR
        SR.remove((_session, _r))
    SESSIONS.remove(session)                        # maintain SESSIONS

def AddActiveRole(user, session, role):
    assert user in USERS
    assert session in SESSIONS
    assert role in ROLES
    assert (session,user) in SU
    assert (session,role) not in SR
    assert role in AssignedRoles(user)
    SR.add((session,role))

def DropActiveRole(user, session, role):
    assert user in USERS
    assert session in SESSIONS
    assert role in ROLES
    assert (session,user) in SU
    assert (session,role) in SR
    SR.remove((session,role))

def CheckAccess(session, operation, object):
    assert session in SESSIONS
    assert operation in OPS
    assert object in OBJS
    return bool({r for r in ROLES
                   if (session,r) in SR
                   if (operation,object,r) in PR})

def CheckAccess_nodemand(session, operation, object):
    assert session in SESSIONS
    assert operation in OPS
    assert object in OBJS
    return bool(NODEMAND({r for r in ROLES
                            if (session,r) in SR
                            if (operation,object,r) in PR}))

# review functions

def AssignedUsers(role):
    assert role in ROLES
    return {u for u in USERS if (u,role) in UR}

def AssignedRoles(user):
    assert user in USERS
    return {r for r in ROLES if (user,r) in UR}

# advanced review functions

def RolePermissions(role):
    assert role in ROLES
    return {(op,obj) for op in OPS for obj in OBJS 
                     if (op,obj,role) in PR}

def UserPermissions(user):
    assert user in USERS
    return {(op,obj) for r in ROLES
                     for op in OPS for obj in OBJS
                     if (user,r) in UR if (op,obj,r) in PR}

def SessionRoles(session):
    assert session in SESSIONS
    return {r for r in ROLES if (session,r) in SR}

def SessionPermissions(session):
    assert session in SESSIONS
    return {(op,obj) for r in ROLES
                     for op in OPS for obj in OBJS
                     if (session,r) in SR if (op,obj,r) in PR}

def RoleOperationsOnObject(role, object):
    assert role in ROLES 
    assert object in OBJS
    return {op for op in OPS if (op,object,role) in PR}

def UserOperationsOnObject(user, object):
    assert user in USERS
    assert object in OBJS
    return {op for r in ROLES for op in OPS
               if (user,r) in UR if (op,object,r) in PR}
