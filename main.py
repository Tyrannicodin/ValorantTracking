#Import requirements
from json import dump, load
from tkinter import BooleanVar, Button, Label, TclError, Tk, Checkbutton, Toplevel, Frame
from requests import get
from functools import partial
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

#Add match to data
def add_match(dat):
    with open("data.json", "r") as f:
        file = load(f)
    file["matches"].append(dat)
    with open("data.json", "w") as f:
        dump(file, f)
        tracked.append(dat["ID"])

with open("data.json", "r") as f:
    tracked = [m["ID"] for m in load(f)["matches"]]

#History
def remove_button_add_match(button, match):
    button.grid_forget()
    add_match(match)

def openHistory():
    historyWindow = Toplevel(root)
    for game in cli.get_history(MAX_MATCHES):
        f = Frame(historyWindow)
        game = get(f"https://pd.{cli.region}.a.pvp.net/match-details/v1/matches/{game['MatchID']}", headers=cli.headers).json()
        game = cli.parse_match(game)
        text=f"Map: {game['map']}      Queue: {game['type']}\nKills: "
        text += str([p["stats"]["kills"] for p in game["players"] if p["ID"] == cli.puuid][0])
        l = Label(f, text=text)
        l.grid(column=0, row=0)
        if not game["ID"] in tracked:
            add = Button(f, text="Add match")
            add.configure(command=partial(remove_button_add_match, add, game))
            add.grid(column=1, row=0)
        f.pack(anchor="n")

#Add buttons, labels, etc.
trackLabel = Label(root, text="Tracking enabled: ")
trackOn = BooleanVar()
trackOnCheck = Checkbutton(root, variable=trackOn)
trackOnCheck.select()
history = Button(root, text=f"View history ({MAX_MATCHES} matches)", command=openHistory)
view = Button(root, text="View data")

trackLabel.grid(row=0, column=0)
trackOnCheck.grid(row=0, column=1)
history.grid(row=1, column=0)
view.grid(row=2, column=0)

#Init values used in mainloop
next_check = timestamp() + CHECK_INTERVAL
lastID = cli.parse_match()["ID"]

#mainloop
while True:
    if timestamp() >= next_check and trackOn:
        next_check = timestamp() + CHECK_INTERVAL
        dat = cli.parse_match()
        if dat["ID"] != lastID:
            add_match(dat)
    elif not trackOn:
        next_check = timestamp() + CHECK_INTERVAL*10
    try:
        root.update()
    except TclError:
        break