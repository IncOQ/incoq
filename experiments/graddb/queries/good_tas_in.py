from incoq.mars.runtime import *

def main():
    students = Set()
    sem = 'a'
    
    print(QUERY('Q',
        {s for s in students 
           for t in s.taught
           if t.semester == sem and t.grade > 4}))
