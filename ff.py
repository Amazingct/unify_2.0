import socket

s = socket.socket()

s.bind(('', 8090 ))
s.listen(0)

while True:

    client, addr = s.accept()

    while True:
        content = client.recv(32)
        print(content)

    client.close()