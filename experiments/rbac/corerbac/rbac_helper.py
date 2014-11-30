###############################################################################
# rbac_helper.py                                                              #
# Author: Jon Brandvein                                                       #
###############################################################################

"""Utility that assists with generating rbac operations.

There are two main contributions: A logger that combines the execution
of RBAC operations with the appending of their call information to a
list; and an emitter that provides no-argument methods for generating
random RBAC operations.

Ironically, there are some performance issues with running the generator
to produce large sequences of operations. It looks like the generator
itself could benefit from a partially incrementalized RBAC
implementation.
"""


import random
from itertools import count
from time import clock
from collections import Counter
from operator import itemgetter

from .coreRBAC import CoreRBAC


corerbac_update_names = [
    'AddUser',
    'DeleteUser',
    'AddRole',
    'DeleteRole',
    'AssignUser',
    'DeassignUser',
    'AddOperation',     # These two are not in the ANSI standard.
    'AddObject',        #
    'GrantPermission',
    'RevokePermission',
    'CreateSession',
    'DeleteSession',
    'AddActiveRole',
    'DropActiveRole',
]
corerbac_query_names = [
    'CheckAccess',
    'AssignedUsers',
    'AssignedRoles',
    'RolePermissions',
    'UserPermissions',
    'SessionRoles',
    'SessionPermissions',
    'RoleOperationsOnObject',
    'UserOperationsOnObject',
]
corerbac_op_names = corerbac_update_names + corerbac_query_names

def choice(seq):
    """Like random.choice(), but accept sets, and raise ValueError
    if seq is empty.
    """
    if len(seq) == 0:
        raise ValueError
    if isinstance(seq, set):
        seq = list(seq)
    return random.choice(seq)

def strcounter(prefix):
    """Yield strings "p0", "p1", "p2", ..., where p is the given prefix."""
    for i in count():
        yield prefix + str(i)


class LoggingCoreRBAC(CoreRBAC):
    
    """A version of CoreRBAC that adds, for each query or update
    operation OP, a method log_OP that calls OP and appends the
    call info to self.log. The log is a list of tuples (OP name, *args).
    """
    
    # The log_* methods are auto-generated as wrapper functions
    # after this class definition.
    
    def __init__(self):
        super().__init__()  # Init internal rbac state.
        self.log = []

def make_logger(name):
    """Given an operation name, return a logger method that
    appends (name, *args) to self.log and then calls the operation
    method by that name.
    """
    def logger(self, *args):
        self.log.append((name,) + args)
        f = getattr(self, name)
        return f(*args)
    
    logger.__name__ = 'log_' + name
    return logger

for n in corerbac_op_names:
    setattr(LoggingCoreRBAC, 'log_' + n, make_logger(n))


