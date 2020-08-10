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
import urllib
from kivy.core.text import LabelBase

# window graphics
from kivy.config import Config

Config.set('graphics', 'fullscreen', 'fake')
Config.set('graphics', 'position', 'center')
Config.set('graphics', 'top', '0')
Config.set('graphics', 'right', '0')
# from kivy.core.window import Window
# Window.borderless = True
# Window.fullscreen = True
# ##################################
LabelBase.register(name="font", fn_regular="font.ttf")

class MyButton(Button):
    #add these three properties in the class
    icon = ObjectProperty(None)
    icon_size = (0,0)
    icon_padding = NumericProperty(0)    #Enter any default value like 50 if you will
                                         #always use an icon, or specify this field
                                         #while creating the button
    def __init__(self, **kwargs):
        #no changes here, just for reference
        return super(MyButton, self).__init__(**kwargs)

class Unify(App):
    def build(self):
        return wrapper


def start():
    Unify().run()


