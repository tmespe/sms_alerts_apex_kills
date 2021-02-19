import os
from datetime import datetime
from pprint import PrettyPrinter

import requests
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from dotenv import load_dotenv

from main import send_message

scheduler = BlockingScheduler()
load_dotenv()

API_KEY = os.getenv("GG_TRACKERS_API_KEY")
PHONES = str.split(os.getenv("PHONES"), ",")

BASE_URL = "https://public-api.tracker.gg/apex/v1/standard/profile/"
HEADERS = {"TRN-Api-Key": API_KEY}


def get_player_stats(platform, profile_name, segment_type=None):
    """Gets stats for a given platform (PC, Xbox, PSN) for a given player profile name


    Args:
        platform (int): The platform of the profile (5 = pc, 1 = xbl, 2 = psn)
        profile_name (string): Profile name of player to get data for
    """
    pp = PrettyPrinter(indent=4)

    url = f"{BASE_URL}{platform}/{profile_name}"

    # If segment type is selected use url for fetching segment data
    if segment_type:
        url = f"{url}/segments/{segment_type}"
    # print(url)
    r = requests.get(url, headers=HEADERS)
    # Get json from api data
    json_data = r.json()["data"]

    account_data = {
        "profile_name": profile_name,
        "level": json_data["metadata"]["level"],
        "season_rank": json_data["metadata"]["rankName"],
        "legend_data": [],
    }

    # Get legend data from the children node of the json
    legend_data = json_data["children"]
    # Loop over legends and get stat key and stat value and save in dict
    for legend in legend_data:
        stats = {stat.get("metadata")["name"]: stat.get("displayValue") for stat in legend.get("stats")}

        legend_data = {
            "legend": legend["metadata"]["legend_name"],
            "stats": stats
        }
        account_data["legend_data"].append(legend_data)

    # pp.pprint(account_data)
    return account_data


def check_100_kills(player_stats, legend_to_check):
    legends = player_stats["legend_data"]

    for legend in legends:
        legend_name = legend["legend"].lower()
        if legend_name == legend_to_check.lower():
            kills = legend.get("stats").get("Kills").replace(",", "")
            print(legend_name, kills)
            if int(kills) % 100 == 0:
                return kills
    return False


def check_players():
    magga = get_player_stats(2, "magnusnyquist")
    chilhoss = get_player_stats(2, "chilhoss")
    helibent = get_player_stats(2, "helibent")

    magga_100 = check_100_kills(magga, "gibraltar")
    chilhoss_100 = check_100_kills(chilhoss, "horizon")
    helibent_100 = check_100_kills(helibent, "pathfinder")

    return magga_100, chilhoss_100, helibent_100


@scheduler.scheduled_job(IntervalTrigger(minutes=1))
def send_sms_100():
    players = check_players()
    player_kills = {
        "magga": players[0],
        "chilhoss": players[1],
        # "chilhoss": 500,
        "helibent": players[2],
    }

    for player, kills in player_kills.items():
        if kills:
            for num in PHONES:
                send_message(num, f"Gratulerer {player} med {kills} kills!!!")
                print("Sent message to", num)
    print("Checked stats", datetime.now())


# send_sms_100()
scheduler.start()
