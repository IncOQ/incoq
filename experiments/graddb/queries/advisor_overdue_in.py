from incoq.runtime import *

def main():
    no_advisor = Set()
    sem = 'a'
    
    # Changed string concatenation to tuple, to trick type analysis
    # into not complaining.
    print(QUERY('Q',
        {s for s in no_advisor
           for p in s.program.all
           if not (p.start and p.start > sem or p.end and p.end < sem)
           if p.program=='phd' and s.joined < sem or
              p.program=='ms' and s.joined <= sem}))
