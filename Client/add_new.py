from machine import UART
import json

uart = UART(2, 115200)
uart.init(115200, bits=8, parity=None, stop=1)
config = []

ch = b''
while 1:
    if uart.any() > 0:
        ch = uart.readline()
        rx = str(ch, "utf-8")
        if rx == "config":
            uart.write(b'Enter Hub-wifi name, password and ip: \n')
            while not uart.any() > 0:
                pass
            ch = uart.readline()
            rx = str(ch, "utf-8")
            config = rx.split("-")
            print(config)
            with open("config.json", "w") as c:
                config = {"ssid": config[0], "password": config[1], "hub": config[2]}
                c.write(json.dumps(config))
            uart.write("done!!!\n")


        else:
            print(rx)
            uart.write(ch + "\n")

'''
HUB SIDE CODE:

import serial
arduino = serial.Serial('/dev/ttyUSB1',115200)

while 1:
    d = input(">>")
    arduino.write(bytes(d, "utf-8"))
    rx=str(arduino.readline(), "utf-8")
    print(rx[0:-1])
    if rx[0:-1] == "done!!!"
    break

'''



