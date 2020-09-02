import pyrebase
import json, time
import client as cl
import threading as t
import logs
from random import randint
import os

from time import sleep
#  path to configuration files
pwd = str(os.getcwd())
path = pwd+ "/configurations/"
child = "users" # fire-base real-time db child
ready = False
hub = None


def change_state(device, state, button, switch):
    try:
        button = button.text
    except:
        button = button

    def changing():
        global hub, ready
        # stop syncing
        ready = False
        if button == "OFF" and state == "down":
            new_state = False
            all = hub.get_localdb_data()
            all[device.ip]["State"] = new_state


        elif button == "ON" and state == "down":
            new_state = True
            all = hub.get_localdb_data()
            all[device.ip]["State"] = new_state


        elif state == "down":
            pass

        elif button == "+":
            old_state = hub.get_client_info_from_localdb(device.name)["State"]
            new_state = old_state + 1
            if new_state >= 5: new_state = 0
            elif new_state < 0: new_state = 0
            all = hub.get_localdb_data()
            all[device.ip]["State"] = new_state
            state.text = str(new_state)


        elif button == "-":
            old_state = hub.get_client_info_from_localdb(device.name)["State"]
            new_state = old_state - 1
            if new_state >= 5: new_state = 0
            elif new_state < 0: new_state = 0
            all = hub.get_localdb_data()
            all[device.ip]["State"] = new_state
            state.text = str(new_state)



        # when syncing(internet)is off update local db and client manually
        # if there is internet this will be done by the sync thread automatically
        if not cl.Gui.connection == "cloud":
            # update client state and local db
            try:
                device.send_to_client(int(new_state), switch)
                hub.update_localdb_data(all)
            except Exception as e:
                print("send", e)

        # update database
        try:
            if cl.Gui.connection == "cloud":
                hub.update_client(device.name, State=new_state)
        except Exception as e:
            print("update failed: no internet")
        ready = True

    t.Thread(target=changing).start()






try:
    with open(path + "firebase_config.json") as config_file:
        config = json.loads(config_file.read())
    fire_base = pyrebase.initialize_app(config)
    auth = fire_base.auth()
    database = fire_base.database()
except Exception as e:
    print("fire base init:", e)



def update_hub_sensor_data():
    from datetime import datetime
    global hub
    while 1:
        sleep(2)
        temperature = randint(31,32) #get from sensor
        humidity = datetime.now()
        data = {"State": temperature}
        cl.Gui.home.hub_temperature.text =str(temperature) + u'\N{DEGREE SIGN}' + "C"
        cl.Gui.home.hub_humidity.text =str(humidity)[:-10]
        try:
            if cl.Gui.connection == "cloud":
                d = database.child("users").child(hub.id).child(hub.get_client_info_from_localdb("Temperature")["ID"]).update(data)
        except:
            pass




class Hub:

    def __init__(self, user):
        self.id = user["localId"]
        self.email = user["email"]
        print(self.email)

    def _connection_thread(self):
        # logs.log_cinfig()
        # logs.log("hy")
        global ready
        print("socket started")
        # start socket, create client device object, print out connected device info
        while True:
            while ready:
                try:
                    conn, addr = cl.start_client_connection()
                    # create client device object and append to cl.devices list
                    new = cl.Client(conn, addr, database, self)

                    if new.conn != None:
                        # if device has been previously added
                        print("new:", new.ip)

                        for device in cl.devices:

                            print("conected before:", device.ip)
                            if device.ip == new.ip:
                                #remove control
                                print("reseting control....")
                                cl.Gui.home.devices_box.remove_widget(device.control.device_box)
                                device.close()
                                print("reset done!")

                        #add control
                        cl.devices.append(new)
                        cl.devices[-1].control = cl.Gui.device_control(cl.devices[-1],
                                                                    hub.get_client_info_from_localdb(cl.devices[-1].name)["State"],
                                                                    change_state)


                    else:
                        print("not added")
                except Exception as e:
                    print("Connection:", e)
                    # logs.log(e)

    def _sync(self):
        print("sync started")
        global ready, cl
        while True:
            # if ready is true and connection is set to cloud, start syncing cloud db to local db
            if ready and cl.Gui.connection == "cloud":
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
                        for device in cl.devices:
                            try:
                                device.send_to_client(int(data[device.ip]["State"]))
                                if data[device.ip]["State"] == True and device.type == "T":
                                    device.control.bt_on.state = "down"; device.control.bt_off.state = "normal"
                                elif data[device.ip]["State"] == False and device.type == "T":
                                    device.control.bt_off.state = "down";device.control.bt_on.state = "normal"
                                else:
                                    device.control.level.text = str(data[device.ip]["State"])

                            except Exception as e:
                                print("sync send to client:", e)
                                device.conn.close()
                                # logs.log(e)



                except Exception as e:
                    print("Sync:", e)
                    #logs.log(e)

    def start_connection_thread(self):
        t.Thread(target=self._connection_thread).start()

    def start_sync_thread(self):
        t.Thread(target=self._sync).start()

    def __repr__(self):
        return self.id, self.email

    def get_localdb_data(self):
        try:
            with open(path + "db.json", "r") as db:
                return json.loads(db.read())
        except Exception as e:
            print("Error reading local database", e)
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
        for i in cl.devices:
            i.close()
        cl.devices = []
        ready = False


def p():
    global update_hub_sensor_data
    global ready, hub
    while ready == False:
        try:
            with open(path + "user.json", "r") as user_file:
                user = json.loads(user_file.read())
                hub =Hub(user)
                hub.start_connection_thread()
                hub.start_sync_thread()
                sleep(2)
                ready = True
                t.Thread(target=update_hub_sensor_data).start()

        except Exception as e:
            pass

def start():
    t.Thread(target=p).start()
    cl.Gui.start()
    #hub.close()