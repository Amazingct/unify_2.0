import socket
import json

path = "/home/amazing/Desktop/PROJECTS_AND_CODES/unify_2.0/configurations/"
HOST = ''
PORT = 65433  # Port to listen on (non-privileged ports are > 1023) for client devices
s = ""

def start_socket():
    global s
    s = socket.socket()
    s.bind((HOST, PORT))
    s.listen(5)

start_socket()

def new_client_or_not(ip):
    # check if ip exit in local db and return IP if yes
    with open(path+"db.json", "r") as local_db:
        db = json.loads(local_db.read())
        for i in db.keys():
            if ip == i:
                # if it exit, return False (not new) and row belonging to the ip in table
                return False, db[i]
                break

        return True, {"NEW":"NEW"}


def add_new_client_to_db(hub, ip):
    wrong = True
    while wrong is True:
        col = {}
        c_name = input("Enter Name: ")
        c_type = input("Enter Type: ").upper()
        print(c_type, c_name)

        if c_type =="T":
            # post new data with new tag
            result = hub.add_client(IP=ip, Name=c_name, Type=c_type, State=False)
            wrong = False
        elif c_type == "R" or c_type == "S":
            # post new data with new tag
            result = hub.add_client(IP=ip, Name=c_name, Type=c_type, State=0)
            wrong = False
        else:
            print("Invalid Type (R,T or S)")
            wrong = True

    # sync will automatically add to local database
    print(result)
    c_id = result["name"]
    # add to local db
    col.update({ip: {"ID": c_id, "Name": c_name, "Type": c_type, "state": 0}})
    # return info
    return c_id,c_name,c_type


def start_client_connection():
    conn, addr = s.accept()
    s.setblocking(1)  # prevent timeout
    return  conn, addr


class Client:
    def __init__(self, conn, addr, database, hub):
        # check if connected device is new or not
        neww, row = new_client_or_not(addr[0])
        if neww is False:
            self.name = (row["Name"])
            self.id = (row["ID"])
            self.type = row["Type"]
            print(self.name, "connected")

        elif neww is True:
            print(addr, "connected")
            a = input("Do you want to add new client (y/n) ? ")
            if a == "y":
                id, name, ttype = add_new_client_to_db(hub, addr[0])
                self.name = name
                self.id = id
                self.type = ttype
            else:
                pass

        # add conn object
        self.conn = conn
        self.ip = addr[0]

    def send_to_client(self, state):
        self.conn.send(str.encode(str(state)))
        return str(self.conn.recv(1024), "utf-8")

    def close(self):
        self.conn.close()

