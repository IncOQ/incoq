from incoq.mars.runtime import *

def main():
    current = Set()
    sem = 'a'
    stutype = 'a'
    
    print(QUERY('Q',
        {s for s in current
           for p in s.program.all
           if (p.program == stutype and
               not (p.start and p.start > sem or p.end and p.end < sem))
           if s.joined == sem or p.start and p.start == sem}))
