# Q1 : count(unwrap(S_wrapped)) : Number
# Q2 : sum(unwrap(S_wrapped)) : Number
# Q3 : min(unwrap(S_wrapped)) : Number
# Q4 : max(unwrap(S_wrapped)) : Number
from incoq.mars.runtime import *
# A_Q1 : {(): Number}
A_Q1 = Map()
# A_Q2 : {(): Number}
A_Q2 = Map()
# A_Q3 : {(): (Number)}
A_Q3 = Map()
# A_Q4 : {(): (Number)}
A_Q4 = Map()
def _maint_A_Q4_for_S_wrapped_add(_elem):
    (_elem_v1,) = _elem
    _v9_key = ()
    _v9_value = _elem_v1
    _v9_state = A_Q4.get(_v9_key, (Tree(), None))
    (_v9tree, _) = _v9_state
    _v9tree[_v9_value] = None
    _v9_state = (_v9tree, _v9tree.__max__())
    if (_v9_key in A_Q4):
        del A_Q4[_v9_key]
    A_Q4[_v9_key] = _v9_state

def _maint_A_Q4_for_S_wrapped_remove(_elem):
    (_elem_v1,) = _elem
    _v10_key = ()
    _v10_value = _elem_v1
    _v10_state = A_Q4[_v10_key]
    (_v10tree, _) = _v10_state
    del _v10tree[_v10_value]
    _v10_state = (_v10tree, _v10tree.__max__())
    del A_Q4[_v10_key]
    if (not (len(index(_v10_state, 0)) == 0)):
        A_Q4[_v10_key] = _v10_state

def _maint_A_Q3_for_S_wrapped_add(_elem):
    (_elem_v1,) = _elem
    _v7_key = ()
    _v7_value = _elem_v1
    _v7_state = A_Q3.get(_v7_key, (Tree(), None))
    (_v7tree, _) = _v7_state
    _v7tree[_v7_value] = None
    _v7_state = (_v7tree, _v7tree.__min__())
    if (_v7_key in A_Q3):
        del A_Q3[_v7_key]
    A_Q3[_v7_key] = _v7_state

def _maint_A_Q3_for_S_wrapped_remove(_elem):
    (_elem_v1,) = _elem
    _v8_key = ()
    _v8_value = _elem_v1
    _v8_state = A_Q3[_v8_key]
    (_v8tree, _) = _v8_state
    del _v8tree[_v8_value]
    _v8_state = (_v8tree, _v8tree.__min__())
    del A_Q3[_v8_key]
    if (not (len(index(_v8_state, 0)) == 0)):
        A_Q3[_v8_key] = _v8_state

def _maint_A_Q2_for_S_wrapped_add(_elem):
    (_elem_v1,) = _elem
    _v5_key = ()
    _v5_value = _elem_v1
    _v5_state = A_Q2.get(_v5_key, (0, 0))
    _v5_state = ((index(_v5_state, 0) + _v5_value), (index(_v5_state, 1) + 1))
    if (_v5_key in A_Q2):
        del A_Q2[_v5_key]
    A_Q2[_v5_key] = _v5_state

def _maint_A_Q2_for_S_wrapped_remove(_elem):
    (_elem_v1,) = _elem
    _v6_key = ()
    _v6_value = _elem_v1
    _v6_state = A_Q2[_v6_key]
    _v6_state = ((index(_v6_state, 0) - _v6_value), (index(_v6_state, 1) - 1))
    del A_Q2[_v6_key]
    if (not (index(_v6_state, 1) == 0)):
        A_Q2[_v6_key] = _v6_state

def _maint_A_Q1_for_S_wrapped_add(_elem):
    (_elem_v1,) = _elem
    _v3_key = ()
    _v3_value = _elem_v1
    _v3_state = A_Q1.get(_v3_key, 0)
    _v3_state = (_v3_state + 1)
    if (_v3_key in A_Q1):
        del A_Q1[_v3_key]
    A_Q1[_v3_key] = _v3_state

def _maint_A_Q1_for_S_wrapped_remove(_elem):
    (_elem_v1,) = _elem
    _v4_key = ()
    _v4_value = _elem_v1
    _v4_state = A_Q1[_v4_key]
    _v4_state = (_v4_state - 1)
    del A_Q1[_v4_key]
    if (not (_v4_state == 0)):
        A_Q1[_v4_key] = _v4_state

def _maint_S_wrapped_for_S_add(_elem):
    _v1_v = (_elem,)
    _maint_A_Q4_for_S_wrapped_add(_v1_v)
    _maint_A_Q3_for_S_wrapped_add(_v1_v)
    _maint_A_Q2_for_S_wrapped_add(_v1_v)
    _maint_A_Q1_for_S_wrapped_add(_v1_v)

def main():
    for x in [1, 2, 3, 4]:
        _maint_S_wrapped_for_S_add(x)
    print(A_Q1.get((), 0))
    print(index(A_Q2.get((), (0, 0)), 0))
    print(index(A_Q3.get((), (Tree(), None)), 1))
    print(index(A_Q4.get((), (Tree(), None)), 1))

if (__name__ == '__main__'):
    main()
