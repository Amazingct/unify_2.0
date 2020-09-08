import socket
from time import sleep
HOST = '192.168.43.152'
PORT = 65433  # Port to listen on (non-privileged ports are > 1023) for client devices


def bind():
    global s
    s = socket.socket()
    s.bind((HOST, PORT))

try:
    bind()
except:
    s.close()
    sleep(3)
    bind()

s.listen(5)
conn, addr = s.accept()
s.setblocking(1)  # prevent timeout
print("connected to", addr)

while 1:
    data = input("data: >>> ")
    conn.send(str.encode(str(data)))
    rxx = str(conn.recv(1024), "utf-8")
    print("response", rxx)