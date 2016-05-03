# Q1 : count(unwrap(S)) : Top
# Q2 : sum(unwrap(S)) : Top
# Q3 : min(unwrap(S)) : Top
# Q4 : max(unwrap(S)) : Top
# Q5 : min(S) : (Number)
# Q6 : max(S) : (Number)
from incoq.mars.runtime import *
# A_Q1 : {(): Number}
A_Q1 = Map()
# A_Q2 : {(): Number}
A_Q2 = Map()
# A_Q3 : {(): (Number)}
A_Q3 = Map()
# A_Q4 : {(): (Number)}
A_Q4 = Map()
# A_Q5 : {(): (Number)}
A_Q5 = Map()
# A_Q6 : {(): (Number)}
A_Q6 = Map()
def _maint_A_Q6_for_S_add(_elem):
    # Cost: O(?)
    #       O(?)
    (_elem_v1,) = _elem
    _v13_key = ()
    _v13_value = (_elem_v1,)
    _v13_state = A_Q6.get(_v13_key, (Tree(), None))
    (_v13tree, _) = _v13_state
    _v13tree[_v13_value] = None
    _v13_state = (_v13tree, _v13tree.__max__())
    if (_v13_key in A_Q6):
        del A_Q6[_v13_key]
    A_Q6[_v13_key] = _v13_state

def _maint_A_Q6_for_S_remove(_elem):
    # Cost: O(?)
    #       O(?)
    (_elem_v1,) = _elem
    _v14_key = ()
    _v14_value = (_elem_v1,)
    _v14_state = A_Q6[_v14_key]
    (_v14tree, _) = _v14_state
    del _v14tree[_v14_value]
    _v14_state = (_v14tree, _v14tree.__max__())
    del A_Q6[_v14_key]
    if (not (len(index(_v14_state, 0)) == 0)):
        A_Q6[_v14_key] = _v14_state

def _maint_A_Q5_for_S_add(_elem):
    # Cost: O(?)
    #       O(?)
    (_elem_v1,) = _elem
    _v11_key = ()
    _v11_value = (_elem_v1,)
    _v11_state = A_Q5.get(_v11_key, (Tree(), None))
    (_v11tree, _) = _v11_state
    _v11tree[_v11_value] = None
    _v11_state = (_v11tree, _v11tree.__min__())
    if (_v11_key in A_Q5):
        del A_Q5[_v11_key]
    A_Q5[_v11_key] = _v11_state

def _maint_A_Q5_for_S_remove(_elem):
    # Cost: O(?)
    #       O(?)
    (_elem_v1,) = _elem
    _v12_key = ()
    _v12_value = (_elem_v1,)
    _v12_state = A_Q5[_v12_key]
    (_v12tree, _) = _v12_state
    del _v12tree[_v12_value]
    _v12_state = (_v12tree, _v12tree.__min__())
    del A_Q5[_v12_key]
    if (not (len(index(_v12_state, 0)) == 0)):
        A_Q5[_v12_key] = _v12_state

def _maint_A_Q4_for_S_add(_elem):
    # Cost: O(?)
    #       O(?)
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

def _maint_A_Q4_for_S_remove(_elem):
    # Cost: O(?)
    #       O(?)
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

def _maint_A_Q3_for_S_add(_elem):
    # Cost: O(?)
    #       O(?)
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

def _maint_A_Q3_for_S_remove(_elem):
    # Cost: O(?)
    #       O(?)
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

def _maint_A_Q2_for_S_add(_elem):
    # Cost: O(1)
    #       O(1)
    (_elem_v1,) = _elem
    _v5_key = ()
    _v5_value = _elem_v1
    _v5_state = A_Q2.get(_v5_key, (0, 0))
    _v5_state = ((index(_v5_state, 0) + _v5_value), (index(_v5_state, 1) + 1))
    if (_v5_key in A_Q2):
        del A_Q2[_v5_key]
    A_Q2[_v5_key] = _v5_state

def _maint_A_Q2_for_S_remove(_elem):
    # Cost: O(1)
    #       O(1)
    (_elem_v1,) = _elem
    _v6_key = ()
    _v6_value = _elem_v1
    _v6_state = A_Q2[_v6_key]
    _v6_state = ((index(_v6_state, 0) - _v6_value), (index(_v6_state, 1) - 1))
    del A_Q2[_v6_key]
    if (not (index(_v6_state, 1) == 0)):
        A_Q2[_v6_key] = _v6_state

def _maint_A_Q1_for_S_add(_elem):
    # Cost: O(1)
    #       O(1)
    (_elem_v1,) = _elem
    _v3_key = ()
    _v3_value = _elem_v1
    _v3_state = A_Q1.get(_v3_key, 0)
    _v3_state = (_v3_state + 1)
    if (_v3_key in A_Q1):
        del A_Q1[_v3_key]
    A_Q1[_v3_key] = _v3_state

def _maint_A_Q1_for_S_remove(_elem):
    # Cost: O(1)
    #       O(1)
    (_elem_v1,) = _elem
    _v4_key = ()
    _v4_value = _elem_v1
    _v4_state = A_Q1[_v4_key]
    _v4_state = (_v4_state - 1)
    del A_Q1[_v4_key]
    if (not (_v4_state == 0)):
        A_Q1[_v4_key] = _v4_state

def main():
    # Cost: O(?)
    #       O(?)
    for x in [1, 2, 3, 4]:
        _v1 = (x,)
        _maint_A_Q6_for_S_add(_v1)
        _maint_A_Q5_for_S_add(_v1)
        _maint_A_Q4_for_S_add(_v1)
        _maint_A_Q3_for_S_add(_v1)
        _maint_A_Q2_for_S_add(_v1)
        _maint_A_Q1_for_S_add(_v1)
    print(A_Q1.get((), 0))
    print(index(A_Q2.get((), (0, 0)), 0))
    print(index(A_Q3.get((), (Tree(), None)), 1))
    print(index(A_Q4.get((), (Tree(), None)), 1))
    print(index(A_Q5.get((), (Tree(), None)), 1))
    print(index(A_Q6.get((), (Tree(), None)), 1))
    _v2 = (4,)
    _maint_A_Q1_for_S_remove(_v2)
    _maint_A_Q2_for_S_remove(_v2)
    _maint_A_Q3_for_S_remove(_v2)
    _maint_A_Q4_for_S_remove(_v2)
    _maint_A_Q5_for_S_remove(_v2)
    _maint_A_Q6_for_S_remove(_v2)
    print(A_Q1.get((), 0))
    print(index(A_Q2.get((), (0, 0)), 0))
    print(index(A_Q3.get((), (Tree(), None)), 1))
    print(index(A_Q4.get((), (Tree(), None)), 1))
    print(index(A_Q5.get((), (Tree(), None)), 1))
    print(index(A_Q6.get((), (Tree(), None)), 1))
    A_Q1.dictclear()
    A_Q2.dictclear()
    A_Q3.dictclear()
    A_Q4.dictclear()
    A_Q5.dictclear()
    A_Q6.dictclear()
    print(A_Q1.get((), 0))
    print(index(A_Q2.get((), (0, 0)), 0))
    print(index(A_Q3.get((), (Tree(), None)), 1))
    print(index(A_Q4.get((), (Tree(), None)), 1))
    print(index(A_Q5.get((), (Tree(), None)), 1))
    print(index(A_Q6.get((), (Tree(), None)), 1))

if (__name__ == '__main__'):
    main()
