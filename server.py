from flask import Flask, request
from json import load, dump, loads

app = Flask(__name__)

@app.post("/upload")
def upload():
    headers = request.headers
    data = loads(request.data)
    try:
        with open(f"{headers['Region']}.json", "r") as f:
            locdat = load(f)
    except FileNotFoundError:
        with open(f"{headers['Region']}.json", "w") as f:
            dump({"matches":[], "tracked":[]}, f)
            locdat = {"matches":{}, "tracked":[]}
    save = []
    for match in data:
        if not match["ID"] in locdat["tracked"]:
            match["submitted_by"] = [headers["Puuid"]]
            match.pop("completed")
            match["rounds"] = len(match["rounds"])
            for player in match["players"]:
                player.pop("damage")
                player.pop("xpModifiers")
                player["stats"].pop("abilities")
            save.append(match)
            locdat["tracked"].append(headers["Puuid"])
        else:
            i = locdat["matches"].index([m for m in locdat["matches"] if m["ID"] == match["ID"]][0])
            locdat["matches"][i]["submitted_by"].append(headers["Puuid"])
    locdat["matches"].extend(save)
    with open(f"{headers['Region']}.json", "w") as f:
        dump(locdat, f)
    return {"status":200}

app.run()