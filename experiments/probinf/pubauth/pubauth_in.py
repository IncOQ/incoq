from incoq.mars.runtime import *

CONFIG(
    obj_domain = 'true',
)

pubs = Set()

def make_pub(author):
    p = Obj()
    p.author = author
    pubs.add(p)
    return p

def remove_pub(p):
    pubs.remove(p)

def clear_all():
    pubs.clear()

def do_query():
    return count({p for p in pubs if p.author == 'Einstein'})
