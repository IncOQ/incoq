from oinc.runtime import *
# Comp1 := {(low, high, z) : low in Comp1_P_low, high in Comp1_P_high, (x, y) in E, (y, z) in E, (low <= x <= high)}
# Comp10 := {(low, high, z) : low in Comp10_P_low, high in Comp10_P_high, (x, y) in E, (y, z) in E, (low <= x <= high)}
_m_Comp10_bbu = Map('_m_Comp10_bbu')
_m_Comp1_bbu = Map('_m_Comp1_bbu')
_m_E_in = Map('_m_E_in')
_m_E_out = Map('_m_E_out')
Comp10 = RCSet('Comp10')
Comp1 = RCSet('Comp1')
E = Set()
for (v1, v2) in [(1, 2), (2, 3), (3, 4), (4, 5)]:
    E.add((v1, v2))
    # Begin maint _m_E_in after "E.add((v1, v2))"
    (v16_1, v16_2) = (v1, v2)
    if (v16_2 not in _m_E_in):
        _m_E_in[v16_2] = set()
    _m_E_in[v16_2].add(v16_1)
    # End maint _m_E_in after "E.add((v1, v2))"
    # Begin maint _m_E_out after "E.add((v1, v2))"
    (v15_1, v15_2) = (v1, v2)
    if (v15_1 not in _m_E_out):
        _m_E_out[v15_1] = set()
    _m_E_out[v15_1].add(v15_2)
    # End maint _m_E_out after "E.add((v1, v2))"
    # Begin maint Comp10 after "E.add((v1, v2))"
    v8_DAS = set()
    # Iterate {(v8_high, v8_low, v8_x, v8_y, v8_z) : v8_low in Comp10_P_low, v8_high in Comp10_P_high, (v8_x, v8_y) in {(v1, v2)}, (v8_y, v8_z) in E, (v8_low <= v8_x <= v8_high)}
    (v8_x, v8_y) = (v1, v2)
    if ('low' in globals()):
        v8_low = low
        if ('high' in globals()):
            v8_high = high
            if (v8_low <= v8_x <= v8_high):
                for v8_z in (_m_E_out[v8_y] if (v8_y in _m_E_out) else set()):
                    if ((v8_high, v8_low, v8_x, v8_y, v8_z) not in v8_DAS):
                        v8_DAS.add((v8_high, v8_low, v8_x, v8_y, v8_z))
    # Iterate {(v8_high, v8_low, v8_x, v8_y, v8_z) : v8_low in Comp10_P_low, v8_high in Comp10_P_high, (v8_x, v8_y) in E, (v8_y, v8_z) in {(v1, v2)}, (v8_low <= v8_x <= v8_high)}
    (v8_y, v8_z) = (v1, v2)
    if ('low' in globals()):
        v8_low = low
        if ('high' in globals()):
            v8_high = high
            for v8_x in (_m_E_in[v8_y] if (v8_y in _m_E_in) else set()):
                if (v8_low <= v8_x <= v8_high):
                    if ((v8_high, v8_low, v8_x, v8_y, v8_z) not in v8_DAS):
                        v8_DAS.add((v8_high, v8_low, v8_x, v8_y, v8_z))
    for (v8_high, v8_low, v8_x, v8_y, v8_z) in v8_DAS:
        if ((v8_low, v8_high, v8_z) not in Comp10):
            Comp10.add((v8_low, v8_high, v8_z))
            # Begin maint _m_Comp10_bbu after "Comp10.add((v8_low, v8_high, v8_z))"
            (v24_1, v24_2, v24_3) = (v8_low, v8_high, v8_z)
            if ((v24_1, v24_2) not in _m_Comp10_bbu):
                _m_Comp10_bbu[(v24_1, v24_2)] = set()
            _m_Comp10_bbu[(v24_1, v24_2)].add(v24_3)
            # End maint _m_Comp10_bbu after "Comp10.add((v8_low, v8_high, v8_z))"
        else:
            Comp10.incref((v8_low, v8_high, v8_z))
    del v8_DAS
    # End maint Comp10 after "E.add((v1, v2))"
    # Begin maint Comp1 after "E.add((v1, v2))"
    v1_DAS = set()
    # Iterate {(v1_high, v1_low, v1_x, v1_y, v1_z) : v1_low in Comp1_P_low, v1_high in Comp1_P_high, (v1_x, v1_y) in {(v1, v2)}, (v1_y, v1_z) in E, (v1_low <= v1_x <= v1_high)}
    (v1_x, v1_y) = (v1, v2)
    if ('low' in globals()):
        v1_low = low
        if ('high' in globals()):
            v1_high = high
            if (v1_low <= v1_x <= v1_high):
                for v1_z in (_m_E_out[v1_y] if (v1_y in _m_E_out) else set()):
                    if ((v1_high, v1_low, v1_x, v1_y, v1_z) not in v1_DAS):
                        v1_DAS.add((v1_high, v1_low, v1_x, v1_y, v1_z))
    # Iterate {(v1_high, v1_low, v1_x, v1_y, v1_z) : v1_low in Comp1_P_low, v1_high in Comp1_P_high, (v1_x, v1_y) in E, (v1_y, v1_z) in {(v1, v2)}, (v1_low <= v1_x <= v1_high)}
    (v1_y, v1_z) = (v1, v2)
    if ('low' in globals()):
        v1_low = low
        if ('high' in globals()):
            v1_high = high
            for v1_x in (_m_E_in[v1_y] if (v1_y in _m_E_in) else set()):
                if (v1_low <= v1_x <= v1_high):
                    if ((v1_high, v1_low, v1_x, v1_y, v1_z) not in v1_DAS):
                        v1_DAS.add((v1_high, v1_low, v1_x, v1_y, v1_z))
    for (v1_high, v1_low, v1_x, v1_y, v1_z) in v1_DAS:
        if ((v1_low, v1_high, v1_z) not in Comp1):
            Comp1.add((v1_low, v1_high, v1_z))
            # Begin maint _m_Comp1_bbu after "Comp1.add((v1_low, v1_high, v1_z))"
            (v17_1, v17_2, v17_3) = (v1_low, v1_high, v1_z)
            if ((v17_1, v17_2) not in _m_Comp1_bbu):
                _m_Comp1_bbu[(v17_1, v17_2)] = set()
            _m_Comp1_bbu[(v17_1, v17_2)].add(v17_3)
            # End maint _m_Comp1_bbu after "Comp1.add((v1_low, v1_high, v1_z))"
        else:
            Comp1.incref((v1_low, v1_high, v1_z))
    del v1_DAS
    # End maint Comp1 after "E.add((v1, v2))"
