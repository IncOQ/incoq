# Query that finds violations of ANSI RBAC's Static Separation of
# Duties condition.

from incoq.mars.runtime import *

USERS = Set()
UR = Set()
SSDNC = Set()
SSDNR = Set()

def add_user(user):
    USERS.add(user)

def remove_user(user):
    USERS.remove(user)

def add_ur(user, role):
    UR.add((user, role))

def remove_ur(user, role):
    UR.remove((user, role))

def add_ssdnc(name, c):
    SSDNC.add((name, c))

def remove_ssdnc(name, c):
    SSDNC.remove((name, c))

def add_ssdnr(name, role):
    SSDNR.add((name, role))

def remove_ssdnr(name, role):
    SSDNR.remove((name, role))

def do_query():
    return QUERY('Q3',
        {(u, name) for u in USERS for (name, c) in SSDNC
                   if QUERY('Q2', count(QUERY('Q1',
                      {r for (u2, r) in UR for (name2, r2) in SSDNR
                         if u == u2 if name == name2 if r == r2}))) >= c})

def do_query_nodemand():
    return QUERY('Q3',
        {(u, name) for u in USERS for (name, c) in SSDNC
                   if QUERY('Q2', count(QUERY('Q1',
                      {r for (u2, r) in UR for (name2, r2) in SSDNR
                         if u == u2 if name == name2 if r == r2}))) >= c},
        {'nodemand': True})
