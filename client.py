from time import sleep
from requests import get
from os import getenv
from ssl import CERT_NONE
from urllib3 import disable_warnings

disable_warnings()

class Client():
    MAPIDS = {
        "/Game/Maps/Canyon/Canyon":"Fracture",
        "/Game/Maps/Foxtrot/Foxtrot":"Breeze",
        "/Game/Maps/Ascent/Ascent":"Ascent",
        "/Game/Maps/Bonsai/Bonsai":"Split",
        "/Game/Maps/Duality/Duality":"Bind",
        "/Game/Maps/Port/Port":"Icebox",
        "/Game/Maps/Triad/Triad":"Haven"}
    def __init__(self):
        self.headers, self.puuid = self.setup()
    def setup(self):
        try:
            with open(f"{getenv('LOCALAPPDATA')}\\Riot Games\\Riot Client\\Config\\lockfile", "r") as f:
                data = f.readline().split(":")
            headers={"Authorization":f"Basic riot:{data[3]}"}
            self.lockfile=data
            region = get(f"{data[4]}://127.0.0.1:{data[2]}/product-session/v1/external-sessions", headers=headers, verify=CERT_NONE, auth=("riot", data[3])).json()
            region = region[list(region.keys())[0]]
            if "launchConfiguration" in region.keys():
                self.region = [b for b in region["launchConfiguration"]["arguments"] if b.startswith("-ares-deployment=")][0].split("=")[-1]
            else:
                raise FileNotFoundError()
            data=get(f"{data[4]}://127.0.0.1:{data[2]}/entitlements/v1/token", headers=headers, verify=CERT_NONE, auth=("riot", data[3])).json()
            headers={
                "Authorization": f"Bearer {data['accessToken']}",
                "X-Riot-Entitlements-JWT": data["token"],
                "X-Riot-ClientVersion": get("https://valorant-api.com/v1/version").json()["data"]["riotClientVersion"]}
            puuid=data["subject"]
            return headers, puuid
        except FileNotFoundError:
            sleep(5)
            return self.setup()
    def get_latest(self):
        match_id=get(f"https://pd.{self.region}.a.pvp.net/match-history/v1/history/{self.puuid}", headers=self.headers).json()
        try:
            match_id=match_id["History"][0]
            data=get(f"https://pd.{self.region}.a.pvp.net/match-details/v1/matches/{match_id['MatchID']}", headers=self.headers).json()
            return data
        except KeyError:
            self.headers, self.puuid = self.setup()
            return self.get_latest()
    def parsed_latest(self):
        data=self.get_latest()
        parsed_data={
            "ID":data["matchInfo"]["matchId"],
            "map":self.MAPIDS[data["matchInfo"]["mapId"]],
            "gameStart":data["matchInfo"]["gameStartMillis"],
            "gameLength":data["matchInfo"]["gameLengthMillis"],
            "completed":data["matchInfo"]["isCompleted"],
            "type":data["matchInfo"]["queueID"],
            "players":[],
            "teams":[],
            "rounds":[]}
        for player in data.get("players", []):
            parsed_player={
                "ID":player["subject"],
                "name":player["gameName"],
                "discriminator":player["tagLine"],
                "team":player["teamId"],
                "agent":player["characterId"],
                "damage":player["roundDamage"],
                "rank":player["competitiveTier"],
                "card":player["playerCard"],
                "title":player["playerTitle"],
                "level":player["accountLevel"],
                "behaviour":{
                    "afkRounds":player["behaviorFactors"]["afkRounds"],
                    "inFriendlyDamage":player["behaviorFactors"]["friendlyFireIncoming"],
                    "outFriendlyDamage":player["behaviorFactors"]["friendlyFireOutgoing"],
                    "spawnRounds":player["behaviorFactors"]["stayedInSpawnRounds"]
                    },
                "stats":{
                    "score":player["stats"]["score"],
                    "rounds":player["stats"]["roundsPlayed"],
                    "kills":player["stats"]["kills"],
                    "deaths":player["stats"]["deaths"],
                    "assists":player["stats"]["assists"],}}
            if "xpModifications" in player.keys():
                parsed_player["xpModifiers"]=player["xpModifications"]
            else:
                parsed_player["xpModifiers"]=[]
            if "sessionPlaytimeMinutes" in player.keys():
                parsed_player["playTime"]=player["sessionPlaytimeMinutes"]
            else:
                parsed_player["playTime"]=0
            if "abilityCasts" in player["stats"].keys():
                parsed_player["stats"]["abilities"]={
                    "Ability 1":player["stats"]["abilityCasts"]["grenadeCasts"],
                    "Ability 2":player["stats"]["abilityCasts"]["ability1Casts"],
                    "Ability 3":player["stats"]["abilityCasts"]["ability2Casts"],
                    "Ultimate":player["stats"]["abilityCasts"]["ultimateCasts"]}
            else:
                parsed_player["stats"]["abilities"]={
                    "Ability 1":0,
                    "Ability 2":0,
                    "Ability 3":0,
                    "Ultimate":0,
                }
            parsed_data["players"].append(parsed_player)
        for team in data.get("teams", []):
            parsed_team={
                "ID":team["teamId"],
                "won":team["won"],
                "rounds":team["roundsPlayed"],
                "roundsWon":team["roundsWon"],
                "points":team["numPoints"]
            }
            parsed_data["teams"].append(parsed_team)
        for round in data.get("roundResults", []):
            parsed_round={
                "round":round["roundNum"],
                "result":round["roundResult"],
                "ending":round["roundCeremony"],
                "winners":round["winningTeam"],
                "bomb":{
                    "plantLocations":round["plantPlayerLocations"],
                    "defuseLocations":round["defusePlayerLocations"],
                    "plantTime":round["plantRoundTime"],
                    "bombLocation":round["plantLocation"],
                    "plantSite":round["plantSite"],
                    "defuseTime":round["defuseRoundTime"],
                },
                "playerStats":[]
            }
            if "bombPlanter" in player.keys():
                parsed_round["bombPlanter"]=round["bombPlanter"]
            else:
                parsed_round["bombPlanter"]=None
            if "bombDefuser" in player.keys():
                parsed_round["bombDefuser"]=round["bombDefuser"]
            else:
                parsed_round["bombDefuser"]=None
            for player in round["playerStats"]:
                parsed_player={
                    "ID":player["subject"],
                    "kills":[],
                    "damage":player["damage"],
                    "score":player["score"],
                    "loadout":{
                        "value":player["economy"]["loadoutValue"],
                        "weapon":player["economy"]["weapon"],
                        "armour":player["economy"]["armor"],
                        "remaining":player["economy"]["remaining"],
                        "spent":player["economy"]["spent"]
                    },
                    "abilities":{
                        "Ability 1":player["ability"]["grenadeEffects"],
                        "Ability 2":player["ability"]["ability1Effects"],
                        "Ability 3":player["ability"]["ability2Effects"],
                        "Ultimate":player["ability"]["ultimateEffects"]},
                    "afk":player["wasAfk"],
                    "penalized":player["wasPenalized"],
                    "stayedInSpawn":player["stayedInSpawn"],
                    }
                for kill in player["kills"]:
                    parsed_kill={
                        "time":kill["roundTime"],
                        "victim":kill["victim"],
                        "location":kill["victimLocation"],
                        "playerLocation":kill["playerLocations"],
                        "assists":kill["assistants"],
                        "finishingDamage":{
                            "type":kill["finishingDamage"]["damageType"],
                            "item":kill["finishingDamage"]["damageItem"],
                            "secondary":kill["finishingDamage"]["isSecondaryFireMode"]
                        }
                    }
                    parsed_player["kills"].append(parsed_kill)
                parsed_round["playerStats"].append(parsed_player)
            parsed_data["rounds"].append(parsed_round)
        return parsed_data