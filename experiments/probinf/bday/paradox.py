import random
from time import process_time
#import bday_in as bday
import bday_inc as bday

num_bdays = 365
people = range(23)
K = 100000
threshold = 1

t1 = process_time()

bday.setup_bdays(num_bdays)

bdays = {}
for p in people:
    day = random.randrange(num_bdays)
    bday.add_brel(p, day)
    bdays[p] = day

results = []

for _ in range(K):
    p = random.choice(people)
    old_day = bdays[p]
    bday.remove_brel(p, old_day)
    
    new_day = random.randrange(num_bdays)
    bday.add_brel(p, new_day)
    bdays[p] = new_day
    
    results.append(bday.do_query(threshold) > 0)

t2 = process_time()

print('{} people, {} changes'.format(len(people), K))
print('Estimated probability: {:.6f}'.format(sum(results)/len(results)))
print('Took {:.3f} seconds'.format(t2 - t1))
