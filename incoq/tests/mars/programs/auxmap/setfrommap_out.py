from incoq.mars.runtime import *
# SM : {(Number, Number, str)}
SM = Set()
# M : {(Number, Number): (str)}
M = Map()
def _maint_SM_for_M_assign(_key, _val):
    (_key_v1, _key_v2) = _key
    (_val_v1,) = _val
    _v1_elem = (_key_v1, _key_v2, _val_v1)
    SM.add(_v1_elem)

def _maint_SM_for_M_delete(_key):
    _val = M[_key]
    (_key_v1, _key_v2) = _key
    (_val_v1,) = _val
    _v2_elem = (_key_v1, _key_v2, _val_v1)
    SM.remove(_v2_elem)

def main():
    for (k1, k2, v1) in [(1, 2, 'a'), (3, 4, 'b')]:
        k = (k1, k2)
        v = (v1,)
        M[k] = v
        _maint_SM_for_M_assign(k, v)
    print(sorted(SM))
    k = (3, 4)
    _maint_SM_for_M_delete(k)
    del M[k]
    print(sorted(SM))

if (__name__ == '__main__'):
    main()
