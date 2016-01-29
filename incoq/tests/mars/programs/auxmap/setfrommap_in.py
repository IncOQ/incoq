# Test setfrommap() construct.

from incoq.mars.runtime import *

M = Map()

def main():
    for k1, k2, v1 in [(1, 2, 'a'), (3, 4, 'b')]:
        k = (k1, k2)
        v = (v1,)
        M[k] = v
    x = 3
    print(sorted(M.setfrommap('bbu')))
    print(sorted(M.setfrommap('bbu').imglookup('buu', (x,))))
    k = (3, 4)
    del M[k]
    print(sorted(M.setfrommap('bbu')))
    print(sorted(M.setfrommap('bbu').imglookup('buu', (x,))))

if __name__ == '__main__':
    main()
