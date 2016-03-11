# JQL query, one level.

from incoq.mars.runtime import *

CONFIG(
    obj_domain = 'true',
)

class Student(Obj):
    pass

class Course(Obj):
    pass

class Attends(Obj):
    pass

ATTENDS = Set()
STUDENTS = Set()
COURSES = Set()

# Functions for constructing objects and adding them to
# the global sets.

def make_student(name):
    s = Student()
    s.name = name
    STUDENTS.add(s)
    return s

def make_course(name):
    c = Course()
    c.name = name
    COURSES.add(c)
    return c

def make_attends(s, c):
    a = Attends()
    a.student = s
    a.course = c
    ATTENDS.add(a)
    return a

# Replacement takes in an Attends object to remove,
# and the parameters to a new Attends object to construct
# and add to the set.

def replace_attends(old_a, new_s, new_c):
    new_a = make_attends(new_s, new_c)
    ATTENDS.remove(old_a)
    return new_a

def do_query(COMP101):
    return QUERY('Q', {a for a in ATTENDS if a.course == COMP101})

def do_query_nodemand(COMP101):
    return QUERY('Q', {a for a in ATTENDS if a.course == COMP101},
                 {'nodemand': True})