if ('low' in globals()):
    # Begin maint Comp1 before "Comp1_P_low.remove(low)"
    # Iterate {(v2_high, v2_low, v2_x, v2_y, v2_z) : v2_low in {low}, v2_high in Comp1_P_high, (v2_x, v2_y) in E, (v2_y, v2_z) in E, (v2_low <= v2_x <= v2_high)}
    v2_low = low
    if ('high' in globals()):
        v2_high = high
        for (v2_x, v2_y) in E:
            if (v2_low <= v2_x <= v2_high):
                for v2_z in (_m_E_out[v2_y] if (v2_y in _m_E_out) else set()):
                    if (Comp1.getref((v2_low, v2_high, v2_z)) == 1):
                        # Begin maint _m_Comp1_bbu before "Comp1.remove((v2_low, v2_high, v2_z))"
                        (v18_1, v18_2, v18_3) = (v2_low, v2_high, v2_z)
                        _m_Comp1_bbu[(v18_1, v18_2)].remove(v18_3)
                        if (len(_m_Comp1_bbu[(v18_1, v18_2)]) == 0):
                            del _m_Comp1_bbu[(v18_1, v18_2)]
                        # End maint _m_Comp1_bbu before "Comp1.remove((v2_low, v2_high, v2_z))"
                        Comp1.remove((v2_low, v2_high, v2_z))
                    else:
                        Comp1.decref((v2_low, v2_high, v2_z))
    # End maint Comp1 before "Comp1_P_low.remove(low)"
    del low
