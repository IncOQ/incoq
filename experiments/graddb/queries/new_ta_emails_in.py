from incoq.runtime import *

new = Set()

{e for s in new
   for e in s.email
   for support in s.support.all 
   if support.kind == 'ta'}
