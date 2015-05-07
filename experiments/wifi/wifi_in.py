# Wifi query from Tom's thesis.
#
#   wifi -> {ap.ssid : ap in wifi.scan, ap.strength > wifi.threshold}

from incoq.runtime import *

OPTIONS(
    obj_domain = True,
)

QUERYOPTIONS(
    '{ap.ssid for ap in wifi.scan if ap.strength > wifi.threshold}',
    uset_mode = 'all',
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
    return {ap.ssid for ap in wifi.scan
                    if ap.strength > wifi.threshold}

def do_query_nodemand(wifi):
    return NODEMAND({ap.ssid for ap in wifi.scan
                             if ap.strength > wifi.threshold})
