try:
    import usocket as socket
except:
    import socket

from machine import Pin
import network
import esp

esp.osdebug(None)
import gc

gc.collect()

r = Pin(14, Pin.OUT)
r.value(0)

import json
with open("config.txt") as config:
    d = json.loads(config.read())
    password = d["password"]
    ssid = d["ssid"]

hub = network.WLAN(network.STA_IF)
hub.active(True)
hub.connect(ssid, password)

print('Connection successful')
print(hub.ifconfig())
r.value(1)


