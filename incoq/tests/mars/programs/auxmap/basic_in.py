# Basic auxiliary map test.

from incoq.mars.runtime import *

S = Set()

def main():
    for x, y in [(1, 2), (1, 3), (2, 3), (2, 4)]:
        S.add((x, y))
    print(sorted(S.imgset('bu', (x,))))

if __name__ == '__main__':
    main()
