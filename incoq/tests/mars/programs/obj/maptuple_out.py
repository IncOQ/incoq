# Q : m, k -> {(m, k, (x_f, y_f)) for (m,) in REL(_U_Q) for (m, k, m_k) in MAP() for (m_k, t_x_y) in M() for (t_x_y, x, y) in TUP() for (x, x_f) in F(f) for (y, y_f) in F(f)} : {(Top, Number, (Top, Top))}
# Q_T_m : {(m,) for (m,) in REL(_U_Q)} : Bottom
# Q_d_MAP : {(m, k, m_k) for (m,) in REL(R_Q_T_m) for (m, k, m_k) in MAP()} : Bottom
# Q_T_k : {(k,) for (m, k, m_k) in REL(R_Q_d_MAP)} : Bottom
# Q_T_m_k : {(m_k,) for (m, k, m_k) in REL(R_Q_d_MAP)} : Bottom
# Q_d_M : {(m_k, t_x_y) for (m_k,) in REL(R_Q_T_m_k) for (m_k, t_x_y) in M()} : Bottom
# Q_T_t_x_y : {(t_x_y,) for (m_k, t_x_y) in REL(R_Q_d_M)} : Bottom
# Q_d_TUP_2 : {(t_x_y, x, y) for (t_x_y,) in REL(R_Q_T_t_x_y) for (t_x_y, x, y) in TUP()} : Bottom
# Q_T_x : {(x,) for (t_x_y, x, y) in REL(R_Q_d_TUP_2)} : Bottom
# Q_T_y : {(y,) for (t_x_y, x, y) in REL(R_Q_d_TUP_2)} : Bottom
# Q_d_F_f_1 : {(x, x_f) for (x,) in REL(R_Q_T_x) for (x, x_f) in F(f)} : Bottom
# Q_T_x_f : {(x_f,) for (x, x_f) in REL(R_Q_d_F_f_1)} : Bottom
# Q_d_F_f_2 : {(y, y_f) for (y,) in REL(R_Q_T_y) for (y, y_f) in F(f)} : Bottom
# Q_T_y_f : {(y_f,) for (y, y_f) in REL(R_Q_d_F_f_2)} : Bottom
from incoq.mars.runtime import *
# _U_Q : {(Top)}
_U_Q = Set()
# R_Q : {(Top, Number, (Top, Top))}
R_Q = CSet()
# R_Q_T_m : Bottom
R_Q_T_m = Set()
# R_Q_T_k : Bottom
R_Q_T_k = CSet()
# R_Q_T_m_k : Bottom
R_Q_T_m_k = CSet()
# R_Q_T_t_x_y : Bottom
R_Q_T_t_x_y = CSet()
# R_Q_T_x : Bottom
R_Q_T_x = CSet()
# R_Q_T_y : Bottom
R_Q_T_y = CSet()
# R_Q_T_x_f : Bottom
R_Q_T_x_f = CSet()
# R_Q_T_y_f : Bottom
R_Q_T_y_f = CSet()
# _MAP_buu : {Top: Top}
_MAP_buu = Map()
# R_Q_d_MAP_uub : {Bottom: {(Bottom, Bottom)}}
R_Q_d_MAP_uub = Map()
# R_Q_d_M_ub : {Bottom: {Bottom}}
R_Q_d_M_ub = Map()
# R_Q_d_TUP_2_ubu : {Bottom: {(Bottom, Bottom)}}
R_Q_d_TUP_2_ubu = Map()
# R_Q_d_TUP_2_uub : {Bottom: {(Bottom, Bottom)}}
R_Q_d_TUP_2_uub = Map()
# R_Q_bbu : {(Top, Number): {(Top, Top)}}
R_Q_bbu = Map()
def _maint__MAP_buu_for__MAP_add(_elem):
    (_elem_v1, _elem_v2, _elem_v3) = _elem
    _v57_key = _elem_v1
    _v57_value = (_elem_v2, _elem_v3)
    if (_v57_key not in _MAP_buu):
        _v58 = Set()
        _MAP_buu[_v57_key] = _v58
    _MAP_buu[_v57_key].add(_v57_value)

def _maint__MAP_buu_for__MAP_remove(_elem):
    (_elem_v1, _elem_v2, _elem_v3) = _elem
    _v59_key = _elem_v1
    _v59_value = (_elem_v2, _elem_v3)
    _MAP_buu[_v59_key].remove(_v59_value)
    if (len(_MAP_buu[_v59_key]) == 0):
        del _MAP_buu[_v59_key]

def _maint_R_Q_d_MAP_uub_for_R_Q_d_MAP_add(_elem):
    (_elem_v1, _elem_v2, _elem_v3) = _elem
    _v60_key = _elem_v3
    _v60_value = (_elem_v1, _elem_v2)
    if (_v60_key not in R_Q_d_MAP_uub):
        _v61 = Set()
        R_Q_d_MAP_uub[_v60_key] = _v61
    R_Q_d_MAP_uub[_v60_key].add(_v60_value)

