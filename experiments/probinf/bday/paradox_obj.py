import random
from collections import deque
from time import process_time
#import bday_obj_in as bday
import bday_obj_inc as bday

n_people = 23
n_samples = 100000
threshold = 1

t1 = process_time()

bday.init()

persons = deque()
for _ in range(n_people):
    p = bday.add_person(random.randint(1, 365))
    persons.append(p)

samples = []
for _ in range(n_samples):
    samples.append(bday.do_query(threshold) > 0)
    p = persons.popleft()
    bday.remove_person(p)
    p = bday.add_person(random.randint(1, 365))
    persons.append(p)

t2 = process_time()

print('{} people, {} samples'.format(n_people, n_samples))
print('Estimated probability: {:.6f}'.format(sum(samples)/len(samples)))
print('Took {:.3f} seconds'.format(t2 - t1))