if ('low' in globals()):
    # Begin maint Comp10 before "Comp10_P_low.remove(low)"
    # Iterate {(v9_high, v9_low, v9_x, v9_y, v9_z) : v9_low in {low}, v9_high in Comp10_P_high, (v9_x, v9_y) in E, (v9_y, v9_z) in E, (v9_low <= v9_x <= v9_high)}
    v9_low = low
    if ('high' in globals()):
        v9_high = high
        for (v9_x, v9_y) in E:
            if (v9_low <= v9_x <= v9_high):
                for v9_z in (_m_E_out[v9_y] if (v9_y in _m_E_out) else set()):
                    if (Comp10.getref((v9_low, v9_high, v9_z)) == 1):
                        # Begin maint _m_Comp10_bbu before "Comp10.remove((v9_low, v9_high, v9_z))"
                        (v25_1, v25_2, v25_3) = (v9_low, v9_high, v9_z)
                        _m_Comp10_bbu[(v25_1, v25_2)].remove(v25_3)
                        if (len(_m_Comp10_bbu[(v25_1, v25_2)]) == 0):
                            del _m_Comp10_bbu[(v25_1, v25_2)]
                        # End maint _m_Comp10_bbu before "Comp10.remove((v9_low, v9_high, v9_z))"
                        Comp10.remove((v9_low, v9_high, v9_z))
                    else:
                        Comp10.decref((v9_low, v9_high, v9_z))
    # End maint Comp10 before "Comp10_P_low.remove(low)"
    del low
low = 1
# Begin maint Comp10 after "Comp10_P_low.add(1)"
# Iterate {(v10_high, v10_low, v10_x, v10_y, v10_z) : v10_low in {1}, v10_high in Comp10_P_high, (v10_x, v10_y) in E, (v10_y, v10_z) in E, (v10_low <= v10_x <= v10_high)}
v10_low = 1
if ('high' in globals()):
    v10_high = high
    for (v10_x, v10_y) in E:
        if (v10_low <= v10_x <= v10_high):
            for v10_z in (_m_E_out[v10_y] if (v10_y in _m_E_out) else set()):
                if ((v10_low, v10_high, v10_z) not in Comp10):
                    Comp10.add((v10_low, v10_high, v10_z))
                    # Begin maint _m_Comp10_bbu after "Comp10.add((v10_low, v10_high, v10_z))"
                    (v26_1, v26_2, v26_3) = (v10_low, v10_high, v10_z)
                    if ((v26_1, v26_2) not in _m_Comp10_bbu):
                        _m_Comp10_bbu[(v26_1, v26_2)] = set()
                    _m_Comp10_bbu[(v26_1, v26_2)].add(v26_3)
                    # End maint _m_Comp10_bbu after "Comp10.add((v10_low, v10_high, v10_z))"
                else:
                    Comp10.incref((v10_low, v10_high, v10_z))
# End maint Comp10 after "Comp10_P_low.add(1)"
# Begin maint Comp1 after "Comp1_P_low.add(1)"
# Iterate {(v3_high, v3_low, v3_x, v3_y, v3_z) : v3_low in {1}, v3_high in Comp1_P_high, (v3_x, v3_y) in E, (v3_y, v3_z) in E, (v3_low <= v3_x <= v3_high)}
v3_low = 1
if ('high' in globals()):
    v3_high = high
    for (v3_x, v3_y) in E:
        if (v3_low <= v3_x <= v3_high):
            for v3_z in (_m_E_out[v3_y] if (v3_y in _m_E_out) else set()):
                if ((v3_low, v3_high, v3_z) not in Comp1):
                    Comp1.add((v3_low, v3_high, v3_z))
                    # Begin maint _m_Comp1_bbu after "Comp1.add((v3_low, v3_high, v3_z))"
                    (v19_1, v19_2, v19_3) = (v3_low, v3_high, v3_z)
                    if ((v19_1, v19_2) not in _m_Comp1_bbu):
                        _m_Comp1_bbu[(v19_1, v19_2)] = set()
                    _m_Comp1_bbu[(v19_1, v19_2)].add(v19_3)
                    # End maint _m_Comp1_bbu after "Comp1.add((v3_low, v3_high, v3_z))"
                else:
                    Comp1.incref((v3_low, v3_high, v3_z))
