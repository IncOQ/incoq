import sys
import gc
import pickle
from time import process_time as pt
from random import randrange

gc.disable()


n_ops = 100000
n_trials = 10
max_x = 20000


class Obj:
    pass


def run(x, reps):
    objs = [Obj() for _ in range(max_x)]
    col = [(i, (objs[randrange(x)],)) for i in range(n_ops)]
    
    t1 = pt()
    for _ in range(reps):
        for (i, (o,)) in col:
            pass
    t2 = pt()
    return t2 - t1


# Timing.

def avgrun(x, reps):
    print('-- ' + str(x) + ' --')
    times = []
    for _ in range(n_trials):
        r = run(x, reps)
        print(format(r, '.3f'))
        r /= n_ops * reps
        times.append(r)
    print()
    return sum(times) / len(times)


xs = (list(range(250, 5001, 250)) + 
      list(range(6000, 20001, 1000)))


points = []
for x in xs:
    y = avgrun(x, 500)
    points.append((x, y))


xs, ys = zip(*points)
print(xs)
print(ys)

with open('timetest_out.pickle', 'wb') as f:
    pickle.dump(xs, f)
    pickle.dump(ys, f)
    print('Wrote out timetest_out.pickle.')
