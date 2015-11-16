# Manually modified version of wifi_dem_notypecheck.py.
# Got rid of maintenance in make_ap().

from incoq.runtime import *
# Comp1 := {(wifi, ap_ssid) : wifi in _U_Comp1, (wifi, wifi_scan) in _F_scan, (wifi_scan, ap) in _M, (ap, ap_strength) in _F_strength, (wifi, wifi_threshold) in _F_threshold, (ap_strength > wifi_threshold), (ap, ap_ssid) in _F_ssid}
# Comp1_Twifi := {wifi : wifi in _U_Comp1}
# Comp1_d_F_scan := {(wifi, wifi_scan) : wifi in Comp1_Twifi, (wifi, wifi_scan) in _F_scan}
# Comp1_Twifi_scan := {wifi_scan : (wifi, wifi_scan) in Comp1_d_F_scan}
# Comp1_d_M := {(wifi_scan, ap) : wifi_scan in Comp1_Twifi_scan, (wifi_scan, ap) in _M}
# Comp1_Tap := {ap : (wifi_scan, ap) in Comp1_d_M}
# Comp1_d_F_strength := {(ap, ap_strength) : ap in Comp1_Tap, (ap, ap_strength) in _F_strength}
# Comp1_d_F_threshold := {(wifi, wifi_threshold) : wifi in Comp1_Twifi, (wifi, wifi_threshold) in _F_threshold}
# Comp1_d_F_ssid := {(ap, ap_ssid) : ap in Comp1_Tap, (ap, ap_ssid) in _F_ssid}
_m_Comp1_out = Map()
_m_Comp1_d_M_in = Map()
_m_Comp1_d_F_scan_in = Map()
Comp1_d_F_ssid = Set()
Comp1_d_F_threshold = Set()
Comp1_d_F_strength = Set()
Comp1_Tap = RCSet()
Comp1_d_M = Set()
Comp1_Twifi_scan = RCSet()
Comp1_d_F_scan = Set()
Comp1_Twifi = Set()
_U_Comp1 = RCSet()
_UEXT_Comp1 = Set()
def demand_Comp1(wifi):
    # Cost: O((v23_wifi_scan + v3_wifi_scan))
    '{(wifi, ap_ssid) : wifi in _U_Comp1, (wifi, wifi_scan) in _F_scan, (wifi_scan, ap) in _M, (ap, ap_strength) in _F_strength, (wifi, wifi_threshold) in _F_threshold, (ap_strength > wifi_threshold), (ap, ap_ssid) in _F_ssid}'
    if (wifi not in _U_Comp1):
        _U_Comp1.add(wifi)
        # Begin maint Comp1_Twifi after "_U_Comp1.add(wifi)"
        # Cost: O(v23_wifi_scan)
        # Iterate {v15_wifi : v15_wifi in deltamatch(_U_Comp1, 'b', _e, 1)}
        v15_wifi = wifi
        Comp1_Twifi.add(v15_wifi)
        # Begin maint Comp1_d_F_threshold after "Comp1_Twifi.add(v15_wifi)"
        # Cost: O(1)
        # Iterate {(v33_wifi, v33_wifi_threshold) : v33_wifi in deltamatch(Comp1_Twifi, 'b', _e, 1), (v33_wifi, v33_wifi_threshold) in _F_threshold}
        v33_wifi = v15_wifi
        v33_wifi_threshold = v33_wifi.threshold
        Comp1_d_F_threshold.add((v33_wifi, v33_wifi_threshold))
        # End maint Comp1_d_F_threshold after "Comp1_Twifi.add(v15_wifi)"
        # Begin maint Comp1_d_F_scan after "Comp1_Twifi.add(v15_wifi)"
        # Cost: O(v23_wifi_scan)
        # Iterate {(v17_wifi, v17_wifi_scan) : v17_wifi in deltamatch(Comp1_Twifi, 'b', _e, 1), (v17_wifi, v17_wifi_scan) in _F_scan}
        v17_wifi = v15_wifi
        v17_wifi_scan = v17_wifi.scan
        Comp1_d_F_scan.add((v17_wifi, v17_wifi_scan))
        # Begin maint _m_Comp1_d_F_scan_in after "Comp1_d_F_scan.add((v17_wifi, v17_wifi_scan))"
        (v41_1, v41_2) = (v17_wifi, v17_wifi_scan)
        if (v41_2 not in _m_Comp1_d_F_scan_in):
            _m_Comp1_d_F_scan_in[v41_2] = set()
        _m_Comp1_d_F_scan_in[v41_2].add(v41_1)
        # End maint _m_Comp1_d_F_scan_in after "Comp1_d_F_scan.add((v17_wifi, v17_wifi_scan))"
        # Begin maint Comp1_Twifi_scan after "Comp1_d_F_scan.add((v17_wifi, v17_wifi_scan))"
        # Cost: O(v23_wifi_scan)
        # Iterate {(v21_wifi, v21_wifi_scan) : (v21_wifi, v21_wifi_scan) in deltamatch(Comp1_d_F_scan, 'bb', _e, 1)}
        (v21_wifi, v21_wifi_scan) = (v17_wifi, v17_wifi_scan)
        if (v21_wifi_scan not in Comp1_Twifi_scan):
            Comp1_Twifi_scan.add(v21_wifi_scan)
            # Begin maint Comp1_d_M after "Comp1_Twifi_scan.add(v21_wifi_scan)"
            # Cost: O(v23_wifi_scan)
            # Iterate {(v23_wifi_scan, v23_ap) : v23_wifi_scan in deltamatch(Comp1_Twifi_scan, 'b', _e, 1), (v23_wifi_scan, v23_ap) in _M}
            v23_wifi_scan = v21_wifi_scan
            for v23_ap in v23_wifi_scan:
                Comp1_d_M.add((v23_wifi_scan, v23_ap))
                # Begin maint _m_Comp1_d_M_in after "Comp1_d_M.add((v23_wifi_scan, v23_ap))"
                (v43_1, v43_2) = (v23_wifi_scan, v23_ap)
                if (v43_2 not in _m_Comp1_d_M_in):
                    _m_Comp1_d_M_in[v43_2] = set()
                _m_Comp1_d_M_in[v43_2].add(v43_1)
                # End maint _m_Comp1_d_M_in after "Comp1_d_M.add((v23_wifi_scan, v23_ap))"
                # Begin maint Comp1_Tap after "Comp1_d_M.add((v23_wifi_scan, v23_ap))"
                # Cost: O(1)
                # Iterate {(v27_wifi_scan, v27_ap) : (v27_wifi_scan, v27_ap) in deltamatch(Comp1_d_M, 'bb', _e, 1)}
                (v27_wifi_scan, v27_ap) = (v23_wifi_scan, v23_ap)
                if (v27_ap not in Comp1_Tap):
                    Comp1_Tap.add(v27_ap)
                    # Begin maint Comp1_d_F_ssid after "Comp1_Tap.add(v27_ap)"
                    # Cost: O(1)
                    # Iterate {(v37_ap, v37_ap_ssid) : v37_ap in deltamatch(Comp1_Tap, 'b', _e, 1), (v37_ap, v37_ap_ssid) in _F_ssid}
                    v37_ap = v27_ap
                    v37_ap_ssid = v37_ap.ssid
                    Comp1_d_F_ssid.add((v37_ap, v37_ap_ssid))
                    # End maint Comp1_d_F_ssid after "Comp1_Tap.add(v27_ap)"
                    # Begin maint Comp1_d_F_strength after "Comp1_Tap.add(v27_ap)"
                    # Cost: O(1)
                    # Iterate {(v29_ap, v29_ap_strength) : v29_ap in deltamatch(Comp1_Tap, 'b', _e, 1), (v29_ap, v29_ap_strength) in _F_strength}
                    v29_ap = v27_ap
                    v29_ap_strength = v29_ap.strength
                    Comp1_d_F_strength.add((v29_ap, v29_ap_strength))
                    # End maint Comp1_d_F_strength after "Comp1_Tap.add(v27_ap)"
                else:
                    Comp1_Tap.incref(v27_ap)
                # End maint Comp1_Tap after "Comp1_d_M.add((v23_wifi_scan, v23_ap))"
            # End maint Comp1_d_M after "Comp1_Twifi_scan.add(v21_wifi_scan)"
        else:
            Comp1_Twifi_scan.incref(v21_wifi_scan)
        # End maint Comp1_Twifi_scan after "Comp1_d_F_scan.add((v17_wifi, v17_wifi_scan))"
        # End maint Comp1_d_F_scan after "Comp1_Twifi.add(v15_wifi)"
        # End maint Comp1_Twifi after "_U_Comp1.add(wifi)"
        # Begin maint Comp1 after "_U_Comp1.add(wifi)"
        # Cost: O(v3_wifi_scan)
        # Iterate {(v3_wifi, v3_wifi_scan, v3_ap, v3_ap_strength, v3_wifi_threshold, v3_ap_ssid) : v3_wifi in deltamatch(_U_Comp1, 'b', _e, 1), (v3_wifi, v3_wifi_scan) in _F_scan, (v3_wifi_scan, v3_ap) in _M, (v3_ap, v3_ap_strength) in _F_strength, (v3_wifi, v3_wifi_threshold) in _F_threshold, (v3_ap_strength > v3_wifi_threshold), (v3_ap, v3_ap_ssid) in _F_ssid}
        v3_wifi = wifi
        v3_wifi_scan = v3_wifi.scan
        v3_wifi_threshold = v3_wifi.threshold
        for v3_ap in v3_wifi_scan:
            v3_ap_strength = v3_ap.strength
            if (v3_ap_strength > v3_wifi_threshold):
                v3_ap_ssid = v3_ap.ssid
                # Begin maint _m_Comp1_out after "Comp1.add((v3_wifi, v3_ap_ssid))"
                (v45_1, v45_2) = (v3_wifi, v3_ap_ssid)
                if (v45_1 not in _m_Comp1_out):
                    _m_Comp1_out[v45_1] = set()
                _m_Comp1_out[v45_1].add(v45_2)
                # End maint _m_Comp1_out after "Comp1.add((v3_wifi, v3_ap_ssid))"
        # End maint Comp1 after "_U_Comp1.add(wifi)"
    else:
        _U_Comp1.incref(wifi)

