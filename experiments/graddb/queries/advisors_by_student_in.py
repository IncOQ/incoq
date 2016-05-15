from incoq.runtime import *

def main():
    students = Set()
    sem = 'a'
    
    # Changed string concatenation to tuple, to trick type analysis
    # into not complaining.
    print(QUERY('Q',
        {((s.first_name, ' ', s.last_name),
          a.advisor, a.start, a.end)
         for s in students
         for a in s.advisor.all
         if (a.advisor != 'noadvisor' and
             not (a.start and a.start > sem or a.end and a.end < sem))}))
