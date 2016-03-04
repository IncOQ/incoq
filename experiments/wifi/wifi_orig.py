from .wifi_in import *

def do_query(wifi):
    return {ap.ssid for ap in wifi.scan
                    if ap.strength > wifi.threshold}

do_query_nodemand = do_query
