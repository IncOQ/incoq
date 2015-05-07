from incoq.runtime import *
_m_R_out = Map()
def _maint__m_R_out_add(_e):
    (v1_1, v1_2) = _e
    if (v1_1 not in _m_R_out):
        _m_R_out[v1_1] = set()
    _m_R_out[v1_1].add(v1_2)

def query_Comp1(a):
    'a -> {e : (a, _tup1) in R, (_tup1, b2, _) in _TUP2, (b2, _tup2) in R, (_tup2, _, e) in _TUP2}'
    result = set()
    for _tup1 in (_m_R_out[a] if (a in _m_R_out) else set()):
        if (isinstance(_tup1, tuple) and (len(_tup1) == 2)):
            for b2 in setmatch({(_tup1, _tup1[0], _tup1[1])}, 'buw', _tup1):
                for _tup2 in (_m_R_out[b2] if (b2 in _m_R_out) else set()):
                    if (isinstance(_tup2, tuple) and (len(_tup2) == 2)):
                        for e in setmatch({(_tup2, _tup2[0], _tup2[1])}, 'bwu', _tup2):
                            if (e not in result):
                                result.add(e)
    return result

for (x, y) in [(1, (2, 3)), (2, (3, 4)), (3, (4, 5))]:
    # Begin maint _m_R_out after "R.add((x, y))"
    _maint__m_R_out_add((x, y))
    # End maint _m_R_out after "R.add((x, y))"
a = 1
print(sorted(query_Comp1(a)))