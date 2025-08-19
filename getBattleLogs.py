
import os
from dotenv import load_dotenv
import requests
import json
import time

load_dotenv()
CLASH_API_KEY = os.getenv("CLASH_API_KEY")
BASE_URL = os.getenv("BASE_URL")

PLAYER_TAG = "" 
REQUEST_DELAY_SECONDS = 0.15  
top_players = []
#"20250712T160311.000Z-9UR9R9Q8V_LUYG2PY0Y"
#format: YYYYMMDDTHHMMSS.SSSZ_<player_tag>_<player_tag>
battle_id_set = set()  # To avoid duplicate battle IDs
 
SKIPPED_COUNT = 0
ACCEPTED_COUNT = 0

accepted_gamemodes = ["Ranked1v1_NewArena2","Ladder"]
headers = {
    "Accept": "application/json",
    "Authorization": f"Bearer {CLASH_API_KEY}"
}


with open("top_players.csv", "r") as f:
    top_players = f.read().splitlines()

def get_battle_id(player_tag):
    url = f"{BASE_URL}/players/%23{player_tag}/battlelog"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Fetched {len(data)} battles for player {player_tag}")
        for battle in data:
            game_mode = battle.get("gameMode", {})
            mode_name = game_mode.get("name")
            mode_id = game_mode.get("id")
            if mode_name in accepted_gamemodes and mode_id is not None:
                team = battle.get("team", [])
                opponent = battle.get("opponent", [])
                battle_time = battle.get("battleTime")
                tag1 = team[0]["tag"] if team and "tag" in team[0] else "UNKNOWN"
                tag2 = opponent[0]["tag"] if opponent and "tag" in opponent[0] else "UNKNOWN"
                if not battle_time:
                    
                    print(f"Skipping battle (missing battleTime)")
                    continue
                sorted_tags = sorted([tag1, tag2])
                battle_id = f'{battle_time}_{sorted_tags[0]}_{sorted_tags[1]}'
                global ACCEPTED_COUNT
                ACCEPTED_COUNT += 1
                battle_id_set.add(battle_id)
                print(f"{ACCEPTED_COUNT} ladder battles accepted")
            else:
                global SKIPPED_COUNT
                SKIPPED_COUNT += 1
    else:
        print(f"Error fetching battle logs for player {player_tag}: {response.status_code} - {response.text}")
        return []


import sys

def print_progress_bar(iteration, total, prefix='', suffix='', length=40, fill='█', color='\033[92m', reset='\033[0m'):
    percent = f"{100 * (iteration / float(total)):.1f}"
    filled_length = int(length * iteration // total)
    bar = color + fill * filled_length + reset + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% ({iteration}/{total}) {suffix}', end='')
    if iteration == total:
        print()  # New line on complete


# Test with a known player tag (e.g., "2PQLGQQ82" is a valid tag for testing)
# test_player_tag = "2PQLGQQ82"
# print(f"\nTesting get_battle_id with player tag: {test_player_tag}")
# get_battle_id(test_player_tag)
# print("\nCurrent battle_id_set:")
# print(battle_id_set)
# print(len(battle_id_set))  # Print the length of the battle_id_set
# Uncomment below to run for all players as before
total_players = len(top_players)
for idx, i in enumerate(top_players, 1):
    print_progress_bar(idx, total_players, prefix='Progress', suffix=f'Player: {i}', color='\033[94m')
    get_battle_id(i)

print(f"Total battles accepted: {ACCEPTED_COUNT}")
print(f"Total battles skipped: {SKIPPED_COUNT}")