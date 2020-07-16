import socket
HOST = ''
PORT = 65433  # Port to listen on (non-privileged ports are > 1023) for client devices
s = ""
s = socket.socket()
s.bind((HOST, PORT))
s.listen(5)
conn, addr = s.accept()


while 1:
    state = input(">>")
    conn.send(str.encode(str(state)))
    print("waiting")
    print(str(conn.recv(1024), "utf-8"))