# End maint Comp1 after "Comp1_P_low.add(1)"
if ('high' in globals()):
    # Begin maint Comp1 before "Comp1_P_high.remove(high)"
    # Iterate {(v4_high, v4_low, v4_x, v4_y, v4_z) : v4_low in Comp1_P_low, v4_high in {high}, (v4_x, v4_y) in E, (v4_y, v4_z) in E, (v4_low <= v4_x <= v4_high)}
    v4_high = high
    if ('low' in globals()):
        v4_low = low
        for (v4_x, v4_y) in E:
            if (v4_low <= v4_x <= v4_high):
                for v4_z in (_m_E_out[v4_y] if (v4_y in _m_E_out) else set()):
                    if (Comp1.getref((v4_low, v4_high, v4_z)) == 1):
                        # Begin maint _m_Comp1_bbu before "Comp1.remove((v4_low, v4_high, v4_z))"
                        (v20_1, v20_2, v20_3) = (v4_low, v4_high, v4_z)
                        _m_Comp1_bbu[(v20_1, v20_2)].remove(v20_3)
                        if (len(_m_Comp1_bbu[(v20_1, v20_2)]) == 0):
                            del _m_Comp1_bbu[(v20_1, v20_2)]
                        # End maint _m_Comp1_bbu before "Comp1.remove((v4_low, v4_high, v4_z))"
                        Comp1.remove((v4_low, v4_high, v4_z))
                    else:
                        Comp1.decref((v4_low, v4_high, v4_z))
    # End maint Comp1 before "Comp1_P_high.remove(high)"
    del high
if ('high' in globals()):
    # Begin maint Comp10 before "Comp10_P_high.remove(high)"
    # Iterate {(v11_high, v11_low, v11_x, v11_y, v11_z) : v11_low in Comp10_P_low, v11_high in {high}, (v11_x, v11_y) in E, (v11_y, v11_z) in E, (v11_low <= v11_x <= v11_high)}
    v11_high = high
    if ('low' in globals()):
        v11_low = low
        for (v11_x, v11_y) in E:
            if (v11_low <= v11_x <= v11_high):
                for v11_z in (_m_E_out[v11_y] if (v11_y in _m_E_out) else set()):
                    if (Comp10.getref((v11_low, v11_high, v11_z)) == 1):
                        # Begin maint _m_Comp10_bbu before "Comp10.remove((v11_low, v11_high, v11_z))"
                        (v27_1, v27_2, v27_3) = (v11_low, v11_high, v11_z)
                        _m_Comp10_bbu[(v27_1, v27_2)].remove(v27_3)
                        if (len(_m_Comp10_bbu[(v27_1, v27_2)]) == 0):
                            del _m_Comp10_bbu[(v27_1, v27_2)]
                        # End maint _m_Comp10_bbu before "Comp10.remove((v11_low, v11_high, v11_z))"
                        Comp10.remove((v11_low, v11_high, v11_z))
                    else:
                        Comp10.decref((v11_low, v11_high, v11_z))
    # End maint Comp10 before "Comp10_P_high.remove(high)"
    del high
high = 3
# Begin maint Comp10 after "Comp10_P_high.add(3)"
# Iterate {(v12_high, v12_low, v12_x, v12_y, v12_z) : v12_low in Comp10_P_low, v12_high in {3}, (v12_x, v12_y) in E, (v12_y, v12_z) in E, (v12_low <= v12_x <= v12_high)}
v12_high = 3
if ('low' in globals()):
    v12_low = low
    for (v12_x, v12_y) in E:
        if (v12_low <= v12_x <= v12_high):
            for v12_z in (_m_E_out[v12_y] if (v12_y in _m_E_out) else set()):
                if ((v12_low, v12_high, v12_z) not in Comp10):
                    Comp10.add((v12_low, v12_high, v12_z))
                    # Begin maint _m_Comp10_bbu after "Comp10.add((v12_low, v12_high, v12_z))"
                    (v28_1, v28_2, v28_3) = (v12_low, v12_high, v12_z)
                    if ((v28_1, v28_2) not in _m_Comp10_bbu):
                        _m_Comp10_bbu[(v28_1, v28_2)] = set()
                    _m_Comp10_bbu[(v28_1, v28_2)].add(v28_3)
                    # End maint _m_Comp10_bbu after "Comp10.add((v12_low, v12_high, v12_z))"
                else:
                    Comp10.incref((v12_low, v12_high, v12_z))
