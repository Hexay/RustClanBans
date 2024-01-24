import requests
import json
from datetime import datetime, timezone
import time
import os
import sys
import re

class Api(object):
    def __init__(self, steamKey, discordKey):
        self.steamKey = steamKey
        self.discordKey = discordKey

    def get_data(self, guild, channel, name, offset):
        print("GETTING DATA")
        url = "https://discord.com/api/v9/guilds/" + guild + "/messages/search"
        params = {
            "channel_id": channel,
            "content": name,
            "include_nsfw": "true",
            "offset":offset
        }
        headers = {
            "authorization": self.discordKey
        }
        return requests.get(url, headers=headers, params=params).json()

    def get_steam(self, steamID):
        url = f"http://api.steampowered.com/ISteamUser/GetPlayerBans/v1/?key={self.steamKey}&steamids={steamID}"
        return requests.get(url=url).json()



class Utils(object):
    @staticmethod
    def days_difference(date_str):
        given_date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
        current_date = datetime.utcnow().replace(tzinfo=timezone.utc)
        difference = (current_date - given_date).days
        return difference

    @staticmethod
    def getSteamIDS(text):
        steam_id_pattern = re.compile(r'https://steamcommunity\.com/profiles/(\d+)')
        steam_ids = steam_id_pattern.findall(text)
        return steam_ids


class FileHandler(object):
    @staticmethod
    def read_json(fileDir):
        with open(fileDir, 'r') as f:
            data = f.read()
        return json.loads(data)

    @staticmethod
    def write_json(fileDir, data):
        with open(fileDir, 'w') as f:
            f.write(json.dumps(data))

    @staticmethod
    def list_dir(dir):
        files = os.listdir(dir)
        return files

    @staticmethod
    def read_file(fileDir):
        with open(fileDir, 'r') as f:
            data = f.read()
        return data

    @staticmethod
    def write_file(fileDir, data):
        with open(fileDir, "w", encoding="utf-8") as f:
            f.write(data)



class config(object):
    def __init__(self):
        self.data = self.exists()
        self.steamKey = self.data["steamKey"]
        self.discordKey = self.data["discordKey"]
        self.name = self.data["searchQuery"]
        self.guildID = self.data["guildID"]
        self.channelID = self.data["channelID"]

    def exists(self):
        if "configGB.json" in FileHandler.list_dir(os.getcwd()): # Lists files in current directory
            return FileHandler.read_json("configGB.json")
        else:
            self.no_config()

    def no_config(self):
        print("Copy config file from github!");
        FileHandler.write_json("configGB.json", "")
        time.sleep(3);
        sys.exit()

def find_banned_accounts(data, exploredIDs, bannedInfo):
    FileHandler.write_json("outpu2.txt", data)
    for message in data["messages"]:
        fields = message[0]["embeds"][0]["fields"]
        print(fields)
        print(bannedInfo)

        for i in fields:
            currentField = i["value"]
            currentIDs = Utils.getSteamIDS(currentField)
            for id in currentIDs:
                if id not in exploredIDs:
                    info = api.get_steam(id)["players"][0]
                    exploredIDs[id] = 1
                    FileHandler.write_json("output.txt", info)
                    if info["NumberOfGameBans"]-info["NumberOfVacBans"] >= 1:
                        bannedInfo[id] = (info["DaysSinceLastBan"], info["NumberOfGameBans"])

config = config()
api = Api(config.steamKey, config.discordKey)
data = api.get_data(config.guildID, config.channelID, config.name, 0)
time = time.time()
global exploredIDs
global bannedInfo
exploredIDs = dict()
bannedInfo = dict()
find_banned_accounts(data, exploredIDs, bannedInfo)
offset = 24
total_results = data["total_results"]
while total_results > offset:
    data = api.get_data(config.guildID, config.channelID, config.name, offset)
    find_banned_accounts(data, exploredIDs, bannedInfo)
    offset += 24

bannedString = ""
for i,v in bannedInfo.items():
    bannedString += f"{i} {v[0]} {v[1]}\n"
FileHandler.write_file("output.txt", bannedString)



print(data)



