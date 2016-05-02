# Q : {(c,) for (a, b) in REL(S) for (a,) in REL(R_wrapped) for (b, c) in REL(S)} : {(Number)}
from incoq.mars.runtime import *
# R : {Number}
R = Set()
# R_wrapped : {(Number)}
R_wrapped = Set()
# R_Q : {(Number)}
R_Q = CSet()
# R_Q_unwrapped : {Number}
R_Q_unwrapped = Set()
# S_bu : {Number: {Number}}
S_bu = Map()
# S_ub : {Number: {Number}}
S_ub = Map()
def _maint_S_bu_for_S_add(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v9_key = _elem_v1
    _v9_value = _elem_v2
    if (_v9_key not in S_bu):
        _v10 = Set()
        S_bu[_v9_key] = _v10
    S_bu[_v9_key].add(_v9_value)

def _maint_S_bu_for_S_remove(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v11_key = _elem_v1
    _v11_value = _elem_v2
    S_bu[_v11_key].remove(_v11_value)
    if (len(S_bu[_v11_key]) == 0):
        del S_bu[_v11_key]

def _maint_S_ub_for_S_add(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v12_key = _elem_v2
    _v12_value = _elem_v1
    if (_v12_key not in S_ub):
        _v13 = Set()
        S_ub[_v12_key] = _v13
    S_ub[_v12_key].add(_v12_value)

def _maint_S_ub_for_S_remove(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v14_key = _elem_v2
    _v14_value = _elem_v1
    S_ub[_v14_key].remove(_v14_value)
    if (len(S_ub[_v14_key]) == 0):
        del S_ub[_v14_key]

def _maint_R_Q_unwrapped_for_R_Q_add(_elem):
    _v15_v = index(_elem, 0)
    R_Q_unwrapped.add(_v15_v)

def _maint_R_Q_unwrapped_for_R_Q_remove(_elem):
    _v16_v = index(_elem, 0)
    R_Q_unwrapped.remove(_v16_v)

def _maint_R_Q_for_S_add(_elem):
    # Cost: O((S_bu + S_ub))
    (_v5_a, _v5_b) = _elem
    if ((_v5_a,) in R_wrapped):
        for _v5_c in (S_bu[_v5_b] if (_v5_b in S_bu) else ()):
            if ((_v5_b, _v5_c) != _elem):
                _v5_result = (_v5_c,)
                if (_v5_result not in R_Q):
                    R_Q.add(_v5_result)
                    _maint_R_Q_unwrapped_for_R_Q_add(_v5_result)
                else:
                    R_Q.inccount(_v5_result)
    (_v5_b, _v5_c) = _elem
    for _v5_a in (S_ub[_v5_b] if (_v5_b in S_ub) else ()):
        if ((_v5_a,) in R_wrapped):
            _v5_result = (_v5_c,)
            if (_v5_result not in R_Q):
                R_Q.add(_v5_result)
                _maint_R_Q_unwrapped_for_R_Q_add(_v5_result)
            else:
                R_Q.inccount(_v5_result)

def _maint_R_Q_for_S_remove(_elem):
    # Cost: O((S_bu + S_ub))
    (_v6_a, _v6_b) = _elem
    if ((_v6_a,) in R_wrapped):
        for _v6_c in (S_bu[_v6_b] if (_v6_b in S_bu) else ()):
            if ((_v6_b, _v6_c) != _elem):
                _v6_result = (_v6_c,)
                if (R_Q.getcount(_v6_result) == 1):
                    _maint_R_Q_unwrapped_for_R_Q_remove(_v6_result)
                    R_Q.remove(_v6_result)
                else:
                    R_Q.deccount(_v6_result)
    (_v6_b, _v6_c) = _elem
    for _v6_a in (S_ub[_v6_b] if (_v6_b in S_ub) else ()):
        if ((_v6_a,) in R_wrapped):
            _v6_result = (_v6_c,)
            if (R_Q.getcount(_v6_result) == 1):
                _maint_R_Q_unwrapped_for_R_Q_remove(_v6_result)
                R_Q.remove(_v6_result)
            else:
                R_Q.deccount(_v6_result)

def _maint_R_Q_for_R_wrapped_add(_elem):
    # Cost: O((S_bu * S_bu))
    (_v7_a,) = _elem
    for _v7_b in (S_bu[_v7_a] if (_v7_a in S_bu) else ()):
        for _v7_c in (S_bu[_v7_b] if (_v7_b in S_bu) else ()):
            _v7_result = (_v7_c,)
            if (_v7_result not in R_Q):
                R_Q.add(_v7_result)
                _maint_R_Q_unwrapped_for_R_Q_add(_v7_result)
            else:
                R_Q.inccount(_v7_result)

def _maint_R_Q_for_R_wrapped_remove(_elem):
    # Cost: O((S_bu * S_bu))
    (_v8_a,) = _elem
    for _v8_b in (S_bu[_v8_a] if (_v8_a in S_bu) else ()):
        for _v8_c in (S_bu[_v8_b] if (_v8_b in S_bu) else ()):
            _v8_result = (_v8_c,)
            if (R_Q.getcount(_v8_result) == 1):
                _maint_R_Q_unwrapped_for_R_Q_remove(_v8_result)
                R_Q.remove(_v8_result)
            else:
                R_Q.deccount(_v8_result)

def _maint_R_wrapped_for_R_add(_elem):
    # Cost: O((S_bu * S_bu))
    _v3_v = (_elem,)
    R_wrapped.add(_v3_v)
    _maint_R_Q_for_R_wrapped_add(_v3_v)

def _maint_R_wrapped_for_R_remove(_elem):
    # Cost: O((S_bu * S_bu))
    _v4_v = (_elem,)
    _maint_R_Q_for_R_wrapped_remove(_v4_v)
    R_wrapped.remove(_v4_v)

def main():
    for (x, y) in [(1, 2), (1, 3), (2, 3), (2, 4), (3, 5)]:
        _v1 = (x, y)
        _maint_S_bu_for_S_add(_v1)
        _maint_S_ub_for_S_add(_v1)
        _maint_R_Q_for_S_add(_v1)
        if (x not in R):
            R.add(x)
            _maint_R_wrapped_for_R_add(x)
    print(sorted(R_Q_unwrapped))
    _v2 = 1
    _maint_R_wrapped_for_R_remove(_v2)
    R.remove(_v2)
    print(sorted(R_Q_unwrapped))

if (__name__ == '__main__'):
    main()
