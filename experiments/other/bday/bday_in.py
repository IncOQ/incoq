from incoq.mars.runtime import *

def main():
    bdays = Set()
    bdays.update([1, 2, 3])
    BREL = Set()
    BREL.update([('jon', 1), ('bo', 1), ('annie', 2)])
    
    print(QUERY('Q4', count(QUERY('Q3',
          {b for b in bdays if QUERY('Q2', count(QUERY('Q1',
                            {p for (p, b2) in BREL if b2 == b}))) > 1}))))
    
    BREL.remove(('jon', 1))
    BREL.add(('jon', 3))
    
    print(QUERY('Q4', count(QUERY('Q3',
          {b for b in bdays if QUERY('Q2', count(QUERY('Q1',
                            {p for (p, b2) in BREL if b2 == b}))) > 1}))))
