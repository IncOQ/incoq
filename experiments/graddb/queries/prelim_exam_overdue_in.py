from incoq.runtime import *

students = Set()
mon = 'a'

# Changed string concatenation to tuple, to trick type analysis
# into not complaining.
{s for s in students
   for rpe in s.rpe
   if rpe.passed and rpe.date.add(2,0) < mon}
