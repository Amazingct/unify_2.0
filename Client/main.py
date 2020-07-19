from machine import Pin
from time import sleep
import socket
import json
connected = 0

g = Pin(14, Pin.OUT)  # d5
b = Pin(5, Pin.OUT)  # d1
r = Pin(4, Pin.OUT)  # d2
load = Pin(13, Pin.OUT)  # d7


def led(color):
    r.value(color[0])
    g.value(color[1])
    b.value(color[2])


# set load to off
load.value(0)


with open("config.txt") as config:
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
            led([0 ,0 ,1])
            sleep(0.5)
            led([0 ,0 ,0])
            sleep(0.5)
        led([0 ,0 ,1])

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
        elif data == bytes("0", "utf-8"):
            load.value(0)
            led([1 ,0 ,0])
        elif data == bytes("1", "utf-8"):
            load.value(1)
            led([0 ,1 ,0])
        rx = "done"
        s.sendall(bytes(rx, "utf-8"))

    except Exception as e:
        connect2hub()
        print(e)


led([1 ,0 ,0])
s.close()