def _maint_R_Q_d_MAP_uub_for_R_Q_d_MAP_remove(_elem):
    (_elem_v1, _elem_v2, _elem_v3) = _elem
    _v62_key = _elem_v3
    _v62_value = (_elem_v1, _elem_v2)
    R_Q_d_MAP_uub[_v62_key].remove(_v62_value)
    if (len(R_Q_d_MAP_uub[_v62_key]) == 0):
        del R_Q_d_MAP_uub[_v62_key]

def _maint_R_Q_d_M_ub_for_R_Q_d_M_add(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v63_key = _elem_v2
    _v63_value = _elem_v1
    if (_v63_key not in R_Q_d_M_ub):
        _v64 = Set()
        R_Q_d_M_ub[_v63_key] = _v64
    R_Q_d_M_ub[_v63_key].add(_v63_value)

def _maint_R_Q_d_M_ub_for_R_Q_d_M_remove(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v65_key = _elem_v2
    _v65_value = _elem_v1
    R_Q_d_M_ub[_v65_key].remove(_v65_value)
    if (len(R_Q_d_M_ub[_v65_key]) == 0):
        del R_Q_d_M_ub[_v65_key]

def _maint_R_Q_d_TUP_2_ubu_for_R_Q_d_TUP_2_add(_elem):
    (_elem_v1, _elem_v2, _elem_v3) = _elem
    _v66_key = _elem_v2
    _v66_value = (_elem_v1, _elem_v3)
    if (_v66_key not in R_Q_d_TUP_2_ubu):
        _v67 = Set()
        R_Q_d_TUP_2_ubu[_v66_key] = _v67
    R_Q_d_TUP_2_ubu[_v66_key].add(_v66_value)

def _maint_R_Q_d_TUP_2_ubu_for_R_Q_d_TUP_2_remove(_elem):
    (_elem_v1, _elem_v2, _elem_v3) = _elem
    _v68_key = _elem_v2
    _v68_value = (_elem_v1, _elem_v3)
    R_Q_d_TUP_2_ubu[_v68_key].remove(_v68_value)
    if (len(R_Q_d_TUP_2_ubu[_v68_key]) == 0):
        del R_Q_d_TUP_2_ubu[_v68_key]

def _maint_R_Q_d_TUP_2_uub_for_R_Q_d_TUP_2_add(_elem):
    (_elem_v1, _elem_v2, _elem_v3) = _elem
    _v69_key = _elem_v3
    _v69_value = (_elem_v1, _elem_v2)
    if (_v69_key not in R_Q_d_TUP_2_uub):
        _v70 = Set()
        R_Q_d_TUP_2_uub[_v69_key] = _v70
    R_Q_d_TUP_2_uub[_v69_key].add(_v69_value)

def _maint_R_Q_d_TUP_2_uub_for_R_Q_d_TUP_2_remove(_elem):
    (_elem_v1, _elem_v2, _elem_v3) = _elem
    _v71_key = _elem_v3
    _v71_value = (_elem_v1, _elem_v2)
    R_Q_d_TUP_2_uub[_v71_key].remove(_v71_value)
    if (len(R_Q_d_TUP_2_uub[_v71_key]) == 0):
        del R_Q_d_TUP_2_uub[_v71_key]

def _maint_R_Q_bbu_for_R_Q_add(_elem):
    (_elem_v1, _elem_v2, _elem_v3) = _elem
    _v72_key = (_elem_v1, _elem_v2)
    _v72_value = _elem_v3
    if (_v72_key not in R_Q_bbu):
        _v73 = Set()
        R_Q_bbu[_v72_key] = _v73
    R_Q_bbu[_v72_key].add(_v72_value)

def _maint_R_Q_bbu_for_R_Q_remove(_elem):
    (_elem_v1, _elem_v2, _elem_v3) = _elem
    _v74_key = (_elem_v1, _elem_v2)
    _v74_value = _elem_v3
    R_Q_bbu[_v74_key].remove(_v74_value)
    if (len(R_Q_bbu[_v74_key]) == 0):
        del R_Q_bbu[_v74_key]

def _maint_R_Q_T_y_f_for_R_Q_d_F_f_2_add(_elem):
    (_v55_y, _v55_y_f) = _elem
    _v55_result = (_v55_y_f,)
    if (_v55_result not in R_Q_T_y_f):
        R_Q_T_y_f.add(_v55_result)
    else:
        R_Q_T_y_f.inccount(_v55_result)

def _maint_R_Q_T_y_f_for_R_Q_d_F_f_2_remove(_elem):
    (_v56_y, _v56_y_f) = _elem
    _v56_result = (_v56_y_f,)
    if (R_Q_T_y_f.getcount(_v56_result) == 1):
        R_Q_T_y_f.remove(_v56_result)
    else:
        R_Q_T_y_f.deccount(_v56_result)

def _maint_R_Q_d_F_f_2_for_R_Q_T_y_add(_elem):
    (_v51_y,) = _elem
    if hasfield(_v51_y, 'f'):
        _v51_y_f = _v51_y.f
        _v51_result = (_v51_y, _v51_y_f)
        _maint_R_Q_T_y_f_for_R_Q_d_F_f_2_add(_v51_result)

def _maint_R_Q_d_F_f_2_for_R_Q_T_y_remove(_elem):
    (_v52_y,) = _elem
    if hasfield(_v52_y, 'f'):
        _v52_y_f = _v52_y.f
        _v52_result = (_v52_y, _v52_y_f)
        _maint_R_Q_T_y_f_for_R_Q_d_F_f_2_remove(_v52_result)

def _maint_R_Q_d_F_f_2_for__F_f_add(_elem):
    (_v53_y, _v53_y_f) = _elem
    if ((_v53_y,) in R_Q_T_y):
        _v53_result = (_v53_y, _v53_y_f)
        _maint_R_Q_T_y_f_for_R_Q_d_F_f_2_add(_v53_result)

def _maint_R_Q_d_F_f_2_for__F_f_remove(_elem):
    (_v54_y, _v54_y_f) = _elem
    if ((_v54_y,) in R_Q_T_y):
        _v54_result = (_v54_y, _v54_y_f)
        _maint_R_Q_T_y_f_for_R_Q_d_F_f_2_remove(_v54_result)

def _maint_R_Q_T_x_f_for_R_Q_d_F_f_1_add(_elem):
    (_v49_x, _v49_x_f) = _elem
    _v49_result = (_v49_x_f,)
    if (_v49_result not in R_Q_T_x_f):
        R_Q_T_x_f.add(_v49_result)
    else:
        R_Q_T_x_f.inccount(_v49_result)

def _maint_R_Q_T_x_f_for_R_Q_d_F_f_1_remove(_elem):
    (_v50_x, _v50_x_f) = _elem
    _v50_result = (_v50_x_f,)
    if (R_Q_T_x_f.getcount(_v50_result) == 1):
        R_Q_T_x_f.remove(_v50_result)
    else:
        R_Q_T_x_f.deccount(_v50_result)

def _maint_R_Q_d_F_f_1_for_R_Q_T_x_add(_elem):
    (_v45_x,) = _elem
    if hasfield(_v45_x, 'f'):
        _v45_x_f = _v45_x.f
        _v45_result = (_v45_x, _v45_x_f)
        _maint_R_Q_T_x_f_for_R_Q_d_F_f_1_add(_v45_result)

def _maint_R_Q_d_F_f_1_for_R_Q_T_x_remove(_elem):
    (_v46_x,) = _elem
    if hasfield(_v46_x, 'f'):
        _v46_x_f = _v46_x.f
        _v46_result = (_v46_x, _v46_x_f)
        _maint_R_Q_T_x_f_for_R_Q_d_F_f_1_remove(_v46_result)

def _maint_R_Q_d_F_f_1_for__F_f_add(_elem):
    (_v47_x, _v47_x_f) = _elem
    if ((_v47_x,) in R_Q_T_x):
        _v47_result = (_v47_x, _v47_x_f)
        _maint_R_Q_T_x_f_for_R_Q_d_F_f_1_add(_v47_result)

def _maint_R_Q_d_F_f_1_for__F_f_remove(_elem):
    (_v48_x, _v48_x_f) = _elem
    if ((_v48_x,) in R_Q_T_x):
        _v48_result = (_v48_x, _v48_x_f)
        _maint_R_Q_T_x_f_for_R_Q_d_F_f_1_remove(_v48_result)

def _maint_R_Q_T_y_for_R_Q_d_TUP_2_add(_elem):
    (_v43_t_x_y, _v43_x, _v43_y) = _elem
    _v43_result = (_v43_y,)
    if (_v43_result not in R_Q_T_y):
        R_Q_T_y.add(_v43_result)
        _maint_R_Q_d_F_f_2_for_R_Q_T_y_add(_v43_result)
    else:
        R_Q_T_y.inccount(_v43_result)

def _maint_R_Q_T_y_for_R_Q_d_TUP_2_remove(_elem):
    (_v44_t_x_y, _v44_x, _v44_y) = _elem
    _v44_result = (_v44_y,)
    if (R_Q_T_y.getcount(_v44_result) == 1):
        _maint_R_Q_d_F_f_2_for_R_Q_T_y_remove(_v44_result)
        R_Q_T_y.remove(_v44_result)
    else:
        R_Q_T_y.deccount(_v44_result)

def _maint_R_Q_T_x_for_R_Q_d_TUP_2_add(_elem):
    (_v41_t_x_y, _v41_x, _v41_y) = _elem
    _v41_result = (_v41_x,)
    if (_v41_result not in R_Q_T_x):
        R_Q_T_x.add(_v41_result)
        _maint_R_Q_d_F_f_1_for_R_Q_T_x_add(_v41_result)
    else:
        R_Q_T_x.inccount(_v41_result)

def _maint_R_Q_T_x_for_R_Q_d_TUP_2_remove(_elem):
    (_v42_t_x_y, _v42_x, _v42_y) = _elem
    _v42_result = (_v42_x,)
    if (R_Q_T_x.getcount(_v42_result) == 1):
        _maint_R_Q_d_F_f_1_for_R_Q_T_x_remove(_v42_result)
        R_Q_T_x.remove(_v42_result)
    else:
        R_Q_T_x.deccount(_v42_result)

def _maint_R_Q_d_TUP_2_for_R_Q_T_t_x_y_add(_elem):
    (_v37_t_x_y,) = _elem
    if hasarity(_v37_t_x_y, 2):
        (_v37_x, _v37_y) = _v37_t_x_y
        _v37_result = (_v37_t_x_y, _v37_x, _v37_y)
        _maint_R_Q_d_TUP_2_ubu_for_R_Q_d_TUP_2_add(_v37_result)
        _maint_R_Q_d_TUP_2_uub_for_R_Q_d_TUP_2_add(_v37_result)
        _maint_R_Q_T_y_for_R_Q_d_TUP_2_add(_v37_result)
        _maint_R_Q_T_x_for_R_Q_d_TUP_2_add(_v37_result)

def _maint_R_Q_d_TUP_2_for_R_Q_T_t_x_y_remove(_elem):
    (_v38_t_x_y,) = _elem
    if hasarity(_v38_t_x_y, 2):
        (_v38_x, _v38_y) = _v38_t_x_y
        _v38_result = (_v38_t_x_y, _v38_x, _v38_y)
        _maint_R_Q_T_x_for_R_Q_d_TUP_2_remove(_v38_result)
        _maint_R_Q_T_y_for_R_Q_d_TUP_2_remove(_v38_result)
        _maint_R_Q_d_TUP_2_uub_for_R_Q_d_TUP_2_remove(_v38_result)
        _maint_R_Q_d_TUP_2_ubu_for_R_Q_d_TUP_2_remove(_v38_result)

def _maint_R_Q_d_TUP_2_for__TUP_2_add(_elem):
    (_v39_t_x_y, _v39_x, _v39_y) = _elem
    if ((_v39_t_x_y,) in R_Q_T_t_x_y):
        _v39_result = (_v39_t_x_y, _v39_x, _v39_y)
        _maint_R_Q_d_TUP_2_ubu_for_R_Q_d_TUP_2_add(_v39_result)
        _maint_R_Q_d_TUP_2_uub_for_R_Q_d_TUP_2_add(_v39_result)
        _maint_R_Q_T_y_for_R_Q_d_TUP_2_add(_v39_result)
        _maint_R_Q_T_x_for_R_Q_d_TUP_2_add(_v39_result)

def _maint_R_Q_d_TUP_2_for__TUP_2_remove(_elem):
    (_v40_t_x_y, _v40_x, _v40_y) = _elem
    if ((_v40_t_x_y,) in R_Q_T_t_x_y):
        _v40_result = (_v40_t_x_y, _v40_x, _v40_y)
        _maint_R_Q_T_x_for_R_Q_d_TUP_2_remove(_v40_result)
        _maint_R_Q_T_y_for_R_Q_d_TUP_2_remove(_v40_result)
        _maint_R_Q_d_TUP_2_uub_for_R_Q_d_TUP_2_remove(_v40_result)
        _maint_R_Q_d_TUP_2_ubu_for_R_Q_d_TUP_2_remove(_v40_result)

def _maint_R_Q_T_t_x_y_for_R_Q_d_M_add(_elem):
    (_v35_m_k, _v35_t_x_y) = _elem
    _v35_result = (_v35_t_x_y,)
    if (_v35_result not in R_Q_T_t_x_y):
        R_Q_T_t_x_y.add(_v35_result)
        _maint_R_Q_d_TUP_2_for_R_Q_T_t_x_y_add(_v35_result)
    else:
        R_Q_T_t_x_y.inccount(_v35_result)

def _maint_R_Q_T_t_x_y_for_R_Q_d_M_remove(_elem):
    (_v36_m_k, _v36_t_x_y) = _elem
    _v36_result = (_v36_t_x_y,)
    if (R_Q_T_t_x_y.getcount(_v36_result) == 1):
        _maint_R_Q_d_TUP_2_for_R_Q_T_t_x_y_remove(_v36_result)
        R_Q_T_t_x_y.remove(_v36_result)
    else:
        R_Q_T_t_x_y.deccount(_v36_result)

def _maint_R_Q_d_M_for_R_Q_T_m_k_add(_elem):
    (_v31_m_k,) = _elem
    if isset(_v31_m_k):
        for _v31_t_x_y in _v31_m_k:
            _v31_result = (_v31_m_k, _v31_t_x_y)
            _maint_R_Q_d_M_ub_for_R_Q_d_M_add(_v31_result)
            _maint_R_Q_T_t_x_y_for_R_Q_d_M_add(_v31_result)

def _maint_R_Q_d_M_for_R_Q_T_m_k_remove(_elem):
    (_v32_m_k,) = _elem
    if isset(_v32_m_k):
        for _v32_t_x_y in _v32_m_k:
            _v32_result = (_v32_m_k, _v32_t_x_y)
            _maint_R_Q_T_t_x_y_for_R_Q_d_M_remove(_v32_result)
            _maint_R_Q_d_M_ub_for_R_Q_d_M_remove(_v32_result)

def _maint_R_Q_d_M_for__M_add(_elem):
    (_v33_m_k, _v33_t_x_y) = _elem
    if ((_v33_m_k,) in R_Q_T_m_k):
        _v33_result = (_v33_m_k, _v33_t_x_y)
        _maint_R_Q_d_M_ub_for_R_Q_d_M_add(_v33_result)
        _maint_R_Q_T_t_x_y_for_R_Q_d_M_add(_v33_result)

def _maint_R_Q_d_M_for__M_remove(_elem):
    (_v34_m_k, _v34_t_x_y) = _elem
    if ((_v34_m_k,) in R_Q_T_m_k):
        _v34_result = (_v34_m_k, _v34_t_x_y)
        _maint_R_Q_T_t_x_y_for_R_Q_d_M_remove(_v34_result)
        _maint_R_Q_d_M_ub_for_R_Q_d_M_remove(_v34_result)

def _maint_R_Q_T_m_k_for_R_Q_d_MAP_add(_elem):
    (_v29_m, _v29_k, _v29_m_k) = _elem
    _v29_result = (_v29_m_k,)
    if (_v29_result not in R_Q_T_m_k):
        R_Q_T_m_k.add(_v29_result)
        _maint_R_Q_d_M_for_R_Q_T_m_k_add(_v29_result)
    else:
        R_Q_T_m_k.inccount(_v29_result)

def _maint_R_Q_T_m_k_for_R_Q_d_MAP_remove(_elem):
    (_v30_m, _v30_k, _v30_m_k) = _elem
    _v30_result = (_v30_m_k,)
    if (R_Q_T_m_k.getcount(_v30_result) == 1):
        _maint_R_Q_d_M_for_R_Q_T_m_k_remove(_v30_result)
        R_Q_T_m_k.remove(_v30_result)
    else:
        R_Q_T_m_k.deccount(_v30_result)

def _maint_R_Q_T_k_for_R_Q_d_MAP_add(_elem):
    (_v27_m, _v27_k, _v27_m_k) = _elem
    _v27_result = (_v27_k,)
    if (_v27_result not in R_Q_T_k):
        R_Q_T_k.add(_v27_result)
    else:
        R_Q_T_k.inccount(_v27_result)

def _maint_R_Q_T_k_for_R_Q_d_MAP_remove(_elem):
    (_v28_m, _v28_k, _v28_m_k) = _elem
    _v28_result = (_v28_k,)
    if (R_Q_T_k.getcount(_v28_result) == 1):
        R_Q_T_k.remove(_v28_result)
    else:
        R_Q_T_k.deccount(_v28_result)

def _maint_R_Q_d_MAP_for_R_Q_T_m_add(_elem):
    (_v23_m,) = _elem
    for (_v23_k, _v23_m_k) in _MAP_buu.get(_v23_m, Set()):
        _v23_result = (_v23_m, _v23_k, _v23_m_k)
        _maint_R_Q_d_MAP_uub_for_R_Q_d_MAP_add(_v23_result)
        _maint_R_Q_T_m_k_for_R_Q_d_MAP_add(_v23_result)
        _maint_R_Q_T_k_for_R_Q_d_MAP_add(_v23_result)

def _maint_R_Q_d_MAP_for_R_Q_T_m_remove(_elem):
    (_v24_m,) = _elem
    for (_v24_k, _v24_m_k) in _MAP_buu.get(_v24_m, Set()):
        _v24_result = (_v24_m, _v24_k, _v24_m_k)
        _maint_R_Q_T_k_for_R_Q_d_MAP_remove(_v24_result)
        _maint_R_Q_T_m_k_for_R_Q_d_MAP_remove(_v24_result)
        _maint_R_Q_d_MAP_uub_for_R_Q_d_MAP_remove(_v24_result)

def _maint_R_Q_d_MAP_for__MAP_add(_elem):
    (_v25_m, _v25_k, _v25_m_k) = _elem
    if ((_v25_m,) in R_Q_T_m):
        _v25_result = (_v25_m, _v25_k, _v25_m_k)
        _maint_R_Q_d_MAP_uub_for_R_Q_d_MAP_add(_v25_result)
        _maint_R_Q_T_m_k_for_R_Q_d_MAP_add(_v25_result)
        _maint_R_Q_T_k_for_R_Q_d_MAP_add(_v25_result)

def _maint_R_Q_d_MAP_for__MAP_remove(_elem):
    (_v26_m, _v26_k, _v26_m_k) = _elem
    if ((_v26_m,) in R_Q_T_m):
        _v26_result = (_v26_m, _v26_k, _v26_m_k)
        _maint_R_Q_T_k_for_R_Q_d_MAP_remove(_v26_result)
        _maint_R_Q_T_m_k_for_R_Q_d_MAP_remove(_v26_result)
        _maint_R_Q_d_MAP_uub_for_R_Q_d_MAP_remove(_v26_result)

def _maint_R_Q_T_m_for__U_Q_add(_elem):
    (_v21_m,) = _elem
    _v21_result = (_v21_m,)
    R_Q_T_m.add(_v21_result)
    _maint_R_Q_d_MAP_for_R_Q_T_m_add(_v21_result)

def _maint_R_Q_T_m_for__U_Q_remove(_elem):
    (_v22_m,) = _elem
    _v22_result = (_v22_m,)
    _maint_R_Q_d_MAP_for_R_Q_T_m_remove(_v22_result)
    R_Q_T_m.remove(_v22_result)

def _maint_R_Q_for__U_Q_add(_elem):
    (_v11_m,) = _elem
    for (_v11_k, _v11_m_k) in _MAP_buu.get(_v11_m, Set()):
        if isset(_v11_m_k):
            for _v11_t_x_y in _v11_m_k:
                if hasarity(_v11_t_x_y, 2):
                    (_v11_x, _v11_y) = _v11_t_x_y
                    if hasfield(_v11_x, 'f'):
                        _v11_x_f = _v11_x.f
                        if hasfield(_v11_y, 'f'):
                            _v11_y_f = _v11_y.f
                            _v11_result = (_v11_m, _v11_k, (_v11_x_f, _v11_y_f))
                            if (_v11_result not in R_Q):
                                R_Q.add(_v11_result)
                                _maint_R_Q_bbu_for_R_Q_add(_v11_result)
                            else:
                                R_Q.inccount(_v11_result)

def _maint_R_Q_for__U_Q_remove(_elem):
    (_v12_m,) = _elem
    for (_v12_k, _v12_m_k) in _MAP_buu.get(_v12_m, Set()):
        if isset(_v12_m_k):
            for _v12_t_x_y in _v12_m_k:
                if hasarity(_v12_t_x_y, 2):
                    (_v12_x, _v12_y) = _v12_t_x_y
                    if hasfield(_v12_x, 'f'):
                        _v12_x_f = _v12_x.f
                        if hasfield(_v12_y, 'f'):
                            _v12_y_f = _v12_y.f
                            _v12_result = (_v12_m, _v12_k, (_v12_x_f, _v12_y_f))
                            if (R_Q.getcount(_v12_result) == 1):
                                _maint_R_Q_bbu_for_R_Q_remove(_v12_result)
                                R_Q.remove(_v12_result)
                            else:
                                R_Q.deccount(_v12_result)

def _maint_R_Q_for__MAP_add(_elem):
    (_v13_m, _v13_k, _v13_m_k) = _elem
    if ((_v13_m,) in _U_Q):
        if isset(_v13_m_k):
            for _v13_t_x_y in _v13_m_k:
                if hasarity(_v13_t_x_y, 2):
                    (_v13_x, _v13_y) = _v13_t_x_y
                    if hasfield(_v13_x, 'f'):
                        _v13_x_f = _v13_x.f
                        if hasfield(_v13_y, 'f'):
                            _v13_y_f = _v13_y.f
                            _v13_result = (_v13_m, _v13_k, (_v13_x_f, _v13_y_f))
                            if (_v13_result not in R_Q):
                                R_Q.add(_v13_result)
                                _maint_R_Q_bbu_for_R_Q_add(_v13_result)
                            else:
                                R_Q.inccount(_v13_result)

def _maint_R_Q_for__MAP_remove(_elem):
    (_v14_m, _v14_k, _v14_m_k) = _elem
    if ((_v14_m,) in _U_Q):
        if isset(_v14_m_k):
            for _v14_t_x_y in _v14_m_k:
                if hasarity(_v14_t_x_y, 2):
                    (_v14_x, _v14_y) = _v14_t_x_y
                    if hasfield(_v14_x, 'f'):
                        _v14_x_f = _v14_x.f
                        if hasfield(_v14_y, 'f'):
                            _v14_y_f = _v14_y.f
                            _v14_result = (_v14_m, _v14_k, (_v14_x_f, _v14_y_f))
                            if (R_Q.getcount(_v14_result) == 1):
                                _maint_R_Q_bbu_for_R_Q_remove(_v14_result)
                                R_Q.remove(_v14_result)
                            else:
                                R_Q.deccount(_v14_result)

def _maint_R_Q_for__M_add(_elem):
    (_v15_m_k, _v15_t_x_y) = _elem
    if hasarity(_v15_t_x_y, 2):
        (_v15_x, _v15_y) = _v15_t_x_y
        if hasfield(_v15_x, 'f'):
            _v15_x_f = _v15_x.f
            if hasfield(_v15_y, 'f'):
                _v15_y_f = _v15_y.f
                for (_v15_m, _v15_k) in R_Q_d_MAP_uub.get(_v15_m_k, Set()):
                    if ((_v15_m,) in _U_Q):
                        _v15_result = (_v15_m, _v15_k, (_v15_x_f, _v15_y_f))
                        if (_v15_result not in R_Q):
                            R_Q.add(_v15_result)
                            _maint_R_Q_bbu_for_R_Q_add(_v15_result)
                        else:
                            R_Q.inccount(_v15_result)

def _maint_R_Q_for__M_remove(_elem):
    (_v16_m_k, _v16_t_x_y) = _elem
    if hasarity(_v16_t_x_y, 2):
        (_v16_x, _v16_y) = _v16_t_x_y
        if hasfield(_v16_x, 'f'):
            _v16_x_f = _v16_x.f
            if hasfield(_v16_y, 'f'):
                _v16_y_f = _v16_y.f
                for (_v16_m, _v16_k) in R_Q_d_MAP_uub.get(_v16_m_k, Set()):
                    if ((_v16_m,) in _U_Q):
                        _v16_result = (_v16_m, _v16_k, (_v16_x_f, _v16_y_f))
                        if (R_Q.getcount(_v16_result) == 1):
                            _maint_R_Q_bbu_for_R_Q_remove(_v16_result)
                            R_Q.remove(_v16_result)
                        else:
                            R_Q.deccount(_v16_result)

def _maint_R_Q_for__TUP_2_add(_elem):
    (_v17_t_x_y, _v17_x, _v17_y) = _elem
    if hasfield(_v17_x, 'f'):
        _v17_x_f = _v17_x.f
        if hasfield(_v17_y, 'f'):
            _v17_y_f = _v17_y.f
            for _v17_m_k in R_Q_d_M_ub.get(_v17_t_x_y, Set()):
                for (_v17_m, _v17_k) in R_Q_d_MAP_uub.get(_v17_m_k, Set()):
                    if ((_v17_m,) in _U_Q):
                        _v17_result = (_v17_m, _v17_k, (_v17_x_f, _v17_y_f))
                        if (_v17_result not in R_Q):
                            R_Q.add(_v17_result)
                            _maint_R_Q_bbu_for_R_Q_add(_v17_result)
                        else:
                            R_Q.inccount(_v17_result)

def _maint_R_Q_for__TUP_2_remove(_elem):
    (_v18_t_x_y, _v18_x, _v18_y) = _elem
    if hasfield(_v18_x, 'f'):
        _v18_x_f = _v18_x.f
        if hasfield(_v18_y, 'f'):
            _v18_y_f = _v18_y.f
            for _v18_m_k in R_Q_d_M_ub.get(_v18_t_x_y, Set()):
                for (_v18_m, _v18_k) in R_Q_d_MAP_uub.get(_v18_m_k, Set()):
                    if ((_v18_m,) in _U_Q):
                        _v18_result = (_v18_m, _v18_k, (_v18_x_f, _v18_y_f))
                        if (R_Q.getcount(_v18_result) == 1):
                            _maint_R_Q_bbu_for_R_Q_remove(_v18_result)
                            R_Q.remove(_v18_result)
                        else:
                            R_Q.deccount(_v18_result)

def _maint_R_Q_for__F_f_add(_elem):
    (_v19_x, _v19_x_f) = _elem
    for (_v19_t_x_y, _v19_y) in R_Q_d_TUP_2_ubu.get(_v19_x, Set()):
        if hasfield(_v19_y, 'f'):
            _v19_y_f = _v19_y.f
            if ((_v19_y, _v19_y_f) != _elem):
                for _v19_m_k in R_Q_d_M_ub.get(_v19_t_x_y, Set()):
                    for (_v19_m, _v19_k) in R_Q_d_MAP_uub.get(_v19_m_k, Set()):
                        if ((_v19_m,) in _U_Q):
                            _v19_result = (_v19_m, _v19_k, (_v19_x_f, _v19_y_f))
                            if (_v19_result not in R_Q):
                                R_Q.add(_v19_result)
                                _maint_R_Q_bbu_for_R_Q_add(_v19_result)
                            else:
                                R_Q.inccount(_v19_result)
    (_v19_y, _v19_y_f) = _elem
    for (_v19_t_x_y, _v19_x) in R_Q_d_TUP_2_uub.get(_v19_y, Set()):
        if hasfield(_v19_x, 'f'):
            _v19_x_f = _v19_x.f
            for _v19_m_k in R_Q_d_M_ub.get(_v19_t_x_y, Set()):
                for (_v19_m, _v19_k) in R_Q_d_MAP_uub.get(_v19_m_k, Set()):
                    if ((_v19_m,) in _U_Q):
                        _v19_result = (_v19_m, _v19_k, (_v19_x_f, _v19_y_f))
                        if (_v19_result not in R_Q):
                            R_Q.add(_v19_result)
                            _maint_R_Q_bbu_for_R_Q_add(_v19_result)
                        else:
                            R_Q.inccount(_v19_result)

def _maint_R_Q_for__F_f_remove(_elem):
    (_v20_x, _v20_x_f) = _elem
    for (_v20_t_x_y, _v20_y) in R_Q_d_TUP_2_ubu.get(_v20_x, Set()):
        if hasfield(_v20_y, 'f'):
            _v20_y_f = _v20_y.f
            if ((_v20_y, _v20_y_f) != _elem):
                for _v20_m_k in R_Q_d_M_ub.get(_v20_t_x_y, Set()):
                    for (_v20_m, _v20_k) in R_Q_d_MAP_uub.get(_v20_m_k, Set()):
                        if ((_v20_m,) in _U_Q):
                            _v20_result = (_v20_m, _v20_k, (_v20_x_f, _v20_y_f))
                            if (R_Q.getcount(_v20_result) == 1):
                                _maint_R_Q_bbu_for_R_Q_remove(_v20_result)
                                R_Q.remove(_v20_result)
                            else:
                                R_Q.deccount(_v20_result)
    (_v20_y, _v20_y_f) = _elem
    for (_v20_t_x_y, _v20_x) in R_Q_d_TUP_2_uub.get(_v20_y, Set()):
        if hasfield(_v20_x, 'f'):
            _v20_x_f = _v20_x.f
            for _v20_m_k in R_Q_d_M_ub.get(_v20_t_x_y, Set()):
                for (_v20_m, _v20_k) in R_Q_d_MAP_uub.get(_v20_m_k, Set()):
                    if ((_v20_m,) in _U_Q):
                        _v20_result = (_v20_m, _v20_k, (_v20_x_f, _v20_y_f))
                        if (R_Q.getcount(_v20_result) == 1):
                            _maint_R_Q_bbu_for_R_Q_remove(_v20_result)
                            R_Q.remove(_v20_result)
                        else:
                            R_Q.deccount(_v20_result)

def _demand_Q(_elem):
    if (_elem not in _U_Q):
        _U_Q.add(_elem)
        _maint_R_Q_T_m_for__U_Q_add(_elem)
        _maint_R_Q_for__U_Q_add(_elem)

from itertools import product
def main():
    a = Map()
    b = Map()
    for (i, j) in product(range(4), range(4)):
        p = Obj()
        _v1 = (p, i)
        index(_v1, 0).f = index(_v1, 1)
        _maint_R_Q_d_F_f_2_for__F_f_add(_v1)
        _maint_R_Q_d_F_f_1_for__F_f_add(_v1)
        _maint_R_Q_for__F_f_add(_v1)
        q = Obj()
        _v2 = (q, j)
        index(_v2, 0).f = index(_v2, 1)
        _maint_R_Q_d_F_f_2_for__F_f_add(_v2)
        _maint_R_Q_d_F_f_1_for__F_f_add(_v2)
        _maint_R_Q_for__F_f_add(_v2)
        r = (a if ((i % 2) == 0) else b)
        if (i not in r):
            _v3 = (r, i, Set())
            index(_v3, 0)[index(_v3, 1)] = index(_v3, 2)
            _maint__MAP_buu_for__MAP_add(_v3)
            _maint_R_Q_d_MAP_for__MAP_add(_v3)
            _maint_R_Q_for__MAP_add(_v3)
        _v4 = (r[i], (p, q))
        index(_v4, 0).add(index(_v4, 1))
        _maint_R_Q_d_M_for__M_add(_v4)
        _maint_R_Q_for__M_add(_v4)
    p = Obj()
    _v5 = (p, 5)
    index(_v5, 0).f = index(_v5, 1)
    _maint_R_Q_d_F_f_2_for__F_f_add(_v5)
    _maint_R_Q_d_F_f_1_for__F_f_add(_v5)
    _maint_R_Q_for__F_f_add(_v5)
    m = a
    k = 0
    print(sorted(((_demand_Q((m,)) or True) and R_Q_bbu.get((m, k), Set()))))
    m = b
    k = 1
    print(sorted(((_demand_Q((m,)) or True) and R_Q_bbu.get((m, k), Set()))))
    _v6 = (b, 1, b[1])
    _maint_R_Q_for__MAP_remove(_v6)
    _maint_R_Q_d_MAP_for__MAP_remove(_v6)
    _maint__MAP_buu_for__MAP_remove(_v6)
    del index(_v6, 0)[index(_v6, 1)]
    _v7 = (b, 1, Set())
    index(_v7, 0)[index(_v7, 1)] = index(_v7, 2)
    _maint__MAP_buu_for__MAP_add(_v7)
    _maint_R_Q_d_MAP_for__MAP_add(_v7)
    _maint_R_Q_for__MAP_add(_v7)
    p = Obj()
    _v8 = (p, 100)
    index(_v8, 0).f = index(_v8, 1)
    _maint_R_Q_d_F_f_2_for__F_f_add(_v8)
    _maint_R_Q_d_F_f_1_for__F_f_add(_v8)
    _maint_R_Q_for__F_f_add(_v8)
    q = Obj()
    _v9 = (q, 100)
    index(_v9, 0).f = index(_v9, 1)
    _maint_R_Q_d_F_f_2_for__F_f_add(_v9)
    _maint_R_Q_d_F_f_1_for__F_f_add(_v9)
    _maint_R_Q_for__F_f_add(_v9)
    _v10 = (b[1], (p, q))
    index(_v10, 0).add(index(_v10, 1))
    _maint_R_Q_d_M_for__M_add(_v10)
    _maint_R_Q_for__M_add(_v10)
    print(sorted(((_demand_Q((m,)) or True) and R_Q_bbu.get((m, k), Set()))))

if (__name__ == '__main__'):
    main()
