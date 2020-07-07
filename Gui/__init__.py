from kivy.app import App
import unify
import client
import time
import threading as t
from time import sleep
from kivy.uix.button import Label, Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
import pyrebase
import json

user = {}
hub = unify.Hub({"email":"", "localId":""})
path = "/home/amazing/Desktop/PROJECTS_AND_CODES/unify_2.0/configurations/"
child = "users"  # fire-base real-time db child

# get fire_base sdk configuration
with open(path + "cofig.json") as config_file:
    config = json.loads(config_file.read())
fire_base = pyrebase.initialize_app(config)
auth = fire_base.auth()
database = fire_base.database()

try:
    with open(path + "user.json", "r") as user_file:
        user = json.loads(user_file.read())
        print("logged in: ", user["email"])

except Exception as e:
    user = {}
    print(e)


# screens classes
class Login(Screen):
    password = ObjectProperty(None)
    email = ObjectProperty(None)
    r_password = ObjectProperty(None)

    def button_action(self, button):
        global user
        if button == "login":
            print("user: ", self.email.text, "password:", self.password.text)
            # sign into database
            try:
                user = auth.sign_in_with_email_and_password(self.email.text,self.password.text)
                print("logged in:", user)
                with open(path + "user.json", "w") as user_file:
                    user_file.write(json.dumps(user))
                self.password.text = ""
                self.email.text = ""
                wrapper.current = "home"
                
            except Exception as e:
                print(e)
                print("User dose not exit or Wrong password? Create account using Unify App")
                self.password.text = ""
                self.email.text = ""

        elif button == "register":
            wrapper.current = "register"


class Register(Screen):
    password = ObjectProperty(None)
    email = ObjectProperty(None)
    r_password = ObjectProperty(None)

    def button_action(self, button):
        global user
        try:
            if button == "submit":
                if len(self.password.text) < 6 or self.password.text != self.r_password.text:
                    print("Something went wrong")
                else:
                    user = auth.create_user_with_email_and_password(self.email.text, self.password.text)
                    print(user["email"])
                    # create sensor tag with dummy state
                    data = {"IP": "Local_Hub", "Name": "Temperature Sensor", "Type": "S", "State": 0}
                    rx = database.child(child).child(user["localId"]).push(data)
                    with open(path + "user.json", "w") as user_file:
                        user_file.write(json.dumps(user))
                    self.password.text = ""
                    self.email.text = ""
                    self.r_password.text = ""
                    wrapper.current = "home"
        except Exception as e:
            print("Invalid email")


# _____________________________________________________HOME___________________________________________________
class Home(Screen):
    email = ObjectProperty(None)
    devices = ObjectProperty(None)
    response = ObjectProperty(None)
    hub_temperature = ObjectProperty(None)

    def info_response(self):
        print("response", self.response.text)
        self.response.text = ""
        # add new device

    def render(self, state):
        if state == "fresh_login":
            self.email.text = user["email"]
            global hub
            hub.email = user["email"]
            hub.id = user["localId"]
            hub.close()  # reset connected devices
            hub.start_sync_firebase_clients_localdb_thread()
            hub.start_connection_thread()
            unify.ready = True

        elif state == "logged_out":
            print("User logged out")
            hub.close()  # reset class
            unify.ready = False
        elif state == "state_changed":
            pass

    def button_action(self, button):
        if button == "logout":
            wrapper.current = "login"
            # clear login details
            with open(path + "user.json", "w") as user_file:
                user_file.write("")
            self.render("logged_out")
            

# ________________________________________________________________________________________________________________
# load kv file
sign_in_up = Builder.load_file(path+"unify.kv")


# load screens into Screen Manager
class Wrapper(ScreenManager):
    pass


wrapper = Wrapper()
screens = [Login(name="login"), Register(name="register"), Home(name="home")]
for screen in screens:
    wrapper.add_widget(screen)

if user == {}:
    wrapper.current = "login"
else:
    wrapper.current = "home"


class Unify(App):
    def build(self):
        return wrapper


Unify().run()
