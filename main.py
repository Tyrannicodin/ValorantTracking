#Import requirements
from json import dump, load
from tkinter import BooleanVar, Button, Label, OptionMenu, StringVar, TclError, Tk, Checkbutton, Toplevel, Frame
from tkinter.messagebox import askyesno
from functools import partial
from client import Client
from time import time as timestamp
from PIL.Image import new
from PIL.ImageDraw import Draw
from PIL.ImageFont import truetype
from random import randint
from collections import Counter
from PIL.ImageTk import PhotoImage
from requests import post, get

#Set constants
MAX_MATCHES = 10
CHECK_INTERVAL = 10
URL = "http://129.151.88.198:5000"

#Init data.json and other files
try:
    open("data.json", "r").close()
except FileNotFoundError:
    with open("data.json", "w") as f:
        dump({"matches":[], "tracked":[]}, f)
try:
    open("arial.ttf").close()
except FileNotFoundError:
    with open("arial.ttf", "wb") as f:
        f.write(get("https://github.com/Tyrannicodin/ValorantTracking/blob/main/arial.ttf?raw=true").content)

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
    info = load(f)
    tracked = [m["ID"] for m in info["matches"]]
    [tracked.append(m["ID"]) for m in info["tracked"]]

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

#View stats
pillowFont = truetype("arial.ttf", 7)
def generate_bar(xNames:list, values:list):
    base = new("RGB", (len(xNames)*32+40, max(values)*20+40), (255, 255, 255))
    bDraw = Draw(base)
    bDraw.line((20, 20, 20, base.height-20, base.width-20, base.height-20), (0, 0, 0), 1)
    for name, value, i in zip(xNames, values, range(len(xNames))):
        bDraw.rectangle(((i+1)*32+4, base.height-21, (i+1)*32+20, ((value+1)*-20)+base.height), (0, 255, 255))
        bDraw.text(((i+1)*32+4, base.height-20), str(name), (0, 0, 0), pillowFont)
    return base

def generate_line(xNames:list, values:list):
    base = new("RGB", (len(xNames)*32+40, max(values)*20+40), (255, 255, 255))
    bDraw = Draw(base)
    bDraw.line((20, 20, 20, base.height-20, base.width-20, base.height-20), (0, 0, 0), 1)
    points = [20, base.height-20]
    for i, value, name in zip(range(len(xNames)), values, xNames):
        points.append((i+1)*32+21)
        points.append(((value+1)*-20)+base.height)
        bDraw.text(((i+2)*20, base.height-20), str(name), (0, 0, 0), pillowFont)
    bDraw.line(points, (0, 255, 255), 1)
    return base

def generate_pie(xNames:list, values:list):
    base = new("RGB", (250, 250), (255, 255, 255))
    bDraw = Draw(base)
    multiplier = 360/sum(values)
    values = [value*multiplier for value in values]
    previous = 0
    for value in values:
        bDraw.pieslice((10, 10, 240, 240), previous, previous+value, (randint(0, 256), randint(0, 256), randint(0, 256)))
        previous += value
    return base

def get_info(info):
    if info == "kills":
        with open("data.json", "r") as f:
            dat = load(f)["matches"]
        tlist = []
        [tlist.extend(a) for a in [p["players"] for p in dat]]
        c = [a["stats"]["kills"] for a in tlist if a["ID"] == cli.puuid]
        return [i+1 for i in range(len(c))], c
    elif info == "maps":
        with open("data.json", "r") as f:
            dat = load(f)["matches"]
        c = Counter([m["map"] for m in dat])
        c = c.items()
        return [map[0] for map in c], [map[1] for map in c]

    elif info == "agents":
        with open("data.json", "r") as f:
            dat = load(f)["matches"]
        tlist = []
        [tlist.extend(a) for a in [p["players"] for p in dat]]
        c = Counter([get(f"https://valorant-api.com/v1/agents/{a['agent']}").json()["data"]["displayName"] for a in tlist if a["ID"] == cli.puuid])
        c = c.items()
        return [agent[0] for agent in c], [agent[1] for agent in c]

GRA_OPTIONS = {
    "bar": generate_bar,
    "pie":generate_pie,
    "line":generate_line
}

def openView():
    def gen_and_open():
        data = get_info(typeVar.get())
        win = Toplevel(viewWindow)
        im=PhotoImage(GRA_OPTIONS[graphVar.get()](*data))
        winIcon = Label(win, image=im)
        winIcon.image = im
        winIcon.pack()
        
    viewWindow = Toplevel(root)
    typeVar = StringVar()
    typeSelector = OptionMenu(viewWindow, typeVar, "kills", "maps", "agents")
    graphVar = StringVar()
    graphSelector = OptionMenu(viewWindow, graphVar, "bar", "pie", "line")
    gen = Button(viewWindow, text="Generate", command=gen_and_open)
    typeSelector.grid(column=0, row=0)
    graphSelector.grid(column=1, row=0)
    gen.grid(column=1, row=1)

#Transfer protocol
class fakeResp:
    def __init__(self):
        self.status_code = 0
def upload_data(uploadButton:Button):
    with open("data.json", "r") as f:
        data = load(f)
    upload = []
    for match in data["matches"]:
        if not match["ID"] in data["tracked"]:
            upload.append(match)
            data["tracked"].append(match["ID"])
    data["matches"] = []
    try:
        response = post(f"{URL}/upload", json=upload, headers={"region":cli.region, "puuid":cli.puuid})
    except ConnectionError:
        response = fakeResp()
    if response.status_code == 200:
        with open("dataDone.json", "w") as f:
            dump(data, f)
        uploadButton.configure(background="green")
    else:
        uploadButton.configure(background="red")

def confirm_upload(uploadButton):
    if askyesno("Uploading data", "This will upload all data from your recorded matches, your player id and region.\nAre you sure you want to do this?"):
        upload_data(uploadButton)

#Add buttons, labels, etc.
trackLabel = Label(root, text="Tracking enabled: ")
trackOn = BooleanVar()
trackOnCheck = Checkbutton(root, variable=trackOn)
trackOnCheck.select()
history = Button(root, text=f"View history ({MAX_MATCHES} matches)", command=openHistory)
view = Button(root, text="View data", command=openView)
upload = Button(root, text="Upload data")
upload.configure(command=partial(confirm_upload, upload))

trackLabel.grid(row=0, column=0)
trackOnCheck.grid(row=0, column=1)
history.grid(row=1, column=0)
view.grid(row=2, column=0)
upload.grid(row=3, column=0)

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
            lastID = dat["ID"]
    elif not trackOn:
        next_check = timestamp() + CHECK_INTERVAL*10
    try:
        root.update()
    except TclError:
        break