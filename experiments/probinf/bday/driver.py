import matplotlib.pyplot as plt
import random
from time import clock
import bday_in
import bday_inc
import bday_dem


num_bdays = 100
for bday in [bday_in, bday_inc, bday_dem]:
    bday.setup_bdays(num_bdays)
K = 1000


def run(bday, n, k):
    brel_map = {}
    actions = []
    # Init.
    for person in range(n):
        day = random.randrange(num_bdays)
        bday.add_brel(person, day)
        brel_map[person] = day
    
    for _ in range(k):
        person = random.randrange(n)
        old_day = brel_map[person]
        new_day = random.randrange(num_bdays)
        brel_map[person] = new_day
        actions.append((person, old_day, new_day))
    
    t1 = clock()
    for person, old_day, new_day in actions:
        bday.remove_brel(person, old_day)
        bday.add_brel(person, new_day)
        bday.do_query(1)
    t2 = clock()
    
    bday.clear_all()
    
    print('.', end='', flush=True)
    return t2 - t1


# Go up to 200 for all three.
xs = list(range(20, 200 + 1, 20)) 
# Go up to 5000 for just y2s and y3s.
#xs = list(range(200, 5000 + 1, 200))
y1s = []
y2s = []
y3s = []
for x in xs:
    y1s.append(run(bday_in, x, K))
    y2s.append(run(bday_inc, x, K))
    y3s.append(run(bday_dem, x, K))
    print()

plt.plot(xs, y1s, '-o', label='orig')
plt.plot(xs, y2s, '-o', label='inc')
plt.plot(xs, y3s, '-o', label='dem')
plt.legend()
plt.show()
