import sys
import random
from collections import deque
import argparse
from time import process_time


def run(bday, n_people, n_samples, threshold):
    # Do not call more than once per process; the bday database needs
    # to be cleared between uses.
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='paradox_obj.py')
    parser.add_argument('people', type=int)
    parser.add_argument('samples', type=int)
    parser.add_argument('threshold', type=int, nargs='?', default=1)
    parser.add_argument('--inc', action='store_true')
    
    ns = parser.parse_args(sys.argv[1:])
    
    if ns.inc:
        import bday_obj_inc as bday
    else:
        import bday_obj_in as bday
    
    run(bday, ns.people, ns.samples, ns.threshold)