def undemand_Comp1(wifi):
    # Cost: O((v4_wifi_scan + v24_wifi_scan))
    '{(wifi, ap_ssid) : wifi in _U_Comp1, (wifi, wifi_scan) in _F_scan, (wifi_scan, ap) in _M, (ap, ap_strength) in _F_strength, (wifi, wifi_threshold) in _F_threshold, (ap_strength > wifi_threshold), (ap, ap_ssid) in _F_ssid}'
    if (_U_Comp1.getref(wifi) == 1):
        # Begin maint Comp1 before "_U_Comp1.remove(wifi)"
        # Cost: O(v4_wifi_scan)
        # Iterate {(v4_wifi, v4_wifi_scan, v4_ap, v4_ap_strength, v4_wifi_threshold, v4_ap_ssid) : v4_wifi in deltamatch(_U_Comp1, 'b', _e, 1), (v4_wifi, v4_wifi_scan) in _F_scan, (v4_wifi_scan, v4_ap) in _M, (v4_ap, v4_ap_strength) in _F_strength, (v4_wifi, v4_wifi_threshold) in _F_threshold, (v4_ap_strength > v4_wifi_threshold), (v4_ap, v4_ap_ssid) in _F_ssid}
        v4_wifi = wifi
        v4_wifi_scan = v4_wifi.scan
        v4_wifi_threshold = v4_wifi.threshold
        for v4_ap in v4_wifi_scan:
            v4_ap_strength = v4_ap.strength
            if (v4_ap_strength > v4_wifi_threshold):
                v4_ap_ssid = v4_ap.ssid
                # Begin maint _m_Comp1_out before "Comp1.remove((v4_wifi, v4_ap_ssid))"
                (v46_1, v46_2) = (v4_wifi, v4_ap_ssid)
                _m_Comp1_out[v46_1].remove(v46_2)
                if (len(_m_Comp1_out[v46_1]) == 0):
                    del _m_Comp1_out[v46_1]
                # End maint _m_Comp1_out before "Comp1.remove((v4_wifi, v4_ap_ssid))"
        # End maint Comp1 before "_U_Comp1.remove(wifi)"
        # Begin maint Comp1_Twifi before "_U_Comp1.remove(wifi)"
        # Cost: O(v24_wifi_scan)
        # Iterate {v16_wifi : v16_wifi in deltamatch(_U_Comp1, 'b', _e, 1)}
        v16_wifi = wifi
        # Begin maint Comp1_d_F_scan before "Comp1_Twifi.remove(v16_wifi)"
        # Cost: O(v24_wifi_scan)
        # Iterate {(v18_wifi, v18_wifi_scan) : v18_wifi in deltamatch(Comp1_Twifi, 'b', _e, 1), (v18_wifi, v18_wifi_scan) in _F_scan}
        v18_wifi = v16_wifi
        v18_wifi_scan = v18_wifi.scan
        # Begin maint Comp1_Twifi_scan before "Comp1_d_F_scan.remove((v18_wifi, v18_wifi_scan))"
        # Cost: O(v24_wifi_scan)
        # Iterate {(v22_wifi, v22_wifi_scan) : (v22_wifi, v22_wifi_scan) in deltamatch(Comp1_d_F_scan, 'bb', _e, 1)}
        (v22_wifi, v22_wifi_scan) = (v18_wifi, v18_wifi_scan)
        if (Comp1_Twifi_scan.getref(v22_wifi_scan) == 1):
            # Begin maint Comp1_d_M before "Comp1_Twifi_scan.remove(v22_wifi_scan)"
            # Cost: O(v24_wifi_scan)
            # Iterate {(v24_wifi_scan, v24_ap) : v24_wifi_scan in deltamatch(Comp1_Twifi_scan, 'b', _e, 1), (v24_wifi_scan, v24_ap) in _M}
            v24_wifi_scan = v22_wifi_scan
            for v24_ap in v24_wifi_scan:
                # Begin maint Comp1_Tap before "Comp1_d_M.remove((v24_wifi_scan, v24_ap))"
                # Cost: O(1)
                # Iterate {(v28_wifi_scan, v28_ap) : (v28_wifi_scan, v28_ap) in deltamatch(Comp1_d_M, 'bb', _e, 1)}
                (v28_wifi_scan, v28_ap) = (v24_wifi_scan, v24_ap)
                if (Comp1_Tap.getref(v28_ap) == 1):
                    # Begin maint Comp1_d_F_strength before "Comp1_Tap.remove(v28_ap)"
                    # Cost: O(1)
                    # Iterate {(v30_ap, v30_ap_strength) : v30_ap in deltamatch(Comp1_Tap, 'b', _e, 1), (v30_ap, v30_ap_strength) in _F_strength}
                    v30_ap = v28_ap
                    v30_ap_strength = v30_ap.strength
                    Comp1_d_F_strength.remove((v30_ap, v30_ap_strength))
                    # End maint Comp1_d_F_strength before "Comp1_Tap.remove(v28_ap)"
                    # Begin maint Comp1_d_F_ssid before "Comp1_Tap.remove(v28_ap)"
                    # Cost: O(1)
                    # Iterate {(v38_ap, v38_ap_ssid) : v38_ap in deltamatch(Comp1_Tap, 'b', _e, 1), (v38_ap, v38_ap_ssid) in _F_ssid}
                    v38_ap = v28_ap
                    v38_ap_ssid = v38_ap.ssid
                    Comp1_d_F_ssid.remove((v38_ap, v38_ap_ssid))
                    # End maint Comp1_d_F_ssid before "Comp1_Tap.remove(v28_ap)"
                    Comp1_Tap.remove(v28_ap)
                else:
                    Comp1_Tap.decref(v28_ap)
                # End maint Comp1_Tap before "Comp1_d_M.remove((v24_wifi_scan, v24_ap))"
                # Begin maint _m_Comp1_d_M_in before "Comp1_d_M.remove((v24_wifi_scan, v24_ap))"
                (v44_1, v44_2) = (v24_wifi_scan, v24_ap)
                _m_Comp1_d_M_in[v44_2].remove(v44_1)
                if (len(_m_Comp1_d_M_in[v44_2]) == 0):
                    del _m_Comp1_d_M_in[v44_2]
                # End maint _m_Comp1_d_M_in before "Comp1_d_M.remove((v24_wifi_scan, v24_ap))"
                Comp1_d_M.remove((v24_wifi_scan, v24_ap))
            # End maint Comp1_d_M before "Comp1_Twifi_scan.remove(v22_wifi_scan)"
            Comp1_Twifi_scan.remove(v22_wifi_scan)
        else:
            Comp1_Twifi_scan.decref(v22_wifi_scan)
        # End maint Comp1_Twifi_scan before "Comp1_d_F_scan.remove((v18_wifi, v18_wifi_scan))"
        # Begin maint _m_Comp1_d_F_scan_in before "Comp1_d_F_scan.remove((v18_wifi, v18_wifi_scan))"
        (v42_1, v42_2) = (v18_wifi, v18_wifi_scan)
        _m_Comp1_d_F_scan_in[v42_2].remove(v42_1)
        if (len(_m_Comp1_d_F_scan_in[v42_2]) == 0):
            del _m_Comp1_d_F_scan_in[v42_2]
        # End maint _m_Comp1_d_F_scan_in before "Comp1_d_F_scan.remove((v18_wifi, v18_wifi_scan))"
        Comp1_d_F_scan.remove((v18_wifi, v18_wifi_scan))
        # End maint Comp1_d_F_scan before "Comp1_Twifi.remove(v16_wifi)"
        # Begin maint Comp1_d_F_threshold before "Comp1_Twifi.remove(v16_wifi)"
        # Cost: O(1)
        # Iterate {(v34_wifi, v34_wifi_threshold) : v34_wifi in deltamatch(Comp1_Twifi, 'b', _e, 1), (v34_wifi, v34_wifi_threshold) in _F_threshold}
        v34_wifi = v16_wifi
        v34_wifi_threshold = v34_wifi.threshold
        Comp1_d_F_threshold.remove((v34_wifi, v34_wifi_threshold))
        # End maint Comp1_d_F_threshold before "Comp1_Twifi.remove(v16_wifi)"
        Comp1_Twifi.remove(v16_wifi)
        # End maint Comp1_Twifi before "_U_Comp1.remove(wifi)"
        _U_Comp1.remove(wifi)
    else:
        _U_Comp1.decref(wifi)

