# New student query as in GPCE '08, top-right of p.9.
#
# Semester can be treated as a constrained parameter, but we
# can't automatically determine this because the conditions
# constraining it appear in a disjunction. We'll just leave it
# as an unconstrained parameter and allow the condition clause
# to stand as it is without pattern rewriting.

from incoq.runtime import *

CONFIG(
    obj_domain = 'true',
)

students = Set()

def make_student(id, sem):
    student = Obj()
    student.id = id
    student.joined = sem
    student.programs = Set()
    students.add(student)
    return student

def add_program(student, sem):
    program = Obj()
    program.start = sem
    student.programs.add(program)
    return program

def change_program_start(program, sem):
    del program.start
    program.start = sem

def do_query(sem):
    return QUERY('Q', {s for s in students for p in s.programs
                         if s.joined == sem or
                            (p.start != None and p.start == sem)})

def do_query_nodemand(sem):
    return QUERY('Q', {s for s in students for p in s.programs
                         if s.joined == sem or
                            (p.start != None and p.start == sem)},
                 {'nodemand': True})

def init():
    # Dummy function used in the OSQ version to compile the query.
    return