# End maint Comp10 after "Comp10_P_high.add(3)"
# Begin maint Comp1 after "Comp1_P_high.add(3)"
# Iterate {(v5_high, v5_low, v5_x, v5_y, v5_z) : v5_low in Comp1_P_low, v5_high in {3}, (v5_x, v5_y) in E, (v5_y, v5_z) in E, (v5_low <= v5_x <= v5_high)}
v5_high = 3
if ('low' in globals()):
    v5_low = low
    for (v5_x, v5_y) in E:
        if (v5_low <= v5_x <= v5_high):
            for v5_z in (_m_E_out[v5_y] if (v5_y in _m_E_out) else set()):
                if ((v5_low, v5_high, v5_z) not in Comp1):
                    Comp1.add((v5_low, v5_high, v5_z))
                    # Begin maint _m_Comp1_bbu after "Comp1.add((v5_low, v5_high, v5_z))"
                    (v21_1, v21_2, v21_3) = (v5_low, v5_high, v5_z)
                    if ((v21_1, v21_2) not in _m_Comp1_bbu):
                        _m_Comp1_bbu[(v21_1, v21_2)] = set()
                    _m_Comp1_bbu[(v21_1, v21_2)].add(v21_3)
                    # End maint _m_Comp1_bbu after "Comp1.add((v5_low, v5_high, v5_z))"
                else:
                    Comp1.incref((v5_low, v5_high, v5_z))
# End maint Comp1 after "Comp1_P_high.add(3)"
print(sorted((_m_Comp1_bbu[(low, high)] if ((low, high) in _m_Comp1_bbu) else set())))
if ('high' in globals()):
    # Begin maint Comp1 before "Comp1_P_high.remove(high)"
    # Iterate {(v6_high, v6_low, v6_x, v6_y, v6_z) : v6_low in Comp1_P_low, v6_high in {high}, (v6_x, v6_y) in E, (v6_y, v6_z) in E, (v6_low <= v6_x <= v6_high)}
    v6_high = high
    if ('low' in globals()):
        v6_low = low
        for (v6_x, v6_y) in E:
            if (v6_low <= v6_x <= v6_high):
                for v6_z in (_m_E_out[v6_y] if (v6_y in _m_E_out) else set()):
                    if (Comp1.getref((v6_low, v6_high, v6_z)) == 1):
                        # Begin maint _m_Comp1_bbu before "Comp1.remove((v6_low, v6_high, v6_z))"
                        (v22_1, v22_2, v22_3) = (v6_low, v6_high, v6_z)
                        _m_Comp1_bbu[(v22_1, v22_2)].remove(v22_3)
                        if (len(_m_Comp1_bbu[(v22_1, v22_2)]) == 0):
                            del _m_Comp1_bbu[(v22_1, v22_2)]
                        # End maint _m_Comp1_bbu before "Comp1.remove((v6_low, v6_high, v6_z))"
                        Comp1.remove((v6_low, v6_high, v6_z))
                    else:
                        Comp1.decref((v6_low, v6_high, v6_z))
    # End maint Comp1 before "Comp1_P_high.remove(high)"
    del high