def query_Comp1(wifi):
    # Cost: O((v23_wifi_scan + v3_wifi_scan))
    '{(wifi, ap_ssid) : wifi in _U_Comp1, (wifi, wifi_scan) in _F_scan, (wifi_scan, ap) in _M, (ap, ap_strength) in _F_strength, (wifi, wifi_threshold) in _F_threshold, (ap_strength > wifi_threshold), (ap, ap_ssid) in _F_ssid}'
    if (wifi not in _UEXT_Comp1):
        _UEXT_Comp1.add(wifi)
        demand_Comp1(wifi)
    return True

def make_wifi(threshold):
    # Cost: O((v23_wifi_scan + v5_wifi_scan + v11_wifi_scan))
    wifi = Obj()
    wifi.scan = Set()
    # Begin maint Comp1_d_F_scan after "_F_scan.add((wifi, Set()))"
    # Cost: O(v23_wifi_scan)
    # Iterate {(v19_wifi, v19_wifi_scan) : v19_wifi in Comp1_Twifi, (v19_wifi, v19_wifi_scan) in deltamatch(_F_scan, 'bb', _e, 1)}
    (v19_wifi, v19_wifi_scan) = (wifi, Set())
    if (v19_wifi in Comp1_Twifi):
        Comp1_d_F_scan.add((v19_wifi, v19_wifi_scan))
        # Begin maint _m_Comp1_d_F_scan_in after "Comp1_d_F_scan.add((v19_wifi, v19_wifi_scan))"
        (v41_1, v41_2) = (v19_wifi, v19_wifi_scan)
        if (v41_2 not in _m_Comp1_d_F_scan_in):
            _m_Comp1_d_F_scan_in[v41_2] = set()
        _m_Comp1_d_F_scan_in[v41_2].add(v41_1)
        # End maint _m_Comp1_d_F_scan_in after "Comp1_d_F_scan.add((v19_wifi, v19_wifi_scan))"
        # Begin maint Comp1_Twifi_scan after "Comp1_d_F_scan.add((v19_wifi, v19_wifi_scan))"
        # Cost: O(v23_wifi_scan)
        # Iterate {(v21_wifi, v21_wifi_scan) : (v21_wifi, v21_wifi_scan) in deltamatch(Comp1_d_F_scan, 'bb', _e, 1)}
        (v21_wifi, v21_wifi_scan) = (v19_wifi, v19_wifi_scan)
        if (v21_wifi_scan not in Comp1_Twifi_scan):
            Comp1_Twifi_scan.add(v21_wifi_scan)
            # Begin maint Comp1_d_M after "Comp1_Twifi_scan.add(v21_wifi_scan)"
            # Cost: O(v23_wifi_scan)
            # Iterate {(v23_wifi_scan, v23_ap) : v23_wifi_scan in deltamatch(Comp1_Twifi_scan, 'b', _e, 1), (v23_wifi_scan, v23_ap) in _M}
            v23_wifi_scan = v21_wifi_scan
            for v23_ap in v23_wifi_scan:
                Comp1_d_M.add((v23_wifi_scan, v23_ap))
                # Begin maint _m_Comp1_d_M_in after "Comp1_d_M.add((v23_wifi_scan, v23_ap))"
                (v43_1, v43_2) = (v23_wifi_scan, v23_ap)
                if (v43_2 not in _m_Comp1_d_M_in):
                    _m_Comp1_d_M_in[v43_2] = set()
                _m_Comp1_d_M_in[v43_2].add(v43_1)
                # End maint _m_Comp1_d_M_in after "Comp1_d_M.add((v23_wifi_scan, v23_ap))"
                # Begin maint Comp1_Tap after "Comp1_d_M.add((v23_wifi_scan, v23_ap))"
                # Cost: O(1)
                # Iterate {(v27_wifi_scan, v27_ap) : (v27_wifi_scan, v27_ap) in deltamatch(Comp1_d_M, 'bb', _e, 1)}
                (v27_wifi_scan, v27_ap) = (v23_wifi_scan, v23_ap)
                if (v27_ap not in Comp1_Tap):
                    Comp1_Tap.add(v27_ap)
                    # Begin maint Comp1_d_F_ssid after "Comp1_Tap.add(v27_ap)"
                    # Cost: O(1)
                    # Iterate {(v37_ap, v37_ap_ssid) : v37_ap in deltamatch(Comp1_Tap, 'b', _e, 1), (v37_ap, v37_ap_ssid) in _F_ssid}
                    v37_ap = v27_ap
                    v37_ap_ssid = v37_ap.ssid
                    Comp1_d_F_ssid.add((v37_ap, v37_ap_ssid))
                    # End maint Comp1_d_F_ssid after "Comp1_Tap.add(v27_ap)"
                    # Begin maint Comp1_d_F_strength after "Comp1_Tap.add(v27_ap)"
                    # Cost: O(1)
                    # Iterate {(v29_ap, v29_ap_strength) : v29_ap in deltamatch(Comp1_Tap, 'b', _e, 1), (v29_ap, v29_ap_strength) in _F_strength}
                    v29_ap = v27_ap
                    v29_ap_strength = v29_ap.strength
                    Comp1_d_F_strength.add((v29_ap, v29_ap_strength))
                    # End maint Comp1_d_F_strength after "Comp1_Tap.add(v27_ap)"
                else:
                    Comp1_Tap.incref(v27_ap)
                # End maint Comp1_Tap after "Comp1_d_M.add((v23_wifi_scan, v23_ap))"
            # End maint Comp1_d_M after "Comp1_Twifi_scan.add(v21_wifi_scan)"
        else:
            Comp1_Twifi_scan.incref(v21_wifi_scan)
        # End maint Comp1_Twifi_scan after "Comp1_d_F_scan.add((v19_wifi, v19_wifi_scan))"
    # End maint Comp1_d_F_scan after "_F_scan.add((wifi, Set()))"
    # Begin maint Comp1 after "_F_scan.add((wifi, Set()))"
    # Cost: O(v5_wifi_scan)
    # Iterate {(v5_wifi, v5_wifi_scan, v5_ap, v5_ap_strength, v5_wifi_threshold, v5_ap_ssid) : v5_wifi in _U_Comp1, (v5_wifi, v5_wifi_scan) in deltamatch(Comp1_d_F_scan, 'bb', _e, 1), (v5_wifi, v5_wifi_scan) in Comp1_d_F_scan, (v5_wifi_scan, v5_ap) in _M, (v5_ap, v5_ap_strength) in _F_strength, (v5_wifi, v5_wifi_threshold) in _F_threshold, (v5_ap_strength > v5_wifi_threshold), (v5_ap, v5_ap_ssid) in _F_ssid}
    (v5_wifi, v5_wifi_scan) = (wifi, Set())
    if (v5_wifi in _U_Comp1):
        if ((v5_wifi, v5_wifi_scan) in Comp1_d_F_scan):
            v5_wifi_threshold = v5_wifi.threshold
            for v5_ap in v5_wifi_scan:
                v5_ap_strength = v5_ap.strength
                if (v5_ap_strength > v5_wifi_threshold):
                    v5_ap_ssid = v5_ap.ssid
                    # Begin maint _m_Comp1_out after "Comp1.add((v5_wifi, v5_ap_ssid))"
                    (v45_1, v45_2) = (v5_wifi, v5_ap_ssid)
                    if (v45_1 not in _m_Comp1_out):
                        _m_Comp1_out[v45_1] = set()
                    _m_Comp1_out[v45_1].add(v45_2)
                    # End maint _m_Comp1_out after "Comp1.add((v5_wifi, v5_ap_ssid))"
    # End maint Comp1 after "_F_scan.add((wifi, Set()))"
    wifi.threshold = threshold
    # Begin maint Comp1_d_F_threshold after "_F_threshold.add((wifi, threshold))"
    # Cost: O(1)
    # Iterate {(v35_wifi, v35_wifi_threshold) : v35_wifi in Comp1_Twifi, (v35_wifi, v35_wifi_threshold) in deltamatch(_F_threshold, 'bb', _e, 1)}
    (v35_wifi, v35_wifi_threshold) = (wifi, threshold)
    if (v35_wifi in Comp1_Twifi):
        Comp1_d_F_threshold.add((v35_wifi, v35_wifi_threshold))
    # End maint Comp1_d_F_threshold after "_F_threshold.add((wifi, threshold))"
    # Begin maint Comp1 after "_F_threshold.add((wifi, threshold))"
    # Cost: O(v11_wifi_scan)
    # Iterate {(v11_wifi, v11_wifi_scan, v11_ap, v11_ap_strength, v11_wifi_threshold, v11_ap_ssid) : v11_wifi in _U_Comp1, (v11_wifi, v11_wifi_scan) in _F_scan, (v11_wifi_scan, v11_ap) in _M, (v11_ap, v11_ap_strength) in _F_strength, (v11_wifi, v11_wifi_threshold) in deltamatch(Comp1_d_F_threshold, 'bb', _e, 1), (v11_wifi, v11_wifi_threshold) in Comp1_d_F_threshold, (v11_ap_strength > v11_wifi_threshold), (v11_ap, v11_ap_ssid) in _F_ssid}
    (v11_wifi, v11_wifi_threshold) = (wifi, threshold)
    if (v11_wifi in _U_Comp1):
        if ((v11_wifi, v11_wifi_threshold) in Comp1_d_F_threshold):
            v11_wifi_scan = v11_wifi.scan
            for v11_ap in v11_wifi_scan:
                v11_ap_strength = v11_ap.strength
                if (v11_ap_strength > v11_wifi_threshold):
                    v11_ap_ssid = v11_ap.ssid
                    # Begin maint _m_Comp1_out after "Comp1.add((v11_wifi, v11_ap_ssid))"
                    (v45_1, v45_2) = (v11_wifi, v11_ap_ssid)
                    if (v45_1 not in _m_Comp1_out):
                        _m_Comp1_out[v45_1] = set()
                    _m_Comp1_out[v45_1].add(v45_2)
                    # End maint _m_Comp1_out after "Comp1.add((v11_wifi, v11_ap_ssid))"
    # End maint Comp1 after "_F_threshold.add((wifi, threshold))"
    return wifi

