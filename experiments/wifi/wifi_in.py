# Wifi query from Tom's thesis.

from incoq.mars.runtime import *

CONFIG(
    obj_domain = 'true',
)

SYMCONFIG('Q',
    demand_param_strat = 'all',
    count_elim_safe_override = 'true',
    well_typed_data = 'true',
)

def make_wifi(threshold):
    wifi = Obj()
    wifi.scan = Set()
    wifi.threshold = threshold
    return wifi

def make_ap(ssid, strength):
    ap = Obj()
    ap.ssid = ssid
    ap.strength = strength
    return ap

def add_ap(wifi, ap):
    wifi.scan.add(ap)

def remove_ap(wifi, ap):
    wifi.scan.remove(ap)

def do_query(wifi):
    return QUERY('Q', {ap.ssid for ap in wifi.scan
                               if ap.strength > wifi.threshold})

def do_query_nodemand(wifi):
    return QUERY('Q', {ap.ssid for ap in wifi.scan
                               if ap.strength > wifi.threshold},
                 {'nodemand': True})
