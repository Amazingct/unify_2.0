from kivy.app import App

import time
import threading as t
from time import sleep
from kivy.uix.button import Label, Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
import pyrebase
import json
rx = "no"
done = False
user = {}
path = "/home/amazing/Desktop/PROJECTS_AND_CODES/unify_2/configurations/"
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


class Info(BoxLayout):
    info = ObjectProperty(None)
    yes_button = ObjectProperty(None)
    no_button = ObjectProperty(None)
    def response(self, button):
        global done
        global rx
        if button == "yes":
            rx  = "yes"
        if button == "no":
            rx = "no"
        done = True



class Add_new(BoxLayout):
    info= ObjectProperty(None)
    add = ObjectProperty(None)
    cancle = ObjectProperty(None)
    c_name = ObjectProperty(None)
    c_type = ObjectProperty(None)
    def response(self, button):
        global done
        global rx
        if button == "add":
            rx  = (self.c_name.text, self.c_type.text)
        if button == "cancle":
            rx = (None, None)
        done = True


def show_popup(title, info, type):

    global rx, done
    if type == "add?":
        pop = Info()
        pop.info.text = info
        popUp = Popup(title=title, content=pop, size_hint=(None, None), size = (400,400), auto_dismiss=False)
        pop.yes_button.bind(on_press=popUp.dismiss)
        pop.no_button.bind(on_press=popUp.dismiss)
        popUp.open()
        while done != True:
            pass
        done = False
        return rx

    
    
    elif type == "add":
        pop = Add_new()
        pop.info.text = info
        popUp = Popup(title=title, content=pop, size_hint=(None, None), size=(400, 400), auto_dismiss=False)
        pop.add.bind(on_press=popUp.dismiss)
        pop.cancle.bind(on_press=popUp.dismiss)
        popUp.open()
        while done != True:
            pass
        done = False
        return rx #this will be a tuple instaed (c_name, c_type)





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
    devices_box = ObjectProperty(None)
    hub_temperature = ObjectProperty(None)


    def render(self):
        with open(path + "user.json", "r") as user_file:
            user = json.loads(user_file.read())
        self.email.text = user["email"]


    def button_action( self, button):
        if button == "logout":
            wrapper.current = "login"
            # clear login details
            with open(path + "user.json", "w") as user_file:
                user_file.write("")
        else:
            pass
# ________________________________________________________________________________________________________________
# load kv file
Builder.load_file(path+"unify.kv")
# load screens into Screen Manager
class Wrapper(ScreenManager):
    pass

wrapper = Wrapper()
l = Login(name="login")
r = Register(name="register")
home = Home(name="home")
wrapper.add_widget(l)
wrapper.add_widget(r)
wrapper.add_widget(home)

if user == {}:
    wrapper.current = "login"
else:
    wrapper.current = "home"

class Unify(App):
    def build(self):
        return wrapper

def start():
    Unify().run()


