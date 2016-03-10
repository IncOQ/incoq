from incoq.runtime import *

students = Set()
sem = 'a'

{s for s in students 
   for t in s.taught
   if t.semester == sem and t.grade > 4}
