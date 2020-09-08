from machine import Pin
from time import sleep
from machine import UART
import socket
import json
connected = 0

uart = UART(2, 9600)                         # init with given baudrate
uart.init(9600, bits=8, parity=None, stop=1)
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

load = Pin(4, Pin.OUT)  # d7

# set load to off
load.value(0)


with open("config.json") as config:
    d = json.loads(config.read())
    HOST = d["hub"]
    PORT = 65433

s = 0


def connect2hub():
    global connected, s
    print("Connecting to hub")
    try:
        s = socket.socket()
        s.connect((HOST, PORT))
        connected = 1
        print("Connection successful")

        for i in range(2):
            led_write(green)
            sleep(1)
            led_write(red)
            sleep(1)
            led_write(red)
            sleep(1)
        led_write(red)

    except:
        connected = 0


while connected == 0:
    sleep(5)
    connect2hub()

# if connected proceed
while True:
    try:
        data = s.recv(1024)
        print('Received', repr(data))
        if data == bytes("quit", "utf-8"):
            s.close()
            break
        else:
            if '1' in data:
                led_write(red)
            else:
                led_write(green)
            uart.write(str(data) + "-")
        rx = "done"
        s.sendall(bytes(rx, "utf-8"))

    except Exception as e:
        connect2hub()
        print(e)


led_write(red)
s.close()







