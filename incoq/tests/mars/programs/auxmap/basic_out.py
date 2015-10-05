from incoq.mars.runtime import *
# S : {(Number, Number)}
S = Set()
# S_bu : Bottom
S_bu = Map()
def _maint_S_bu_for_S_add(_elem):
    (_elem_v1, _elem_v2) = _elem
    if ((_elem_v1,) not in S_bu):
        S_bu[(_elem_v1,)] = set()
    S_bu[(_elem_v1,)].add((_elem_v2,))

def _maint_S_bu_for_S_remove(_elem):
    (_elem_v1, _elem_v2) = _elem
    S_bu[(_elem_v1,)].remove((_elem_v2,))
    if (len(S_bu[(_elem_v1,)]) == 0):
        del S_bu[(_elem_v1,)]

def main():
    for _v in [(1, 2), (1, 3), (2, 3), (2, 4)]:
        (x, y) = _v
        S.add((x, y))
        _maint_S_bu_for_S_add((x, y))
    x = 1
    print(sorted(S_bu.get((x,), set())))
    _maint_S_bu_for_S_remove((1, 3))
    S.remove((1, 3))
    print(sorted(S_bu.get((x,), set())))

if (__name__ == '__main__'):
    main()