def make_ap(ssid, strength):
    # Cost: O((Comp1_d_F_scan_in*Comp1_d_M_in))
    ### Deleted maintenance code
    ap = Obj()
    ap.ssid = ssid
    ap.strength = strength
    return ap

def add_ap(wifi, ap):
    # Cost: O(Comp1_d_F_scan_in)
    v1 = wifi.scan
    v1.add(ap)
    # Begin maint Comp1_d_M after "_M.add((v1, ap))"
    # Cost: O(1)
    # Iterate {(v25_wifi_scan, v25_ap) : v25_wifi_scan in Comp1_Twifi_scan, (v25_wifi_scan, v25_ap) in deltamatch(_M, 'bb', _e, 1)}
    (v25_wifi_scan, v25_ap) = (v1, ap)
    if (v25_wifi_scan in Comp1_Twifi_scan):
        Comp1_d_M.add((v25_wifi_scan, v25_ap))
        # Begin maint _m_Comp1_d_M_in after "Comp1_d_M.add((v25_wifi_scan, v25_ap))"
        (v43_1, v43_2) = (v25_wifi_scan, v25_ap)
        if (v43_2 not in _m_Comp1_d_M_in):
            _m_Comp1_d_M_in[v43_2] = set()
        _m_Comp1_d_M_in[v43_2].add(v43_1)
        # End maint _m_Comp1_d_M_in after "Comp1_d_M.add((v25_wifi_scan, v25_ap))"
        # Begin maint Comp1_Tap after "Comp1_d_M.add((v25_wifi_scan, v25_ap))"
        # Cost: O(1)
        # Iterate {(v27_wifi_scan, v27_ap) : (v27_wifi_scan, v27_ap) in deltamatch(Comp1_d_M, 'bb', _e, 1)}
        (v27_wifi_scan, v27_ap) = (v25_wifi_scan, v25_ap)
        if (v27_ap not in Comp1_Tap):
            Comp1_Tap.add(v27_ap)
            # Begin maint Comp1_d_F_ssid after "Comp1_Tap.add(v27_ap)"
            # Cost: O(1)
            # Iterate {(v37_ap, v37_ap_ssid) : v37_ap in deltamatch(Comp1_Tap, 'b', _e, 1), (v37_ap, v37_ap_ssid) in _F_ssid}
            v37_ap = v27_ap
            v37_ap_ssid = v37_ap.ssid
            Comp1_d_F_ssid.add((v37_ap, v37_ap_ssid))
            # End maint Comp1_d_F_ssid after "Comp1_Tap.add(v27_ap)"
            # Begin maint Comp1_d_F_strength after "Comp1_Tap.add(v27_ap)"
            # Cost: O(1)
            # Iterate {(v29_ap, v29_ap_strength) : v29_ap in deltamatch(Comp1_Tap, 'b', _e, 1), (v29_ap, v29_ap_strength) in _F_strength}
            v29_ap = v27_ap
            v29_ap_strength = v29_ap.strength
            Comp1_d_F_strength.add((v29_ap, v29_ap_strength))
            # End maint Comp1_d_F_strength after "Comp1_Tap.add(v27_ap)"
        else:
            Comp1_Tap.incref(v27_ap)
        # End maint Comp1_Tap after "Comp1_d_M.add((v25_wifi_scan, v25_ap))"
    # End maint Comp1_d_M after "_M.add((v1, ap))"
    # Begin maint Comp1 after "_M.add((v1, ap))"
    # Cost: O(Comp1_d_F_scan_in)
    # Iterate {(v7_wifi, v7_wifi_scan, v7_ap, v7_ap_strength, v7_wifi_threshold, v7_ap_ssid) : v7_wifi in _U_Comp1, (v7_wifi, v7_wifi_scan) in Comp1_d_F_scan, (v7_wifi_scan, v7_ap) in deltamatch(Comp1_d_M, 'bb', _e, 1), (v7_wifi_scan, v7_ap) in Comp1_d_M, (v7_ap, v7_ap_strength) in _F_strength, (v7_wifi, v7_wifi_threshold) in _F_threshold, (v7_ap_strength > v7_wifi_threshold), (v7_ap, v7_ap_ssid) in _F_ssid}
    (v7_wifi_scan, v7_ap) = (v1, ap)
    if ((v7_wifi_scan, v7_ap) in Comp1_d_M):
        v7_ap_strength = v7_ap.strength
        v7_ap_ssid = v7_ap.ssid
        for v7_wifi in (_m_Comp1_d_F_scan_in[v7_wifi_scan] if (v7_wifi_scan in _m_Comp1_d_F_scan_in) else set()):
            if (v7_wifi in _U_Comp1):
                v7_wifi_threshold = v7_wifi.threshold
                if (v7_ap_strength > v7_wifi_threshold):
                    # Begin maint _m_Comp1_out after "Comp1.add((v7_wifi, v7_ap_ssid))"
                    (v45_1, v45_2) = (v7_wifi, v7_ap_ssid)
                    if (v45_1 not in _m_Comp1_out):
                        _m_Comp1_out[v45_1] = set()
                    _m_Comp1_out[v45_1].add(v45_2)
                    # End maint _m_Comp1_out after "Comp1.add((v7_wifi, v7_ap_ssid))"
    # End maint Comp1 after "_M.add((v1, ap))"

