import json
import os
from dataclasses import dataclass

import requests
# from requests import HTTPError
from dotenv import load_dotenv

#

# Initialize scheduler
# scheduler = BlockingScheduler()
load_dotenv()

API_KEY = os.getenv("GG_TRACKERS_API_KEY")
PHONES = str.split(os.getenv("PHONES"), ",")
BASE_URL = "https://public-api.tracker.gg/apex/v1/standard/profile/"
HEADERS = {"TRN-Api-Key": API_KEY}
PLATFORMS = {"xbl": 1,
             "psn": 2,
             "pc": 5}

with open("last_kills.json") as f:
    last_kills = json.load(f)


# Store kills with a legend for a given player
@dataclass
class PlayerLegend:
    """ Class for storing data for a legend for a given player"""
    player_name: str
    legend_name: str
    kills: int


@dataclass
class Player:
    """CLass for storing player data for a given player """
    player_name: str
    platform: str
    legends: list[PlayerLegend]
    level: int = 0
    season_rank: int = 0
    total_kills: int = 0

    def __str__(self):
        return f"{self.player_name}({self.platform}) is a level {self.level} player with a current season rank of " \
               f"{self.season_rank} and {self.total_kills} total kills"


def get_player_stats(platform: str, profile_name: str):
    """Gets stats for a given platform (PC, Xbox, PSN) for a given player

    Args:
        platform (str): The platform of the profile xbl,psn, pc
        profile_name (string): Profile name of player to get data for
    """

    # Get data from apextracker.gg for playername on platform. If unsuccessful print error and exit.
    url = f"{BASE_URL}{PLATFORMS.get(platform)}/{profile_name}"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        if "Account not found" in response.text:
            print(f"No account found for {profile_name} on {platform}. Please check username and/or platform")
        raise ValueError(e)

    # Get json from request object and check if valid
    try:
        json_data = response.json()["data"]
        level = json_data["metadata"]["level"]
        season_rank = json_data["metadata"]["rankName"]
    except KeyError as e:
        print("Account data is invalid")
        raise

    # Extract legend stats for all legends
    legends = get_legend_stats(json_data, profile_name=profile_name)
    # Calculate total kills with all legends
    kills = sum(legend.kills for legend in legends)

    # Instantiate a new Player dataclass representing a player's stats
    player = Player(player_name=profile_name, legends=legends, level=level, season_rank=season_rank,
                    platform=platform.lower(), total_kills=kills)

    print(player)
    return player


def get_legend_stats(json_data: json, profile_name: str):
    """
    Extract legend stats from apextracker.gg api and returns a list of PlayerLegend dataclass
    :param json_data: apextracker.gg api result
    :param profile_name: A player's profile name
    :return: PlayerLegend dataclass (profile_name, legend_name, kills)
    """
    legends = []
    for legend_data in json_data["children"]:
        legend_name = legend_data["metadata"]["legend_name"]
        try:
            kills = legend_data["stats"][0].get("value")
        except IndexError:
            kills = 0
        legends.append(PlayerLegend(profile_name, legend_name, kills))
    return legends


def check_100_kills(player_stats, legend_to_check):
    legends = player_stats["legend_data"]
    player_name = player_stats["profile_name"]

    for legend in legends:
        legend_name = legend["legend"].lower()
        if legend_name == legend_to_check.lower():
            kills = legend.get("stats").get("Kills").replace(",", "")
            if last_kills[player_name] == kills:
                print(f"No new kills for {player_name}")
                break
            else:
                last_kills[player_name] = kills
                with open("last_kills.json", "a") as f:
                    json.dump(last_kills, f)
                print(legend_name, kills)
                if int(kills) % 50 == 0:
                    return kills
    return False


def get_players(**platform_player):
    """

    :params Platform_player: Player platform in the form of player1="xbl player_name", player2="psn player2_name"
    :return: A list of the Player dataclass for all players
    """
    players = []
    for player in platform_player.values():
        try:
            player = player.split(" ")
            player_stats = get_player_stats(player[0], player[1])
            players.append(player_stats)
        except ValueError as e:
            print(e)
    # for player in platform_player.values():
    #     player = player.split(" ")
    #     get_player_stats(player[0], player[1])
    return players


# @scheduler.scheduled_job(IntervalTrigger(minutes=1))
# def send_sms_100():
#     players = check_players()
#     player_kills = {
#         "magga": players[0],
#         "chilhoss": players[1],
#         #"chilhoss": 500,
#         "helibent": players[2],
#     }

#     for player, kills in player_kills.items():
#         if kills:
#             for num in PHONES:
#                 send_message(num, f"Gratulerer {player} med {kills} kills!!!")
#                 print("Sent message to", num)
#     print("Checked stats", datetime.now())


# send_sms_100()
# scheduler.start()

# get_player_stats("psn", "heli_bent")
get_players(player1="psn x", player2="psn magnusnyquist", player3="psn chilhoss")
