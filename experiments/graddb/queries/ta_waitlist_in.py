from incoq.runtime import *

students = Set()
stutype = 'a'
sem = 'a'

{s for s in students
   for p in s.program.all
   if p.program == stutype
   for w in s.waitlist
   if w.semester == sem}