def remove_ap(wifi, ap):
    # Cost: O(Comp1_d_F_scan_in)
    v2 = wifi.scan
    # Begin maint Comp1 before "_M.remove((v2, ap))"
    # Cost: O(Comp1_d_F_scan_in)
    # Iterate {(v8_wifi, v8_wifi_scan, v8_ap, v8_ap_strength, v8_wifi_threshold, v8_ap_ssid) : v8_wifi in _U_Comp1, (v8_wifi, v8_wifi_scan) in Comp1_d_F_scan, (v8_wifi_scan, v8_ap) in deltamatch(Comp1_d_M, 'bb', _e, 1), (v8_wifi_scan, v8_ap) in Comp1_d_M, (v8_ap, v8_ap_strength) in _F_strength, (v8_wifi, v8_wifi_threshold) in _F_threshold, (v8_ap_strength > v8_wifi_threshold), (v8_ap, v8_ap_ssid) in _F_ssid}
    (v8_wifi_scan, v8_ap) = (v2, ap)
    if ((v8_wifi_scan, v8_ap) in Comp1_d_M):
        v8_ap_strength = v8_ap.strength
        v8_ap_ssid = v8_ap.ssid
        for v8_wifi in (_m_Comp1_d_F_scan_in[v8_wifi_scan] if (v8_wifi_scan in _m_Comp1_d_F_scan_in) else set()):
            if (v8_wifi in _U_Comp1):
                v8_wifi_threshold = v8_wifi.threshold
                if (v8_ap_strength > v8_wifi_threshold):
                    # Begin maint _m_Comp1_out before "Comp1.remove((v8_wifi, v8_ap_ssid))"
                    (v46_1, v46_2) = (v8_wifi, v8_ap_ssid)
                    _m_Comp1_out[v46_1].remove(v46_2)
                    if (len(_m_Comp1_out[v46_1]) == 0):
                        del _m_Comp1_out[v46_1]
                    # End maint _m_Comp1_out before "Comp1.remove((v8_wifi, v8_ap_ssid))"
    # End maint Comp1 before "_M.remove((v2, ap))"
    # Begin maint Comp1_d_M before "_M.remove((v2, ap))"
    # Cost: O(1)
    # Iterate {(v26_wifi_scan, v26_ap) : v26_wifi_scan in Comp1_Twifi_scan, (v26_wifi_scan, v26_ap) in deltamatch(_M, 'bb', _e, 1)}
    (v26_wifi_scan, v26_ap) = (v2, ap)
    if (v26_wifi_scan in Comp1_Twifi_scan):
        # Begin maint Comp1_Tap before "Comp1_d_M.remove((v26_wifi_scan, v26_ap))"
        # Cost: O(1)
        # Iterate {(v28_wifi_scan, v28_ap) : (v28_wifi_scan, v28_ap) in deltamatch(Comp1_d_M, 'bb', _e, 1)}
        (v28_wifi_scan, v28_ap) = (v26_wifi_scan, v26_ap)
        if (Comp1_Tap.getref(v28_ap) == 1):
            # Begin maint Comp1_d_F_strength before "Comp1_Tap.remove(v28_ap)"
            # Cost: O(1)
            # Iterate {(v30_ap, v30_ap_strength) : v30_ap in deltamatch(Comp1_Tap, 'b', _e, 1), (v30_ap, v30_ap_strength) in _F_strength}
            v30_ap = v28_ap
            v30_ap_strength = v30_ap.strength
            Comp1_d_F_strength.remove((v30_ap, v30_ap_strength))
            # End maint Comp1_d_F_strength before "Comp1_Tap.remove(v28_ap)"
            # Begin maint Comp1_d_F_ssid before "Comp1_Tap.remove(v28_ap)"
            # Cost: O(1)
            # Iterate {(v38_ap, v38_ap_ssid) : v38_ap in deltamatch(Comp1_Tap, 'b', _e, 1), (v38_ap, v38_ap_ssid) in _F_ssid}
            v38_ap = v28_ap
            v38_ap_ssid = v38_ap.ssid
            Comp1_d_F_ssid.remove((v38_ap, v38_ap_ssid))
            # End maint Comp1_d_F_ssid before "Comp1_Tap.remove(v28_ap)"
            Comp1_Tap.remove(v28_ap)
        else:
            Comp1_Tap.decref(v28_ap)
        # End maint Comp1_Tap before "Comp1_d_M.remove((v26_wifi_scan, v26_ap))"
        # Begin maint _m_Comp1_d_M_in before "Comp1_d_M.remove((v26_wifi_scan, v26_ap))"
        (v44_1, v44_2) = (v26_wifi_scan, v26_ap)
        _m_Comp1_d_M_in[v44_2].remove(v44_1)
        if (len(_m_Comp1_d_M_in[v44_2]) == 0):
            del _m_Comp1_d_M_in[v44_2]
        # End maint _m_Comp1_d_M_in before "Comp1_d_M.remove((v26_wifi_scan, v26_ap))"
        Comp1_d_M.remove((v26_wifi_scan, v26_ap))
    # End maint Comp1_d_M before "_M.remove((v2, ap))"
    v2.remove(ap)

def do_query(wifi):
    # Cost: O((v23_wifi_scan + v3_wifi_scan))
    return (query_Comp1(wifi) and (_m_Comp1_out[wifi] if (wifi in _m_Comp1_out) else set()))

def do_query_nodemand(wifi):
    # Cost: O(1)
    return (_m_Comp1_out[wifi] if (wifi in _m_Comp1_out) else set())
