from incoq.mars.runtime import *
# S : {(Number, Number)}
S = Set()
# S_bu : {(Number): {(Number)}}
S_bu = Map()
def _maint_S_bu_for_S_add(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v3_key = (_elem_v1,)
    _v3_value = (_elem_v2,)
    if (_v3_key not in S_bu):
        _v4 = Set()
        S_bu[_v3_key] = _v4
    S_bu[_v3_key].add(_v3_value)

def _maint_S_bu_for_S_remove(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v5_key = (_elem_v1,)
    _v5_value = (_elem_v2,)
    S_bu[_v5_key].remove(_v5_value)
    if (len(S_bu[_v5_key]) == 0):
        del S_bu[_v5_key]

def main():
    for (x, y) in [(1, 2), (1, 3), (2, 3), (2, 4)]:
        _v1 = (x, y)
        S.add(_v1)
        _maint_S_bu_for_S_add(_v1)
    x = 1
    print(sorted(S_bu.get((x,), Set())))
    _v2 = (1, 3)
    _maint_S_bu_for_S_remove(_v2)
    S.remove(_v2)
    print(sorted(S_bu.get((x,), Set())))

if (__name__ == '__main__'):
    main()
