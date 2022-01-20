#Import requirements
from json import dump, load
from tkinter import BooleanVar, Button, Label, TclError, Tk, Checkbutton
from client import Client
from time import time as timestamp

#Set constans
MAX_MATCHES = 10
CHECK_INTERVAL = 10

#Init data.json
try:
    open("data.json", "r").close()
except FileNotFoundError:
    with open("data.json", "w") as f:
        dump({"matches":[]}, f)

#See client.py
cli = Client()

#Init tkinter widget
root = Tk()
root.wm_title("Valorant tracker")

#Add buttons, labels, etc.
trackLabel = Label(root, text="Tracking enabled: ")
trackOn = BooleanVar()
trackOnCheck = Checkbutton(root, variable=trackOn)
trackOnCheck.select()
history = Button(root, text=f"View history ({MAX_MATCHES} matches)")
view = Button(root, text="View data")

trackLabel.grid(row=0, column=0)
trackOnCheck.grid(row=0, column=1)
history.grid(row=1, column=0)
view.grid(row=2, column=0)

#Init values used in mainloop
next_check = timestamp() + CHECK_INTERVAL
lastID = cli.parsed_latest()["ID"]

#mainloop
while True:
    if timestamp() >= next_check and trackOn:
        next_check = timestamp() + CHECK_INTERVAL
        dat = cli.parsed_latest()
        if dat["ID"] != lastID:
            with open("data.json", "r") as f:
                file = load(f)
            file["matches"].append(dat)
            with open("data.json", "w") as f:
                dump(file, f)
    elif not trackOn:
        next_check = timestamp() + CHECK_INTERVAL*10
    try:
        root.update()
    except TclError:
        break