# ////////////////////////////////////////////////// GUI ///////////////////////////////////////////////////////
import threading as t
from time import sleep
from tkinter import *
go_button = False
email =""


def start_gui():
    # WIDGETS (GUI)
    def gui_info(text):
        l_info.configure(text=text)

    def gui_get_command(info):
        gui_info(info)
        global go_button
        go_button = False
        while go_button is False:
            sleep(0.1)
        command = e_command.get()
        go_button = False
        e_command.insert(0, "")
        return command

    def pair():
        rx = gui_get_command("Ensure that device \n is connected and enter  yes")
        if rx == "yes":
            gui_info("PAIRING...")
            sleep(3)
            gui_info("DONE, YOU CAN NOW REMOVE \n DEVICE AND PLUG INTO SOURCE")

    # FUNCTIONS
    def clicked_go():
        a = e_command.get()
        global go_button
        go_button = True

    def clicked_pair():
        t.Thread(target=pair).start()

    window = Tk()
    window.geometry("480x320")
    window.title("UNIFY H.A.S")
    # - labels and buttons
    l_user = Label(window, text="Logged in as: " + email, fg="black", bg="red")
    l_info = Label(window, text="", fg="black", bg="white")
    l_devices = Label(window, text="", fg="blue", bg="white")
    e_command = Entry(window, width=50)
    b_go = Button(window, text="GO", bg="blue", fg="black", command=clicked_go)
    b_pair = Button(window, text="PAIR NEW", bg="green", fg="black", command=clicked_pair)
    l_label = Label(window, text="INFO:                                            CONNECTED:")

    # - griding/packing
    l_user.place(height=20, x=300, y=0)
    b_pair.place(height=20, x=300, y=20)
    e_command.place(height=20, x=10, y=280)
    b_go.place(height=20, x=390, y=280)
    l_info.place(height=100, x=10, y=70)
    l_label.place(height=10, x=10, y=50)
    l_devices.place(height=100, x=390, y=70)
    window.mainloop()
