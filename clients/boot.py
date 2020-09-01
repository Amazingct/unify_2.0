try:
    import usocket as socket
except:
    import socket

from machine import Pin
import network, time
import neopixel
led = neopixel.NeoPixel(Pin(5),1)
red = (255, 0, 0)
green = (120, 153, 23)
blue = (125, 204,233)
off = (0,0,0)


def led_write(color):
    global led
    led[0] = color
    led.write()

import esp

esp.osdebug(None)
import gc

gc.collect()

led_write(red)
time.sleep(2)


import json
with open("config.json") as config:
    d = json.loads(config.read())
    password = d["password"]
    ssid = d["ssid"]

hub = network.WLAN(network.STA_IF)
hub.active(True)
hub.connect(ssid, password)

print('Connection successful')
print(hub.ifconfig())

led_write(green)
time.sleep(2)