class EmittingCoreRBAC(LoggingCoreRBAC):
    
    """Introduces a set of emit_* helper methods for generating
    operations with random valid arguments. If an emit_* method
    succeeds in finding such argument values, it logs the call
    and returns True; otherwise it returns False without actually
    mutating any state.
    
    For debugging and instrumentation purposes, the number of
    attempts, failures, and time taken for each kind of operation
    is tracked.
    """
    
    def __init__(self):
        super().__init__()
        
        # Counters for generating fresh domain values.
        self.n_users = strcounter('u')
        self.n_roles = strcounter('r')
        self.n_ops = strcounter('op')
        self.n_objs = strcounter('obj')
        self.n_sessions = strcounter('s')
        
        self.gentimes = Counter()
        self.attempts = Counter()
        self.failures = Counter()
    
    def report(self):
        """Format the attempts, failures, and gentime info for display."""
        s = ''
        
        s += 'Time:\n'
        total = sum(self.gentimes.values())
        for name, t in sorted(self.gentimes.items(), key=itemgetter(0)):
            s += '  {:<20} {:<8.3f} {:>2.0f}%\n'.format(
                 name + ':', t, t/total * 100)
        s += '-' * 40 + '\n'
        s += '  {:<20} {:.3f}\n\n'.format('Total:', total)
        
        s += 'Failure rate:\n'
        total_fail = sum(self.failures.values())
        total_att = sum(self.attempts.values())
        for name, f in sorted(self.failures.items(), key=itemgetter(0)):
            a = self.attempts[name]
            s += '  {:<20} {:<10} {:>2.0f}%\n'.format(
                 name + ':', str(f) + '/' + str(a), f/a * 100)
        s += '-' * 40 + '\n'
        s += '  {:<20} {:<10} {:>2.0f}%\n'.format(
             'Total:',
             str(total_fail) + '/' + str(total_att),
             total_fail/total_att * 100)
        
        return s
    
    # Emitters are wrappers around gen_* methods. Each gen_*
    # returns valid args for its associated operation, or raises
    # ValueError. The emit_* methods are defined programmatically,
    # after this class definition.
    
    def gen_AddUser(self):
        return (next(self.n_users),)
    
    def gen_DeleteUser(self):
        return (choice(self.USERS),)
    
    def gen_AddRole(self):
        return (next(self.n_roles),)
    
    def gen_DeleteRole(self):
        return (choice(self.ROLES),)
    
    def gen_AssignUser(self):
        dom = {(u, r) for u in self.USERS for r in self.ROLES}
        dom -= self.UR
        return choice(dom)
    
    def gen_DeassignUser(self):
        return choice(self.UR)
    
    def gen_AddOperation(self):
        return (next(self.n_ops),)
    
    def gen_AddObject(self):
        return (next(self.n_objs),)
    
    def gen_GrantPermission(self):
        dom = {((op, obj), r) for op in self.OPS for obj in self.OBJS
                              for r in self.ROLES}
        dom -= self.PR
        ((op, obj), role) = choice(dom)
        return (op, obj, role)
    
    def gen_RevokePermission(self):
        ((op, obj), role) = choice(self.PR)
        return (op, obj, role)
    
    def gen_CreateSession(self):
        u = choice(self.USERS)
        s = next(self.n_sessions)
        roles = self.AssignedRoles(u)
        ars = random.sample(roles, random.randrange(len(roles) + 1))
        # Use frozenset to play nice with hashed containers.
        ars = frozenset(ars)
        return (u, s, ars)
    
    def gen_DeleteSession(self):
        session, user = choice(self.SU)
        return (user, session)
    
    def gen_AddActiveRole(self):
        dom = {(u, s, r) for (s, u) in self.SU
                         for r in self.ROLES if (u, r) in self.UR
                                             if (s, r) not in self.SR}
        return choice(dom)
    
    def gen_DropActiveRole(self):
        (s, r) = choice(self.SR)
        u = next(u for u in self.USERS if (s, u) in self.SU)
        return (u, s, r)
    
    def gen_CheckAccess(self):
        return choice(self.SESSIONS), choice(self.OPS), choice(self.OBJS)
    
    def gen_AssignedUsers(self):
        return (choice(self.ROLES),)
    
    def gen_AssignedRoles(self):
        return (choice(self.USERS),)
    
    def gen_RolePermissions(self):
        return (choice(self.ROLES),)
    
    def gen_UserPermissions(self):
        return (choice(self.USERS),)
    
    def gen_SessionRoles(self):
        return (choice(self.SESSIONS),)
    
    def gen_SessionPermissions(self):
        return (choice(self.SESSIONS),)
    
    def gen_RoleOperationsOnObject(self):
        return (choice(self.ROLES), choice(self.OBJS))
    
    def gen_UserOperationsOnObject(self):
        return (choice(self.USERS), choice(self.OBJS))

def make_emitter(name):
    """Given an operation name, return an emitter method that
    uses the corresponding gen_* to produce arguments (if possible),
    and then calls the corresponding log_* method; and returns a
    bool indicating whether it succeeded.
    """
    def emitter(self):
        f_gen = getattr(self, 'gen_' + name)
        f_log = getattr(self, 'log_' + name)
        
        self.attempts[name] += 1
        
        try:
            t1 = clock()
            args = f_gen()
            t2 = clock()
            self.gentimes[name] += t2 - t1
            assert isinstance(args, tuple)
        
        except ValueError:
            self.failures[name] += 1
            return False
        
        f_log(*args)
        return True
    
    emitter.__name__ = 'emit_' + n
    return emitter

for n in corerbac_op_names:
    setattr(EmittingCoreRBAC, 'emit_' + n, make_emitter(n))


class DemandEmittingCoreRBAC(EmittingCoreRBAC):
    
    """Refinement of the above operation generator that also tracks a
    special subset of queryable sessions. The queryable sessions
    cannot be removed by updates (DeleteSession, or indirectly via
    something like DeleteUser). CheckAccess calls will only be emitted
    for queryable sessions, not other sessions.
    """
    
    def __init__(self, n_queryable):
        super().__init__()
        # If there are n queryable sessions, they are named s0 up to
        # s(n-1).
        self.queryable = {'s' + str(i) for i in range(n_queryable)}
    
    # We redefine the appropriate gen_* methods here. No need to
    # programmatically recreate the emit_* methods, since we were
    # careful to define those in a way that doesn't couple them with
    # the particular gen_* implementations in EmittingCoreRBAC.
    
    def gen_DeleteUser(self):
        # Get all users who do *not* have a queryable session.
        dom = [u for u in self.USERS
                 if all((s, u) not in self.SU
                        for s in self.queryable)]
        return (choice(dom),)
    
    def gen_DeleteRole(self):
        # Get all roles who do *not* have a queryable session.
        dom = [r for r in self.ROLES
                 if all((s, r) not in self.SR
                        for s in self.queryable)]
        return (choice(dom),)
    
    def gen_DeassignUser(self):
        # Get all user/role pairs where there is no queryable session
        # for that user with that role activated.
        dom = [(u, r) for (u, r) in self.UR
                      if all(not ((s, u) in self.SU and (s, r) in self.SR)
                             for s in self.queryable)]
        return choice(dom)
    
    def gen_DeleteSession(self):
        # Only choose non-queryable sessions.
        dom = [(s, u) for (s, u) in self.SU
                      if s not in self.queryable]
        session, user = choice(dom)
        return (user, session)
    
    def gen_CheckAccess(self):
        # Only choose queryable sessions.
        dom = list(self.queryable & self.SESSIONS)
        return choice(dom), choice(self.OPS), choice(self.OBJS)


