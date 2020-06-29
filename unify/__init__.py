import pyrebase
import json
import client as cl
import threading as t
import Gui as g
import logs
from time import sleep
#  path to configuration files
path = "/home/amazing/Desktop/PROJECTS_AND_CODES/unify_2.0/configurations/"
child = "users" # fire-base real-time db child
devices = []



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


def sign_up():
    print("CREATE NEW ACCOUNT")
    email = input("email: ")
    password = input("password: ")
    try:
        user = auth.create_user_with_email_and_password(email, password)
        print(user["localId"])
        # create sensor tag with dummy state
        data = {"IP":"Local_Hub", "Name": "Temperature Sensor", "Type": "S", "State": 0}
        d = database.child(child).child(user["localId"]).push(data)
        print(d)

    except Exception as e:
        print("User exits")
        print(e)


def sign_in():

    try:
        with open(path + "user.json", "r") as user_file:
            user = json.loads(user_file.read())
            print("ID:", user["localId"])
            g.email = user["email"]
            return user
    except Exception as e:
        print("Not logged in yet")
        email = input("email: ")
        password = input("password: ")

    try:
        user = auth.sign_in_with_email_and_password(email, password)
        print("logged in:", user)
        with open(path + "user.json", "w") as user_file:
            user_file.write(json.dumps(user))
            g.email = user["email"]
            return user
    except Exception as e:
        print("User dose not exit or Wrong password? Create account using Unify App")
        return None


def logout():
    with open(path+"user.json", "w") as user:
        user.write("")


class Hub:
    global devices

    def __init__(self, user):
        self.id = user["localId"]
        self.email = user["email"]
        print(self.email)
        logs.log_cinfig()

    def _connection_thread(self):
        print("socket started")
        # start socket, create client device object, print out connected device info
        while True:
            try:
                conn, addr = cl.start_client_connection()
                # create client device object and append to devices list
                devices.append(cl.Client(conn, addr, database, self))
            except Exception as e:
                print("Connection:", e)

    def _sync(self):
        print("sync started")
        while True:
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
                    # send states to client

                    for device in devices:
                        try:
                            device.send_to_client(int(data[device.ip]["State"]))
                        except Exception as e:
                            print("devices:", e)
                            device.close()
                            devices.remove(device)
                    # update sensor value on firebase
                    update_hub_sensor_data(self.id, self.get_client_info_from_localdb("Temperature Sensor")["ID"])
            except Exception as e:
                print("Sync:", e)

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


def start_gui():
    g.start_gui()

