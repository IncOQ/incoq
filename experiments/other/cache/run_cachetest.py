"""Invoke valgrind to repeatedly run cachetest.py and report
LL cache misses.
"""

import pickle
import subprocess
import re


def run(x):
    results = subprocess.check_output(
        ['valgrind',
         '--tool=cachegrind',
         '--cachegrind-out-file=/dev/null',
         
         # 256KB L2 cache
        '--LL=262144,8,64',
         # 3MB L3 cache
#         '--LL=3145728,12,64',
         # 8MB L3 cache
#         '--LL=8388608,16,64',
         
         'python3.3',
         'cachetest.py',
         str(x)],
        universal_newlines=True,
        stderr=subprocess.STDOUT)
    return results


def parse_results(results):
    """Parse and return LL stats."""
    num_pat = r'(\d+([,.]\d+)*)'
    drefs_pat = r'D   refs:\s*' + num_pat
    d1misses_pat = r'D1  misses:\s*' + num_pat
    d1missrate_pat = r'D1  miss rate:\s*' + num_pat
    llrefs_pat = r'LL refs:\s*' + num_pat
    llmisses_pat = r'LL misses:\s*' + num_pat
    llmissrate_pat = r'LL miss rate:\s*' + num_pat
    
    for line in results.split('\n'):
        m = re.search(drefs_pat, line)
        if m is not None:
            drefs = m.group(1)
            continue
        m = re.search(d1misses_pat, line)
        if m is not None:
            d1misses  = m.group(1)
            continue
        m = re.search(d1missrate_pat, line)
        if m is not None:
            d1missrate = m.group(1)
            continue
        
        m = re.search(llrefs_pat, line)
        if m is not None:
            llrefs = m.group(1)
            continue
        m = re.search(llmisses_pat, line)
        if m is not None:
            llmisses = m.group(1)
            continue
        m = re.search(llmissrate_pat, line)
        if m is not None:
            llmissrate = m.group(1)
            continue
    
    return drefs, d1misses, d1missrate, llrefs, llmisses, llmissrate


def toint(s):
    return int(s.replace(',', ''))
def tofloat(s):
    return float(s.replace(',', ''))


xs = (list(range(250, 5001, 250)) + 
      list(range(6000, 20001, 1000)))

data = []

for x in xs:
    res = run(x)
    stats = parse_results(res)
    drefs, d1misses, d1missrate, llrefs, llmisses, llmissrate = stats
    print('x = {:<5}    drefs:  {:<12} d1misses: {:<12} d1missrate: {:<4}\n'
          '             llrefs: {:<12} llmisses: {:<12} llmissrate: {:<4}'
          .format(x, drefs, d1misses, d1missrate,
                  llrefs, llmisses, llmissrate))
    data.append((toint(drefs), toint(d1misses), tofloat(d1missrate),
                 toint(llrefs), toint(llmisses), tofloat(llmissrate)))

print(xs)
print(data)

with open('cachetest_out.pickle', 'wb') as f:
    pickle.dump(xs, f)
    pickle.dump(data, f)
    print('Wrote out cachetest_out.pickle.')
