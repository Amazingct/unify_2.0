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
ready = False
hub = None


def internet():
    pass
    

def change_state(device, state, button):
    global hub
    if button == "OFF" and state == "down":
        new_state = False
        all = hub.get_localdb_data()
        all[device.ip]["State"] = new_state
        hub.update_localdb_data(all)
        device.send_to_client(int(new_state))

    elif button == "ON" and state == "down":
        new_state = True
        all = hub.get_localdb_data()
        all[device.ip]["State"] = new_state
        hub.update_localdb_data(all)
        device.send_to_client(int(new_state))

    elif state == "down":
        pass

    elif button == "+":
        old_state = hub.get_client_info_from_localdb(device.name)["State"]
        new_state = old_state + 1
        if new_state >= 5: new_state = 0
        elif new_state < 0: new_state = 0
        all = hub.get_localdb_data()
        all[device.ip]["State"] = new_state
        device.send_to_client(int(new_state))
        hub.update_localdb_data(all)
        state.text = str(new_state)
    elif button == "-":
        old_state = hub.get_client_info_from_localdb(device.name)["State"]
        new_state = old_state - 1
        if new_state >= 5: new_state = 0
        elif new_state < 0: new_state = 0
        all = hub.get_localdb_data()
        all[device.ip]["State"] = new_state
        device.send_to_client(int(new_state))
        hub.update_localdb_data(all)
        state.text = str(new_state)
    try:
        hub.update_client(device.name, State=new_state)
    except Exception as e:
        print("update failed: ", e)




try:
    with open(path + "cofig.json") as config_file:
        config = json.loads(config_file.read())
    fire_base = pyrebase.initialize_app(config)
    auth = fire_base.auth()
    database = fire_base.database()
except Exception as e:
    print("fire base init:", e)


def create_control_interface(new):
    if new.type == "T":
        device_list = [new.name, "Switch"]
        device_box = cl.Gui.BoxLayout(orientation="horizontal", spacing=0.3, size_hint_y=None, size=(0, 40))
        device_box.add_widget(cl.Gui.Label(text=device_list[0], bold=True, size_hint_x=0.6))
        # get current state and send
        state = hub.get_client_info_from_localdb(new.name)["State"]
        new.send_to_client(state)
        switch = cl.Gui.BoxLayout(orientation="horizontal", spacing=0.3, size_hint_x=0.3, )
        if state is True:
            bt_on = cl.Gui.ToggleButton(text='ON', group='switch', state="down", allow_no_selection=False)
            bt_off = cl.Gui.ToggleButton(text='OFF', group='switch', state="normal", allow_no_selection=False)

        elif state is False:
            bt_on = cl.Gui.ToggleButton(text='ON', group='switch', state="normal", allow_no_selection=False)
            bt_off = cl.Gui.ToggleButton(text='OFF', group='switch', state="down", allow_no_selection=False)
        callback = lambda _: change_state(new, bt_on.state, bt_on.text)
        bt_on.bind(on_release=callback)
        callback = lambda _: change_state(new, bt_off.state, bt_off.text)
        bt_off.bind(on_release=callback)

        switch.add_widget(bt_off)
        switch.add_widget(bt_on)

        device_box.add_widget(switch)
        cl.Gui.home.devices_box.add_widget(device_box)
    elif new.type == "R":
        device_list = [new.name, "Switch"]
        device_box = cl.Gui.BoxLayout(orientation="horizontal", spacing=0.3, size_hint_y=None, size=(0, 40))
        device_box.add_widget(cl.Gui.Label(text=device_list[0], bold=True, size_hint_x=0.6))
        # get current state and send
        state = hub.get_client_info_from_localdb(new.name)["State"]
        new.send_to_client(state)
        switch = cl.Gui.BoxLayout(orientation="horizontal", spacing=0.3, size_hint_x=0.4, )

        bt_up = cl.Gui.Button(text='+', bold = True)
        level = cl.Gui.Label(id = "level" ,text=str(state))
        bt_down = cl.Gui.Button(text='-', bold = True)
        callback = lambda _: change_state(new, level, bt_up.text)
        bt_up.bind(on_release=callback)
        callback = lambda _: change_state(new, level, bt_down.text)
        bt_down.bind(on_release=callback)

        switch.add_widget(bt_down)
        switch.add_widget(level)
        switch.add_widget(bt_up)

        device_box.add_widget(switch)
        cl.Gui.home.devices_box.add_widget(device_box)

def update_hub_sensor_data(user, tag):
    temperature = 32
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
        # logs.log_cinfig()
        # logs.log("hy")
        global ready
        print("socket started")
        # start socket, create client device object, print out connected device info
        while True:
            while ready:
                try:
                    conn, addr = cl.start_client_connection()
                    # create client device object and append to devices list
                    new = cl.Client(conn, addr, database, self)

                    if new.conn != None:
                        devices.append(new)
                        create_control_interface(new)

                    else:
                        print("not added")
                except Exception as e:
                    print("Connection:", e)
                    # logs.log(e)

    def sync(self, device, state):
        all = self.get_localdb_data()
        all[device.ip]["State"] = state
        self.update_localdb_data(all)
        try:
            self.update_client(device.name, State=state)
        except Exception as e:
            print("update failed: ", e)
        

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
    global ready, hub
    while ready == False:
        try:
            with open(path + "user.json", "r") as user_file:
                user = json.loads(user_file.read())
                hub =Hub(user)
                hub.start_connection_thread()
                sleep(3)
                ready = True

        except Exception as e:
            pass


t.Thread(target=p).start()
cl.Gui.start()
hub.close()
