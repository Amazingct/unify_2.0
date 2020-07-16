from kivy.app import App
from kivy.uix.togglebutton import ToggleButton, ToggleButtonBehavior
import time
from kivy.uix.slider import Slider
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
import  urllib
connection = "cloud"
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


def connected_to_internet(host="https://google.com"):
    try:
        urllib.request.urlopen(host)
        print("Internet available")
        return True
    except Exception as e:
        print("internet:", e)
        print("internet Unavailable")
        return False


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

class login_info(BoxLayout):
    info= ObjectProperty(None)



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

    elif type == "info":
        pop = login_info()
        pop.info.text = info
        popUp = Popup(title=title, content=pop, size_hint=(None, None), size=(400, 400))
        popUp.open()
        return rx #this will be a tuple instaed (c_name, c_type)






# screens classes
class Login(Screen):
    password = ObjectProperty(None)
    email = ObjectProperty(None)
    r_password = ObjectProperty(None)

    def button_action(self, button):
        def action():
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
                    #download db from firebase
                    read = database.child("users").child(user["localId"]).get().val()
                    # re -arrange
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
                    with open(path+"db.json", "w") as db:
                        db.write(json.dumps(data))
                    wrapper.current = "home"
                except Exception as e:
                    print(e)
                    show_popup("LOGIN", "Oops! Something went wrong.\nCheck Internet and login details","info")
                    print("User dose not exit or Wrong password? Create account using Unify App")


            elif button == "register":
                wrapper.current = "register"
        t.Thread(target=action).start()


class Register(Screen):
    password = ObjectProperty(None)
    email = ObjectProperty(None)
    r_password = ObjectProperty(None)

    def button_action(self, button):
        global user
        try:
            if button == "submit":
                if len(self.password.text) < 6 or self.password.text != self.r_password.text:
                    show_popup("SIGN UP", "Invalid password","info")
                else:
                    user = auth.create_user_with_email_and_password(self.email.text, self.password.text)
                    print(user["email"])
                    # create sensor tag with dummy state
                    data = {"IP": "Local_Hub", "Name": "Temperature", "Type": "S", "State": 0}
                    # add to cloud
                    rx = database.child(child).child(user["localId"]).push(data)
                    # add locally
                    data_c = {}
                    data_c.update({data["IP"]:
                        {
                            "ID": rx["name"],
                            "Name": data["Name"],
                            "Type": data["Type"],
                            "State": data["State"]
                        }
                    })
                    with open(path + "db.json", "w") as db:
                        db.write(json.dumps(data_c))

                    with open(path + "user.json", "w") as user_file:
                        user_file.write(json.dumps(user))
                    self.password.text = ""
                    self.email.text = ""
                    self.r_password.text = ""
                    wrapper.current = "home"
            elif button == "back_to_login":wrapper.current = "login"
        except Exception as e:
            print(e)
            show_popup("SIGN UP", "Oops! Something went wrong.\nCheck Internet and signup details","info")


# _____________________________________________________HOME___________________________________________________
class Home(Screen):
    email = ObjectProperty(None)
    devices_box = ObjectProperty(None)
    hub_temperature = ObjectProperty(None)
    cloud = ObjectProperty(None)
    local = ObjectProperty(None)




    def render(self):
        global connection
        with open(path + "user.json", "r") as user_file:
            user = json.loads(user_file.read())
        self.email.text = user["email"]

        # toggle connection
        if connected_to_internet()==True:
            connection = "cloud"
            self.cloud.state = "down"
            self.local.state = "normal"
            # update local db
            # download db from firebase
            read = database.child("users").child(user["localId"]).get().val()
            # re -arrange
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
            with open(path + "db.json", "w") as db:
                db.write(json.dumps(data))


        else:
            connection = "local"
            self.local.state = "down"
            self.cloud.state = "normal"



    def button_action( self, button):
        global connection
        if button == "logout":
            wrapper.current = "login"
            # clear login details
            with open(path + "user.json", "w") as user_file:
                user_file.write("")
        elif button == "local":
            connection = "local"
            print(connection)
        elif button == "cloud":
            if connected_to_internet():
                connection = "cloud"
                print(connection)
            else:
                show_popup("NO INTERNET", "you cant switch to cloud mode.\nEnsure you have inernet connection", "info")
                self.local.state = "down"
                self.cloud.state = "normal"

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


