import pyrebase
import json, time
import client as cl

import threading as t
import logs

from time import sleep
#  path to configuration files
path = "/home/amazing/Desktop/PROJECTS_AND_CODES/unify_2/configurations/"
child = "users" # fire-base real-time db child
devices = []
ready = True
hub = None
db_downloaded = False


with open(path + "cofig.json") as config_file:
    config = json.loads(config_file.read())
fire_base = pyrebase.initialize_app(config)
auth = fire_base.auth()
database = fire_base.database()


def update_hub_sensor_data(user, tag):
    temperature = "8 *C"
    data = {"State": temperature}
    d = database.child("users").child(user).child(tag).update(data)
    return


class Hub:
    global devices

    def __init__(self, user):
        self.id = user["localId"]
        self.email = user["email"]
        print(self.email)

    def _connection_thread(self):
        logs.log_cinfig()
        global ready, db_downloaded
        print("socket started")
        # start socket, create client device object, print out connected device info
        while True:
            while ready and db_downloaded:
                try:
                    conn, addr = cl.start_client_connection()
                    # create client device object and append to devices list
                    devices.append(cl.Client(conn, addr, database, self))
                except Exception as e:
                    print("Connection:", e)
                    logs.log(e)

    def _sync(self):
        print("sync started")
        global ready, db_downloaded
        while True:
            update = database.child("users").child("Update").get().val()
            # print("Upate is", update)
            if update is True and ready == True: # if update is set to true on firebase (data has been modified) then sync
                try:
                    read = self.get_all_data()
                    # when it tries to read from fire base and ID has been deleted from firebase read is "None"
                    if str(read) == "None":
                        self.update_localdb_data({})

                    else:
                        # if it exit, proceed to syncing local db
                        data = {}
                        for key, val in read.items():
                            data.update({read[key]["IP"]:
                                {
                                    "ID": key,
                                    "Name": read[key]["Name"],
                                    "Type": read[key]["Type"],
                                    "State": read[key]["State"]
                                }
                            })

                        self.update_localdb_data(data)
                        db_downloaded = True
                        # send states to client

                        for device in devices:
                            try:
                                device.send_to_client(int(data[device.ip]["State"]))
                            except Exception as e:
                                print("devices:", e)
                                device.close()
                                devices.remove(device)
                                logs.log(e)
                        # update sensor value on firebase
                        update_hub_sensor_data(self.id, self.get_client_info_from_localdb("Temperature Sensor")["ID"])
                        time.sleep(1)
                except Exception as e:
                    print("Sync:", e)
                    logs.log(e)

    def start_connection_thread(self):
        t.Thread(target=self._connection_thread).start()


    def __repr__(self):
        return self.id, self.email

    def get_localdb_data(self):
        try:
            with open(path + "db.json", "r") as db:
                return json.loads(db.read())
        except Exception as e:
            print("Error reading local database")
            return None

    def update_localdb_data(self, data):
        with open(path + "db.json", "w") as db:
            db.write(json.dumps(data))
            return True


    def get_all_data(self):
        data = database.child("users").child(self.id).get().val()
        if data != None:
            return dict(data)
        else:
            return None

    def start_sync_firebase_clients_localdb_thread(self):
        """sync local database, clients fire-base"""
        # start thread
        t.Thread(target=self._sync).start()

    def get_client_info_from_localdb(self, name):
        """takes a client name, checks localdb and return given info(IP, tag, State etc)"""
        with open(path+"db.json", "r") as local_db:
            data = json.loads(local_db.read())

        info = {}
        for key, val in data.items():

            if val["Name"] == name:
                id = val["ID"]
                state = val["State"]
                type = val["Type"]
                ip = key
                info.update({"ID":id, "IP":ip, "State":state, "Type":type})
                return info

    def update_client(self, client_name, **kwargs):
        """change client data o firebase"""
        tag = self.get_client_info_from_localdb(client_name)["ID"]
        for key, val in kwargs.items():
            database.child(child).child(self.id).child(tag).update({key:val})

    def add_client(self, **kwargs):
        """ add new client device"""
        data = kwargs
        # post new data with new tag
        rx = database.child(child).child(self.id).push(data)
        return rx

    def close(self):
        global ready
        global devices
        for i in devices:
            i.close()
        devices = []
        ready = False


def p():
    a = True
    global ready, hub
    while a:
        try:
            with open(path + "user.json", "r") as user_file:
                user = json.loads(user_file.read())
                hub =Hub(user)
                hub.start_connection_thread()
                hub.start_sync_firebase_clients_localdb_thread()
                a = False

        except Exception as e:
            print("yee:", e)


t.Thread(target=p).start()
cl.Gui.start()
hub.close()