class FastEmittingCoreRBAC(EmittingCoreRBAC):
    
    """Faster RBAC emitter that is allowed to give up trying to
    generate an operation even when one exists. This may bias
    the generation away from operations for which a random
    assignment of parameters is less likely to be valid.
    
    Specifically, this emitter does not construct expensive
    Cartesian products for things like choosing an element from
    the complement of a relation. As a consequence, some operations
    now only take linear time in the size of the RBAC data structures.
    """
    
    def gen_AssignUser(self):
        tup = (choice(self.USERS), choice(self.ROLES))
        if tup in self.UR:
            raise ValueError
        return tup
    
    def gen_GrantPermission(self):
        op = choice(self.OPS)
        obj = choice(self.OBJS)
        r = choice(self.ROLES)
        if ((op, obj), r) in self.PR:
            raise ValueError
        return (op, obj, r)
    
    def gen_AddActiveRole(self):
        (s, u) = choice(self.SU)
        r = choice({r for (u2, r) in self.UR if u2 == u})
        if (s, r) in self.SR:
            raise ValueError
        return (u, s, r)

class FastDemandEmittingCoreRBAC(DemandEmittingCoreRBAC, FastEmittingCoreRBAC):
    
    """Extension of the demand-aware data generator to also be fast."""
    
    def gen_DeleteUser(self):
        u = choice(self.USERS)
        if any((s, u) in self.SU
               for s in self.queryable):
            raise ValueError
        return (u,)
    
    def gen_DeleteRole(self):
        r = choice(self.ROLES)
        if any((s, r) in self.SR
               for s in self.queryable):
            raise ValueError
        return (r,)
    
    def gen_DeassignUser(self):
        (u, r) = choice(self.UR)
        if any((s, u) in self.SU and (s, r) in self.SR
               for s in self.queryable):
            raise ValueError
        return (u, r)


class SREmittingCoreRBAC(FastDemandEmittingCoreRBAC):
    
    """Emitter that's optimized for AddActiveRole/DropActiveRole."""
    
    # This implementation is derived by (manually) optimizing
    # computations used by FastEmittingCoreRBAC.AddActiveRole()
    # and EmittingCoreRBAC.
    #
    # Specifically, we cache UR.out, SU.out, and list(SU), which
    # do not change at all during sequences of updates to sessions'
    # active roles. We also incrementally compute SR.out, and
    # allow DropActiveRole() to probabilistically return a false
    # negative.
    
    # Some of the mappings may leak memory due to obsolete keys
    # (similar to defaultdict), but that shouldn't be a problem
    # for us.
    
    def __init__(self, *args):
        super().__init__(*args)
        
        # None means "requires recomputation".
        self.URout = None
        self.SUout = None
        self.SUlist = None
        self.SRout = {}
    
    # Updates instrumented with maintenance code.
    
    def AssignUser(self, user, role):
        super().AssignUser(user, role)
        self.URout = None
    
    def DeassignUser(self, user, role):
        super().DeassignUser(user, role)
        self.URout = None
    
    def CreateSession(self, user, session, ars):
        super().CreateSession(user, session, ars)
        self.SUout = None
        self.SUlist = None
        self.SRout.setdefault(session, set()).update(ars)
    
    def DeleteSession(self, user, session):
        super().DeleteSession(user, session)
        self.SUout = None
        self.SUlist = None
        del self.SRout[session]
    
    def AddActiveRole(self, user, session, role):
        super().AddActiveRole(user, session, role)
        self.SRout.setdefault(session, set()).add(role)
    
    def DropActiveRole(self, user, session, role):
        super().DropActiveRole(user, session, role)
        self.SRout[session].remove(role)
    
    # Optimized gen_* functions.
    
    def gen_AddActiveRole(self):
        if self.URout is None:
            self.URout = {}
            for (u, r) in self.UR:
                self.URout.setdefault(u, []).append(r)
        if self.SUlist is None:
            self.SUlist = list(self.SU)
        
        (s, u) = choice(self.SUlist)
        r = choice(self.URout[u])
        if (s, r) in self.SR:
            raise ValueError
        return (u, s, r)
    
    def gen_DropActiveRole(self):
        if self.SUout is None:
            self.SUout = {}
            for (s, u) in self.SU:
                self.SUout[s] = u
        
        s = choice(self.SESSIONS)
        if s not in self.SRout:
            # The present-but-empty case is caught by choice() below.
            raise ValueError
        r = choice(self.SRout[s])
        
        u = self.SUout[s]
        
        return (u, s, r)
