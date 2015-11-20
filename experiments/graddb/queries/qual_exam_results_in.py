from incoq.runtime import *

students = Set()
schema = Obj()
sem = 'a'

# Changed string concatenation to tuple, to trick type analysis
# into not complaining.
{((s.first_name, ' ', s.last_name),
  q.subject, q.score, 'passed' if q.passed else 'failed') 
 for s in students
 for q in s.quals 
 if q.date and schema.date_to_sem(q.date) == sem}
