import sys
import gc
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


run(int(sys.argv[1]), 500)
