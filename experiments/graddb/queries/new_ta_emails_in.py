from incoq.mars.runtime import *

def main():
    new = Set()
    
    print(QUERY('Q',
        {e for s in new
           for e in s.email
           for support in s.support.all 
           if support.kind == 'ta'}))
