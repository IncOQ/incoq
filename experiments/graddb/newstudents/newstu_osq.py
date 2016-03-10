from incoq.runtime import *
from osq import query

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
    # Can't strict-delete first due to OSQ restriction.
    program.start = sem

def do_query(sem):
    return query('''students, sem -> {s for s in students for p in s.programs if s.joined == sem or (p.start != None and p.start == sem)}''',
                 students, sem)

do_query_nodemand = do_query

def init():
    query('''students, sem -> {s for s in students for p in s.programs if s.joined == sem or (p.start != None and p.start == sem)}''',
          Set(), None)
