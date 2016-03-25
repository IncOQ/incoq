from incoq.runtime import *

citations = Set()

def add_cite(sname, sdate, tname, tdate):
    cite = Obj()
    cite.source = Obj()
    cite.source.author = sname
    cite.source.date = sdate
    cite.target = Obj()
    cite.target.author = tname
    cite.target.date = tdate
    citations.add(cite)
    return cite

def remove_cite(cite):
    citations.remove(cite)

def clear_all():
    citations.clear()

def do_query():
    return count({c for c in citations if c.source.author == 'Einstein'
                    if c.target.author == 'Galileo'})
