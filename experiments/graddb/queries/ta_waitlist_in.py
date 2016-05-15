from incoq.runtime import *

def main():
    students = Set()
    stutype = 'a'
    sem = 'a'
    
    print(QUERY('Q',
        {s for s in students
           for p in s.program.all
           if p.program == stutype
           for w in s.waitlist
           if w.semester == sem}))
