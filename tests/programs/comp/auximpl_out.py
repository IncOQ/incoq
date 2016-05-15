# Q : a -> {(c,) for (a, b) in REL(S) for (b, c) in REL(S)} : {(Number)}
from incoq.runtime import *
# S_bu : {Number: {Number}}
S_bu = Map()
def _maint_S_bu_for_S_add(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v2_key = _elem_v1
    _v2_value = _elem_v2
    if (_v2_key not in S_bu):
        _v3 = Set()
        S_bu[_v2_key] = _v3
    S_bu[_v2_key].add(_v2_value)

def _compute_Q(a):
    _result = Set()
    for b in (S_bu[a] if (a in S_bu) else ()):
        for c in (S_bu[b] if (b in S_bu) else ()):
            if ((c,) not in _result):
                _result.add((c,))
    return _result

def main():
    for (x, y) in [(1, 2), (1, 3), (2, 3), (2, 4), (4, 5)]:
        _v1 = (x, y)
        _maint_S_bu_for_S_add(_v1)
    a = 1
    print(sorted(_compute_Q(a)))

if (__name__ == '__main__'):
    main()
