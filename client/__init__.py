import socket
import json
import Gui
from time import sleep
import threading as t
import os
pwd = str(os.getcwd())
path = pwd+ "/configurations/"
HOST = ''
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
devices = []

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
    col = {}
    c_name , c_type = Gui.show_popup("ADD DEVICE", "Enter name and select type?", "add")
    print(c_type, c_name)
    if c_type == None or c_type == None:
        c_id = None
    else:
        try:
            if c_type =="T":
                state = False
                # post new data with new tag
                result = hub.add_client(IP=ip, Name=c_name, Type=c_type, State=state)
                wrong = False
                print(result)
                c_id = result["name"]
            elif c_type == "R" or c_type == "S":
                state = 0
                # post new data with new tag
                result = hub.add_client(IP=ip, Name=c_name, Type=c_type, State=state)
                wrong = False
                print(result)
                c_id = result["name"]
            # add to local db
            col.update({ip: {"ID": c_id, "Name": c_name, "Type": c_type, "State": state}})
            all = hub.get_localdb_data()
            all.update(col)
            hub.update_localdb_data(all)
        except Exception as e:
            print(e)
            c_id = None
            Gui.show_popup("ADD new", "Oops! Something went wrong.\nYou need internet to add new device", "info")

        # return info
    return c_id,c_name,c_type


def start_client_connection():
    conn, addr = s.accept()
    s.setblocking(1)  # prevent timeout
    return  conn, addr


class Client:
    def __init__(self, conn, addr, database, hub):
        # check if connected device is new or not
        self.conn = None
        self.control = None
        neww, row = new_client_or_not(addr[0])
        if neww is False:
            self.name = (row["Name"])
            self.id = (row["ID"])
            self.type = row["Type"]
            print(self.name, "connected")
            # add conn object
            self.conn = conn
            self.ip = addr[0]

        elif neww is True:
            print(addr, "connected")
            a = Gui.show_popup("NEW DEVICE", "Do you want to add?", "add?")
            # a = input("Do you want to add new client (y/n) ? ")
            if a == "yes":
                id, name, ttype = add_new_client_to_db(hub, addr[0])
                self.name = name
                self.id = id
                self.type = ttype
                # add conn object
                if self.name == None or self.type == None:
                    self.conn = None
                    self.ip = None
                else:
                    self.conn = conn
                    self.ip = addr[0]
            else:
                pass

    def send_to_client(self, state, remove=None):
        rxx = None
        # if it takes more than 3 seconds to receive response from client, it means client has disconnected

        def count():
            timer = 0
            while timer < 4:
                sleep(1)
                timer = timer+1
            if rxx == None and remove != None:
                self.conn.close()
                print(" device closed")

        t.Thread(target=count).start()


        try:
            self.conn.send(str.encode(str(state)))
            rxx = str(self.conn.recv(1024), "utf-8")
            return rxx
        except Exception as e:
            # print("send", e)
            self.close()
            return rxx

    def close(self):
        global devices
        self.conn.close()
        devices.remove(self)

