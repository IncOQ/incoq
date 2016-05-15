# Basic auxiliary map test.

from incoq.mars.runtime import *

S = Set()

def main():
    for x, y in [(1, 2), (1, 3), (2, 3), (2, 4)]:
        S.add((x, y))
    x = 1
    print(sorted(S.imglookup('bu', (x,))))
    S.remove((1, 3))
    print(sorted(S.imglookup('bu', (x,))))
    S.add((1, 4))
    print(sorted(S.imglookup('bu', (x,))))
    S.clear()
    print(sorted(S.imglookup('bu', (x,))))

if __name__ == '__main__':
    main()
