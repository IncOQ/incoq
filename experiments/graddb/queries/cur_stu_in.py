from incoq.runtime import *

students = Set()
sem = 'a'
stutype = 'a'

{s for s in students 
   if s.joined <= sem and not has_left(s,sem)
   for p in s.program.all
   if p.program == stutype and
      not (p.start and p.start > sem or p.end and p.end < sem)}
