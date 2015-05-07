# Run using the OSQ system.

from incoq.runtime import *
from osq import query

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
    return query('wifi -> {ap.ssid for ap in wifi.scan if ap.strength > wifi.threshold}', wifi)

do_query_nodemand = do_query
