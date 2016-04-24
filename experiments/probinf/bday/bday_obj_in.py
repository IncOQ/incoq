from incoq.mars.runtime import *

CONFIG(
    obj_domain = 'true',
)

calendar = Set()
room = Set()

def init():
    for i in range(1, 365 + 1):
        calendar.add(i)

def add_person(bday):
    p = Obj()
    p.bday = bday
    room.add(p)
    return p

def remove_person(p):
    room.remove(p)

def clear_room():
    room.clear()

def do_query(threshold):
    return count({day for day in calendar
                      if count({person for person in room
                                       if person.bday == day}) > threshold})
