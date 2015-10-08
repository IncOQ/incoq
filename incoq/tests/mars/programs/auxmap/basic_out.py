from incoq.mars.runtime import *
# S : {(Number, Number)}
S = Set()
# S_bu : {(Number): {(Number)}}
S_bu = Map()
def _maint_S_bu_for_S_add(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v4_key = (_elem_v1,)
    _v4_value = (_elem_v2,)
    if (_v4_key not in S_bu):
        _v5 = set()
        S_bu[_v4_key] = _v5
    S_bu[_v4_key].add(_v4_value)

def _maint_S_bu_for_S_remove(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v6_key = (_elem_v1,)
    _v6_value = (_elem_v2,)
    S_bu[_v6_key].remove(_v6_value)
    if (len(S_bu[_v6_key]) == 0):
        del S_bu[_v6_key]

def main():
    for _v1 in [(1, 2), (1, 3), (2, 3), (2, 4)]:
        (x, y) = _v1
        _v2 = (x, y)
        S.add(_v2)
        _maint_S_bu_for_S_add(_v2)
    x = 1
    print(sorted(S_bu.get((x,), set())))
    _v3 = (1, 3)
    _maint_S_bu_for_S_remove(_v3)
    S.remove(_v3)
    print(sorted(S_bu.get((x,), set())))

if (__name__ == '__main__'):
    main()