if ('high' in globals()):
    # Begin maint Comp10 before "Comp10_P_high.remove(high)"
    # Iterate {(v13_high, v13_low, v13_x, v13_y, v13_z) : v13_low in Comp10_P_low, v13_high in {high}, (v13_x, v13_y) in E, (v13_y, v13_z) in E, (v13_low <= v13_x <= v13_high)}
    v13_high = high
    if ('low' in globals()):
        v13_low = low
        for (v13_x, v13_y) in E:
            if (v13_low <= v13_x <= v13_high):
                for v13_z in (_m_E_out[v13_y] if (v13_y in _m_E_out) else set()):
                    if (Comp10.getref((v13_low, v13_high, v13_z)) == 1):
                        # Begin maint _m_Comp10_bbu before "Comp10.remove((v13_low, v13_high, v13_z))"
                        (v29_1, v29_2, v29_3) = (v13_low, v13_high, v13_z)
                        _m_Comp10_bbu[(v29_1, v29_2)].remove(v29_3)
                        if (len(_m_Comp10_bbu[(v29_1, v29_2)]) == 0):
                            del _m_Comp10_bbu[(v29_1, v29_2)]
                        # End maint _m_Comp10_bbu before "Comp10.remove((v13_low, v13_high, v13_z))"
                        Comp10.remove((v13_low, v13_high, v13_z))
                    else:
                        Comp10.decref((v13_low, v13_high, v13_z))
    # End maint Comp10 before "Comp10_P_high.remove(high)"
    del high
high = 2
# Begin maint Comp10 after "Comp10_P_high.add(2)"
# Iterate {(v14_high, v14_low, v14_x, v14_y, v14_z) : v14_low in Comp10_P_low, v14_high in {2}, (v14_x, v14_y) in E, (v14_y, v14_z) in E, (v14_low <= v14_x <= v14_high)}
v14_high = 2
if ('low' in globals()):
    v14_low = low
    for (v14_x, v14_y) in E:
        if (v14_low <= v14_x <= v14_high):
            for v14_z in (_m_E_out[v14_y] if (v14_y in _m_E_out) else set()):
                if ((v14_low, v14_high, v14_z) not in Comp10):
                    Comp10.add((v14_low, v14_high, v14_z))
                    # Begin maint _m_Comp10_bbu after "Comp10.add((v14_low, v14_high, v14_z))"
                    (v30_1, v30_2, v30_3) = (v14_low, v14_high, v14_z)
                    if ((v30_1, v30_2) not in _m_Comp10_bbu):
                        _m_Comp10_bbu[(v30_1, v30_2)] = set()
                    _m_Comp10_bbu[(v30_1, v30_2)].add(v30_3)
                    # End maint _m_Comp10_bbu after "Comp10.add((v14_low, v14_high, v14_z))"
                else:
                    Comp10.incref((v14_low, v14_high, v14_z))
# End maint Comp10 after "Comp10_P_high.add(2)"
# Begin maint Comp1 after "Comp1_P_high.add(2)"
# Iterate {(v7_high, v7_low, v7_x, v7_y, v7_z) : v7_low in Comp1_P_low, v7_high in {2}, (v7_x, v7_y) in E, (v7_y, v7_z) in E, (v7_low <= v7_x <= v7_high)}
v7_high = 2
if ('low' in globals()):
    v7_low = low
    for (v7_x, v7_y) in E:
        if (v7_low <= v7_x <= v7_high):
            for v7_z in (_m_E_out[v7_y] if (v7_y in _m_E_out) else set()):
                if ((v7_low, v7_high, v7_z) not in Comp1):
                    Comp1.add((v7_low, v7_high, v7_z))
                    # Begin maint _m_Comp1_bbu after "Comp1.add((v7_low, v7_high, v7_z))"
                    (v23_1, v23_2, v23_3) = (v7_low, v7_high, v7_z)
                    if ((v23_1, v23_2) not in _m_Comp1_bbu):
                        _m_Comp1_bbu[(v23_1, v23_2)] = set()
                    _m_Comp1_bbu[(v23_1, v23_2)].add(v23_3)
                    # End maint _m_Comp1_bbu after "Comp1.add((v7_low, v7_high, v7_z))"
                else:
                    Comp1.incref((v7_low, v7_high, v7_z))
# End maint Comp1 after "Comp1_P_high.add(2)"
print(sorted((_m_Comp10_bbu[(low, high)] if ((low, high) in _m_Comp10_bbu) else set())))