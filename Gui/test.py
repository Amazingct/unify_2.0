from kivy.app import App
from kivy.uix.button import Label, Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
import pyrebase
import json
user_id = ""
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
        user_id = json.loads(user_file.read())["localId"]
        print("logged in: ", id)

except Exception as e:
    user_id = ""
    print(e)


# screens classes
class Login(Screen):
    password = ObjectProperty(None)
    email = ObjectProperty(None)
    r_password = ObjectProperty(None)

    def button_action(self, button):
        if button == "login":
            print("user: ", self.password.text, "password:", self.email.text)
            # sign into database
            try:
                user = auth.sign_in_with_email_and_password(self.password.text, self.email.text)
                print("logged in:", user)
                with open(path + "user.json", "w") as user_file:
                    user_file.write(json.dumps(user))
                wrapper.current = "home"
            except Exception as e:
                print("User dose not exit or Wrong password? Create account using Unify App")
                self.password.text = ""
                self.email.text = ""

        elif button == "register":
            wrapper.current = "register"


class Home(Screen):
    email = ObjectProperty(None)
    h = user_id

    def button_action(self, button):
        if button == "logout":
                wrapper.current = "login"
                with open(path + "user.json", "w") as user_file:
                    user_file.write("")


class Register(Screen):
    password = ObjectProperty(None)
    email = ObjectProperty(None)
    r_password = ObjectProperty(None)

    def button_action(self, button):
        if button == "submit":
            if len(self.password.text) < 6 or self.password.text != self.r_password.text:
                print("Something went wrong")
            else:
                user = auth.create_user_with_email_and_password(self.email.text, self.password.text)
                print(user["localId"])
                # create sensor tag with dummy state
                data = {"IP": "Local_Hub", "Name": "Temperature Sensor", "Type": "S", "State": 0}
                d = database.child(child).child(user["localId"]).push(data)
                self.password.text = ""
                self.email.text = ""
                self.r_password.text = ""
                wrapper.current = "home"


class Wrapper(ScreenManager):
    pass


# load kv file
sign_in_up = Builder.load_file("log_in.kv")

# load screens into Screen Manager
wrapper = Wrapper()
screens = [Login(name="login"), Register(name="register"), Home(name="home")]
for screen in screens:
    wrapper.add_widget(screen)

if user_id == "":
    wrapper.current = "login"
else:
    wrapper.current = "home"


class Unify(App):
    def build(self):
        return wrapper


Unify().run()




