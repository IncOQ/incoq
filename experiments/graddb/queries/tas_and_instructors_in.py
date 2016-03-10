from incoq.runtime import *

current = Set()
sem = 'a'
onleave = Set()
parttime = Set()

{s for s in current
   for su in s.support.all
   if (su.kind == 'ta' and
       not (su.start and su.start > sem or su.end and su.end < sem))
   if s not in onleave
   if s not in parttime}

{s for s in current
   for t in s.taught
   if t.semester and t.semester == sem}
