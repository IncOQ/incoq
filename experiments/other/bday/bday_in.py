from incoq.runtime import *

bdays = set()
BREL = set()

def setup_bdays(n):
    for i in range(n):
        bdays.add(i)

def add_brel(person, day):
    BREL.add((person, day))

def remove_brel(person, day):
    BREL.remove((person, day))

def clear_all():
    BREL.clear()

def do_query():
    return count({b for b in bdays if count({p for (p, b2) in BREL if b2 == b}) > 1})
