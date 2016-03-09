from incoq.mars.runtime import *
# SM : {(Number, Number, str)}
SM = Set()
# M : {(Number, Number): str}
M = Map()
# SM_buu : {Number: {(Number, str)}}
SM_buu = Map()
def _maint_SM_buu_for_SM_add(_elem):
    (_elem_v1, _elem_v2, _elem_v3) = _elem
    _v3_key = _elem_v1
    _v3_value = (_elem_v2, _elem_v3)
    if (_v3_key not in SM_buu):
        _v4 = Set()
        SM_buu[_v3_key] = _v4
    SM_buu[_v3_key].add(_v3_value)

def _maint_SM_buu_for_SM_remove(_elem):
    (_elem_v1, _elem_v2, _elem_v3) = _elem
    _v5_key = _elem_v1
    _v5_value = (_elem_v2, _elem_v3)
    SM_buu[_v5_key].remove(_v5_value)
    if (len(SM_buu[_v5_key]) == 0):
        del SM_buu[_v5_key]

def _maint_SM_for_M_assign(_key, _val):
    (_key_v1, _key_v2) = _key
    _v1_elem = (_key_v1, _key_v2, _val)
    SM.add(_v1_elem)
    _maint_SM_buu_for_SM_add(_v1_elem)

def _maint_SM_for_M_delete(_key):
    _val = M[_key]
    (_key_v1, _key_v2) = _key
    _v2_elem = (_key_v1, _key_v2, _val)
    _maint_SM_buu_for_SM_remove(_v2_elem)
    SM.remove(_v2_elem)

def main():
    for (k1, k2, v1) in [(1, 2, 'a'), (3, 4, 'b')]:
        k = (k1, k2)
        v = v1
        M[k] = v
        _maint_SM_for_M_assign(k, v)
    x = 3
    print(sorted(SM))
    print(sorted(SM_buu.get(x, Set())))
    k = (3, 4)
    _maint_SM_for_M_delete(k)
    del M[k]
    print(sorted(SM))
    print(sorted(SM_buu.get(x, Set())))
    SM_buu.dictclear()
    SM.clear()
    M.dictclear()
    print(sorted(SM))

if (__name__ == '__main__'):
    main()
